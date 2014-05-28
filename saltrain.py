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
		viper = DataMan_viper()
		viper.make_data()
		savefile(viper, datafile_viper)

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
	conv2 = ConvLayer(input=conv1.output(), image_shape=(bs, nfilter1, outL, outL), 
				filter_shape=(nfilter2, nfilter1, filterL2, filterL2), 
				flatten=True,
				actfun=tanh,
				tag='_conv2')

	outL2 = outL-filterL2+1

	# nfilter3 = 16
	# filterL3 = 3
	# conv3 = ConvLayer(input=conv2.output(), image_shape=(bs, nfilter2, outL2, outL2), 
	# 			filter_shape=(nfilter3, nfilter2, filterL3, filterL3), 
	# 			flatten=True,
	# 			actfun=tanh,
	# 			tag='_conv3')

	# outL3 = outL2-filterL3+1

	fc3 = FCLayer(input=conv2.output(), n_in=nfilter2*outL2*outL2, n_out=1024, actfun=sigmoid, tag='_fc3')
	fc4 = FCLayer(input=fc3.output(), n_in=1024, n_out=256, actfun=sigmoid, tag='_fc4')
	fc5 = FCLayer(input=fc4.output(), n_in=256, n_out=1, actfun=sigmoid, tag='_fc5')
	params_cmb = conv1.params + fc3.params + fc4.params + fc5.params

	ypred = fc5.output().flatten()

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
					n_epochs=20)

	sgd.fit_viper()

	filepath = datapath + 'model/model.pkl'
	savefile(model, filepath)
	os.system('ls -lh ' + filepath)


if __name__ == '__main__':

    main()