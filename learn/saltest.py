import matplotlib
matplotlib.use('agg')

import os
import theano
import numpy as np

from sklearn.cluster import KMeans
from sals.utils.ImageHelper import immontage, imsave, imresize, drawrect

from sals.utils.DataHelper import DataMan_viper
from sals.utils.utils import loadfile, savefile

import pylab as pl 

def main():
	''' pipeline for testing and evaluation '''
	# preset parameters
	save_path = '../data_viper/model/'

	# load data
	imL = 48
	bs = 100
	datafile_viper = '../data_viper/viper_class.pkl'
	viper = loadfile(datafile_viper)

	# load model
	modelfile_viper = '../data_viper/model/model.pkl'
	model = loadfile(modelfile_viper)

	# evaluation and testing
	# test_x = viper.test_x.get_value(borrow=True)
	test_x = np.asarray(viper.test_ims)
	test_y = viper.test_y.get_value(borrow=True)
	n_test = test_x.shape[0]
	n_batches_test = np.int(1.0*n_test/bs)
	n_test = n_batches_test * bs
	test_ypred = [model.test(i)[-1] for i in range(n_batches_test)]
	test_ypred = np.asarray(test_ypred).flatten()

	test_ims = test_x[:n_test].reshape((n_test, imL, imL, -1))

	# assign predicted scores to images
	h, w = viper.imgs[0].shape[:2]
	mh, mw = len(np.unique(viper.yy)), len(np.unique(viper.xx))
	msk0 = np.zeros(mh*mw)
	msks = [msk0.copy() for im in viper.imgs]

	showlist = []
	for i in range(n_test):
		imgid = viper.test_imgids[i]
		patid = viper.test_ctrids[i]
		score = test_ypred[i]
		msks[imgid][patid] = score

	# resize predicted salience map to match image size
	msks_rs = [imresize(msk.reshape((mh, mw)), size=(h, w))/255. for msk in msks]

	# save salience map for comparison
	test_imids = np.asarray(np.unique(viper.test_imgids))
	salmap_gt = np.asarray(viper.salmsks) #np.asarray([viper.salmsks[imid] for imid in test_imids])
	salmap_pred = np.asarray(msks_rs) #np.asarray([msks_rs[imid]/255. for imid in test_imids])
	savefile(save_path+'salmaps_comparison.pkl', [test_imids, salmap_gt, salmap_pred])

	# quantize to show different test patches
	kmeans = KMeans(init='k-means++', n_clusters=10, n_init=10)
	kmeans.fit(test_ypred.reshape(n_test, 1))

	# save to result folder
	for i in range(10):
		idx = kmeans.labels_== i
		if any(idx): 
			im = immontage(list(test_ims[idx])) 
			imsave(save_path+'{}.jpg'.format(kmeans.cluster_centers_[i]), im)

	print 'testing finished'
	os.system('xdg-open '+save_path)

if __name__ == '__main__':

    main()