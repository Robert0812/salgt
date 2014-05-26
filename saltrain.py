import os
import numpy as np

import theano 
import theano.tensor as T 

from sals.models import sgd_optimizer
from sals.models import FCLayer, GeneralModel, ConvLayer
from sals.utils.DataHelper import DataMan_viper
from sals.utils.FunctionHelper import *


def main():
	''' pipeline for supervised salience evaluation '''

	# prepare training data for supervised salience training 
	datafile_viper = '../data_viper/viper.pkl'
	if not os.path.isfile(datafile_viper):
		viper = DataMan_viper()
		viper.convert2pkl(datafile_viper)

	viper = DataMan_viper(datafile_viper)
	cpudata = viper.load()
	viper.share2gpumem(cpudata)

	bs = 2000
	imL = 48
	nfilter1 = 32
	filterL = 5
	recfield = 2

	x = T.matrix(name='x', dtype=theano.config.floatX)
	y = T.vector(name='y', dtype=theano.config.floatX)

	layer0 = x.reshape((bs, 3, imL, imL))
	conv1 = ConvLayer(input=layer0, image_shape=(bs, 3, imL, imL), 
				filter_shape=(nfilter1, 3, filterL, filterL), 
				pool_shape=(recfield, recfield),
				flatten=True,
				actfun=tanh,
				tag='_conv1')

	outL = np.floor((imL-filterL+1.)/recfield).astype(np.int)
	fc2 = FCLayer(input=conv1.output(), n_in=nfilter1*outL*outL, n_out=1, actfun=sigmoid, tag='_fc2')
	params_cmb = conv1.params + fc2.params

	ypred = fc2.output().flatten()

	model = GeneralModel(input=x, data=viper, output=ypred,
				target=y, params=params_cmb,
				regularizers=0, 
				cost_func=cross_entropy,
				error_func=sqr_error, 
				batch_size=bs)

	sgd = sgd_optimizer(data=viper,  
					model=model,
					batch_size=bs, 
					learning_rate=0.5,
					learning_rate_decay=0.7,
					n_epochs=-1)

	sgd.fit_viper()


if __name__ == '__main__':

    main()