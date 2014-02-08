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
        self.widget.setGeometry(QtCore.QRect(180, 30, 600, 711))
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
        QObject.connect(self.pushButton[0], QtCore.SIGNAL(_fromUtf8("clicked()")), self.slot_query)
        QObject.connect(self.pushButton[1], QtCore.SIGNAL(_fromUtf8("clicked()")), self.slot_gallery)
        QObject.connect(self.pushButton[2], QtCore.SIGNAL(_fromUtf8("clicked()")), self.slot_merge)
        QObject.connect(self.pushButton[3], QtCore.SIGNAL(_fromUtf8("clicked()")), self.slot_next)
        QObject.connect(self.pushButton[4], QtCore.SIGNAL(_fromUtf8("clicked()")), self.slot_previous)
        for i in range(len(self.label)):
            QObject.connect(self.label[i], SIGNAL('clicked()'), lambda pyr = i: self.slot_click(pyr))

        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        files = sorted(glob.glob('../data/query/*.bmp'))

        self.index = 0
        self.image = QPixmap(files[self.index])
        for i in range(len(self.label)):
            self.label[i].setPixmap(self.image.scaled(self.label[i].size(), Qt.KeepAspectRatio))
        self.mergeSegs = []

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Saliency Part Annotation", None))
        for i in range(len(self.label)):
            self.label[i].setText(_translate("MainWindow", "Image{}".format(i), None))

        self.pushButton[0].setText(_translate("MainWindow", "Load Query", None))
        self.pushButton[1].setText(_translate("MainWindow", "Load Gallery", None))
        self.pushButton[2].setText(_translate("MainWindow", "Merge Segs", None))
        self.pushButton[3].setText(_translate("MainWindow", "Next", None))
        self.pushButton[4].setText(_translate("MainWindow", "Previous", None))
        self.pushButton[5].setText(_translate("MainWindow", "Exit", None))
    
    def slot_click(self, pyr):

        cx = self.label[pyr].cx
        cy = self.label[pyr].cy
        mb = self.npdraw[pyr]

        click_label = self.nplabel[pyr][cy, cx]
                   
        # update image label map
        idx = self.nplabel[pyr] == click_label

        if pyr == 0 :
            if click_label not in self.mergeSegs[pyr]:
                self.mergeSegs[pyr].append(click_label) 
                for i in range(0, 2):
                    self.npdraw[pyr][:, :, i][idx] = 0

            else:
                self.mergeSegs[pyr].pop(self.mergeSegs[pyr].index(click_label))
                for i in range(0, 2):
                    self.npdraw[pyr][:, :, i][idx] = self.npdraw0[pyr][:, :, i][idx]
                    
        else:
            cover_labels = np.unique(self.nplabel[0][idx])
            inter_labels = []
            idx_comb = idx & False
            for l in cover_labels:
                idx_partial = self.nplabel[0][idx] == l
                idx_seg = self.nplabel[0] == l
                ratio = idx_partial.sum()*1.0/idx_seg.sum()
                if ratio >= 0.5:
                    inter_labels.append(l)
                    idx_comb += idx_seg

            if click_label not in self.mergeSegs[pyr]:
                self.mergeSegs[pyr].append(click_label) 
                if len(inter_labels) > 0:
                    map(lambda l: self.mergeSegs[0].append(l), inter_labels)
                    for i in range(0, 2):
                        self.npdraw[pyr][:, :, i][idx] = 0
                        self.npdraw[0][:, :, i][idx_comb] = 0

            else:
                self.mergeSegs[pyr].pop(self.mergeSegs[pyr].index(click_label))
                if len(inter_labels) > 0:
                    map(lambda l: self.mergeSegs[0].pop(self.mergeSegs[0].index(l)), inter_labels)
                    for i in range(0, 2):
                        self.npdraw[pyr][:, :, i][idx] = self.npdraw0[pyr][:, :, i][idx]
                        self.npdraw[0][:, :, i][idx_comb] = self.npdraw0[0][:, :, i][idx_comb]

            qimage_slic = array2qimage(self.npdraw[0])
            # QImage to QPixmap
            pixmap = QPixmap.fromImage(qimage_slic)
            self.label[0].setPixmap(pixmap.scaled(self.label[0].size(), Qt.KeepAspectRatio))

        #print self.mergeSegs[0], pyr
        # numpy to QImage
        qimage_slic = array2qimage(self.npdraw[pyr])
        # QImage to QPixmap
        pixmap = QPixmap.fromImage(qimage_slic)
        self.label[pyr].setPixmap(pixmap.scaled(self.label[pyr].size(), Qt.KeepAspectRatio))

    def slot_query(self):
        newDialog = QDialog();
        #fpath = QFileDialog.getExistingDirectory(newDialog, "Select Directory", '../data')
        fpath = '../data/query'
        self.qFiles = sorted(glob.glob(str(fpath) + '/*.bmp'))
        self.qNames = map(lambda x: os.path.basename(x[0:x.find('_')]), self.qFiles)

        self.index = 0
        self.query = QPixmap(self.qFiles[self.index])
        
        w = self.label[0].size().width()
        h = self.label[0].size().height()
        
        npyr = len(self.label)
        self.npimg = [np.zeros((h, w, 3), dtype=np.uint32) for i in range(npyr)]
        self.nplabel = [np.zeros((h, w), dtype=np.uint32) for i in range(npyr)]
        self.npdraw = [np.zeros((h, w, 3), dtype=np.uint32) for i in range(npyr)]
        self.npdraw0 = [np.zeros((h, w, 3), dtype=np.uint32) for i in range(npyr)]
        self.qdraw  = [QPixmap(w, h) for i in range(npyr)]
        self.mergeSegs = [[] for i in range(npyr)]
        
        for i in range(npyr):
            self.slot_slic(i)
            self.label[i].setPixmap(self.qdraw[i].scaled(self.label[i].size(), Qt.KeepAspectRatio))

        #self.mergeSegs = []
        self.querySegs = []
        self.querySegs.append(self.nplabel[0])


    def slot_gallery(self):
        newDialog = QDialog();
        #fpath = QFileDialog.getExistingDirectory(newDialog, "Select Directory", '../data')
        fpath = '../data/gallery'
        self.gFiles = sorted(glob.glob(str(fpath) + '/*.bmp'))
        self.gNames = map(lambda x: os.path.basename(x[0:x.find('_')]), self.gFiles)

        qid = self.gNames.index(self.qNames[self.index])

        idx0 = np.setdiff1d(range(len(self.gFiles)), [qid])
        idx = np.append(idx0[0:len(self.labelset)-1], qid)
        np.random.shuffle(idx)

        for i in range(len(self.labelset)):
            image = QPixmap(self.gFiles[idx[i]])
            self.labelset[i].setPixmap(image.scaled(self.labelset[i].size(), Qt.KeepAspectRatio))

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
        self.npimg[pyr] = imresize(imgarr, (self.label[pyr].size().height(), self.label[pyr].size().width()), interp='bicubic')
        self.nplabel[pyr] = slic.slic_n(self.npimg[pyr], np.round(300./(6**pyr)), 10)
        contours = slic.contours(self.npimg[pyr], self.nplabel[pyr], 10)
        self.npdraw[pyr] = contours[:, :, :-1]
        self.npdraw0[pyr] = self.npdraw[pyr].copy()

        # numpy to QImage
        qimage_slic = array2qimage(self.npdraw[pyr])
        # QImage to QPixmapself.nplabel[pyr]
        self.qdraw[pyr] = QPixmap.fromImage(qimage_slic)
 
    def slot_merge(self):

        for pyr in range(len(self.label)):

            if pyr == 0 :
                # update image label map
                if len(self.mergeSegs) > 0:
                    min_label = min(self.mergeSegs[pyr])
                    for i in range(len(self.mergeSegs[pyr])):
                        label = self.mergeSegs[pyr][i]
                        self.nplabel[pyr][self.nplabel[pyr] == label] = min_label

                    contours = slic.contours(self.npimg[pyr], self.nplabel[pyr], 10)
                    b = contours[:, :, :-1]
                    self.npdraw[pyr] = b
                    self.npdraw0[pyr] = b.copy()
                    self.mergeSegs[pyr] = []

            else:

                
                idx = (self.nplabel[pyr]*0).astype(np.bool)
                for l in self.mergeSegs[pyr]:
                    idx += self.nplabel[pyr] == l

                for i in range(1):
                    self.npdraw[pyr][:, :, i][idx] = 125
                    #self.npdraw[pyr][:, :, i] = 0
                    #self.npdraw[pyr] = self.npdraw0[pyr]
                    #print self.npdraw[pyr].max()
                    #im = Image.fromarray(self.npdraw[pyr])
                    #im.show()
            # numpy to QImage
            qimage_slic = array2qimage(self.npdraw[pyr])
            # QImage to QPixmap
            pixmap = QPixmap.fromImage(qimage_slic)
            self.label[pyr].setPixmap(pixmap.scaled(self.label[pyr].size(), Qt.KeepAspectRatio))

    def slot_previous(self):

        label = self.nplabel[0].copy()*0
        n = 1
        for l in self.mergeSegs[0]:
            label[self.nplabel[0] == l] = n
            n += 1
        self.querySegs[self.index] = label


        self.index -= 1
        if self.index >= 0:
            self.query = QPixmap(self.qFiles[self.index])
            qimage = self.query.toImage()
            # QImage to numpy
            imgarr = rgb_view(qimage)
            for pyr in range(len(self.label)):
                self.npimg[pyr] = imresize(imgarr, (self.label[pyr].size().height(), self.label[pyr].size().width()), interp='bicubic')
                self.nplabel[pyr] = self.querySegs[self.index]
                contours = slic.contours(self.npimg[pyr], self.nplabel[pyr], 10)
                b = contours[:, :, :-1]
                self.npdraw[pyr] = b
                self.npdraw0[pyr] = b.copy()

                # numpy to QImage
                qimage_slic = array2qimage(b)
                # QImage to QPixmap
                pixmap = QPixmap.fromImage(qimage_slic)
                self.label[pyr].setPixmap(pixmap.scaled(self.label[pyr].size(), Qt.KeepAspectRatio))
            
                self.mergeSegs[pyr] = []


    def slot_next(self):
        
        # save current label to self.querySegs
        label = self.nplabel[0].copy()*0
        n = 1
        for l in self.mergeSegs[0]:
            label[self.nplabel[0] == l] = n
            n += 1
        self.querySegs[self.index] = label

        # initialize for labeling the next image
        self.index += 1
        
        if self.index < len(self.qFiles):
            self.query = QPixmap(self.qFiles[self.index])
            
            if len(self.querySegs) == self.index:

                for i in range(len(self.label)):
                    self.slot_slic(i)
                    self.label[i].setPixmap(self.qdraw[i].scaled(self.label[i].size(), Qt.KeepAspectRatio))

                self.querySegs.append(self.nplabel[0])

            else:
                qimage = self.query.toImage()
                # QImage to numpy
                imgarr = rgb_view(qimage)
                for pyr in range(len(self.label)):
                    self.npimg[pyr] = imresize(imgarr, (self.label[pyr].size().height(), self.label[pyr].size().width()), interp='bicubic')
                    self.nplabel[pyr] = self.querySegs[self.index]
                    contours = slic.contours(self.npimg[pyr], self.nplabel[pyr], 10)
                    b = contours[:, :, :-1]
                    self.npdraw[pyr] = b
                    self.npdraw0[pyr] = b.copy()

                    # numpy to QImage
                    qimage_slic = array2qimage(b)
                    # QImage to QPixmap
                    pixmap = QPixmap.fromImage(qimage_slic)
                    self.label[pyr].setPixmap(pixmap.scaled(self.label[pyr].size(), Qt.KeepAspectRatio))
            
            for pyr in range(len(self.label)):
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