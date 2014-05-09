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
import cPickle

from PySide.QtGui import *
from PySide.QtCore import * 
from PySide import QtCore, QtGui

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

def rgb_view(qimage):
    '''
    Convert QImage into a numpy array
    '''
    qimage = qimage.convertToFormat(QtGui.QImage.Format_RGB32)

    w = qimage.width()
    h = qimage.height()

    ptr = qimage.constBits()
    arr = np.array(ptr).reshape(h, w, 4)
    arr = arr[...,:3]
    arr = arr[:, :, [2, 1, 0]]
    return arr

def array2qimage(rgb):
    """Convert the 3D np array `rgb` into a 32-bit QImage.  `rgb` must
    have three dimensions with the vertical, horizontal and RGB image axes.

    ATTENTION: This QImage carries an attribute `ndimage` with a
    reference to the underlying np array that holds the data. On
    Windows, the conversion into a QPixmap does not copy the data, so
    that you have to take care that the QImage does not get garbage
    collected (otherwise PyQt will throw away the wrapper, effectively
    freeing the underlying memory - boom!)."""
    if len(rgb.shape) != 3:
        raise ValueError("rgb2QImage can only convert 3D arrays")
    if rgb.shape[2] not in (3, 4):
        raise ValueError("rgb2QImage can expects the last dimension to contain exactly three (R,G,B) or four (R,G,B,A) channels")

    h, w, channels = rgb.shape

    # Qt expects 32bit BGRA data for color images:
    bgra = np.empty((h, w, 4), np.uint8, 'C')
    bgra[...,0] = rgb[...,2]
    bgra[...,1] = rgb[...,1]
    bgra[...,2] = rgb[...,0]
    if rgb.shape[2] == 3:
        bgra[...,3].fill(255)
    else:
        bgra[...,3] = rgb[...,3]

    fmt = QImage.Format_ARGB32
    result = QImage(bgra.data, w, h, fmt)
    result.ndarray = bgra
    return result

