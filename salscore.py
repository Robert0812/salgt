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
import numpy as np
import cPickle

from PySide.QtGui import *
from PySide.QtCore import * 
from PySide import QtCore, QtGui
from skimage.transform import resize

import string 
import random 

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

def gen_tag(size=6, chars = string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

def imresize(im, shape, interp='bicubic'):
    '''
        replacement of scipy imresize
    '''
    if interp is 'bicubic':
        return (resize(im, shape, order=4)*255).astype(np.uint8)

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

    def mousePressEvent(self, event):
        
        self.emit(SIGNAL('clicked()'))
        event.accept()

class viewer(QtGui.QWidget):

    def __init__(self, imfiles, labeldata):
        super(viewer, self).__init__()

        self.imfiles = imfiles
        self.data = labeldata
        self.initWin()

    def initWin(self):

        self.setGeometry(QtCore.QRect(1095, 10, 400, 820))
        self.centralwidget = QtGui.QWidget(self)
        self.imlabel = QLabel(self.centralwidget)
        self.imlabel.setGeometry(QtCore.QRect(65, 30, 270, 720))

        self.widget1 = QtGui.QWidget(self.centralwidget)
        self.widget1.setGeometry(QtCore.QRect(10, 730, 380, 100))
        self.horizontalLayout = QtGui.QHBoxLayout(self.widget1)
        self.btn_prev = QPushButton(self.widget1)
        self.btn_next = QPushButton(self.widget1)
        self.btn_prev.setText('Prev')
        self.btn_next.setText('Next')
        self.horizontalLayout.addWidget(self.btn_prev)
        self.horizontalLayout.addWidget(self.btn_next)

        QtCore.QObject.connect(self.btn_next, QtCore.SIGNAL("clicked()"), self.slot_next)
        QtCore.QObject.connect(self.btn_prev, QtCore.SIGNAL("clicked()"), self.slot_prev)

        self.index = 0
        #qimage = QPixmap(self.imfiles[self.index])
        #self.imlabel.setPixmap(qimage.scaled(self.imlabel.size(), Qt.KeepAspectRatio))
        self.show_qpixmap(self.index, self.imlabel)
        self.setWindowTitle('Image Viewer')
        self.show()


    def slot_prev(self):
        ''' previous button '''
        self.index = max(self.index - 1, 0)
        #qimage = QPixmap(self.imfiles[self.index])
        #self.imlabel.setPixmap(qimage.scaled(self.imlabel.size(), Qt.KeepAspectRatio))
        self.show_qpixmap(self.index, self.imlabel)

    def slot_next(self):
        ''' next button '''
        self.index = min(self.index + 1, len(self.imfiles)-1)
        #self.imlabel.setPixmap(qimage.scaled(self.imlabel.size(), Qt.KeepAspectRatio))
        self.show_qpixmap(self.index, self.imlabel)

    def show_qpixmap(self, fidx, qlabel):
        '''
            show a QPixmap to a QLabel 
        '''
        qpixmap = QPixmap(self.imfiles[fidx])
        qimage = qpixmap.toImage()
        imgarr = rgb_view(qimage)
        draw0 = imresize(imgarr, (qlabel.height(), qlabel.width()), interp='bicubic')

        draw1 = self.customized_function(draw0, fidx)
         
        qimage = array2qimage(draw1)
        qpixmap_new = QPixmap.fromImage(qimage)
        qlabel.setPixmap(qpixmap_new.scaled(qlabel.size(), Qt.KeepAspectRatio))      

    def customized_function(self, draw0, fidx):
        '''
            customized function for processing the image data 
        '''
        for partid in self.data['scores'][fidx].keys():
            idx = self.data['labels'][fidx] != partid
            diclabel = self.data['scores'][fidx][partid]
            for i in range(2, 3):
                draw0[:, :, i][idx] = np.round(diclabel[0]/(1+diclabel[1])*255.).astype(np.uint8)

        return draw0    


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):

        self.w = 270 #self.label[0].size().width()
        self.h = 720 #self.label[0].size().height()

        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.setGeometry(QtCore.QRect(10, 10, 1080, 820)) #resize(1080, 820)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.label = QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(170, 30, self.w, self.h))
        self.label.setObjectName(_fromUtf8("label"))
        
        self.widget = QtGui.QWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(20, 70, 130, 611))
        self.widget.setObjectName(_fromUtf8("widget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.widget)
        #self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        # add a name tag for each labeler's work
        self.labeler = QPushButton(self.widget)
        self.verticalLayout.addWidget(self.labeler)
        self.labeler.setText('@Login')
        self.labeltag = gen_tag()

        self.pushButton = []
        for i in range(4):
            button = QPushButton(self.widget)
            button.setObjectName('pushButton_{}'.format(i))
            self.pushButton.append(button)
            self.verticalLayout.addWidget(self.pushButton[-1])

        self.widget1 = QtGui.QWidget(self.centralwidget)
        self.widget1.move(460, 30)
        #self.widget1.setGeometry(QtCore.QRect(500, 30, 651, 721))
        self.widget1.setObjectName(_fromUtf8("widget1"))
        self.gridLayout_2 = QtGui.QGridLayout(self.widget1)
        #self.gridLayout_2.setMargin(0)
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
        QtCore.QObject.connect(self.labeler, QtCore.SIGNAL("clicked()"), self.slot_regist)
        #QtCore.QObject.connect(self.pushButton[0], QtCore.SIGNAL(_fromUtf8("clicked()")), self.slot_load)
        QtCore.QObject.connect(self.pushButton[0], QtCore.SIGNAL(_fromUtf8("clicked()")), self.slot_next)
        QtCore.QObject.connect(self.pushButton[1], QtCore.SIGNAL(_fromUtf8("clicked()")), self.slot_prev)
        QtCore.QObject.connect(self.pushButton[2], QtCore.SIGNAL(_fromUtf8("clicked()")), self.slot_unlock)
        #QtCore.QObject.connect(self.pushButton[2], QtCore.SIGNAL(_fromUtf8("clicked()")), self.slot_cheat)
        QtCore.QObject.connect(self.pushButton[3], QtCore.SIGNAL(_fromUtf8("clicked()")), self.slot_exit)
        #QtCore.QObject.connect(self.pushButton[4], QtCore.SIGNAL(_fromUtf8("clicked()")), self.slot_reset)

        self.pushButton[2].setText('Edit mode[off]')
        self.edit = False
        #self.pushButton[4].setDisabled(True)

        for i in range(len(self.labelset)):
            QObject.connect(self.labelset[i], SIGNAL('clicked()'), lambda idx = i: self.slot_click(idx))
        
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # default initialization
        self.data_path = '../data/' # default path

        self.qfiles = sorted(glob.glob(self.data_path + 'query/*.bmp'))
        self.gfiles = sorted(glob.glob(self.data_path + 'gallery/*.bmp'))
        self.qnames = map(lambda x: os.path.basename(x[0:x.find('_')]), self.qfiles)
        self.gnames = map(lambda x: os.path.basename(x[0:x.find('_')]), self.gfiles)
        
        # load source parts
        self.src_path = self.data_path + 'parts_new.pkl'
        if os.path.isfile(self.src_path):
            # labeled data exists

            f = open(self.src_path, 'rb')
            self.data = cPickle.load(f)
            f.close()
            
        else:
            print 'Label data does not exist!'
            QApplication.quit()

        # initial save path
        self.save_path = None

        image = QPixmap('../data/temp.jpg')
        self.label.setPixmap(image.scaled(self.label.size(), Qt.KeepAspectRatio))   
        for i in range(len(self.labelset)):
            self.labelset[i].setPixmap(image.scaled(self.labelset[i].size(), Qt.KeepAspectRatio))


    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Saliency Score Annotation", None))
        self.label.setText(_translate("MainWindow", "TextLabel", None))
        #self.pushButton[0].setText(_translate("MainWindow", "Load Path", None))
        self.pushButton[0].setText(_translate("MainWindow", "Save && Next", None))
        self.pushButton[1].setText(_translate("MainWindow", "Save && Prev", None))
        self.pushButton[2].setText(_translate("MainWindow", "Unlock", None))
        #self.pushButton[2].setText(_translate("MainWindow", "Cheat", None))
        self.pushButton[3].setText(_translate("MainWindow", "Exit", None))
        #self.pushButton[4].setText(_translate("MainWindow", "Reset ALL", None))

        for i in range(4):
            for j in range(8):
                self.labelset[i*8+j].setText(_translate("MainWindow", "Image{}".format(i*8+j+1), None))


    def slot_regist(self):
        '''
            Ask the user to regist a tag for their labeling task 
        '''
        
        seed, result = QtGui.QInputDialog.getInt(None, "Labeling Registration",
                                            "Assigned random seed:")
        if result is False:
            return
        text, result = QtGui.QInputDialog.getText(None, "Labeling Registration",
                                            "Labeler last name:")
        if len(text) is 0:
            return
        
        self.labeltag = '#%02d_%s' % (seed, text)
        self.save_path = self.data_path + self.labeltag + '.pkl'
        self.userdata = {}
        self.userdata['pairidx'] = 0
        self.userdata['scores'] = self.data['scores']
        self.userdata['sflags'] = self.data['sflags']
        self.userdata['marks'] = np.zeros(len(self.qfiles))

        if os.path.isfile(self.save_path):
            # labeled data exists
            f = open(self.save_path, 'rb')
            self.userdata = cPickle.load(f)
            f.close()

        self.pairidx = self.userdata['pairidx'] # index of image-part pair 
        self.seed = seed
        self.random_list(seed)
        self.index = self.pairs[self.pairidx][0]
        self.partid = self.pairs[self.pairidx][1]
        self.qid = self.data['identity'][self.index]

        self.labeler.setText(self.labeltag+':'+str(self.pairidx))
        self.labeler.setDisabled(True)

        # initial visualization 
        self.show_query()
        self.show_gallery()


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
        '''
            show gallery images
        '''

        idx_match = self.gnames.index(self.qnames[self.index])
        idx_mismatch = np.setdiff1d(range(len(self.gfiles)), [idx_match])
        np.random.seed(self.seed + self.pairidx)
        np.random.shuffle(idx_mismatch)
        idx = np.append(idx_mismatch[0:len(self.labelset)-1], idx_match)
        np.random.seed(self.seed + self.pairidx)
        np.random.shuffle(idx)

        self.gidx = idx
        for i in range(len(self.labelset)):
            image = QPixmap(self.gfiles[idx[i]])
            self.labelset[i].setPixmap(image.scaled(self.labelset[i].size(), Qt.KeepAspectRatio))

        if self.userdata['sflags'][self.index][self.partid] is None:
            self.flags = np.zeros(len(self.labelset))
        else:
            self.flags = self.userdata['sflags'][self.index][self.partid]
            for i in range(len(self.labelset)):
                if self.flags[i] == 1:
                    self.draw_rect(i, 'red')
                elif self.flags[i] == 2:
                    self.draw_rect(i, 'green')


    def draw_rect(self, index, color):

        if color is 'red':
            r = 255
            g = 0
        elif color is 'green':
            r = 0
            g = 255

        gimage = QPixmap(self.gfiles[self.gidx[index]]).toImage()
        draw = rgb_view(gimage)
        w = gimage.size().width()
        h = gimage.size().height()
        xx = np.tile(np.asarray(range(w)), (h, 1))
        yy = np.tile(np.asarray(range(h)), (w, 1)).transpose()
            
        idx_x = (xx < 3) + (xx > (w -3))
        idx_y = (yy < 3) + (yy > (h -3))

        draw[:, :, 0][idx_x + idx_y] = r
        draw[:, :, 1][idx_x + idx_y] = g
        draw[:, :, 2][idx_x + idx_y] = 0

        if color is 'red':
            draw[:, :, 0] = 255

        qimage = array2qimage(draw)
        qpixmap = QPixmap.fromImage(qimage)
        self.labelset[index].setPixmap(qpixmap.scaled(self.labelset[index].size(), Qt.KeepAspectRatio))


    def slot_unlock(self):
        # unlock a query to be able to cancel selections

        if self.edit:
            self.pushButton[2].setText('Edit mode[off]')
            self.edit = False
        else:
            self.pushButton[2].setText('Edit mode[on]')
            self.edit = True


    def slot_click(self, index):
        '''
            once clicked, draw rectangle around the selected gallery image
        '''

        if self.userdata['marks'][self.index] == 1 and not self.edit:
            # if is not in edit mode and the current query is marked labeled. 
            return

        elif self.flags[index] == 0:
            # if current gallery image is not selected 

            correct = self.gidx[index] == self.gnames.index(self.qnames[self.index])
            if correct:
                self.userdata['marks'][self.index] = True 

            gimage = QPixmap(self.gfiles[self.gidx[index]]).toImage()
            draw = rgb_view(gimage)

            w = gimage.size().width()
            h = gimage.size().height()
            xx = np.tile(np.asarray(range(w)), (h, 1))
            yy = np.tile(np.asarray(range(h)), (w, 1)).transpose()
            
            idx_x = (xx < 3) + (xx > (w -3))
            idx_y = (yy < 3) + (yy > (h -3))
            idx_xy = idx_x + idx_y

            draw[:, :, 0][idx_xy] = 255*(not correct)
            draw[:, :, 1][idx_xy] = 255*correct
            draw[:, :, 2][idx_xy] = 0

            if not correct:
                draw[:, :, 0] = 255

            self.flags[index] = 1 + correct

            qimage = array2qimage(draw)
            qpixmap = QPixmap.fromImage(qimage)
            self.labelset[index].setPixmap(qpixmap.scaled(self.labelset[index].size(), Qt.KeepAspectRatio))

        elif self.edit:
            # in edit mode: user is allowed to cancel selections

            # if gt is cancelled, reset the marks of current query to False
            if self.flags[index] == 2:
                self.userdata['marks'][self.index] = False

            self.flags[index] = 0
            # show original image without rectangle in border
            gimage = QPixmap(self.gfiles[self.gidx[index]]).toImage()
            draw = rgb_view(gimage)
            qimage = array2qimage(draw)
            qpixmap = QPixmap.fromImage(qimage)
            self.labelset[index].setPixmap(qpixmap.scaled(self.labelset[index].size(), Qt.KeepAspectRatio))


    def save_label(self):

        # save labeled flags 
        self.userdata['sflags'][self.index][self.partid] = self.flags
        # save salience scores
        self.userdata['scores'][self.index][self.partid] = self.flags.sum() - 1 if self.flags.sum() else 0
        # if selections don't include gt, then score is 0
        if self.userdata['marks'][self.index] == 0:
            self.userdata['scores'][self.index][self.partid] = 0
        
        #select_ids = [self.gnames[idx] for idx in self.gidx[self.flags.astype(bool)]]
        #if self.qid in select_ids:
        #    self.userdata['scores'][self.index][self.partid] = 1./self.flags.sum() if self.flags.sum() else 0

        f = open(self.save_path, 'wb')
        cPickle.dump(self.userdata, f, cPickle.HIGHEST_PROTOCOL)
        f.close()

    def slot_prev(self):
        '''
            re-random query and gallery for a new round of annotation
        '''

        if self.save_path is None:
            msg = QMessageBox.warning(None, 'Warning', 'Regist first!', QMessageBox.Ok)
            return 

        self.userdata['pairidx'] = max(self.pairidx - 1, 0)
        self.save_label()

        # print score
        print '[{0:03d}/{1:03d}] image-part ({2:03d}-{3:03d}) selection {4:.2f}'.format(self.pairidx, len(self.pairs), 
            self.index, self.partid,
            self.userdata['scores'][self.index][self.partid]) 

        # prepare for the previous round
        self.pairidx = max(self.pairidx-1, 0)
        self.index = self.pairs[self.pairidx][0]
        self.partid = self.pairs[self.pairidx][1]
        self.qid = self.data['identity'][self.index]

        # visualization 
        self.labeler.setText(self.labeltag + ':' + str(self.pairidx))
        self.show_query()
        self.show_gallery()


    def slot_next(self):
        '''
            re-random query and gallery for a new round of annotation
        '''

        if self.save_path is None:
            msg = QMessageBox.warning(None, 'Warning', 'Regist first!', QMessageBox.Ok)
            return 

        self.userdata['pairidx'] = min(self.pairidx + 1, len(self.pairs)-1)
        self.save_label()

        # print score
        print '[{0:03d}/{1:03d}] image-part ({2:03d}-{3:03d}) selection {4:.2f}'.format(self.pairidx, len(self.pairs), 
            self.index, self.partid,
            self.userdata['scores'][self.index][self.partid]) 

        # prepare for the next round
        self.pairidx = min(self.pairidx+1, len(self.pairs)-1)
        self.index = self.pairs[self.pairidx][0]
        self.partid = self.pairs[self.pairidx][1]
        self.qid = self.data['identity'][self.index]
 
        # visualization 
        self.labeler.setText(self.labeltag + ':' + str(self.pairidx))
        self.show_query()
        self.show_gallery()


    def slot_cheat(self):
        '''
            A dialog for checking the groundtruth image of query
        '''
        self.cheatUI = QWidget()
        self.cheatUI.setWindowTitle('Groundtruth')
        self.cheatUI.setGeometry(QtCore.QRect(1090, 10, 300, 740))
        qlabel = QLabel(self.cheatUI)
        qlabel.setGeometry(QtCore.QRect(10, 10, 270, 720))
        qpixmap = QPixmap(self.qfiles[self.index])
        qimage = qpixmap.toImage()
        imgarr = rgb_view(qimage)
        draw0 = imresize(imgarr, (qlabel.height(), qlabel.width()), interp='bicubic')         
        qimage = array2qimage(draw0)
        qpixmap_new = QPixmap.fromImage(qimage)
        qlabel.setPixmap(qpixmap_new.scaled(qlabel.size(), Qt.KeepAspectRatio)) 
        self.cheatUI.show()


    def slot_viewer(self):
        '''
            A dialog for viewing the labeling result
        '''
        self.viewer = viewer(self.qfiles, self.data)    


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
                score0 = self.userdata['scores'][i]
                for p in score0.keys():
                    score0[p] = 0
                    self.userdata['sflags'][i][p] = np.zeros(len(self.labelset))    

        self.userdata['pairidx'] = 0

        f = open(self.save_path, 'wb')
        cPickle.dump(self.userdata, f, cPickle.HIGHEST_PROTOCOL)
        f.close()

        image = QPixmap('../data/temp.jpg')
        self.label.setPixmap(image.scaled(self.label.size(), Qt.KeepAspectRatio))   
        for i in range(len(self.labelset)):
            self.labelset[i].setPixmap(image.scaled(self.labelset[i].size(), Qt.KeepAspectRatio))
        self.labeler.setText('@Login')
        self.labeler.setDisabled(False)


def main():

    app = QApplication(sys.argv)
    mw = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(mw)
    mw.show()
    sys.exit(app.exec_())

if __name__ == '__main__':

    main()