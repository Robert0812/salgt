from sals.utils.DataHelper import DataMan
from sals.utils.ImageHelper import imresize
from skimage import color 
import numpy as np
import pylab as pl
from glob import glob 

def print_labeling(src_file = '../parts_new.pkl', 
					usr_file = '../data/yi#03.pkl'):

	src = DataMan(src_file)
	usr = DataMan(usr_file)
	srcdata = src.load()
	usrdata = usr.load()

	data_path = '../' # default path
	save_path = '../data/result/'
	qfiles = sorted(glob(data_path + 'data/query/*.bmp'))
	im = pl.imread(qfiles[0])
	imsz = im.shape[0:2]
	msk0 = np.zeros(srcdata['labels'][0].shape)

	for i in range(len(qfiles)):
		im = pl.imread(qfiles[i])
		msk = msk0.copy()
		for k in usrdata['scores'][i].keys():
			idx = srcdata['labels'][i] == k
			if usrdata['scores'][i][k] == 0:
				msk[idx] = 0
			else:
				sal = 1./usrdata['scores'][i][k]
				msk[idx] = np.exp(-sal**2/(2**2))*255.
		#msk_rs = imresize(msk, imsz, interp='bicubic')
		#draw = overlay(im, msk_rs, 0.6)
		im_rs = imresize(im, msk0.shape, interp='bicubic')
		#draw = overlay(im_rs, msk.astype(np.uint8), 0.6)
		#pl.imsave(save_path+'{0:03d}.jpg'.format(i), draw, cmap='jet')
		pl.figure(1)
		pl.subplot(1, 2, 1)
		pl.imshow(im_rs)
		pl.subplot(1, 2, 2)
		pl.imshow(msk, cmap='hot')
		pl.savefig(save_path+'{0:03d}.jpg'.format(i))
		print save_path+'{0:03d}.jpg'.format(i) + ' saved!'


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

	print_labeling()
	





