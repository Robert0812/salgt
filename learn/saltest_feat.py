import matplotlib
matplotlib.use('agg')

import os
import theano
import numpy as np

from sklearn.cluster import KMeans
from sals.utils.ImageHelper import immontage, imsave, imresize

from sals.utils.DataHelper import DataMan_viper
from sals.utils.utils import loadfile, savefile

import pylab as pl 

def main():
	''' pipeline for testing and evaluation '''
	# preset parameters
	save_path = '../data_viper/model_feat/'

	# load data
	# imL = 48
	bs = 100
	datafile_viper = '../data_viper/viper.pkl'
	viper = loadfile(datafile_viper)

	# load model
	modelfile_viper = '../data_viper/model_feat/model.pkl'
	model = loadfile(modelfile_viper)

	# evaluation and testing
	# test_x = viper.test_x.get_value(borrow=True)
	test_x = np.asarray(viper.test_feat)
	test_y = viper.test_y
	n_test = test_x.shape[0]
	test_ypred = model.predict(viper.test_feat)
	test_ypred = np.asarray(test_ypred).flatten()

	# test_ims = test_x.reshape((n_test, imL, imL, -1))

	# assign predicted scores to images
	h, w = viper.imgs[0].shape[:2]
	mh, mw = len(np.unique(viper.yy)), len(np.unique(viper.xx))
	msk0 = np.zeros(mh*mw).astype(np.uint8)
	msks = [msk0.copy() for im in viper.imgs]

	showlist = []
	for i in range(n_test):
		imgid = viper.test_imgids[i]
		patid = viper.test_ctrids[i]
		score = test_ypred[i]
		msks[imgid][patid] = score*255

	# resize predicted salience map to match image size
	msks_rs = [imresize(msk.reshape((mw, mh)).T, size=(h, w))/255. for msk in msks]

	# save salience map for comparison
	test_imids = np.asarray(np.unique(viper.test_imgids))
	salmap_gt = np.asarray(viper.salmsks) #np.asarray([viper.salmsks[imid] for imid in test_imids])
	salmap_pred = np.asarray(msks_rs) #np.asarray([msks_rs[imid]/255. for imid in test_imids])
	savefile(save_path+'salmaps_comparison.pkl', [test_imids, salmap_gt, salmap_pred])

	# quantize to show different test patches
	# kmeans = KMeans(init='k-means++', n_clusters=10, n_init=10)
	# kmeans.fit(test_ypred.reshape(n_test, 1))

	# # save to result folder
	# for i in range(10):
	# 	idx = kmeans.labels_== i
	# 	if any(idx): 
	# 		im = immontage(list(test_ims[idx])) 
	# 		imsave(save_path+'{}.jpg'.format(kmeans.cluster_centers_[i]), im)

	print 'testing finished'

if __name__ == '__main__':

    main()