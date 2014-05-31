import os
import numpy as np

import theano 
import theano.tensor as T 

from sals.models import sgd_optimizer
from sals.models import FCLayer, GeneralModel, ConvLayer, ConvPoolLayer
from sals.utils.DataHelper import DataMan_viper
from sals.utils.FunctionHelper import *
from sals.utils.utils import savefile, loadfile

def main():
	''' pipeline for supervised salience training '''

	if os.path.isdir('../data_viper/'):
		datapath = '../data_viper/'
	else:
		datapath = '../data/'

	# prepare training data for supervised salience training 
	datafile_viper = datapath + 'viper_class.pkl'
	if not os.path.isfile(datafile_viper):
		viper = DataMan_viper_small()
		viper.make_data()
		savefile(datafile_viper, viper)

	viper = loadfile(datafile_viper)

	bs = 100
	imL = 48
	nfilter1 = 16
	filterL = 5
	recfield = 2

	x = T.matrix(name='x', dtype=theano.config.floatX)
	y = T.vector(name='y', dtype=theano.config.floatX)

	layer0 = x.reshape((bs, 3, imL, imL))
	conv1 = ConvPoolLayer(input=layer0, image_shape=(bs, 3, imL, imL), 
				filter_shape=(nfilter1, 3, filterL, filterL), 
				pool_shape = (recfield, recfield), 
				flatten=False,
				actfun=tanh,
				tag='_convpool1')

	# outL = np.floor((imL-filterL+1.)/recfield).astype(np.int)
	outL = np.floor((imL-filterL+1.)/recfield).astype(np.int)

	nfilter2 = 16
	filterL2 = 3
	conv2 = ConvPoolLayer(input=conv1.output(), image_shape=(bs, nfilter1, outL, outL), 
				filter_shape=(nfilter2, nfilter1, filterL2, filterL2), 
				pool_shape = (recfield, recfield),
				flatten=True,
				actfun=tanh,
				tag='_convpool2')

	outL2 = np.floor((outL-filterL2+1.)/recfield).astype(np.int)

	# nfilter3 = 16
	# filterL3 = 3
	# conv3 = ConvLayer(input=conv2.output(), image_shape=(bs, nfilter2, outL2, outL2), 
	# 			filter_shape=(nfilter3, nfilter2, filterL3, filterL3), 
	# 			flatten=True,
	# 			actfun=tanh,
	# 			tag='_conv3')

	# outL3 = outL2-filterL3+1

	fc3 = FCLayer(input=conv2.output(), n_in=nfilter2*outL2*outL2, n_out=1, actfun=sigmoid, tag='_fc3')
	params_cmb = conv1.params + conv2.params + fc3.params 

	ypred = fc3.output().flatten()

	model = GeneralModel(input=x, data=viper, output=ypred,
				target=y, params=params_cmb,
				regularizers=0, 
				cost_func=cross_entropy,
				error_func=abs_error, 
				batch_size=bs)

	sgd = sgd_optimizer(data=viper,  
					model=model,
					batch_size=bs, 
					learning_rate=0.0001,
					learning_rate_decay=0.7,
					n_epochs=200)

	sgd.fit_viper()

	filepath = datapath + 'model/model.pkl'
	savefile(filepath, model)
	os.system('ls -lh ' + filepath)


if __name__ == '__main__':

    main()