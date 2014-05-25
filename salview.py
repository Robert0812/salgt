import matplotlib
matplotlib.use('agg')

from sals.utils.DataHelper import DataMan
from sals.utils.ImageHelper import imresize, imread
from skimage import color 
import numpy as np
import pylab as pl
from glob import glob 

# from PySide.QtGui import *
# from PySide.QtCore import * 
from sals.utils.utils import visualize_imfolder
from sklearn.preprocessing import MinMaxScaler


def hit2score(nhits):
	''' convert number of hits to salience score '''
	score = 0
	nonzero_hits = nhits[nhits != 0] 
	if len(nonzero_hits)>0:
		score = np.exp(-(nonzero_hits.mean()**2)/(3**2)) * np.exp(-(nonzero_hits.std()**2) / 1.25)
	return score


def print_labeling(data_path = None): 

	# if data_path is None:
	# 	newDialog = QDialog()
	# 	fpath = QFileDialog.getExistingDirectory(newDialog, "Select data directory", '../')
				
	# 	if len(fpath) == 0:
	# 		QMessageBox.warning(None, 'Warning!', 'Nothing loaded.')
	# 		return

	# 	data_path = str(fpath) + '/' # loaded path

	src_file = data_path + 'parts.pkl'
	usr_file = sorted(glob(data_path + '#*.pkl'))
	
	src = DataMan(src_file)
	srcdata = src.load()
	
	usrhits = []
	for f in usr_file:
		tmp = DataMan(f)
		tmpdata = tmp.load()
		usrhits.append(tmpdata['scores'])

	save_path = data_path + 'result/'
	qfiles = sorted(glob(data_path + 'query/*'))
	im = imread(qfiles[0])
	imsz = im.shape[0:2]
	msk0 = np.zeros(srcdata['labels'][0].shape)

	salmsks = []
	for i in range(len(qfiles)):
		im = imread(qfiles[i])
		msk = msk0.copy()
		for k in usrhits[0][i].keys():
			idx = srcdata['labels'][i] == k
			nhits = np.asarray([nhit[i][k] for nhit in usrhits])
			msk[idx] = hit2score(nhits)
		salmsks.append(msk)

	# normalize all msk 
	# scaler = MinMaxScaler()
	# salscores = scaler.fit_transform(np.asarray(salmsks))

	for i in range(len(qfiles)):
		im = imread(qfiles[i])
		msk = salmsks[i]*255.
		im_rs = imresize(im, msk0.shape, interp='bicubic')
		pl.figure(1)
		pl.clf()
		pl.subplot(1, 2, 1)
		pl.imshow(im_rs)
		pl.subplot(1, 2, 2)
		pl.imshow(color.rgb2grey(im_rs), cmap='gray', alpha=0.6)
		pl.imshow(msk, cmap='hot', vmin=0, vmax=255, alpha=0.6)
		pl.savefig(save_path+'{0:03d}.jpg'.format(i))
		print save_path +'{0:03d}.jpg'.format(i) + ' saved!'

	visualize_imfolder(save_path)


if __name__== '__main__':

	print_labeling('../data_viper/')
	





