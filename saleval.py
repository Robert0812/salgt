import matplotlib
matplotlib.use('agg')

import os
import numpy as np
from sals.utils.utils import loadfile, savefile

from sals.utils.ImageHelper import immontage, imsave, imresize, mapresize
from sals.utils.FunctionHelper import get_roc_curve, abs_error

import pylab as pl 


def main():
	''' pipeline for evaluating salience '''
	# three types: 
	# 1) unsupervised, knnsal
	# 2) groundtruth, gtsal 
	# 3) prediction, predsal

	## load cnn salience with groundtruth
	supsal_path = '../data_viper/model_feat/salmaps_comparison.pkl'
	test_imids, salmap_gt, salmap_pred = loadfile(supsal_path)

	mapsz = salmap_gt[0].shape

	## load knn salience 
	knnsal_path = '../data_viper/salience_all.mat'
	tmp = loadfile(knnsal_path)
	knn_gal = tmp['salience_all_gal'] # view a
	knn_prb = tmp['salience_all_gal'] # view b

	labeled_imidx_path = '../data_viper/labeled_imidx.mat'
	tmp = loadfile(labeled_imidx_path)
	labeled_imidx = tmp['labeled_imidx'].flatten()
	salmap_knn_small = knn_gal[:, :, labeled_imidx].transpose((2, 0, 1))
	salmap_knn_all = [mapresize(im, size=mapsz) for im in salmap_knn_small]

	# get rid of background for better illustration 
	datafile_viper = '../data_viper/viper.pkl'
	viper = loadfile(datafile_viper)
	salmap_knn = []
	for seg, msk in zip(viper.segmsks, salmap_knn_all): 
		idx = seg == 0
		msk[idx] = 0
		salmap_knn.append(msk)
	salmap_knn = np.asarray(salmap_knn)

	# qualitative evaluation
	save_path = '../data_viper/model_feat/'
	for i in test_imids:
		pl.figure(1)
		pl.subplot(1, 4, 1) # show image
		pl.imshow(viper.imgs[i])
		pl.title('image')
		pl.subplot(1, 4, 2) # show groundtruth salience
		pl.imshow(salmap_gt[i]*255., cmap='hot', vmin=0, vmax=255)
		pl.title('groundtruth')
		pl.subplot(1, 4, 3) # show knn salience
		pl.imshow(salmap_knn[i]*255., cmap='hot', vmin=0, vmax=255)
		pl.title('KNN salience')
		pl.xlabel('abserr={0:.2f}'.format(abs_error(salmap_knn[i], salmap_gt[i])))
		pl.subplot(1, 4, 4) # show CNN prediction salience
		pl.imshow(salmap_pred[i]*255., cmap='hot', vmin=0, vmax=255)
		pl.title('LR salience')
		pl.xlabel('abserr={0:.2f}'.format(abs_error(salmap_pred[i], salmap_gt[i])))
		pl.savefig(save_path + '{0:03d}.jpg'.format(i))
		print save_path +'{0:03d}.jpg'.format(i) + ' saved!'

	# quantitative evaluation
	test_idx = np.unique(test_imids)
	print 'mean abs error - KNN vs Gt: {0:.2f}'.format(abs_error(salmap_knn[test_idx], salmap_gt[test_idx]))
	print 'mean abs error - SVR vs Gt: {0:.2f}'.format(abs_error(salmap_pred[test_idx], salmap_gt[test_idx]))

	# pl.figure(2)	
	# test_idx = np.unique(test_imids)
	# recall_knn, precision_knn = get_roc_curve(salmap_gt[test_idx], salmap_knn[test_idx])
	# pl.plot(recall_knn, precision_knn, 'b', linewidth=2, label='knn vs. gt')
	# recall_cnn, precision_cnn = get_roc_curve(salmap_gt[test_idx], salmap_pred[test_idx])
	# pl.plot(recall_cnn, precision_cnn, 'r', linewidth=2, label='cnn vs. gt')
	# pl.xlabel('recall')
	# pl.ylabel('precision')
	# pl.legend()
	# pl.savefig(save_path+'roc.jpg')
	# print 'ROC curve saved!'

	os.system('xdg-open '+save_path)

if __name__ == '__main__':

    main()