import matplotlib
matplotlib.use('agg')

import numpy as np

from sals.utils.utils import *
from sals.utils.ImageHelper import immontage, imshow, mapresize

import pylab as pl 
import os

def histmapping(hist1, hist2):
	j = 0
	sum_i = 0
	sum_j = hist2[j]
	nbin1 = len(hist1)
	nbin2 = len(hist2)
	mapping  = np.zeros(nbin1)

	for i in np.arange(nbin1):
		
		sum_i += hist1[i]
		if sum_i <= sum_j or (int(sum_i)==1 and int(sum_j) == 1):
			mapping[i] = float(j)/nbin2
		else:
			j_start = j 
			while sum_i > sum_j and j < nbin2-1:
				j += 1
				sum_j += hist2[j]
			mapping[i] = float(np.mean((j_start, j)))/nbin2

	return mapping

def get_calibrated_gtsal():
	''' get calibrated groundtruth salience maps '''

	# load viper dataset
	viper = loadfile('../../data_viper/viper.pkl')

	## load knn salience 
	knnsal_path = '../../data_viper/salience_all.mat'
	tmp = loadfile(knnsal_path)
	knn_gal = tmp['salience_all_gal'] # view a
	knn_prb = tmp['salience_all_gal'] # view b

	mapsz = viper.imgs[0].shape[:2]

	labeled_imidx_path = '../../data_viper/labeled_imidx.mat'
	tmp = loadfile(labeled_imidx_path)
	labeled_imidx = tmp['labeled_imidx'].flatten()
	salmap_knn_small = knn_gal[:, :, labeled_imidx].transpose((2, 0, 1))
	salmap_knn_all = [mapresize(im, size=mapsz) for im in salmap_knn_small]

	knn_arr = []
	gt_arr = []
	for seg, sal, msk in zip(viper.segmsks, viper.salmsks, salmap_knn_all): 
		idx = seg != 0
		gt_arr	= np.hstack((gt_arr, sal[idx]))
		knn_arr = np.hstack((knn_arr, msk[idx]))

	nBin_gt = 100
	nBin_knn = 100
	gt_hist = np.histogram(gt_arr, bins=nBin_gt, range=(0, 1))[0]/float(len(gt_arr))
	knn_hist = np.histogram(knn_arr, bins=nBin_knn, range=(0, 1))[0]/float(len(knn_arr))
	
	mapping = np.asarray(histmapping(knn_hist, gt_hist))

	pl.figure(1)
	pl.plot(mapping)
	pl.savefig('mapping.jpg')

	# mapping from knn to gt maps
	# salmap_knn_mapped = [mapping[np.floor(sal*nBin_knn).astype(int)] for sal in salmap_knn_small]
	salmap_gt_mapped = [mapping[np.floor(sal*nBin_gt).astype(int)] for sal in viper.salmsks]
	return salmap_gt_mapped


def main():

	salmap_gt_mapped = get_calibrated_gtsal()

	pl.figure(1)
	pl.imshow(immontage(salmap_gt_mapped, [6, 17]))
	pl.savefig('tmp1.jpg')
	os.system('open tmp1.jpg')

if __name__ == '__main__':

	main()