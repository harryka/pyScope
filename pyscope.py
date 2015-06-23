#!/usr/bin/env python
#---change log
#---date                author          descption
#---2015-06-18 17:58    harry.zhang     use QtCore.QTimer replace threding.Timer
#---2015-06-19 01:15    harry.zhang     Just test git
#---2015-06-19 01:15    zp8613          adjust hor lens
#---2015-06-20 00:50    harry.zhang     Add PyScopeUI class
#---2015-06-24 00:01    harry.zhang     Add Slider to control trigger level
from PyQt4 import QtCore, QtGui
import random,math

class PyScopeUI(QtGui.QWidget):
    def __init__(self, parent=None):
        super(PyScopeUI, self).__init__(parent)
        self.setWindowTitle(QtCore.QObject.tr(self, "Scope"))
        layout = QtGui.QGridLayout()
        layoutBtn = QtGui.QVBoxLayout()
        self.VerticalGroupBox = QtGui.QGroupBox("vertical layout")

        self.pyscope = PyScope()
        self.startBtn = QtGui.QPushButton("start")
        self.startBtn.clicked.connect(self.funcBtnStart)
        self.closeBtn = QtGui.QPushButton("close")
        self.closeBtn.clicked.connect(self.funcBtnClose)
        self.colorBtn = QtGui.QPushButton("color")
        self.colorBtn.clicked.connect(self.funcBtnColor)
        self.triggerSlider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.triggerSlider.setRange(0,100)
        self.triggerSlider.valueChanged.connect(self.funcSliderTrigger)

        layoutBtn.addWidget( self.startBtn)
        layoutBtn.addWidget( self.closeBtn)
        layoutBtn.addWidget( self.colorBtn)
        layoutBtn.addWidget( self.triggerSlider)

        self.VerticalGroupBox.setLayout(layoutBtn)

        layout.addWidget(self.pyscope,0,0)
        layout.addWidget(self.VerticalGroupBox,0,1)
        self.setLayout(layout)
    def funcSliderTrigger(self,val):
        print 'slider val:%d' % val
        self.pyscope.triggerLevel = val
        self.pyscope.repaint()
    def funcBtnStart (self):
        self.pyscope.StarRefresh()
    def funcBtnColor(self):
        c = QtGui.QColorDialog.getColor()
        if c.isValid():
            self.pyscope.signalColor = c
    def funcBtnClose(self):
        self.close()
    def keyReleaseEvent (self, ev):
        if ev.key() == QtCore.Qt.Key_Escape:
            self.close()
        print 'key press:%d' % ev.key()

class PyScope(QtGui.QWidget):
    def __init__(self, parent=None):
        super(PyScope, self).__init__(parent)
        self.setWindowTitle(QtCore.QObject.tr(self, "Scope"))
        self.setFixedSize(800,400)
        self.resize(800, 400)
        self.signalColor = QtGui.QColor(200, 50, 0)
        self.gridColor = QtGui.QColor(0, 100, 0, 250)
        self.centergridColor = QtGui.QColor(0, 60, 0, 250)
        self.outlierColor = QtGui.QColor(0, 80, 0, 250)
        self.triggerColor = QtGui.QColor(180, 180, 0, 250)
        self.triggerLevel = 0
        self.a=[]
        for i in range(0,200):
            self.a.append (math.sin(2*math.pi*i/300.0)*0.5+0.5)
        for i in range(0,200):
            self.a.append ((i%50)/50.0)
        for i in range(0,200):
            self.a.append (0.2 if (((i/20)%2)==1) else 0.8)
        #--config params
        self.screen_hgrid_num = 16
        self.screen_vgrid_num = 8
        self.screen_outblank = 20
        #----screen time window ms
        self.screen_time_window = 1000
        #---screen refresh time ms
        self.screen_refresh_time = 20
        #---data sample time ms
        self.screen_sample_time = 2
        
        print 'height:%d  width:%d' % (self.height(),self.width())
    def StarRefresh(self):
        #--config timer 1
        self.timer1 = QtCore.QTimer()
        self.timer1.timeout.connect(self.TimerISR)
        self.timer1.start(100)
        #--config timer refresh
        self.timer_refresh = QtCore.QTimer()
        self.timer_refresh.timeout.connect(self.RefreshTimerISR)
        self.timer_refresh.start(20)

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
        painter.setBrush( QtGui.QBrush( self.triggerColor))
        painter.setPen( QtGui.QPen( self.triggerColor))
        painter.drawConvexPolygon( self.CreateTriggerPoly( 3, self.src_y - self.src_hei*self.triggerLevel/100-5))
        
        painter.drawText(QtCore.QPoint( 10, self.width()-20), QtCore.QString("Test"))
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
            painter.drawLine(self.src_x + j, self.src_y - self.a[j] * self.src_hei,
                    self.src_x + (j+1), self.src_y - self.src_hei * self.a[j+1])
        #--end paint
        painter.end()
    def TimerISR(self):
        print "hello"
        if len(self.a) > self.src_wid:
            del self.a[0]
        self.a.append(random.random())
        
    def RefreshTimerISR(self):
        self.repaint()
    def close(self):
        self.timer1.stop()
        self.timer_refresh.stop()
if __name__ == "__main__":
    import sys

    app = QtGui.QApplication(sys.argv)
    clock = PyScopeUI()
    clock.show()
    sys.exit(app.exec_())

