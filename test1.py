# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'test.ui'
#
# Created: Thu Feb  6 20:20:48 2014
#      by: PyQt4 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!
import os
import sys
import glob
import slic
import numpy as np
from scipy.misc import imresize
from qimage2ndarray import *

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

    def mousePressEvent(self, event):
        self.cx = event.pos().x()
        self.cy = event.pos().y()
        self.emit(SIGNAL('clicked()'))
         
        event.accept()


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(1269, 794)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.label = CLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(180, 30, 270, 720))
        self.label.setObjectName(_fromUtf8("label"))
        
        self.widget = QtGui.QWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(10, 70, 102, 611))
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

        self.widget1 = QtGui.QWidget(self.centralwidget)
        self.widget1.setGeometry(QtCore.QRect(550, 30, 651, 721))
        self.widget1.setObjectName(_fromUtf8("widget1"))
        self.gridLayout_2 = QtGui.QGridLayout(self.widget1)
        self.gridLayout_2.setMargin(0)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.labelset = []
        for i in range(4):
            for j in range(8):
                label_tmp = QtGui.QLabel(self.widget1)
                label_tmp.setObjectName(_fromUtf8('label_{}'.format(i*7+j+2)))
                self.labelset.append(label_tmp)
                self.gridLayout_2.addWidget(self.labelset[-1], i, j, 1, 1)

        
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QObject.connect(self.pushButton[0], QtCore.SIGNAL(_fromUtf8("clicked()")), self.slot_query)
        QtCore.QObject.connect(self.pushButton[1], QtCore.SIGNAL(_fromUtf8("clicked()")), self.slot_gallery)
        QtCore.QObject.connect(self.pushButton[2], QtCore.SIGNAL(_fromUtf8("clicked()")), self.slot_merge)
        QtCore.QObject.connect(self.pushButton[3], QtCore.SIGNAL(_fromUtf8("clicked()")), self.slot_next)
        QtCore.QObject.connect(self.pushButton[4], QtCore.SIGNAL(_fromUtf8("clicked()")), self.slot_previous)
        QtCore.QObject.connect(self.label, SIGNAL('clicked()'), self.slot_click)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        files = sorted(glob.glob('../data/query/*.bmp'))

        self.index = 0
        self.image = QPixmap(files[self.index])
        self.label.setPixmap(self.image.scaled(self.label.size(), Qt.KeepAspectRatio))
        self.mergeSegs = []

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.label.setText(_translate("MainWindow", "TextLabel", None))
        self.pushButton[0].setText(_translate("MainWindow", "Load Query", None))
        self.pushButton[1].setText(_translate("MainWindow", "Load Gallery", None))
        self.pushButton[2].setText(_translate("MainWindow", "Merge Segs", None))
        self.pushButton[3].setText(_translate("MainWindow", "Next", None))
        self.pushButton[4].setText(_translate("MainWindow", "Previous", None))
        self.pushButton[5].setText(_translate("MainWindow", "Exit", None))
        for i in range(4):
            for j in range(8):
                self.labelset[i*8+j].setText(_translate("MainWindow", "Image{}".format(i*8+j+1), None))

    def slot_click(self):
        cx = self.label.cx
        cy = self.label.cy
        mb = self.npdraw
        # update image label map
        if self.nplabel[cy, cx] not in self.mergeSegs:
            self.mergeSegs.append(self.nplabel[cy, cx]) 
            
            for i in range(0, 2):
                tmp = mb[:, :, i]
                tmp[self.nplabel == self.nplabel[cy, cx]] = 0
                mb[:, :, i] = tmp
        else:
            self.mergeSegs.pop(self.mergeSegs.index(self.nplabel[cy, cx]))
            for i in range(0, 2):
                tmp = mb[:, :, i]
                initb = self.npdraw0[:, :, i]
                idx = self.nplabel == self.nplabel[cy, cx]
                
                tmp[idx] = initb[idx]
                mb[:, :, i] = tmp

            #test = Image.fromarray(initb)
            #test.show()
        self.npdraw = mb
        #print self.mergeSegs

        # numpy to QImage
        qimage_slic = array2qimage(mb)
        # QImage to QPixmap
        pixmap = QPixmap.fromImage(qimage_slic)
        self.label.setPixmap(pixmap.scaled(self.label.size(), Qt.KeepAspectRatio))

    def slot_query(self):
        newDialog = QDialog();
        #fpath = QFileDialog.getExistingDirectory(newDialog, "Select Directory", '../data')
        fpath = '../data/query'
        self.qFiles = sorted(glob.glob(str(fpath) + '/*.bmp'))
        self.qNames = map(lambda x: os.path.basename(x), self.qFiles)

        self.index = 0
        self.query = QPixmap(self.qFiles[self.index])
        self.slot_slic()
        self.label.setPixmap(self.qdraw.scaled(self.label.size(), Qt.KeepAspectRatio))

        self.mergeSegs = []
        self.querySegs = []
        self.querySegs.append(self.nplabel)

    def slot_gallery(self):
        newDialog = QDialog();
        #fpath = QFileDialog.getExistingDirectory(newDialog, "Select Directory", '../data')
        fpath = '../data/gallery'
        self.gFiles = sorted(glob.glob(str(fpath) + '/*.bmp'))
        self.gNames = map(lambda x: os.path.basename(x), self.gFiles)
        idx = range(len(self.gFiles))
        np.random.shuffle(idx)


        for i in range(len(self.labelset)):
            image = QPixmap(self.gFiles[idx[i]])
            self.labelset[i].setPixmap(image.scaled(self.labelset[i].size(), Qt.KeepAspectRatio))

    def slot_slic(self):
        '''
            perform SLIC superpixel segmentation
            Input: QPixmap self.query
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
        self.npimg = imresize(imgarr, (self.label.size().height(), self.label.size().width()), interp='bicubic')
        self.nplabel = slic.slic_n(self.npimg, 200, 10)
        contours = slic.contours(self.npimg, self.nplabel, 10)
        self.npdraw = contours[:, :, :-1]
        self.npdraw0 = self.npdraw.copy()

        # numpy to QImage
        qimage_slic = array2qimage(self.npdraw)
        # QImage to QPixmap
        self.qdraw = QPixmap.fromImage(qimage_slic)
 
    def slot_merge(self):

        mb = self.npdraw
        # update image label map
        min_label = min(self.mergeSegs)
        for i in range(len(self.mergeSegs)):
            label = self.mergeSegs[i]
            self.nplabel[self.nplabel == label] = min_label

        self.querySegs[self.index] = self.nplabel

        contours = slic.contours(self.npimg, self.nplabel, 10)
        b = contours[:, :, :-1]
        self.npdraw = b
        self.npdraw0 = b.copy()
        self.mergeSegs = []

        mb = self.npdraw

        # numpy to QImage
        qimage_slic = array2qimage(mb)
        # QImage to QPixmap
        pixmap = QPixmap.fromImage(qimage_slic)
        self.label.setPixmap(pixmap.scaled(self.label.size(), Qt.KeepAspectRatio))

    def slot_previous(self):
        self.index -= 1
        if self.index >= 0:
            self.query = QPixmap(self.qFiles[self.index])
            qimage = self.query.toImage()
            # QImage to numpy
            imgarr = rgb_view(qimage)
            self.npimg = imresize(imgarr, (self.label.size().height(), self.label.size().width()), interp='bicubic')
            self.nplabel = self.querySegs[self.index]
            contours = slic.contours(self.npimg, self.nplabel, 10)
            b = contours[:, :, :-1]
            self.npdraw = b
            self.npdraw0 = b.copy()

            # numpy to QImage
            qimage_slic = array2qimage(b)
            # QImage to QPixmap
            pixmap = QPixmap.fromImage(qimage_slic)
            self.label.setPixmap(pixmap.scaled(self.label.size(), Qt.KeepAspectRatio))
            
            self.mergeSegs = []


    def slot_next(self):
        
        self.index += 1
        
        if self.index < len(self.qFiles):
            self.query = QPixmap(self.qFiles[self.index])
            
            if len(self.querySegs) == self.index:

                self.slot_slic()        
                self.label.setPixmap(self.qdraw.scaled(self.label.size(), Qt.KeepAspectRatio))

                self.querySegs.append(self.nplabel)

            else:
                qimage = self.query.toImage()
                # QImage to numpy
                imgarr = rgb_view(qimage)
                self.npimg = imresize(imgarr, (self.label.size().height(), self.label.size().width()), interp='bicubic')
                self.nplabel = self.querySegs[self.index]
                contours = slic.contours(self.npimg, self.nplabel, 10)
                b = contours[:, :, :-1]
                self.npdraw = b
                self.npdraw0 = b.copy()

                # numpy to QImage
                qimage_slic = array2qimage(b)
                # QImage to QPixmap
                pixmap = QPixmap.fromImage(qimage_slic)
                self.label.setPixmap(pixmap.scaled(self.label.size(), Qt.KeepAspectRatio))
            
            self.mergeSegs = []


def main():

    app = QApplication(sys.argv)
    mw = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(mw)
    mw.show()
    sys.exit(app.exec_())

if __name__ == '__main__':

    main()