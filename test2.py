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
from scipy.misc import imresize
from qimage2ndarray import *
import cPickle
import Image

from PyQt4.QtGui import *
from PyQt4.QtCore import * 
from PyQt4 import QtCore, QtGui

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

class CLabel(QLabel):

    def __init__(self, parent):
        QLabel.__init__(self, parent)
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        self.cx = event.pos().x()
        self.cy = event.pos().y()
        self.emit(SIGNAL('clicked()'))
         
        event.accept()


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(800, 794)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        #self.label = CLabel(self.centralwidget)
        #self.label.setGeometry(QtCore.QRect(180, 30, 270, 720))
        #self.label.setObjectName(_fromUtf8("label"))
        
        self.widget = QtGui.QWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(30, 70, 102, 611))
        self.widget.setObjectName(_fromUtf8("widget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.widget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.pushButton = []
        for i in range(6):
            button = QPushButton(self.widget)
            button.setObjectName('pushButton_{}'.format(i))
            self.pushButton.append(button)
            self.verticalLayout.addWidget(self.pushButton[-1])

        self.widget = QtGui.QWidget(self.centralwidget)
        self.widget.move(180, 30)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.widget)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = []
        for i in range(2):
            label = CLabel(self.widget)
            label.setObjectName(_fromUtf8("label_{}".format(i)))
            self.label.append(label)
            self.label[-1].setGeometry(QRect(180+i*280, 30, 270, 720))
            self.horizontalLayout.addWidget(self.label[-1])
        
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QObject.connect(self.pushButton[0], QtCore.SIGNAL(_fromUtf8("clicked()")), self.slot_reset)
        QObject.connect(self.pushButton[1], QtCore.SIGNAL(_fromUtf8("clicked()")), self.slot_reset)
        QObject.connect(self.pushButton[2], QtCore.SIGNAL(_fromUtf8("clicked()")), self.slot_merge)
        QObject.connect(self.pushButton[3], QtCore.SIGNAL(_fromUtf8("clicked()")), self.slot_previous)
        QObject.connect(self.pushButton[4], QtCore.SIGNAL(_fromUtf8("clicked()")), self.slot_next)
        for i in range(len(self.label)):
            QObject.connect(self.label[i], SIGNAL('clicked()'), lambda pyr = i: self.slot_click(pyr))

        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # load default files
        default_query = '../data/query'
        self.qfiles = sorted(glob.glob(default_query+'/*.bmp'))

        self.w = self.label[0].size().width()
        self.h = self.label[0].size().height()
        self.npyr = len(self.label)
        self.mergeSegs = [[] for i in range(self.npyr)]

        # load label data
        default_file = '../parts.pkl'

        self.save_path = default_file
        if os.path.isfile(self.save_path):
            # labeled data exists

            f = open(self.save_path, 'rb')
            self.data = cPickle.load(f)
            f.close()
            self.index = self.data['index']

            # initialize labeled data {label0, auxlabel}
            self.label0 = self.data['labels'][self.index]
            self.query = QPixmap(self.qfiles[self.index])
            qimage = self.query.toImage()
            imgarr = rgb_view(qimage)
            self.npimg = imresize(imgarr, (self.h, self.w), interp='bicubic')
            self.auxlabel = slic.slic_n(self.npimg, 50, 10)

        else:
            # no previous annotation available
            self.data = {}
            self.data['index'] = self.index
            self.data['labels'] = [np.zeros((self.h, self.w), dtype=np.int32) for i in range(len(self.qfiles))]
            self.data['identity'] = map(lambda x: os.path.basename(x[0:x.find('_')]), self.qfiles)
            self.data['flags'] = np.zeros(len(self.qfiles))
            
            self.index = 0
            self.query = QPixmap(self.qfiles[self.index])

            # compute the initial label map given self.query
            for i in range(self.npyr):
                self.slot_slic(i)

        for i in range(self.npyr):
            self.show_label(i)


    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Saliency Part Annotation", None))
        for i in range(len(self.label)):
            self.label[i].setText(_translate("MainWindow", "Image{}".format(i), None))

        self.pushButton[0].setText(_translate("MainWindow", "Reset", None))
        self.pushButton[1].setText(_translate("MainWindow", "Reset", None))
        self.pushButton[2].setText(_translate("MainWindow", "Merge Segs", None))
        self.pushButton[3].setText(_translate("MainWindow", "Previous", None))
        self.pushButton[4].setText(_translate("MainWindow", "Next", None))
        self.pushButton[5].setText(_translate("MainWindow", "Exit", None))

    def slot_click(self, pyr):

        cx = self.label[pyr].cx
        cy = self.label[pyr].cy

        # if click the fine level label
        if pyr == 0 :
            click_label = self.label0[cy, cx]
            #idx = self.label0 == click_label

            if click_label not in self.mergeSegs[pyr]:
                self.mergeSegs[pyr].append(click_label) 
                
            else:
                self.mergeSegs[pyr].pop(self.mergeSegs[pyr].index(click_label))
                
        # if click the caurse level label
        else:

            click_label = self.auxlabel[cy, cx]
            idx = self.auxlabel == click_label

            cover_labels = list(np.unique(self.label0[idx]))

            if click_label not in self.mergeSegs[pyr]:
                self.mergeSegs[pyr].append(click_label) 
                map(lambda l: self.mergeSegs[0].append(l), cover_labels)

            else:
                self.mergeSegs[pyr].pop(self.mergeSegs[pyr].index(click_label))
                for l in cover_labels:
                    if self.mergeSegs[0].count(l):
                        self.mergeSegs[0].pop(self.mergeSegs[0].index(l))
                #if len(self.mergeSegs[0]):
                    #cover_labels = list(np.setdiff1d(cover_labels, np.asarray(self.mergeSegs[0])))
                    #map(lambda l: self.mergeSegs[0].pop(self.mergeSegs[0].index(l)), cover_labels)

        self.show_label(pyr)
        #print self.mergeSegs[0]

    def show_label(self, pyr):
        '''
            Update map when click 
            Given QPixmap self.query

        '''

        try:
            self.npimg
        except: # self.npimg not exist
            qimage = self.query.toImage()
            imgarr = rgb_view(qimage)
            self.npimg = imresize(imgarr, (self.h, self.w), interp='bicubic')
        

        contours = slic.contours(self.npimg, self.label0, 10)
        draw0 = contours[:, :, :-1]
        
        self.drawMask(draw0, self.label0, self.mergeSegs[0], 0)
        
        if pyr is not 0:
            contours = slic.contours(self.npimg, self.auxlabel, 10)
            draw = contours[:, :, :-1]
            self.drawMask(draw, self.auxlabel, self.mergeSegs[pyr], pyr)

    def drawMask(self, draw, label, roi, pyr):
        '''
            revise the map by masking the ROI segs, and set the map on QLabel
        '''

        idx = np.zeros(label.shape, dtype=bool)
        for l in roi:
            idx += label == l

        for i in range(0, 2):
            draw[:, :, i][idx] = 0

        qimage = array2qimage(draw)
        qpixmap = QPixmap.fromImage(qimage)
        self.label[pyr].setPixmap(qpixmap.scaled(self.label[0].size(), Qt.KeepAspectRatio))      

    def slot_slic(self, pyr):
        '''
            perform SLIC superpixel segmentation
            Input: 
                    QPixmap self.query
                    int32   number of superpixel
            Output: 
                    ndarray self.npimg      - input image 
                    ndarray self.nplabel    - seg label
                    ndarray self.npdraw     - draw map
                    QPixmap self.qdraw      - a draw map with segmentation boundary
        '''
        #w = self.image.width()
        #h = self.image.height()
        # QPixmap to QImage
        qimage = self.query.toImage()
        # QImage to numpy
        imgarr = rgb_view(qimage)
        #imgarr = qimage2numpy(qimage)
        self.npimg = imresize(imgarr, (self.label[pyr].size().height(), self.label[pyr].size().width()), interp='bicubic')
        
        if pyr == 0:
            self.label0 = slic.slic_n(self.npimg, 300, 10)
            #contours = slic.contours(self.npimg, self.label0, 10)
        else:
            self.auxlabel = slic.slic_n(self.npimg, 50, 10)
            #contours = slic.contours(self.npimg, self.auxlabel, 10)

        # numpy to QImage
        #qimage_slic = array2qimage(contours[:, :, :-1])
        # QImage to QPixmapself.nplabel[pyr]
        #qpixmap_slic = QPixmap.fromImage(qimage_slic)
        #self.label[pyr].setPixmap(qpixmap_slic.scaled(self.label[0].size(), Qt.KeepAspectRatio))

    def slot_merge(self):
        # update image label map
        if len(self.mergeSegs[0]) > 0:
            min_label = min(self.mergeSegs[0])
            for i in range(len(self.mergeSegs[0])):
                l = self.mergeSegs[0][i]
                self.label0[self.label0 == l] = min_label

        for i in range(self.npyr):
            self.mergeSegs[i] = []
            self.show_label(i)

        self.data['flags'][self.index] = 1

    def slot_reset(self):
        '''
            reset label 
        '''
        self.query = QPixmap(self.qfiles[self.index])
        for i in range(self.npyr):
            self.slot_slic(i)
            self.show_label(i)
            self.mergeSegs[i] = []              

    def slot_previous(self):

        # save finished label
        self.data['labels'][self.index] = self.label0
        f = open(self.save_path, 'wb')
        cPickle.dump(self.data, f, cPickle.HIGHEST_PROTOCOL)
        f.close()

        # initialize for labeling the next image
        self.index = max(self.index-1, 0)
        self.data['index'] = self.index
        
        self.query = QPixmap(self.qfiles[self.index])
        for i in range(self.npyr):
            self.slot_slic(i)

        if self.data['flags'][self.index]:
            # has been labeled
            self.label0 = self.data['labels'][self.index]
            for pyr in range(self.npyr):
                self.show_label(pyr)
        
        for pyr in range(self.npyr):
            self.mergeSegs[pyr] = []

    def slot_next(self):

        # save finished label
        self.data['labels'][self.index] = self.label0
        f = open(self.save_path, 'wb')
        cPickle.dump(self.data, f, cPickle.HIGHEST_PROTOCOL)
        f.close()

        # initialize for labeling the next image
        self.index = min(self.index+1, len(self.qfiles)-1)
        self.data['index'] = self.index
        
        self.query = QPixmap(self.qfiles[self.index])
        for i in range(self.npyr):
            self.slot_slic(i)

        if self.data['flags'][self.index]:
            # has been labeled
            self.label0 = self.data['labels'][self.index]
            
        for pyr in range(self.npyr):
            self.show_label(pyr)
            self.mergeSegs[pyr] = []            


def main():

    app = QApplication(sys.argv)
    mw = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(mw)
    mw.show()
    sys.exit(app.exec_())

if __name__ == '__main__':

    main()