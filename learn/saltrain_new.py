import matplotlib
matplotlib.use('agg')

import os
import numpy as np

import theano 
import theano.tensor as T 

# from sals.models import sgd_optimizer
# from sals.models import FCLayer, GeneralModel, ConvLayer, ConvPoolLayer
from sals.utils.DataHelper import DataMan_viper_small, DataMan_traindata
from sals.utils.FunctionHelper import *
from sals.utils.ImageHelper import imresize, immontage, imsave, mapresize
from sals.utils.utils import savefile, loadfile

from sklearn.cluster import KMeans
import time

# import warnings 
# warnings.filterwarnings("ignore")

import pylab as pl


def downsample_data(viper, ntrn = 2000, nbin=10):

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


def preprocess_data(viper, opt):
	''' get training data: pixel or feature, PCA or not PCA'''
	print 'preprocessing data with option :{}'.format(opt)

	# downsampling training data
	# viper = downsample_data(viper)

	# get data 
	if opt.find('pixel') >= 0:
		train_feat = viper.get_pixeldata('train')
		train_feat = train_feat.reshape((viper.train_y.shape[0], -1))

		valid_feat = viper.get_pixeldata('valid')
		valid_feat = valid_feat.reshape((viper.valid_y.shape[0], -1))

		test_feat = viper.get_pixeldata('test')
		test_feat = test_feat.reshape((viper.test_y.shape[0], -1))		

	else:
		train_feat, valid_feat, test_feat = viper.train_feat, viper.valid_feat, viper.test_feat

	if opt.find('PCA') >= 0:
		train_feat, valid_feat, test_feat = PCA_whitening(train_feat, valid_feat, test_feat, n_dim=50)

	if opt.find('01norm') >= 0:
		train_feat = normalize01(train_feat)
		valid_feat = normalize01(valid_feat)
		test_feat = normalize01(test_feat)

	viper.train_feat 	= train_feat.astype(np.float32)
	viper.valid_feat 	= valid_feat.astype(np.float32)
	viper.test_feat  	= test_feat.astype(np.float32)

	viper.train_y 		= viper.train_y.astype(np.float32)
	viper.valid_y 		= viper.valid_y.astype(np.float32)
	viper.test_y 		= viper.test_y.astype(np.float32)

	return viper 


def stripe_range(stripe_id, imH, nStripe=10.):

	y_min = stripe_id /nStripe*imH
	y_max = (stripe_id+1) /nStripe*imH

	if stripe_id == 0:
		y_min = 0

	return y_min, y_max


def indices_in_stripe(y_in, stripe, imH):
	''' find indices patchs are within a stripe ''' 

	y_min, y_max = stripe_range(stripe, imH)
	return np.where((y_in >= y_min) & (y_in < y_max))[0]


def get_stripe_data(viper, stripe):
	''' get a stripe of data '''

	train_idx = indices_in_stripe(viper.yy[viper.train_ctrids], stripe, viper.imH)
	valid_idx = indices_in_stripe(viper.yy[viper.valid_ctrids], stripe, viper.imH)
	test_idx = indices_in_stripe(viper.yy_test[viper.test_ctrids], stripe, viper.imH)

	traindata = DataMan_traindata(stripe)
	traindata.set_train(viper.downsample_train(train_idx))
	traindata.set_valid(viper.downsample_valid(valid_idx))
	traindata.set_test(viper.downsample_test(test_idx))

	return traindata 


def train_SVR(viper):

	from sklearn.svm import SVR
	model = SVR(C=10, kernel='rbf', shrinking=False, verbose=True)
	model.fit(viper.train_feat, viper.train_y)

	return model


def train_model(viper, opt, nStripe=6):
	print 'training model {}'.format(opt)

	# put the training options here
	if opt is 'SVR':
		train_func = train_SVR
	else:	
		raise NameError('training option not recognized')

	model = []
	for stripe_id in np.arange(nStripe):
		data = get_stripe_data(viper, stripe_id)
		print 'training for {}-th stripe with data shape: {}'.format(stripe_id, data.train_feat.shape)
		model.append(train_func(data))

	return model


