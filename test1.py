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
        self.pushButton = QtGui.QPushButton(self.widget)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.verticalLayout.addWidget(self.pushButton)
        self.pushButton_6 = QtGui.QPushButton(self.widget)
        self.pushButton_6.setObjectName(_fromUtf8("pushButton_6"))
        self.verticalLayout.addWidget(self.pushButton_6)
        self.pushButton_2 = QtGui.QPushButton(self.widget)
        self.pushButton_2.setObjectName(_fromUtf8("pushButton_2"))
        self.verticalLayout.addWidget(self.pushButton_2)
        self.pushButton_3 = QtGui.QPushButton(self.widget)
        self.pushButton_3.setObjectName(_fromUtf8("pushButton_3"))
        self.verticalLayout.addWidget(self.pushButton_3)
        self.pushButton_4 = QtGui.QPushButton(self.widget)
        self.pushButton_4.setObjectName(_fromUtf8("pushButton_4"))
        self.verticalLayout.addWidget(self.pushButton_4)
        self.pushButton_5 = QtGui.QPushButton(self.widget)
        self.pushButton_5.setObjectName(_fromUtf8("pushButton_5"))
        self.verticalLayout.addWidget(self.pushButton_5)
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
        QtCore.QObject.connect(self.pushButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.slot_load)
        QtCore.QObject.connect(self.pushButton_2, QtCore.SIGNAL(_fromUtf8("clicked()")), self.slot_slic)
        QtCore.QObject.connect(self.pushButton_3, QtCore.SIGNAL(_fromUtf8("clicked()")), self.slot_merge)
        QtCore.QObject.connect(self.pushButton_4, QtCore.SIGNAL(_fromUtf8("clicked()")), self.slot_next)
        QtCore.QObject.connect(self.pushButton_6, QtCore.SIGNAL(_fromUtf8("clicked()")), self.slot_gallery)
        QtCore.QObject.connect(self.label, SIGNAL('clicked()'), self.slot_click)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        files = sorted(glob.glob('../data/*.bmp'))

        self.index = 0
        self.image = QPixmap(files[self.index])
        self.label.setPixmap(self.image.scaled(self.label.size(), Qt.KeepAspectRatio))
        self.mergeSegs = []

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.label.setText(_translate("MainWindow", "TextLabel", None))
        self.pushButton.setText(_translate("MainWindow", "Load Image", None))
        self.pushButton_6.setText(_translate("MainWindow", "Load Gallery", None))
        self.pushButton_2.setText(_translate("MainWindow", "Run SLIC", None))
        self.pushButton_3.setText(_translate("MainWindow", "Merge Segs", None))
        self.pushButton_4.setText(_translate("MainWindow", "Next Image", None))
        self.pushButton_5.setText(_translate("MainWindow", "Exit", None))
        for i in range(4):
            for j in range(8):
                self.labelset[i*8+j].setText(_translate("MainWindow", "ImageLabel", None))

    def slot_click(self):
        cx = self.label.cx
        cy = self.label.cy
        mb = self.showb
        # update image label map
        if self.sliclabel[cy, cx] not in self.mergeSegs:
            self.mergeSegs.append(self.sliclabel[cy, cx]) 
            
            for i in range(1, 3):
                tmp = mb[:, :, i]
                tmp[self.sliclabel == self.sliclabel[cy, cx]] = 0
                mb[:, :, i] = tmp
        else:
            self.mergeSegs.pop(self.mergeSegs.index(self.sliclabel[cy, cx]))
            for i in range(1, 3):
                tmp = mb[:, :, i]
                initb = self.initb[:, :, i]
                idx = self.sliclabel == self.sliclabel[cy, cx]
                
                tmp[idx] = initb[idx]
                mb[:, :, i] = tmp

            #test = Image.fromarray(initb)
            #test.show()
        self.showb = mb
        print self.mergeSegs

        # numpy to QImage
        qimage_slic = array2qimage(mb)
        # QImage to QPixmap
        pixmap = QPixmap.fromImage(qimage_slic)
        self.label.setPixmap(pixmap.scaled(self.label.size(), Qt.KeepAspectRatio))

    def slot_load(self):
        newDialog = QDialog();
        fpath = QFileDialog.getExistingDirectory(newDialog, "Select Directory")
        self.files = sorted(glob.glob(str(fpath) + '/*.bmp'))

        self.index = 0
        self.image = QPixmap(self.files[self.index])
        self.label.setPixmap(self.image.scaled(self.label.size(), Qt.KeepAspectRatio))
        self.slot_slic()
        self.mergeSegs = []

    def slot_gallery(self):
        newDialog = QDialog();
        fpath = QFileDialog.getExistingDirectory(newDialog, "Select Directory", '../data')
        files = sorted(glob.glob(str(fpath) + '/*.bmp'))
        self.gfiles = map(lambda x: os.path.basename(x), files)
        print self.gfiles
        for i in range(len(self.labelset)):
            image = QPixmap(files[i])
            self.labelset[i].setPixmap(image.scaled(self.labelset[i].size(), Qt.KeepAspectRatio))

    def slot_slic(self):
        w = self.image.width()
        h = self.image.height()
        # QPixmap to QImage
        qimage = self.image.toImage()
        # QImage to numpy
        imgarr = rgb_view(qimage)
        #imgarr = qimage2numpy(qimage)
        a = imresize(imgarr, (self.label.size().height(), self.label.size().width()), interp='bicubic')
        slic_label = slic.slic_n(a, 200, 10)
        contours = slic.contours(a, slic_label, 10)
        b = contours[:, :, :-1]
        # numpy to QImage
        qimage_slic = array2qimage(b)
        # QImage to QPixmap
        pixmap = QPixmap.fromImage(qimage_slic)
        self.label.setPixmap(pixmap.scaled(self.label.size(), Qt.KeepAspectRatio))
        self.img = a
        self.sliclabel = slic_label
        self.initb = b
        self.showb = b.copy()

    def slot_merge(self):
        print 'merge'

    def slot_next(self):
        self.index += 1
        if self.index < len(self.files):
            self.image = QPixmap(self.files[self.index])
            self.label.setPixmap(self.image.scaled(self.label.size(), Qt.KeepAspectRatio))
            self.slot_slic()

def main():

    app = QApplication(sys.argv)
    mw = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(mw)
    mw.show()
    sys.exit(app.exec_())

if __name__ == '__main__':

    main()