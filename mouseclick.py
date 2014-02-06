import os
import sys
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import * 
import glob
import slic
import itertools

class LabelSegs(QMainWindow): 

    def __init__(self, parent=None):
        super(QMainWindow, self).__init__(parent)

        self.setWindowTitle('Select Window')
        self.local_image = QImage('test.bmp')

        self.local_grview = QGraphicsView()
        self.setCentralWidget( self.local_grview )

        self.local_scene = QGraphicsScene()

        self.image_format = self.local_image.format()
        #self.pixMapItem = self.local_scene.addPixmap( QPixmap(self.local_image) )
        self.pixMapItem = QGraphicsPixmapItem(QPixmap(self.local_image), None, self.local_scene)
        self.pixMapItem2 = self.local_scene.addPixmap(QPixmap(self.local_image))
        self.pixMapItem2.setOffset(QPointF(50, 0))

        self.local_grview.setScene(self.local_scene)

        self.pixMapItem.mousePressEvent = self.pixelSelect
        self.pixMapItem2.mousePressEvent = self.pixelSelect

    def pixelSelect( self, event ):
        print 'hello'
        position = QPoint( event.pos().x(),  event.pos().y())
        color = QColor.fromRgb(self.local_image.pixel( position ) )
        if color.isValid():
            rgbColor = '('+str(color.red())+','+str(color.green())+','+str(color.blue())+','+str(color.alpha())+')'
            self.setWindowTitle( 'Pixel position = (' + str( event.pos().x() ) + ' , ' + str( event.pos().y() )+ ') - Value (R,G,B,A)= ' + rgbColor)
        else:
            self.setWindowTitle( 'Pixel position = (' + str( event.pos().x() ) + ' , ' + str( event.pos().y() )+ ') - color not valid')

class LabelParts(QWidget):

    def __init__(self):
        super(QWidget, self).__init__()

        self.setWindowTitle('Label Superpixel to Parts')
        grid = QGridLayout()

        local_scene = self.load_files()

        btn_loadfiles = QPushButton('load files', self)
        btn_loadfiles.clicked.connect(self.load_files)

        grid.addWidget(local_scene, 0, 1)
        grid.addWidget(btn_loadfiles, 0, 0)

        self.setLayout(grid)

        self.move(300, 150)

        #self.connect(self.btn_loadfiles, SIGNAL("clicked()"), self.load_files)
        
        #for i in range(len(files)):
        #    self.local_image = QImage(files[i])
        #    self.local_grview = QGraphicsView()
        #    self.setCentralWidget( self.local_grview )

    def load_files(self):
        local_scene = QGraphicsScene()

        fpath = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        files = sorted(glob.glob(fpath + '/*.bmp'))
        print fpath
        self.pixMapItem = []
        for i in range(len(files)):
            print i
            local_image = QImage(files[i])
            pixMapItem = QGraphicsPixmapItem(QPixmap(local_image), None, local_scene)
            self.pixMapItem.append(pixMapItem)
            pixMapItem.setOffset(QPointF(50*i, 0))

        return local_scene

class RectWidget(QtGui.QGraphicsWidget):
    def __init__(self, thumb_path, parent = None):
        QGraphicsWidget.__init__(self, parent)

        self.labelheight = 30
        self.bordersize = 1
        self.picdims = [100, 75]
        self.thumb_path = thumb_path
        self.pic = self.getpic(thumb_path)

        self._boundingRect = QtCore.QRect()
        
        self.setAcceptHoverEvents(True)


    def boundingRect(self):
        width = self.pic.rect().width() + self.bordersize * 2
        #height = self.pic.rect().height() + self.labelheight + self.bordersize * 2
        height = self.pic.rect().height() + self.bordersize * 2
        
        thumb_widget_rect = QtCore.QRectF(0.0, 0.0, width, height)
        self._boundingRect = thumb_widget_rect

        return thumb_widget_rect


    def sizeHint(self, which, constraint = QtCore.QSizeF()):
        return self._boundingRect.size()


    def getpic(self, thumb_path):
        orpixmap = QtGui.QPixmap()
        orpixmap.load(self.thumb_path)

        return orpixmap    


    def paint(self, painter, option, widget):
        pen = QtGui.QPen()
        pen.setWidth(1)
        pen.setBrush(QtCore.Qt.black)
        painter.setPen(pen)
        
        # Draw border
        painter.drawRect(QtCore.QRect(0, 
                          0, 
                          self.pic.rect().width() + self.bordersize, 
                          self.pic.rect().height() + self.bordersize))
        #                  self.pic.rect().height() + self.labelheight + self.bordersize))

        # Fill label
        #painter.fillRect(QtCore.QRect(self.bordersize, 
        #                              self.bordersize + self.pic.rect().height(), 
        #                              self.pic.rect().width(), 
        #                              self.labelheight), 
        #                              QtCore.Qt.gray)

        # Draw image
        painter.drawPixmap(QtCore.QRect(self.bordersize, 
                                        self.bordersize, 
                                        self.pic.rect().width(), 
                                        self.pic.rect().height()), 
                           self.pic, 
                           self.pic.rect())

        # Draw text
        #text_rect = QtCore.QRect(0, 
        #                         self.pic.rect().y() + self.pic.rect().height(), 
        #                         self.pic.rect().width(), 
        #                         self.labelheight)
                                 
        #painter.drawText(text_rect, QtCore.Qt.AlignCenter, 'hello there')
        
        
    def mousePressEvent(self, event):
        #print('Widget Clicked')

    def mouseHoverEvent(self, event):
        print('Widget enter')

    def mouseReleaseEvent(self, event):
        print('Widget release')

class ImageWidget(QGraphicsLayoutItem):

    def __init__(self, image, parent=None):
        QGraphicsLayoutItem.__init__(self, parent)
        #super(ImageWidget, self).__init__(parent)
        self.gitem = QGraphicsPixmapItem()
        self.gitem.setPixmap(QPixmap(image))
    
    def sizeHint(which, constraint, other):
        return QSizeF(200, 200) 

    def setGeometry(self, rect):
        self.gitem.setPos(rect.topLeft())

    def getGraphicsItem(self):
        return self.gitem

    def setGraphicsItem(self, item):
        self.gitem = item


class MainWindow(QMainWindow): 

    def __init__(self):
        super(MainWindow, self).__init__()

        self.resize(800, 700)
        self.setWindowTitle('test application')

        self.scene = QtGui.QGraphicsScene()
        self.view = QtGui.QGraphicsView(self.scene)
        self.panel = QtGui.QGraphicsWidget()
        self.scene.addItem(self.panel)
        #self.pixMapItem = QGraphicsPixmapItem(QPixmap(QImage('test.bmp')), None, self.scene)
        layout = QtGui.QGraphicsGridLayout()
        self.panel.setLayout(layout)

        COLUMNS=4
        ROWS=4
        files = sorted(glob.glob('./label/select/*.bmp'))

        i = 0
        for row, column in itertools.product(range(ROWS),range(COLUMNS)):
            print('Drawing', row, column, files[i])

            #local_image = QImage(files[i])
            im_widget = RectWidget(files[i])

            layout.addItem(im_widget, row, column, 1, 1)
            layout.setColumnSpacing (column, 5)
            layout.setRowSpacing(row, 5)
            i += 1 

        self.setCentralWidget(self.view)
        self.view.show()

def main():
    app = QtGui.QApplication(sys.argv)
    form = MainWindow()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()