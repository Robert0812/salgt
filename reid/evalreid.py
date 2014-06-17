import matplotlib
matplotlib.use('agg')

import os
import numpy as np

from glob import glob
from scipy.spatial.distance import cdist	
import time

from sals.utils.utils import *
from sals.utils.ImageHelper import mapresize


def patchmatch(imfeat1, imfeat2, ny, nx):
	''' generate patch matching distances, return an ny by nx distance matrix '''

	pwdist = np.zeros((ny, nx))
	indmat = np.zeros((ny, nx))
	# take out each row
	for y in range(ny):
		dist = cdist(imfeat1[y], imfeat2[y])
		pwdist[y] = dist.min(axis=1)
		indmat[y] = dist.argmin(axis=1)

	return pwdist, indmat


def rearrange_feat(imfeats, ny, nx):
	'''
		INPUT: n_im by n_pat by n_feat, (n_pat patches are in F order)
		OUTPUT: n_im by n_row by n_colomn by n_feat 
	''' 
	n_im, n_pat, n_feat = imfeats.shape
	return imfeats.reshape((n_im, ny, nx, n_feat), order='F')

def compute_cmc(pwdist):
	''' compute CMC 
		INPUT: pairwise matching distance (query to gallery distances)
		OUTPUT: a vector representing CMC 
	'''
	
	qsize, gsize = pwdist.shape
	
	order = np.argsort(pwdist, axis=1)
	match = order == np.tile(np.arange(qsize).reshape((qsize, 1)), (1, gsize))
	cmc = match.sum(axis=0).cumsum()/float(qsize)
	return cmc
	
def get_mask(segmsks, ny, nx):
	''' get foreground masks '''
	return np.asarray([mapresize(msk, size=(ny, nx))>0 for msk in segmsks])


def get_knn_salience(labeled_imidx, ny, nx):
	''' as name '''
	knnsal_path = '../../data_viper/salience_all.mat'
	tmp = loadfile(knnsal_path)
	knn_gal = tmp['salience_all_gal'] # view a
	knn_prb = tmp['salience_all_prb'] # view b

	salmap_knn_sub = knn_gal[:, :, labeled_imidx].transpose((2, 0, 1))
	salmap_knn_query = [mapresize(im, size=(ny, nx)) for im in salmap_knn_sub]

	salmap_knn_sub = knn_prb[:, :, labeled_imidx].transpose((2, 0, 1))
	salmap_knn_gallery = [mapresize(im, size=(ny, nx)) for im in salmap_knn_sub]

	return np.asarray(salmap_knn_query), np.asarray(salmap_knn_gallery)

def get_gt_salience(ny, nx):
	''' get groundtruth salience ''' 
	gtsal_path = '../../data_viper/salience_gt.pkl'
	salmap_gt_query = loadfile(gtsal_path)

	return np.asarray([mapresize(im, size=(ny, nx)) for im in salmap_gt_query])

def tsal2(sal2, ind_x):
	''' transformed salience in gallery image '''
	ny, nx = ind_x.shape
	ind_y = np.tile(np.arange(ny).reshape((ny, 1)), [1, nx])

	return sal2[ind_y, ind_x]


