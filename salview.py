from sals.utils.DataHelper import DataMan
from sals.utils.ImageHelper import imresize
from skimage import color 
import numpy as np
import pylab as pl
from glob import glob 

from PySide.QtGui import *
from PySide.QtCore import * 
from sals.utils.utils import visualize_imfolder


def hit2score(hits):
	''' convert number of hits to salience score '''
	score = 0
	if hits > 0:
		score = np.exp(-hits**2/(3**2))
	return score

def print_labeling(data_path = None): 

	if data_path is None:
		newDialog = QDialog()
		fpath = QFileDialog.getExistingDirectory(newDialog, "Select data directory", '../')
				
		if len(fpath) == 0:
			QMessageBox.warning(None, 'Warning!', 'Nothing loaded.')
			return

		data_path = str(fpath) + '/' # loaded path

	src_file = data_path + 'parts.pkl'
	usr_file = sorted(glob(data_path + '#*.pkl'))
	
	src = DataMan(src_file)
	srcdata = src.load()
	
	usrdata = []
	for f in usr_file:
		tmp = DataMan(f)
		usrdata.append(tmp.load())

	save_path = data_path + 'result/'
	qfiles = sorted(glob(data_path + 'query/*.bmp'))
	im = pl.imread(qfiles[0])
	imsz = im.shape[0:2]
	msk0 = np.zeros(srcdata['labels'][0].shape)

	for i in range(len(qfiles)):
		im = pl.imread(qfiles[i])
		msk = msk0.copy()
		for k in usrdata[0]['scores'][i].keys():
			idx = srcdata['labels'][i] == k
			msk[idx] = np.mean([hit2score(tmp['scores'][i][k]) for tmp in usrdata])
		
		msk = 0.5 + 0.4*msk
		msk *= 255.
		im_rs = imresize(im, msk0.shape, interp='bicubic')
		#draw = overlay(im_rs, msk.astype(np.uint8), 0.6)
		#pl.imsave(save_path+'{0:03d}.jpg'.format(i), draw, cmap='jet')
		pl.figure(1)
		pl.clf()
		pl.subplot(1, 2, 1)
		pl.imshow(im_rs)
		pl.subplot(1, 2, 2)
		pl.imshow(color.rgb2grey(im_rs), cmap='gray', alpha=0.6)
		pl.imshow(msk, cmap='jet', vmin=0, vmax=255, alpha=0.6)
		pl.savefig(save_path+'{0:03d}.jpg'.format(i))
		print save_path+'{0:03d}.jpg'.format(i) + ' saved!'

	visualize_imfolder(save_path)

def overlay(img, msk, alpha):

	msk0 = np.zeros(img.shape[0:2])
	msk_rgb = np.dstack((msk, msk0, msk0))
	img_hsv = color.rgb2hsv(img)
	msk_hsv = color.rgb2hsv(msk_rgb)

	img_hsv[..., 0] = msk_hsv[..., 0]
	img_hsv[..., 1] = msk_hsv[..., 1]*alpha

	img_masked = color.hsv2rgb(img_hsv)

	return img_masked

if __name__== '__main__':

	print_labeling('../data_test/')
	