class CLabel(QLabel):

    def __init__(self, parent):
        QLabel.__init__(self, parent)
        self.setMouseTracking(True)
        self.cx = -1
        self.cy = -1

    def mousePressEvent(self, event):
        self.cx = event.pos().x()
        self.cy = event.pos().y()
        self.emit(SIGNAL('clicked()'))
        event.accept()
        

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):

        self.w = 270 #self.label[0].size().width()
        self.h = 720 #self.label[0].size().height()

        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(3*self.w +180, self.h+90)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        #self.label = CLabel(self.centralwidget)
        #self.label.setGeometry(QtCore.QRect(180, 30, 270, 720))
        #self.label.setObjectName(_fromUtf8("label"))
        
        self.widget = QtGui.QWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(20, 70, 110, 611))
        self.widget.setObjectName(_fromUtf8("widget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.widget)
        # self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.pushButton = []
        for i in range(7):
            button = QPushButton(self.widget)
            button.setObjectName('pushButton_{}'.format(i))
            self.pushButton.append(button)
            self.verticalLayout.addWidget(self.pushButton[-1])

        self.widget = QtGui.QWidget(self.centralwidget)
        self.widget.move(150, 20)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.widget)
        # self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = []
        for i in range(2):
            label = CLabel(self.widget)
            label.setObjectName(_fromUtf8("label_{}".format(i)))
            self.label.append(label)
            self.label[-1].setGeometry(QRect(150, 20, self.w, self.h))
            self.horizontalLayout.addWidget(self.label[-1])

        self.reflabel = QLabel(self.widget)
        self.reflabel.setObjectName('label_{}'.format(i+1))
        self.reflabel.setGeometry(QRect(150, 20, self.w, self.h))
        self.horizontalLayout.addWidget(self.reflabel)

        self.readme = QPlainTextEdit(self.centralwidget)
        self.readme.setReadOnly(True)
        self.readme.setGeometry(QRect(150, self.h+40, 3*self.w, 25))
        self.readme.setPlainText("Important: before clicking 'Save Parts' button, please select all body part!")

        
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        
        QObject.connect(self.pushButton[2], QtCore.SIGNAL(_fromUtf8("clicked()")), self.slot_previous)
        QObject.connect(self.pushButton[3], QtCore.SIGNAL(_fromUtf8("clicked()")), self.slot_next)
        QObject.connect(self.pushButton[1], QtCore.SIGNAL(_fromUtf8("clicked()")), self.slot_merge)
        QObject.connect(self.pushButton[5], QtCore.SIGNAL(_fromUtf8("clicked()")), self.slot_save)
        QObject.connect(self.pushButton[4], QtCore.SIGNAL(_fromUtf8("clicked()")), self.slot_reset)
        QObject.connect(self.pushButton[6], QtCore.SIGNAL(_fromUtf8("clicked()")), self.slot_exit)
        QObject.connect(self.pushButton[0], QtCore.SIGNAL(_fromUtf8("clicked()")), self.slot_load)

        for i in range(len(self.label)):
            QObject.connect(self.label[i], SIGNAL('clicked()'), lambda pyr = i: self.slot_click(pyr))

        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # load default files
        self.data_path = '../data_cuhk/' # default path
        self.qfiles = sorted(glob.glob(self.data_path+'query/*'))

        
        self.npyr = len(self.label)
        self.mergeSegs = [[] for i in range(self.npyr)]

        # load label data
        self.save_path = self.data_path + 'parts.pkl'
        
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
            self.index = 0
            self.query = QPixmap(self.qfiles[self.index])

            self.data = {}
            self.data['index'] = self.index
            self.data['labels'] = [np.zeros((self.h, self.w), dtype=np.int32) for i in range(len(self.qfiles))]
            self.data['scores'] = [[] for i in range(len(self.qfiles))]
            self.data['identity'] = map(lambda x: os.path.basename(x)[0:os.path.basename(x).find('_')], self.qfiles)
            self.data['flags'] = np.zeros(len(self.qfiles))
            self.data['sflags'] = [[] for i in range(len(self.qfiles))]

            # compute the initial label map given self.query
            for i in range(self.npyr):
                self.slot_slic(i)

        for i in range(self.npyr):
            self.show_label(i)


    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Saliency Part Annotation", None))
        for i in range(len(self.label)):
            self.label[i].setText(_translate("MainWindow", "Image{}".format(i), None))

        self.pushButton[2].setText(_translate("MainWindow", "Previous", None))
        self.pushButton[3].setText(_translate("MainWindow", "Next", None))
        self.pushButton[1].setText(_translate("MainWindow", "Merge Segs", None))
        self.pushButton[5].setText(_translate("MainWindow", "Save Parts", None))
        self.pushButton[4].setText(_translate("MainWindow", "Reset Segs", None))
        self.pushButton[6].setText(_translate("MainWindow", "Exit", None))
        self.pushButton[0].setText(_translate("MainWindow", "Load Path", None))
        


    def slot_load(self):

        newDialog = QDialog()
        fpath = QFileDialog.getExistingDirectory(newDialog, "Select data directory", '../')
        
        if len(fpath) == 0:
            QMessageBox.warning(None, 'Warning!', 'Nothing loaded.')
            return

        self.data_path = str(fpath) + '/' # loaded path
        self.qfiles = sorted(glob.glob(self.data_path+'query/*'))
        
        self.npyr = len(self.label)
        self.mergeSegs = [[] for i in range(self.npyr)]

        # load label data
        self.save_path = self.data_path + 'parts.pkl'
        print self.qfiles
        
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
            self.data['scores'] = [[] for i in range(len(self.qfiles))]
            self.data['identity'] = map(lambda x: os.path.basename(x)[0:os.path.basename(x).find('_')], self.qfiles)
            self.data['flags'] = np.zeros(len(self.qfiles))
            self.data['sflags'] = [[] for i in range(len(self.qfiles))]
            
            self.index = 0
            self.query = QPixmap(self.qfiles[self.index])

            # compute the initial label map given self.query
            for i in range(self.npyr):
                self.slot_slic(i)

        for i in range(self.npyr):
            self.show_label(i)


    def slot_click(self, pyr):
        '''
            Update image to show selected segment 
        '''

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
                
        # if click the coarse level label
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

        # show reference label
        draw = self.npimg.copy()
        xx = np.tile(np.asarray(range(self.w)), (self.h, 1))
        yy = np.tile(np.asarray(range(self.h)), (self.w, 1)).transpose()
            
        idx_x = abs(xx - self.label[0].cx) < 5
        idx_y = abs(yy -self.label[0].cy) < 5

        for i in range(3):
            draw[:, :, i][idx_x & idx_y] = 255

        qimage = array2qimage(draw)
        qpixmap = QPixmap.fromImage(qimage)
        self.reflabel.setPixmap(qpixmap.scaled(self.reflabel.size(), Qt.KeepAspectRatio))  

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

    def slot_merge(self):
        '''
            Update segmentation label by merging selected segments
        '''

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

    def slot_save(self):
        '''
            save labeled body parts
        '''
        # save finished label
        if len(self.mergeSegs[0]):
            self.data['scores'][self.index] = dict.fromkeys(self.mergeSegs[0], 0)
            self.data['sflags'][self.index] = dict.fromkeys(self.mergeSegs[0], None)

            f = open(self.save_path, 'wb')
            cPickle.dump(self.data, f, cPickle.HIGHEST_PROTOCOL)
            f.close()

            self.readme.setPlainText('Saved.')
            #self.statusBar().showMessage('Saved.')

        else:

            msg = QMessageBox.warning(None, 'Warning!', 'No body part is selected.')

    
    def slot_previous(self):

        # save finished label
        self.data['labels'][self.index] = self.label0
        #if len(self.mergeSegs[0]):
        #    self.data['scores'][self.index] = dict.fromkeys(self.mergeSegs[0], [0, 0])

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

        self.label[0].cx = -1
        self.label[0].cy = -1

        self.readme.setPlainText("Important: before clicking 'Save Parts' button, please select all body part!")

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

        self.label[0].cx = -1
        self.label[0].cy = -1

        self.readme.setPlainText("Important: before clicking 'Save Parts' button, please select all body part!")


    def slot_reset(self):
        '''
            Reset labeling
        '''
        
        msg = QMessageBox.question(None, 'Reset', 'Reset all previous labels?', QMessageBox.Yes, QMessageBox.No)
        if msg == QMessageBox.Yes:
            self.label[0].cx = -1
            self.label[0].cy = -1

            self.query = QPixmap(self.qfiles[self.index])
            for i in range(self.npyr):
                self.slot_slic(i)
                self.show_label(i)
                self.mergeSegs[i] = []


    def slot_exit(self):
        '''
            Quit the application
        '''
        msg = QMessageBox.question(None, 'Exit', 'Quit the application?', QMessageBox.Yes, QMessageBox.No)
        if msg == QMessageBox.Yes:
            QApplication.quit()


def main():

    app = QApplication(sys.argv)
    mw = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(mw)
    mw.show()
    sys.exit(app.exec_())

if __name__ == '__main__':

    main()