def evaluation(pwdists, indmats, fgmsk, knnsal_query, knnsal_gallery, evaltag, n_eval=80, nTrial=10):
	''' compute image pairwise distances '''
	
	sigma = 2.8

	cmc = []
	func = []
	tag = []
	
	# define functions to be evaluated
	# func.append(lambda sim, ind,sal1, sal2: sim.sum())
	# tag.append( 'masked patch match')
	# func.append(lambda sim, ind, sal1, sal2: (sal1*sim).sum())
	# tag.append( evaltag + ' salience')
	func.append(lambda sim, ind, sal1, sal2: (sim/(1+abs(sal1-tsal2(sal2, ind)))).sum())
	tag.append( evaltag + ' salience')


	n_total = pwdists.shape[0]

	for t in range(nTrial):
		print 'evaluation trial {}'.format(t)
		np.random.seed(t)
		trial_idx 		= np.random.permutation(n_total)[:n_eval]
		pwdists_trial 	= pwdists[:, trial_idx][trial_idx]
		indmats_trial 	= indmats[:, trial_idx][trial_idx]

		impwdists 		= [np.zeros((n_eval, n_eval)) for f in func]
		for i, msk, sal1, sal2 in zip(range(n_eval), fgmsk[trial_idx], knnsal_query[trial_idx], knnsal_gallery[trial_idx]):
			for j in range(n_eval):
				# convert distances to similarity
				sim = np.exp(-(pwdists_trial[i, j])/(sigma**2))**2
				sim[~msk] = 0 
				ind = indmats_trial[i, j]
				for k, evalfun in zip(range(len(func)), func):
					impwdists[k][i, j] = evalfun(sim, ind, sal1, sal2)

		cmc.append([compute_cmc(-impw) for impw in impwdists])


	return np.asarray(cmc).mean(axis=0), tag


def main():

	# load viper dataset
	viper = loadfile('../../data_viper/viper.pkl')
	ny = viper.ny+1
	nx = viper.nx+1
	feats_query = rearrange_feat(viper.feats, ny, nx)

	# load gallery features
	labeled_imidx_path = '../../data_viper/labeled_imidx.mat'
	tmp = loadfile(labeled_imidx_path)
	labeled_imidx = tmp['labeled_imidx'].flatten()

	gallery_feat_path = '../../data_viper/galleryfeats.mat'
	tmp = loadfile(gallery_feat_path)
	galleryfeats = np.asarray(tmp['galleryfeats'], dtype=float).transpose((2, 1, 0))

	feats_gallery = rearrange_feat(galleryfeats, ny, nx)

	# patch matching 
	patch_match_path = '../../data_viper/pwmap.pkl'
	
	if not os.path.isfile(patch_match_path):
		
		n_query = feats_query.shape[0]
		n_gallery = feats_gallery.shape[0]
		pwdists = np.zeros((n_query, n_gallery, ny, nx), dtype=float)
		indmats = np.zeros((n_query, n_gallery, ny, nx), dtype=int)
		for iq in range(n_query):
			for ig in range(n_gallery):
				t0 = time.clock()
				pwdists[iq, ig, :, :], indmats[iq, ig, :, :] = patchmatch(feats_query[iq], feats_gallery[ig], ny, nx)
				t1 = time.clock()
				print '{0:02d}-{1:02d}: eclapsed {2:.2f} sec'.format(iq, ig, t1-t0)

		savefile(patch_match_path, [pwdists, indmats])
	
	else:
		pwdists, indmats = loadfile(patch_match_path)

	# masked patch matching
	fgmsk = get_mask(viper.segmsks, ny, nx)
	# knn salience
	knnsal_query, knnsal_gallery = get_knn_salience(labeled_imidx, ny, nx)
	# gt salience
	gtsal_query = get_gt_salience(ny, nx)

	# evaluation 
	cmc_knn, tag_knn = evaluation(pwdists, indmats, fgmsk, knnsal_query, knnsal_gallery, evaltag='knn', n_eval=30, nTrial=5)
	cmc_gt, tag_gt = evaluation(pwdists, indmats, fgmsk, gtsal_query, knnsal_gallery, evaltag='gt', n_eval=30, nTrial=5)
	
	cmc_all = np.vstack((cmc_knn, cmc_gt[-1]))
	tag_all = tag_knn 
	tag_all.append(tag_gt[-1])

	import pylab as pl
	for cmc, tag in zip(cmc_all, tag_all):
		pl.plot(cmc, label=tag)

	pl.legend()
	pl.axis([0, 30, 0.5, 1])
	pl.show()
	pl.savefig('tmp1.jpg')
	os.system('xdg-open tmp1.jpg')


if __name__ == '__main__':

	main()