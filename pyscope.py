#!/usr/bin/env python
#---change log
#---date                author          descption
#---2015-06-18 17:58    harry.zhang     use QtCore.QTimer replace threding.Timer
from PyQt4 import QtCore, QtGui
import random,math


class PyScope(QtGui.QWidget):
    def __init__(self, parent=None):
        super(PyScope, self).__init__(parent)
        self.setWindowTitle(QtCore.QObject.tr(self, "Scope"))
        self.resize(800, 400)
        self.signalColor = QtGui.QColor(0, 250, 0)
        self.gridColor = QtGui.QColor(0, 100, 0, 250)
        self.centergridColor = QtGui.QColor(0, 60, 0, 250)
        self.outlierColor = QtGui.QColor(0, 80, 0, 250)
        self.triggerColor = QtGui.QColor(180, 180, 0, 250)
        self.a=[]
        for i in range(0,20):
            self.a.append (math.sin(math.pi*i/20.0))
        self.timer1 = QtCore.QTimer()
        self.timer1.timeout.connect(self.TimerISR)
        self.timer1.start(100)
        self.isExit = False
        #--config params
        self.screen_hgrid_num = 16
        self.screen_vgrid_num = 8
        self.screen_outblank = 20
        
        print 'height:%d  width:%d' % (self.height(),self.width())
    def CreateTriggerPoly(self, x, y):
        a = QtGui.QPolygon([
            QtCore.QPoint(x,y),
            QtCore.QPoint(x+10,y),
            QtCore.QPoint(x+15,y+5),
            QtCore.QPoint(x+10,y+10),
            QtCore.QPoint(x,y+10),
        ])
        return a
    def paintEvent(self, event):
        #--screen grid
        self.screen_hgrid_len = (self.width()-2*self.screen_outblank)/self.screen_hgrid_num
        self.screen_vgrid_len = (self.height()-2*self.screen_outblank)/self.screen_vgrid_num
        #--draw src_x,src_y
        self.src_x = self.screen_outblank
        self.src_y = self.height() - self.screen_outblank
        self.src_wid = self.screen_hgrid_num*self.screen_hgrid_len
        self.src_hei = self.screen_vgrid_num*self.screen_vgrid_len
        #--begin paint
        painter = QtGui.QPainter()
        painter.begin(self)
        #---draw backgound
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(0,0,0)))
        painter.drawRect(0,0,self.width(), self.height())

        #---draw outlier
        brush = QtGui.QBrush()
        brush.setStyle(QtCore.Qt.NoBrush)
        painter.setBrush(brush)
        painter.setPen(QtGui.QPen(self.outlierColor))
        painter.drawRect(self.screen_outblank,self.screen_outblank,self.src_wid, self.src_hei)

        #---draw trigger point        
        
        painter.save()
        painter.setBrush(QtGui.QBrush(self.triggerColor))
        painter.setPen(QtGui.QPen(self.triggerColor))
        painter.drawConvexPolygon(self.CreateTriggerPoly(3,100))
        
        painter.drawText(QtCore.QPoint(10,self.width()-20),QtCore.QString("T"))
        painter.restore()

        #---draw grid
        pen = QtGui.QPen(self.gridColor)
        pen.setWidth(1)
        pen.setStyle(QtCore.Qt.DotLine)
        painter.setPen(pen)
        brush = QtGui.QBrush()
        brush.setStyle(QtCore.Qt.NoBrush)
        painter.setBrush(brush)
        #----draw vertical grid 
        for j in range(1,self.screen_hgrid_num):
            x_point = self.src_x+j*self.screen_hgrid_len
            painter.drawLine( x_point, self.src_y, x_point, self.src_y-self.src_hei )
        #----draw ver center line
        x_point = self.src_x + self.screen_hgrid_num*self.screen_hgrid_len/2

        painter.save()
        pen = QtGui.QPen(self.centergridColor)
        pen.setStyle(QtCore.Qt.DotLine)
        pen.setWidth(2)
        painter.setPen(pen)

        painter.drawLine( x_point, self.src_y, x_point, self.src_y-self.src_hei )
        pen.setWidth(1)
        painter.restore()

        #----draw hor grid
        for j in range(1,self.screen_vgrid_num):
            y_point = self.src_y - j*self.screen_vgrid_len
            painter.drawLine( self.src_x, y_point, self.src_x + self.src_wid, y_point )

        #----draw hor center line

        y_point = self.src_y - self.screen_vgrid_num*self.screen_vgrid_len/2
        painter.save()
        pen = QtGui.QPen(self.centergridColor)
        pen.setStyle(QtCore.Qt.DotLine)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine( self.src_x, y_point, self.src_x + self.src_wid, y_point )
        painter.restore()


        #---draw signal
        pen = QtGui.QPen(self.signalColor)
        pen.setWidth(1)
        painter.setPen(pen)
        for j in range(0,len(self.a)-1):
            #print self.a[j]
            painter.drawLine(self.src_x + j*10, self.src_y - self.a[j] * self.src_hei,
                    self.src_x + (j+1)*10, self.src_y - self.src_hei * self.a[j+1])
        #--end paint
        painter.end()
    def keyReleaseEvent (self, ev):
        if ev.key() == QtCore.Qt.Key_Escape:
            self.timer1.stop()
            self.close()
        print 'key press:%d' % ev.key()
    def TimerISR(self):
        print "hello"
        if len(self.a) > 80:
            del self.a[0]
        self.a.append(random.random())
        self.repaint()
        if self.isExit == True:
            return
    def closeEvent(self, ev):
        self.isExit = True
        
if __name__ == "__main__":
    import sys

    app = QtGui.QApplication(sys.argv)
    clock = PyScope()
    clock.show()
    sys.exit(app.exec_())

