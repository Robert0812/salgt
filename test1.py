# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'test1.ui'
#
# Created: Thu Feb  6 20:20:48 2014
#      by: Rui Zhao, The Chinese University of Hong Kong
#          Email: rzhao@ee.cuhk.edu.hk
#
# WARNING! All changes made in this file will be lost!

import os
import sys
import glob
import slic
import numpy as np
from qimage2ndarray import *
import cPickle

from PyQt4.QtGui import *
from PyQt4.QtCore import * 
from PyQt4 import QtCore, QtGui
from skimage.transform import resize
#from scipy.mics import imresize

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

def imresize(im, shape, interp='bicubic'):
    '''
        replacement of scipy imresize
    '''
    if interp is 'bicubic':
        return (resize(im, shape, order=4)*255).astype(np.uint8)

class CLabel(QLabel):

    def __init__(self, parent):
        QLabel.__init__(self, parent)
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        
        self.emit(SIGNAL('clicked()'))
        event.accept()


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):

        self.w = 270 #self.label[0].size().width()
        self.h = 720 #self.label[0].size().height()

        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(1080, 794)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.label = QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(150, 30, self.w, self.h))
        self.label.setObjectName(_fromUtf8("label"))
        
        self.widget = QtGui.QWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(20, 70, 110, 611))
        self.widget.setObjectName(_fromUtf8("widget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.widget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.pushButton = []
        for i in range(5):
            button = QPushButton(self.widget)
            button.setObjectName('pushButton_{}'.format(i))
            self.pushButton.append(button)
            self.verticalLayout.addWidget(self.pushButton[-1])

        self.widget1 = QtGui.QWidget(self.centralwidget)
        self.widget1.move(460, 30)
        #self.widget1.setGeometry(QtCore.QRect(500, 30, 651, 721))
        self.widget1.setObjectName(_fromUtf8("widget1"))
        self.gridLayout_2 = QtGui.QGridLayout(self.widget1)
        self.gridLayout_2.setMargin(0)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.labelset = []
        for i in range(4):
            for j in range(8):
                label_tmp = CLabel(self.widget1)
                label_tmp.setObjectName(_fromUtf8('label_{}'.format(i*7+j+2)))
                self.labelset.append(label_tmp)
                self.labelset[-1].setGeometry(QRect(500, 30, 70, 176))
                self.gridLayout_2.addWidget(self.labelset[-1], i, j, 1, 1)

        
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QObject.connect(self.pushButton[0], QtCore.SIGNAL(_fromUtf8("clicked()")), self.slot_load)
        QtCore.QObject.connect(self.pushButton[1], QtCore.SIGNAL(_fromUtf8("clicked()")), self.slot_next)
        QtCore.QObject.connect(self.pushButton[2], QtCore.SIGNAL(_fromUtf8("clicked()")), self.slot_viewer)
        QtCore.QObject.connect(self.pushButton[3], QtCore.SIGNAL(_fromUtf8("clicked()")), self.slot_exit)
        QtCore.QObject.connect(self.pushButton[4], QtCore.SIGNAL(_fromUtf8("clicked()")), self.slot_reset)

        for i in range(len(self.labelset)):
            QObject.connect(self.labelset[i], SIGNAL('clicked()'), lambda idx = i: self.slot_click(idx))
        
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # default initialization
        self.data_path = '../' # default path

        self.qfiles = sorted(glob.glob(self.data_path + 'data/query/*.bmp'))
        self.gfiles = sorted(glob.glob(self.data_path + 'data/gallery/*.bmp'))
        self.qnames = map(lambda x: os.path.basename(x[0:x.find('_')]), self.qfiles)
        self.gnames = map(lambda x: os.path.basename(x[0:x.find('_')]), self.gfiles)
        

        self.save_path = self.data_path + 'parts.pkl'
        print self.save_path
        if os.path.isfile(self.save_path):
            # labeled data exists

            f = open(self.save_path, 'rb')
            self.data = cPickle.load(f)
            f.close()
            
        else:
            print 'Label data does not exist!'
            QApplication.quit()

        # randomly sample image index and part index
        self.pairidx = 0 # index of image-part pair 
        seed = 1
        self.random_list(seed)
        self.index = self.pairs[0][0]
        self.partid = self.pairs[0][1]
        self.qid = self.data['identity'][self.index]

        # initial visualization 
        self.show_query()
        self.show_gallery()


    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Saliency Score Annotation", None))
        self.label.setText(_translate("MainWindow", "TextLabel", None))
        self.pushButton[0].setText(_translate("MainWindow", "Load Path", None))
        self.pushButton[1].setText(_translate("MainWindow", "Save && Next", None))
        self.pushButton[2].setText(_translate("MainWindow", "Open Viewer", None))
        self.pushButton[3].setText(_translate("MainWindow", "Exit", None))
        self.pushButton[4].setText(_translate("MainWindow", "Reset ALL", None))

        for i in range(4):
            for j in range(8):
                self.labelset[i*8+j].setText(_translate("MainWindow", "Image{}".format(i*8+j+1), None))


    def random_list(self, seed):
        '''
            Generate a random list of image-part pairs that covering all images and all parts
        '''
        self.pairs = []
        for i in range(len(self.qfiles)):
            for p in self.data['scores'][i].keys():
                self.pairs.append([i, p])

        np.random.seed(seed)
        np.random.shuffle(self.pairs)


    def slot_load(self):
        newDialog = QDialog();
        fpath = QFileDialog.getExistingDirectory(newDialog, "Select Directory", '../')
        
        if fpath is None:
            return

        self.data_path = str(fpath) + '/'
        self.qfiles = sorted(glob.glob(self.data_path + 'data/query/*.bmp'))
        self.gfiles = sorted(glob.glob(self.data_path + 'data/gallery/*.bmp'))
        self.qnames = map(lambda x: os.path.basename(x[0:x.find('_')]), self.qfiles)
        self.gnames = map(lambda x: os.path.basename(x[0:x.find('_')]), self.gfiles)
        
        self.save_path = self.data_path + 'parts.pkl'
        
        if os.path.isfile(self.save_path):
            # labeled data exists

            f = open(self.save_path, 'rb')
            self.data = cPickle.load(f)
            f.close()
            
        else:
            print 'Label data does not exist!'
            QApplication.quit()

        # randomly sample image index and part index
        self.pairidx = 0 # index of image-part pair 
        seed = 1
        self.random_list(seed)
        self.index = self.pairs[0][0]
        self.partid = self.pairs[0][1]
        self.qid = self.data['identity'][self.index]

        # initial visualization 
        self.show_query()
        self.show_gallery()

    #def random_query(self): #X

        # randomly sample image index and part index
    #    self.index = np.random.randint(0, len(self.qfiles))
    #    self.query = QPixmap(self.qfiles[self.index])
            
        # initialize labeled data {label0, auxlabel}
    #    self.label0 = self.data['labels'][self.index]
    #    self.score0 = self.data['scores'][self.index]
    #    self.qid = self.data['identity'][self.index]

    #    rnd_idx = np.random.randint(0, len(self.score0.keys()))
    #    self.partid = self.score0.keys()[rnd_idx]

    #def random_part(self):

    #    rnd_idx = np.random.randint(0, len(self.score0.keys()))
    #    self.partid = self.score0.keys()[rnd_idx]

    def show_query(self):
        '''
            show query image with only one visible part for labeling
        '''
        query = QPixmap(self.qfiles[self.index])
        qimage = query.toImage()
        imgarr = rgb_view(qimage)
        draw0 = imresize(imgarr, (self.h, self.w), interp='bicubic')

        idx = self.data['labels'][self.index] != self.partid
        for i in range(3):
            draw0[:, :, i][idx] = 255

        qimage = array2qimage(draw0)
        qpixmap = QPixmap.fromImage(qimage)
        self.label.setPixmap(qpixmap.scaled(self.label.size(), Qt.KeepAspectRatio))          

    def show_gallery(self):
        #newDialog = QDialog();
        #fpath = QFileDialog.getExistingDirectory(newDialog, "Select Directory", '../data')
        #fpath = '../data/gallery'
        #self.gFiles = sorted(glob.glob(str(fpath) + '/*.bmp'))
        #self.gNames = map(lambda x: os.path.basename(x[0:x.find('_')]), self.gFiles)

        #qid = self.gnames.index(self.qNames[self.index])
        
        idx_match = self.gnames.index(self.qnames[self.index])
        idx_mismatch = np.setdiff1d(range(len(self.gfiles)), [idx_match])
        idx = np.append(idx_mismatch[0:len(self.labelset)-1], idx_match)
        np.random.shuffle(idx)

        self.gidx = idx
        for i in range(len(self.labelset)):
            image = QPixmap(self.gfiles[idx[i]])
            self.labelset[i].setPixmap(image.scaled(self.labelset[i].size(), Qt.KeepAspectRatio))
            #print self.labelset[i].size()

        self.flags = np.zeros(len(self.labelset))

    def slot_click(self, index):
        
        # once clicked, draw rectangle around the selected gallery image
        gimage = QPixmap(self.gfiles[self.gidx[index]]).toImage()
        draw = rgb_view(gimage)

        if self.flags[index] == 0:

            w = gimage.size().width()
            h = gimage.size().height()
            xx = np.tile(np.asarray(range(w)), (h, 1))
            yy = np.tile(np.asarray(range(h)), (w, 1)).transpose()
            
            idx_x = (xx < 3) + (xx > (w -3))
            idx_y = (yy < 3) + (yy > (h -3))

            draw[:, :, 0][idx_x + idx_y] = 255
            draw[:, :, 1][idx_x + idx_y] = 0
            draw[:, :, 2][idx_x + idx_y] = 0

            self.flags[index] = 1
        
        else:
            self.flags[index] = 0


        qimage = array2qimage(draw)
        qpixmap = QPixmap.fromImage(qimage)
        self.labelset[index].setPixmap(qpixmap.scaled(self.labelset[index].size(), Qt.KeepAspectRatio))
        
    def slot_next(self):
        '''
            re-random query and gallery for a new round of annotation
        '''
        # save current labeling
        if self.flags.sum():
            #print self.flags.sum()
            # record current label
            # 1./self.flags.sum() represents confidence of correct match
            select_ids = [self.gnames[idx] for idx in self.gidx[self.flags.astype(bool)]]
            #print select_ids
            if self.qid in select_ids:
                self.score0[self.partid][0] += 1./self.flags.sum()
            # record number of annotation rounds 
            self.score0[self.partid][1] += 1

            print 'part score {} (labeled {} times)'.format(self.score0[self.partid][0], self.score0[self.partid][1])

        f = open(self.save_path, 'wb')
        cPickle.dump(self.data, f, cPickle.HIGHEST_PROTOCOL)
        f.close()

        self.pairidx += 1
        self.index = self.pairs[self.pairidx][0]
        self.partid = self.pairs[self.pairidx][1]
        self.qid = self.data['identity'][self.index]

        # initial visualization 
        self.show_query()
        self.show_gallery()

    def slot_viewer(self):
        '''
            A dialog for viewing the labeling result
        '''
        self.viewer  = QDialog()
        self.viewer.show()

    def slot_exit(self):
        '''
            Quit the application
        '''
        msg = QMessageBox.question(None, 'Exit', 'Quit the application?', QMessageBox.Yes, QMessageBox.No)
        if msg == QMessageBox.Yes:
            QApplication.quit()

    def slot_reset(self):
        '''
            Reset all previous labels of salience score to 0 
        '''
        msg = QMessageBox.question(None, 'Reset', 'Reset all previous labels?', QMessageBox.Yes, QMessageBox.No)
        if msg == QMessageBox.Yes:
            for i in range(len(self.qfiles)):
                score0 = self.data['scores'][i]
                for p in score0.keys():
                    score0[p][0] = 0
                    score0[p][1] = 0

def main():

    app = QApplication(sys.argv)
    mw = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(mw)
    mw.show()
    sys.exit(app.exec_())

if __name__ == '__main__':

    main()