def predict(model, data, data_y, imH, nStripe=6):
	''' make prediction for test data '''

	# model_hs, model_ub, model_lb = model

	ypred = np.zeros(data.shape[0])

	for stripe_id in np.arange(nStripe):
		idx_stripe = indices_in_stripe(data_y, stripe_id, imH)
		ypred[idx_stripe] = model[stripe_id].predict(data[idx_stripe])

	return ypred

def main():
	''' pipeline for supervised salience training '''

	if os.path.isdir('../data_viper/'):
		datapath = '../data_viper/'
	else:
		datapath = '../data/'

	save_path = '../data_viper/model_feat/'

	DATA_OPT = 'feat' 		# feature type
	TRAIN_OPT = 'SVR'				# training model option
	TRAIN = True 					# wheather re-train the model

	# prepare training data for supervised salience training 
	#=======================================================
	datafile_viper = datapath + 'viper.pkl'
	if not os.path.isfile(datafile_viper):
		viper = DataMan_viper_small()
		viper.make_data()
		savefile(datafile_viper, viper)
	else:
		viper = loadfile(datafile_viper)
	
	viper = preprocess_data(viper, DATA_OPT)

	# training 
	# ==============
	modelfile = datapath + 'model_feat/model.pkl'

	if TRAIN:
		tic = time.clock()
		model = train_model(viper, TRAIN_OPT)
		toc = time.clock()
		print 'Elapsed training time: {0:.2f} min'.format((toc-tic)/60.)

		savefile(modelfile, model)
		os.system('ls -lh ' + modelfile)		
	else:
		model = loadfile(modelfile)
	
	## validation
	#=========================================
	print 'validating trained model'
	nValid = 5000
	valididx = np.random.permutation(viper.valid_feat.shape[0])[:nValid]
	# valid_ypred = model.predict(viper.valid_feat[valididx])
	valid_ypred = predict(model, viper.valid_feat[valididx], viper.yy[viper.valid_ctrids][valididx], viper.imH)

	#- quantize patches based on testing scores
	kmeans = KMeans(init='k-means++', n_clusters=10, n_init=10, verbose=1)
	kmeans.fit(valid_ypred.reshape(nValid, 1))

	#- crop patches for testing image
	valid_patset = np.asarray(viper.get_patchset('valid'))[valididx]

	#- save to result folder
	os.system('rm '+save_path+'*.jpg')
	for i in range(10):
		idx = kmeans.labels_== i
		if any(idx): 
			pats = immontage(list(valid_patset[idx])) 
			imsave(save_path+'{}.jpg'.format(kmeans.cluster_centers_[i]), pats)
			print 'patchset {} saved'.format(i)

	### testing 
	#===============
	print 'testing'
	# test_ypred = model.predict(viper.test_feat)
	test_ypred = predict(model, viper.test_feat, viper.yy_test[viper.test_ctrids], viper.imH)
	
	## assign predicted scores to images
	h, w = viper.imgs[0].shape[:2]
	mh, mw = len(np.unique(viper.yy_test)), len(np.unique(viper.xx_test))
	msk0 = np.zeros(mh*mw, dtype=np.float32)
	msks = [msk0.copy() for im in viper.imgs]

	showlist = []
	n_test = len(test_ypred)
	for i in range(n_test):
		imgid = viper.test_imgids[i]
		patid = viper.test_ctrids[i]
		score = test_ypred[i]
		msks[imgid][patid] = score

	# resize predicted salience map to match image size
	msks_rs = [mapresize(msk.reshape((mw, mh)).T, size=(h, w)) for msk in msks]
	# msks_rs = msks

	# save salience map for comparison
	test_imids = np.asarray(np.unique(viper.test_imgids))
	salmap_gt = np.asarray(viper.salmsks) #np.asarray([viper.salmsks[imid] for imid in test_imids])
	salmap_pred = np.asarray(msks_rs) #np.asarray([msks_rs[imid]/255. for imid in test_imids])
	savefile(save_path+'salmaps_comparison.pkl', [test_imids, salmap_gt, salmap_pred])


if __name__ == '__main__':

    main()