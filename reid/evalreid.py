from glob import glob
from scipy.spatial.distance import cdist	
import time

from sals.utils.utils import *
import numpy as np

def patchmatch(imfeat1, imfeat2, ny, nx):
	''' generate patch matching distances, return an ny by nx distance matrix '''

	pwdist = np.zeros((ny, nx))
	indmat = np.zeros((ny, nx))
	# take out each row
	for y in range(ny):
		dist = cdist(imfeat1[y], imfeat2[y])
		pwdist[y] = dist.min(axis=1)
		indmat[y] = dist.argmin(axis=1)


def rearrange_feat(imfeats, ny, nx):
	'''
		INPUT: n_im by n_pat by n_feat, (n_pat patches are in F order)
		OUTPUT: n_im by n_row by n_colomn by n_feat 
	''' 
	n_im, n_pat, n_feat = imfeats.shape
	return imfeats.reshape((n_im, ny, nx, n_feat), order='F')

def compute_cmc(pwdist):
	''' compute CMC '''
	
	
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
		pwdists = np.zeros((n_query, n_gallery))
		for iq in range(n_query):
			for ig in range(n_gallery):
				t0 = time.clock()
				pwdists[iq, ig] = patchmatch(feats_query[iq], feats_gallery[ig], ny, nx)
				t1 = time.clock()
				print '{0:02d}-{1:02d}: eclapsed {2:.2f} sec'.format(iq, ig, t1-t0)

		savefile(patch_match_path, pwdists)
	
	else:
		loadfile(patch_match_path)

	# salience matching 




if __name__ == '__main__':

	main()