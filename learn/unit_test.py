import matplotlib
matplotlib.use('agg')

import os

from sals.utils.ImageHelper import imresize, immontage, imsave, imshow, drawrect
from sals.utils.utils import savefile, loadfile
import numpy as np
from sals.utils.FunctionHelper import abs_error

import pylab as pl

def downsample_data(viper, ntrn = 1000, nbin=10):

	train_y10 = np.ceil(viper.train_y*nbin).astype(np.int32)
	train_ctrids = []
	train_imgids = []
	train_feat = []
	train_y = []
	for y in np.unique(train_y10):
		index_y = np.where(train_y10 == y)[0]
		index_sp = np.random.permutation(len(index_y))[:min(len(index_y), ntrn)]
		index = index_y[index_sp]
		train_ctrids.append(viper.train_ctrids[index])
		train_imgids.append(viper.train_imgids[index])
		train_feat.append(viper.train_feat[index])
		train_y.append(viper.train_y[index])

	viper.train_ctrids = np.hstack(np.asarray(train_ctrids))
	viper.train_imgids = np.hstack(np.asarray(train_imgids))
	viper.train_feat = np.vstack(np.asarray(train_feat))
	viper.train_y = np.hstack(np.asarray(train_y))
	print 'Training samples downsampled'
	return viper

def test_knn():

	datafile_viper = '../data_viper/viper.pkl'
	viper = loadfile(datafile_viper)
	viper = downsample_data(viper)
	# from sklearn.neighbors import KNeighborsRegressor
	# model = KNeighborsRegressor(n_neighbors=5, weights='uniform', metric='euclidean')
	# model.fit(viper.train_feat, viper.train_y)
	from sklearn.neighbors import KDTree
	
	# divide into stripes
	nStripe = 10
	y_max = viper.yy.max()
	y_min = viper.yy.min()
	y_len = np.int((y_max - y_min)/10.)
	y_centers = np.round(np.linspace(y_min+y_len, y_max-y_len, nStripe))

	k = 5
	y_ctr = y_centers[k] 

	stripe_idx = np.where((viper.yy[viper.train_ctrids] >= y_ctr-y_len) & (viper.yy[viper.train_ctrids] < y_ctr+y_len))[0]
	
	model = KDTree(viper.train_feat[stripe_idx, :288], metric='euclidean')

	train_patset = viper.get_patchset('train')
	test_patset = viper.get_patchset('test')

	test_ids = np.where((viper.yy[viper.test_ctrids] >= y_ctr-y_len) & (viper.yy[viper.test_ctrids] < y_ctr+y_len))[0]
	np.random.shuffle(test_ids)
	for i in test_ids:

		get_testrect = lambda i: [viper.xx[viper.test_ctrids[i]] - viper.patL/2, 
								viper.yy[viper.test_ctrids[i]] - viper.patL/2,
								viper.patL, viper.patL]

		get_trainrect = lambda i: [viper.xx[viper.train_ctrids[i]] - viper.patL/2, 
								viper.yy[viper.train_ctrids[i]] - viper.patL/2,
								viper.patL, viper.patL]

		gray2color = lambda grayim: np.dstack((grayim, grayim, grayim))

		imlist = []
		patlist = []
		maplist = []
		patlist.append(imresize(test_patset[i], size=(100, 100)))
		imlist.append(drawrect(viper.imgs[viper.test_imgids[i]], get_testrect(i)))
		maplist.append(viper.salmsks[viper.test_imgids[i]])
		dist, ind = model.query(viper.test_feat[i, :288], k=30, return_distance=True)
		print viper.test_y[i]
		hist = np.histogram(viper.train_y[stripe_idx[ind[0]]])
		print hist[0]
		print hist[1]
		print dist
		for id in stripe_idx[ind[0]]:
			patlist.append(imresize(train_patset[id], size=(100, 100)))
			imlist.append(drawrect(viper.imgs[viper.train_imgids[id]], get_trainrect(id)))
			maplist.append(viper.salmsks[viper.train_imgids[id]])
		pats = immontage(patlist)
		imgs = immontage(imlist)
		maps = immontage(maplist)
		imsave('tmp1.jpg', pats)
		imsave('tmp2.jpg', imgs)
		imsave('tmp3.jpg', maps)

		raw_input()

	os.system('xdg-open tmp1.jpg')

def test_linear_regression():
	datafile_viper = '../data_viper/viper.pkl'
	viper = loadfile(datafile_viper)

	from sklearn.linear_model import LinearRegression

	model = LinearRegression(normalize=True)
	model.fit(viper.train_feat, viper.train_y)

	y_pred = model.predict(viper.test_feat)
	print 'testing error {}'.format(abs_error(y_pred, viper.test_y)) 


def test_ridge_regression():
	datafile_viper = '../data_viper/viper.pkl'
	viper = loadfile(datafile_viper)

	from sklearn.linear_model import Ridge

	model = Ridge(alpha=100)
	model.fit(viper.train_feat, viper.train_y)

	y_pred = model.predict(viper.test_feat)
	print 'testing error {}'.format(abs_error(y_pred, viper.test_y)) 

def test_lasso_regression():
	datafile_viper = '../data_viper/viper.pkl'
	viper = loadfile(datafile_viper)

	from sklearn.linear_model import Lasso

	model = Lasso(alpha=1e-3)
	model.fit(viper.train_feat, viper.train_y)

	y_pred = model.predict(viper.test_feat)
	print 'testing error {}'.format(abs_error(y_pred, viper.test_y)) 

def test_SVR():
	datafile_viper = '../data_viper/viper.pkl'
	viper = loadfile(datafile_viper)

	from sklearn.svm import SVR
	model = SVR(C=10, kernel='rbf', shrinking=False, verbose=True)

	model.fit(viper.train_feat, viper.train_y)

	y_pred = model.predict(viper.test_feat)
	print 'testing error {}'.format(abs_error(y_pred, viper.test_y)) 

def test_knn_regression():

	datafile_viper = '../data_viper/viper.pkl'
	viper = loadfile(datafile_viper)

	from sklearn.neighbors import KNeighborsRegressor
	model = KNeighborsRegressor(n_neighbors=5, weights='uniform', metric='euclidean')
	model.fit(viper.train_feat, viper.train_y)

	n_test = len(viper.test_feat)
	y_pred = np.zeros(n_test)
	for i, feat in zip(np.arange(n_test), viper.test_feat):
		dist, ind = model.kneighbors(feat)
		y_pred[i] = (viper.train_y[ind]*np.exp(-dist**2)).sum()/(np.exp(-dist**2)).sum()
	
	# y_pred = model.predict(viper.test_feat)
	print 'testing error {}'.format(abs_error(y_pred, viper.test_y)) 

if __name__ == '__main__':

	test_knn()
	# test_linear_regression()
	# test_ridge_regression()
	# test_lasso_regression()
	# test_SVR()
	# test_knn_regression()