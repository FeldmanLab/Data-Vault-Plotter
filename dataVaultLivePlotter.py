from __future__ import division
import sys
import twisted
from PyQt4 import QtCore, QtGui, QtTest, uic
from twisted.internet.defer import inlineCallbacks, Deferred
import numpy as np
import pyqtgraph as pg
import exceptions
import time
import copy
import datetime as dt
import subprocess
from subprocess import *

path = sys.path[0]

sys.path.append(sys.path[0] + '\Resources')
import dvPlotterResources_rc

mainWinGUI = path + r"\startPlotter.ui"
plotExtentGUI = path + r"\extentPrompt.ui"
plot2DWinGUI = path + r"\plot2DWindow.ui"
plot1DWinGUI = path + r"\plot1DWindow.ui"
plotSavedWin1GUI = path + r"\plot2DWindow.ui"#r"\plotSavedWindow1.ui"
dvExplorerGUI = path + r"\dvExplorer.ui"
dirExplorerGUI = path + r"\dirExplorer.ui"
editInfoGUI = path + r"\editDatasetInfo.ui"
plotSetupUI = path + r"\plotSetup.ui"

Ui_MainWin, QtBaseClass = uic.loadUiType(mainWinGUI)
Ui_ExtPrompt, QtBaseClass = uic.loadUiType(plotExtentGUI)
Ui_PlotWin, QtBaseClass = uic.loadUiType(plot2DWinGUI)
Ui_Plot1DWin, QtBaseClass = uic.loadUiType(plot1DWinGUI)
Ui_PlotSavedWin, QtBaseClass = uic.loadUiType(plotSavedWin1GUI)
Ui_DataVaultExp, QtBaseClass = uic.loadUiType(dvExplorerGUI)
Ui_DirExp, QtBaseClass = uic.loadUiType(dirExplorerGUI)
Ui_EditDataInfo, QtBaseClass = uic.loadUiType(editInfoGUI)
Ui_PlotSetup, QtBaseClass = uic.loadUiType(plotSetupUI)


class dvPlotter(QtGui.QMainWindow, Ui_MainWin):
	def __init__(self, reactor, parent = None):
		super(dvPlotter, self).__init__(parent)
		QtGui.QMainWindow.__init__(self)
		
		self.setupUi(self)
		self.reactor = reactor
		
		self.moveDefault()
		self.initReact(self.reactor)
		
		self.plotSavedBtn.clicked.connect(self.plotSavedDataFunc)
		self.listen.clicked.connect(self.setupListener)
		self.closeWin.clicked.connect(self.closePlotter)
		self.plotLive.clicked.connect(self.plotLiveData)
		
		self.changeDir.setEnabled(False)
		
		self.listStatus = False
		
		self.listenTo = ['']
		
		self.IDs = [00001, 00002, 00003]
		
	def moveDefault(self):
		self.move(25,25)
		
	@inlineCallbacks
	def initReact(self, c):
		from labrad.wrappers import connectAsync
		try:
			self.cxn = yield connectAsync(name = 'dirExplorer')
			self.dv = yield self.cxn.data_vault
		except:
			print 'Either no LabRad connection or DataVault connection.'
		
	@inlineCallbacks
	def initListener(self, c):
		if self.listStatus == False:
			self.listen.clicked.disconnect()
			self.changeDir.clicked.connect(self.setupListener)
		
		try:
			#self.cxn = yield connectAsync(name = 'dirExplorer')
			#self.dv = yield self.cxn.data_vault

			yield self.dv.signal__new_dataset(00001)
			yield self.dv.addListener(listener=self.open_dataset, source=None, ID=00001)
			#yield self.dv.signal__data_available(self.IDs[1])
			#yield self.dv.addListener(listener = plot1DWindow.updatePlot, source=None, ID=self.IDs[1])
			#yield self.dv.signal__new_parameter(self.ID_NEWPARAM)
			#yield self.dv.addListener(listener=self.update_params, source=None, ID=self.ID_NEWPARAM)
			yield self.dv.cd(self.listenTo)

			self.listen.setText('Listening!')
			self.changeDir.setEnabled(True)
			self.listStatus = True
			
			reg = "QPushButton#listen"
			press = "QPushButton:pressed#listen"
			regStr = reg + "{color: rgb(10,200,30);background-color:rgb(0,0,0);border: 2px solid rgb(10,200,30);border-radius: 5px}"
			pressStr = press + "{color: rgb(0,0,0); background-color:rgb(10,200,30);border: 2px solid rgb(10,200,30);border-radius: 5px}" 
			style = regStr + " " + pressStr
			self.listen.setStyleSheet(style)	
			
			reg = "QPushButton#changeDir"
			press = "QPushButton:pressed#changeDir"
			regStr = reg + "{color: rgb(200,60,0);background-color:rgb(0,0,0);border: 2px solid rgb(200,60,0);border-radius: 5px}"
			pressStr = press + "{color: rgb(0,0,0); background-color:rgb(200,60,0);border: 2px solid rgb(200,60,0);border-radius: 5px}" 
			style = regStr + " " + pressStr
			self.changeDir.setStyleSheet(style)
			
		except:
			print 'Either no LabRad connection or DataVault connection.'

	@inlineCallbacks
	def update(self, c):
		yield self.sleep(0.5)
		
	def open_dataset(self, c, signal):
		self.listenPlotFile =  signal
		setupListenPlot = plotSetup(self.reactor, signal, self.listenTo, self.cxn, self.dv, 0, self)
		setupListenPlot.show()
	
	def update_params(self):
		pass
		
	def setListenDir(self, dir, list):
		self.listenDir.setText(str(dir))
		self.listenDir.setStyleSheet("QLabel#listenDir {color: rgb(131,131,131);}")
		self.listenTo = list
		
	def openLivePlots(self, twoPlots, onePlots, fresh):

		x0, y0 = 450, 25
		for index in range(0, len(twoPlots)):
			new2DPlot = plot2DWindow(self.reactor, twoPlots[index], self.listenTo, self.listenPlotFile, x0, y0, fresh, self)
			new2DPlot.show()			
			y0 += 50
		x0, y0 = 1250, 25
		for index in range(0, len(onePlots)):
			new1DPlot = plot1DWindow(self.reactor, onePlots[index], self.listenTo, self.listenPlotFile, x0, y0, fresh, self)
			new1DPlot.show()
			y0 += 50
			
	
	def openSavedPlots(self, file, dir, twoPlots):
		x0, y0 = 450, 25
		for index in range(0, len(twoPlots)):
			self.thing = plotSavedWin(self.reactor, file, dir, twoPlots[index], x0, y0)
			self.thing.show()	
			y0 += 50


		

	def plotLiveData(self):
		dvExplorer = dataVaultExplorer(self.reactor, 'live', self)
		dvExplorer.show()
		
	def setupListener(self):
		self.listen.setEnabled(False)
		self.changeDir.setEnabled(False)
		drcExplorer = dirExplorer(self.reactor, self.listStatus, self)
		drcExplorer.show()
		
	def plotSavedDataFunc(self):

		dvExplorer = dataVaultExplorer(self.reactor, 'saved', self)
		dvExplorer.show()
		
	def sleep(self,secs):
		d = Deferred()
		self.reactor.callLater(secs,d.callback,'Sleeping')
		return d
		
	def closePlotter(self, e):
		self.reactor.stop()
		self.close()
		print 'Reactor shut down.'

	def closeEvent(self, e):
		self.reactor.stop()
		print 'Reactor shut down.'

class extentPrompt(QtGui.QDialog, Ui_ExtPrompt):
	def __init__(self, reactor, plotInfo, x0, y0, parent = None):
		super(extentPrompt, self).__init__(parent)
		QtGui.QDialog.__init__(self)
		
		self.reactor = reactor
		self.plotInfo = plotInfo
		self.mainWin = parent
		self.setupUi(self)
		
		self.x0, self.y0 = x0, y0
		self.moveDefault()
		
		self.setupTable()
		
		self.ok.clicked.connect(self.checkExt)
	
	def editExt(self, r, c):
		self.extTable.item(r, c).setText('')
		self.extTable.editItem(self.extTable.item(r, c))
		
		
	def setupTable(self):
		self.extTable.horizontalHeader().hide()
		self.extTable.verticalHeader().hide()
		self.extTable.cellDoubleClicked.connect(self.editExt)

		self.extTable.setColumnCount(4)
		self.extTable.setRowCount(len(self.plotInfo) + 1)

		min, max, pts = QtGui.QTableWidgetItem(), QtGui.QTableWidgetItem(), QtGui.QTableWidgetItem(), 
		
		headers = [min, max, pts]
		
		min.setText('Minimum Value')		
		min.setTextColor(QtGui.QColor(131,131,131))
		max.setText('Maximum Value')
		max.setTextColor(QtGui.QColor(131,131,131))
		pts.setText('Number of Points')
		pts.setTextColor(QtGui.QColor(131,131,131))

		for ii in range(0, 3):
			self.extTable.setItem(0, ii+1, headers[ii])
			self.extTable.item(0, ii+1).setFont(QtGui.QFont("MS Shell Dlg 2",weight=QtGui.QFont.Bold))
			self.extTable.item(0, ii+1).setFlags(QtCore.Qt.NoItemFlags)

		self.extTable.setColumnWidth(0, 100)
		self.extTable.setColumnWidth(1, 125)
		self.extTable.setColumnWidth(2, 125)
		self.extTable.setColumnWidth(3, 125)
		
		for ii in range(0, len(self.plotInfo)):
			item = QtGui.QTableWidgetItem()
			item.setText(self.plotInfo[ii])
			item.setFont(QtGui.QFont("MS Shell Dlg 2",weight=QtGui.QFont.Bold))
			self.extTable.setItem(ii+1, 0, item)
			self.extTable.item(ii+1, 0).setFlags(QtCore.Qt.NoItemFlags)
		for r in range(1, len(self.plotInfo) + 1):
			for c in range(1, 4):
				item = QtGui.QTableWidgetItem()
				self.extTable.setItem(r, c, item)
				self.extTable.item(r, c).setBackgroundColor(QtGui.QColor(255,255,255))
				
		


				

	def moveDefault(self):
		self.move(self.x0, self.y0)
		
	def checkExt(self):
		extents , pxsize = {}, {}
		errCell = []
		
		for r in range(1, len(self.plotInfo) + 1):
			for c in range(1, 4):
				self.extTable.item(r, c).setBackgroundColor(QtGui.QColor(255,255,255))
		
		for r in range(1, self.extTable.rowCount()):
			try:
				extents[str(self.extTable.item(r, 0).text())] = [float(self.extTable.item(r, 1).text()), float(self.extTable.item(r, 2).text())]
				if float(self.extTable.item(r, 1).text()) == float(self.extTable.item(r, 2).text()):
					errCell.append([r,1])
					errCell.append([r,2])
			except:
				errCell.append([r,1])
				errCell.append([r,2])

			try:
				pxsize[str(self.extTable.item(r, 0).text())] = int(self.extTable.item(r, 3).text())
				if int(self.extTable.item(r, 3).text()) == 0:
					errCell.append([r,3])
			except:
				errCell.append([r,3])

		
		
		if len(errCell) == 0:
			self.mainWin.extents = extents
			self.mainWin.pxsize = pxsize
			self.accept()
		else:
			print errCell
			for ii in range(0, len(errCell)):
				self.extTable.item(errCell[ii][0], errCell[ii][1]).setBackgroundColor(QtGui.QColor(250,190,160))
				
	def closeEvent(self, e):
		self.reject()
		
class plot2DWindow(QtGui.QMainWindow, Ui_PlotWin):
	def __init__(self, reactor, plotInfo, dir, file, x0, y0, fresh, parent = None):
		super(plot2DWindow, self).__init__(parent)
		QtGui.QMainWindow.__init__(self)

		self.reactor = reactor
		self.mainWin = parent
		self.dir = dir
		self.fileName = file
		self.plotInfo = plotInfo
		#fresh specifies if the dataset to be plotted already has data (1) or is empty (0)
		self.fresh = fresh
		

		self.setupUi(self)
		
		self.pX, self.pY = x0, y0
		self.extents = [self.plotInfo[0][2][0], self.plotInfo[0][2][1], self.plotInfo[1][2][0], self.plotInfo[1][2][1]]
		self.pxsize = [self.plotInfo[0][3], self.plotInfo[0][3]]

		self.moveDefault()
		
		self.xIndex = self.plotInfo[0][0]
		self.yIndex = self.plotInfo[1][0]
		self.zIndex = self.plotInfo[2][0]
	
		self.isData = False	
		
		self.Data = np.array([])
		
		self.setupPlot()
		self.setupListener(self.reactor)
		
	def moveDefault(self):
		self.move(self.pX, self.pY)
		
	@inlineCallbacks
	def getExtents(self, c):
		yield self.dv.open()
		
	@inlineCallbacks
	def setupListener(self, c):
		from labrad.wrappers import connectAsync
		self.cxn = yield connectAsync(name = '2DPlot')
		self.dv = yield self.cxn.data_vault
		yield self.dv.cd(self.dir)
		yield self.dv.open(self.fileName)
		newData = yield self.dv.get()
		if len(newData) != 0:
			inx = np.delete(np.arange(0, len(newData[0])), [self.xIndex, self.yIndex, self.zIndex])
			newData = np.delete(np.asarray(newData), inx, axis = 1)
			newData[::, 0] = np.digitize(newData[::, 0], self.xBins) - 1
			newData[::, 1] = np.digitize(newData[::, 1], self.yBins) - 1

			for pt in newData:
				self.plotData[int(pt[0]), int(pt[1])] = pt[2]

			self.mainPlot.setImage(self.plotData, autoRange = True , autoLevels = True, pos=[self.extents[0], self.extents[2]],scale=[self.xscale, self.yscale])
			self.isData = True			
		
		yield self.dv.signal__data_available(00002)
		yield self.dv.addListener(listener=self.updatePlot, source=None, ID=00002)
		'''
		if self.fresh == 1:
			newData = yield self.dv.get()
			inx = np.delete(np.arange(0, len(newData[0])), [self.xIndex, self.yIndex, self.zIndex])
			newData = np.delete(np.asarray(newData), inx, axis = 1)
			newData[::, 0] = np.digitize(newData[::, 0], self.xBins) - 1
			newData[::, 1] = np.digitize(newData[::, 1], self.yBins) - 1

			for pt in newData:
				self.plotData[int(pt[0]), int(pt[1])] = pt[2]

			self.mainPlot.setImage(self.plotData, autoRange = True , autoLevels = True, pos=[self.extents[0], self.extents[2]],scale=[self.xscale, self.yscale])
			self.isData = True
		'''
		
		
	def setupPlot(self):
		self.plotTitle.setText(self.plotInfo[-1])
		self.plotTitle.setStyleSheet("QLabel#plotTitle {color: rgb(131,131,131); font: bold 11pt;}")
		
		self.viewBig = pg.PlotItem(name = "Plot")
		self.viewBig.showAxis('top', show = True)
		self.viewBig.showAxis('right', show = True)
		self.viewBig.setLabel('left', self.plotInfo[1][1])
		self.viewBig.setLabel('bottom', self.plotInfo[0][1])
		self.viewBig.setAspectLocked(lock = False, ratio = 1)
		self.mainPlot = pg.ImageView(parent = self.plot2DFrame, view = self.viewBig)
		self.mainPlot.setGeometry(QtCore.QRect(0, 0, 700, 550))
		self.mainPlot.ui.menuBtn.hide()
		self.mainPlot.ui.histogram.item.gradient.loadPreset('bipolar')
		self.mainPlot.ui.roiBtn.hide()
		self.mainPlot.ui.menuBtn.hide()
		self.viewBig.setAspectLocked(False)
		self.viewBig.invertY(False)
		self.viewBig.setXRange(-1, 1)
		self.viewBig.setYRange(-1, 1)

		self.plotData = np.zeros([self.pxsize[0], self.pxsize[1]])
		
		self.xscale, self.yscale = np.absolute((self.extents[1] - self.extents[0])/self.pxsize[0]), np.absolute((self.extents[3] - self.extents[2])/self.pxsize[1])
		self.mainPlot.setImage(self.plotData, autoRange = True , autoLevels = True, pos=[self.extents[0], self.extents[2]],scale=[self.xscale, self.yscale])
		
		
		self.xBins = np.linspace(self.extents[0] - 0.5 * self.xscale, self.extents[1] + 0.5 * self.xscale, self.pxsize[0]+1)
		self.yBins = np.linspace(self.extents[2] - 0.5 * self.yscale, self.extents[3]+0.5 * self.yscale, self.pxsize[1]+1)
		
	@inlineCallbacks	
	def updatePlot(self, c, signal):
		newData = yield self.dv.get()
		inx = np.delete(np.arange(0, len(newData[0])), [self.xIndex, self.yIndex, self.zIndex])
		newData = np.delete(np.asarray(newData), inx, axis = 1)
		newData[::, 0] = np.digitize(newData[::, 0], self.xBins) - 1
		newData[::, 1] = np.digitize(newData[::, 1], self.yBins) - 1

		for pt in newData:
			self.plotData[int(pt[0]), int(pt[1])] = pt[2]

		self.mainPlot.setImage(self.plotData, autoRange = True , autoLevels = True, pos=[self.extents[0], self.extents[2]],scale=[self.xscale, self.yscale])

		
	def closeEvent(self, e):
		self.cxn.disconnect()
		self.close()		

class plot1DWindow(QtGui.QDialog, Ui_Plot1DWin):
	def __init__(self, reactor, plotInfo, dir, file, x0, y0, fresh, parent = None):
		super(plot1DWindow, self).__init__(parent)
		QtGui.QDialog.__init__(self)

		self.reactor = reactor
		self.mainWin = parent
		self.dir = dir
		self.fileName = file
		self.plotInfo = plotInfo
		self.fresh = fresh
		self.setupUi(self)
		
		self.pX, self.pY = x0, y0
		self.moveDefault()
		
		self.isData = False
		self.Data = np.array([])
		
		self.xIndex = self.plotInfo[0][0]
		self.yIndex = self.plotInfo[1][0]
		
		self.extents = [self.plotInfo[0][2][0], self.plotInfo[0][2][1]]
		self.pxsize = self.plotInfo[0][3]
		
		self.setupPlot()
		self.setupListener(self.reactor)
		
	def moveDefault(self):
		self.move(self.pX, self.pY)
		
	def setupPlot(self):
		
		self.plotTitle.setText(self.plotInfo[-1])
		self.plotTitle.setStyleSheet("QLabel#plotTitle {color: rgb(131,131,131); font: bold 11pt;}")
		self.plot1D = pg.PlotWidget(parent = self.plot1DFrame)
		self.plot1D.setGeometry(QtCore.QRect(0, 0, 600, 320))
		self.plot1D.showAxis('right', show = True)
		self.plot1D.showAxis('top', show = True)
		self.plot1D.setLabel('left', self.plotInfo[1][1])
		self.plot1D.setLabel('bottom', self.plotInfo[0][1])
		self.plot1D.enableAutoRange(enable = True)
		
		self.xScale = np.absolute((self.extents[1] - self.extents[0])/ self.pxsize)
		self.xBins = np.linspace(self.extents[0] - 0.5*self.xScale, self.extents[1] + 0.5*self.xScale, self.pxsize + 1)


	@inlineCallbacks
	def setupListener(self, c):
		from labrad.wrappers import connectAsync
		self.cxn = yield connectAsync(name = '1DPlot')
		self.dv = yield self.cxn.data_vault
		yield self.dv.cd(self.dir)
		yield self.dv.open(self.fileName)
		yield self.dv.signal__data_available(00002)
		yield self.dv.addListener(listener=self.updatePlot, source=None, ID=00002)
		if self.fresh == 1:
			newData = yield self.dv.get()
			inx = np.delete(np.arange(0, len(newData[0])), [self.xIndex, self.yIndex])
			newData = np.delete(np.asarray(newData), inx, axis = 1)
			self.Data = newData
			self.isData = True
			self.binned = np.digitize(newData[::, 0], self.xBins) - 1
			
			if len(self.binned) > 2:
				p = np.argwhere(np.diff(self.binned) != np.diff(self.binned)[0])
				if len(p) != 0:
					xVals = newData[p[-1][0]+1::, 0]
					yVals = newData[p[-1][0]+1::, 1]
				else:
					xVals, yVals = newData[::, 0], newData[::, 1]
				
			else:
				xVals, yVals = newData[::, 0], newData[::, 1]

			self.plot1D.clear()
			self.plot1D.plot(x = xVals, y = yVals, pen =pg.mkPen(color=(0,255,255)))

	@inlineCallbacks
	def updatePlot(self, c, signal):
		newData = yield self.dv.get()
		inx = np.delete(np.arange(0, len(newData[0])), [self.xIndex, self.yIndex])
		newData = np.delete(np.asarray(newData), inx, axis = 1)
		self.Data = newData
		if self.isData != False:
			self.Data = np.vstack((self.Data, newData))
		else:
			self.Data = newData
			self.isData = True
		self.binned = np.digitize(self.Data[::, 0], self.xBins) - 1
		
		if len(self.binned) > 2:
			p = np.argwhere(np.diff(self.binned) != np.diff(self.binned)[0])
			if len(p) != 0:
				xVals = self.Data[p[-1][0]+1::, 0]
				yVals = self.Data[p[-1][0]+1::, 1]
			else:
				xVals, yVals = self.Data[::, 0], self.Data[::, 1]
			
		else:
			xVals, yVals = self.Data[::, 0], self.Data[::, 1]

		self.plot1D.clear()
		self.plot1D.plot(x = xVals, y = yVals, pen =pg.mkPen(color=(0,255,255)))
		'''
		newData = yield self.dv.get()
		inx = np.delete(np.arange(0, len(newData[0])), [self.xIndex, self.yIndex])

		newData = np.delete(np.asarray(newData), inx, axis = 1)

		if self.isData != False:
			self.Data = np.vstack((self.Data, newData))
		else:
			self.Data = newData
			self.isData = True

		allX, allY = self.Data[::, 0], self.Data[::, 1]

		if len(allX) > 2:
			p = np.argwhere(np.diff(allX) != np.diff(allX)[0])
			
			if len(p) != 0:
				
				xVals = allX[p[-1][0]+1::]
				yVals = allY[p[-1][0]+1::]
			else:
				xVals, yVals = allX, allY
			
		else:
			xVals, yVals = allX, allY

		self.plot1D.clear()
		self.plot1D.plot(x = xVals, y = yVals, pen =pg.mkPen(color=(0,255,255)))
		'''
		

	def closeEvent(self, e):
		self.cxn.disconnect()
		self.close()
		
class plotSavedWin(QtGui.QMainWindow, Ui_PlotSavedWin):
	def __init__(self, reactor, file, dir, plotInfo, x0, y0, parent = None):
		super(plotSavedWin, self).__init__(parent)
		QtGui.QMainWindow.__init__(self)

		
		self.setupUi(self)

		self.reactor = reactor
		self.file = str(file)
		self.dir = dir
		self.plotInfo = plotInfo
		self.mainWin = parent
		self.pX, self.pY = x0, y0
		

		self.extents = [self.plotInfo[0][2][0], self.plotInfo[0][2][1], self.plotInfo[1][2][0], self.plotInfo[1][2][1]]
		self.pxsize = [self.plotInfo[0][3], self.plotInfo[0][3]]

		self.moveDefault()
		
		self.xIndex = self.plotInfo[0][0]
		self.yIndex = self.plotInfo[1][0]
		self.zIndex = self.plotInfo[2][0]
				
		self.setupPlot()
		self.connect(self.reactor)

		
		
	def moveDefault(self):
		self.move(self.pX, self.pY)
		
	def setupPlot(self):
		self.plotTitle.setText(self.plotInfo[-1])
		self.plotTitle.setStyleSheet("QLabel#plotTitle {color: rgb(131,131,131); font: bold 11pt;}")
		
		self.viewBig = pg.PlotItem(name = "Plot")
		self.viewBig.showAxis('top', show = True)
		self.viewBig.showAxis('right', show = True)
		self.viewBig.setLabel('left', self.plotInfo[1][1])
		self.viewBig.setLabel('bottom', self.plotInfo[0][1])
		self.viewBig.setAspectLocked(lock = False, ratio = 1)
		self.mainPlot = pg.ImageView(parent = self.plot2DFrame, view = self.viewBig)
		self.mainPlot.setGeometry(QtCore.QRect(0, 0, 700, 550))
		self.mainPlot.ui.menuBtn.hide()
		self.mainPlot.ui.histogram.item.gradient.loadPreset('bipolar')
		self.mainPlot.ui.roiBtn.hide()
		self.mainPlot.ui.menuBtn.hide()
		self.viewBig.setAspectLocked(False)
		self.viewBig.invertY(False)
		self.viewBig.setXRange(-1, 1)
		self.viewBig.setYRange(-1, 1)
		
		self.plotData = np.zeros([self.pxsize[0], self.pxsize[1]])
		
		self.xscale, self.yscale = np.absolute((self.extents[1] - self.extents[0])/self.pxsize[0]), np.absolute((self.extents[3] - self.extents[2])/self.pxsize[1])
		self.mainPlot.setImage(self.plotData, autoRange = True , autoLevels = True, pos=[self.extents[0], self.extents[2]],scale=[self.xscale, self.yscale])
		

		self.xBins = np.linspace(self.extents[0] - 0.5 * self.xscale, self.extents[1] + 0.5 * self.xscale, self.pxsize[0]+1)
		self.yBins = np.linspace(self.extents[2] - 0.5 * self.yscale, self.extents[3]+0.5 * self.yscale, self.pxsize[1]+1)

	
	@inlineCallbacks
	def connect(self, c):
		from labrad.wrappers import connectAsync

		self.cxnS = yield connectAsync(name = 'name')
		self.dv = yield self.cxnS.data_vault
		self.initPlot(self.reactor)
		
	@inlineCallbacks
	def initPlot(self, c):
		yield self.dv.cd(self.dir)
		yield self.dv.open(self.file)
		print 'loading data'
		self.loadData(self.reactor)

		
	@inlineCallbacks
	def loadData(self, c):
		getFlag = True
		self.Data = np.array([])
		while getFlag == True:
			line = yield self.dv.get(1000L)

			try:
				if len(self.Data) != 0 and len(line) > 0:
					self.Data = np.vstack((self.Data, line))						
				elif len(self.Data) == 0 and len(line) > 0:
					self.Data = np.asarray(line)
				else:
					getFlag = False
			except:
				getFlag = False
		print 'got all data'
		inx = np.delete(np.arange(0, len(self.Data[0])), [self.xIndex, self.yIndex, self.zIndex])
		self.Data = np.delete(self.Data, inx, axis = 1)
		self.Data[::, 0] = np.digitize(self.Data[::, 0], self.xBins) - 1
		self.Data[::, 1] = np.digitize(self.Data[::, 1], self.yBins) - 1
		print 'digitized'
		for pt in self.Data:
			self.plotData[int(pt[0]), int(pt[1])] = pt[2]
		print 'plotting it all'
		self.mainPlot.setImage(self.plotData, autoRange = True , autoLevels = True, pos=[self.extents[0], self.extents[2]],scale=[self.xscale, self.yscale])	
		print 'plotting complete'
		
	def sleep(self,secs):
		d = Deferred()
		self.reactor.callLater(secs,d.callback,'Sleeping')
		return d
		
	def closeEvent(self, e):
		print 'closing window why?'

class plotSetup(QtGui.QDialog, Ui_PlotSetup):
	def __init__(self, reactor, file, dir, cxn, dv, fresh, parent = None):
		super(plotSetup, self).__init__(parent)
		QtGui.QDialog.__init__(self)

		self.reactor = reactor
		self.file = str(file)
		self.dir = dir
		self.cxn = cxn
		self.dv = dv
		self.fresh = fresh
		
		self.mainWin = parent
		
		self.setupUi(self)
		self.moveDefault()
		
		self.formFlag = True
		self.setupTables()
	
		self.cancel.clicked.connect(self.closeWindow)
		self.ok.clicked.connect(self.initPlot)
		
		self.add1D.clicked.connect(self.add1DPlot)
		self.add2D.clicked.connect(self.add2DPlot)
		
		self.rmv1D.clicked.connect(self.rmv1DPlot)
		self.rmv2D.clicked.connect(self.rmv2DPlot)
		
		print "file: ", self.file
		print "dir: ", self.dir
		
		self.plot2DInfo = []
		self.plot1DInfo = []
		
		
		self.popAxes(self.reactor)
		
	def moveDefault(self):
		self.move(400,25)
		
	def editLabel1(self, r, c):
		if c == 0:
			self.backtext1 = str(self.onePlots.item(r, c).text())
			item = self.onePlots.item(r, c)
			item.setText('')
			self.onePlots.editItem(self.onePlots.item(r, c))

	def editLabel2(self, r, c):
		if c == 0:
			self.backtext2 = str(self.twoPlots.item(r, c).text())
			item = self.twoPlots.item(r, c)
			item.setText('')
			self.twoPlots.editItem(self.twoPlots.item(r, c))

	def setupTables(self):
		
		self.onePlots.horizontalHeader().hide()
		self.onePlots.verticalHeader().hide()
		self.twoPlots.horizontalHeader().hide()
		self.twoPlots.verticalHeader().hide()
		
		self.onePlots.cellDoubleClicked.connect(self.editLabel1)
		self.twoPlots.cellDoubleClicked.connect(self.editLabel2)
		self.onePlots.itemSelectionChanged.connect(lambda: self.formatTable(1))
		self.twoPlots.itemSelectionChanged.connect(lambda: self.formatTable(2))

		self.onePlots.setColumnCount(4)
		self.twoPlots.setColumnCount(4)
		
		self.onePlots.insertRow(0)
		self.twoPlots.insertRow(0)
		num1, num2, lbl1, lbl2, x1, y1, x2, y2, z2 = QtGui.QTableWidgetItem(), QtGui.QTableWidgetItem(), QtGui.QTableWidgetItem(), QtGui.QTableWidgetItem(), QtGui.QTableWidgetItem(), QtGui.QTableWidgetItem(), QtGui.QTableWidgetItem(), QtGui.QTableWidgetItem(), QtGui.QTableWidgetItem()
		
		headers = [lbl1, x1, y1, lbl2, x2, y2, z2]
		
		num1.setText('Plot')		
		num1.setTextColor(QtGui.QColor(131,131,131))
		num2.setText('Plot')
		num2.setTextColor(QtGui.QColor(131,131,131))
		
		lbl1.setText('Plot Title')
		lbl1.setTextColor(QtGui.QColor(131,131,131))
		lbl2.setText('Plot Title')
		lbl2.setTextColor(QtGui.QColor(131,131,131))
		
		x1.setText('X Axis')
		x1.setTextColor(QtGui.QColor(131,131,131))
		y1.setText('Y Axis')
		y1.setTextColor(QtGui.QColor(131,131,131))
		
		x2.setText('X Axis')
		x2.setTextColor(QtGui.QColor(131,131,131))
		y2.setText('Y Axis')
		y2.setTextColor(QtGui.QColor(131,131,131))
		z2.setText('Z Axis')
		z2.setTextColor(QtGui.QColor(131,131,131))
		
		for ii in range(0, 3):
			self.onePlots.setItem(0, ii, headers[ii])
			self.onePlots.item(0, ii).setFont(QtGui.QFont("MS Shell Dlg 2",weight=QtGui.QFont.Bold))
			self.onePlots.item(0, ii).setFlags(QtCore.Qt.NoItemFlags)
		for ii in range(3, 7):
			self.twoPlots.setItem(0, ii - 3, headers[ii])
			self.twoPlots.item(0, ii - 3).setFont(QtGui.QFont("MS Shell Dlg 2",weight=QtGui.QFont.Bold))
			self.twoPlots.item(0, ii - 3).setFlags(QtCore.Qt.NoItemFlags)
			

		self.onePlots.setColumnWidth(0, 98)
		self.onePlots.setColumnWidth(1, 100)
		self.onePlots.setColumnWidth(2, 100)
		self.onePlots.setColumnWidth(3, 100)
		

		self.twoPlots.setColumnWidth(1, 100)
		self.twoPlots.setColumnWidth(2, 100)
		self.twoPlots.setColumnWidth(3, 100)
		self.twoPlots.setColumnWidth(0, 98)
		
	def formatTable(self, num = None):

		if num == 1:
			for c in range(0, 4):
				for r in range(0, self.onePlots.rowCount()):
					if self.onePlots.item(r, c) != None:
						self.onePlots.item(r, c).setBackground(QtGui.QColor(0,0,0))
						self.onePlots.item(r, c).setTextColor(QtGui.QColor(131,131,131))
						if c != 0:
							self.onePlots.item(r, c).setFlags(QtCore.Qt.NoItemFlags)
						elif c == 0 and r != 0:
							
							item = self.onePlots.item(r, c)
							if item.text() == '':
								item.setText(self.backtext1)
							item.setBackgroundColor(QtGui.QColor(100,100,150))
							item.setTextColor(QtGui.QColor(0,0,0))
		elif num ==2:
			for c in range(0, 4):
				for r in range(0, self.twoPlots.rowCount()):
					if self.twoPlots.item(r, c) != None:
						self.twoPlots.item(r, c).setBackground(QtGui.QColor(0,0,0))
						self.twoPlots.item(r, c).setTextColor(QtGui.QColor(131,131,131))	
						if c != 0:
							self.twoPlots.item(r, c).setFlags(QtCore.Qt.NoItemFlags)
						elif c == 0 and r != 0:
							
							item = self.twoPlots.item(r, c)
							if item.text() == '':
								item.setText(self.backtext2)
							item.setBackgroundColor(QtGui.QColor(100,100,150))
							item.setTextColor(QtGui.QColor(0,0,0))
							

		else:
			pass
		self.formFlag = True
		
		
	def add1DPlot(self):
		lbl, xAx, yAx = QtGui.QTableWidgetItem(), QtGui.QTableWidgetItem(), QtGui.QTableWidgetItem()
		self.onePlots.insertRow(self.onePlots.rowCount())
		
		title = 'Plot '+ str(self.onePlots.rowCount() - 1)
		lbl.setText(title)
		xAx.setText(self.x1.currentText())
		yAx.setText(self.y1.currentText())
		
		
		newItems = [lbl, xAx, yAx]
		
		self.plot1DInfo.append([[self.x1.currentIndex(),str(self.x1.currentText())] , [self.y1.currentIndex(), str(self.y1.currentText())]])
		
		for i in range(0, 3):
			self.onePlots.setItem(self.onePlots.rowCount() - 1, i, newItems[i])
		self.formatTable(1)
		
		
		
	def add2DPlot(self):
		lbl, xAx, yAx, zAx = QtGui.QTableWidgetItem(), QtGui.QTableWidgetItem(), QtGui.QTableWidgetItem(), QtGui.QTableWidgetItem()
		self.twoPlots.insertRow(self.twoPlots.rowCount())
		
		title = 'Plot '+ str(self.twoPlots.rowCount() - 1)
		lbl.setText(title)
		xAx.setText(self.x2.currentText())
		yAx.setText(self.y2.currentText())
		zAx.setText(self.z2.currentText())
		
		newItems = [lbl, xAx, yAx, zAx]
		
		self.plot2DInfo.append([[self.x2.currentIndex(), str(self.x2.currentText())], [self.y2.currentIndex(), str(self.y2.currentText())], [self.z2.currentIndex(), str(self.z2.currentText())]])
		
		for i in range(0, 4):
			self.twoPlots.setItem(self.twoPlots.rowCount() - 1, i, newItems[i])
		self.formatTable(2)
		
	def rmv1DPlot(self):
		pass
	def rmv2DPlot(self):
		pass		
		
	@inlineCallbacks
	def popAxes(self, c = None):
		yield self.dv.cd(self.dir)
		yield self.dv.open(self.file)
		vars =	yield self.dv.variables()
		self.indVars = vars[0]
		self.depVars = vars[1]
		
		for var in self.indVars:
			self.x2.addItem(str(var[0]))
			self.y2.addItem(str(var[0]))
			self.x1.addItem(str(var[0]))
			
			self.z2.addItem(str(var[0]))
			self.y1.addItem(str(var[0]))
		
		for var in self.depVars:
			self.x2.addItem(str(var[0]))
			self.y2.addItem(str(var[0]))
			self.x1.addItem(str(var[0]))

			self.z2.addItem(str(var[0]))
			self.y1.addItem(str(var[0]))
			
	def initPlot(self):
		self.extents, self.pxsize = {},{}
		if self.plot2DInfo != [] or self.plot1DInfo != []:
			needExtents = []
			for r in range(1, self.twoPlots.rowCount()):
				title = str(self.twoPlots.item(r,0).text())
				self.plot2DInfo[r - 1].append(title)
				if not str(self.plot2DInfo[r - 1][0][1]) in needExtents:
					needExtents.append(self.plot2DInfo[r - 1][0][1])
				if not str(self.plot2DInfo[r - 1][1][1]) in needExtents:
					needExtents.append(self.plot2DInfo[r - 1][1][1])				
			for r in range(1, self.onePlots.rowCount()):
				title = str(self.onePlots.item(r,0).text())
				self.plot1DInfo[r - 1].append(title)	
				if not str(self.plot1DInfo[r - 1][0][1]) in needExtents:
					needExtents.append(self.plot1DInfo[r - 1][0][1])
			print needExtents
			extPrompt = extentPrompt(self.reactor, needExtents, 450, 25, self)
			extPrompt.exec_()

			print '2D Info: ', self.plot2DInfo
			print '1D Info: ', self.plot1DInfo
			if extPrompt.accepted:
				for ii in range(0, len(self.plot2DInfo)):
					self.plot2DInfo[ii][0].append(self.extents[self.plot2DInfo[ii][0][1]])
					self.plot2DInfo[ii][0].append(self.pxsize[self.plot2DInfo[ii][0][1]])
					self.plot2DInfo[ii][1].append(self.extents[self.plot2DInfo[ii][0][1]])
					self.plot2DInfo[ii][1].append(self.pxsize[self.plot2DInfo[ii][0][1]])
				for ii in range(0, len(self.plot1DInfo)):
					self.plot1DInfo[ii][0].append(self.extents[self.plot1DInfo[ii][0][1]])
					self.plot1DInfo[ii][0].append(self.pxsize[self.plot1DInfo[ii][0][1]])
				print '2D Info: ', self.plot2DInfo
				print '1D Info: ', self.plot1DInfo
				if self.fresh == 0 or self.fresh == 1:
					self.mainWin.openLivePlots(copy.copy(self.plot2DInfo), copy.copy(self.plot1DInfo), copy.copy(self.fresh))
					self.close()
				elif self.fresh == 2:
					self.mainWin.openSavedPlots(copy.copy(self.file), copy.copy(self.dir), copy.copy(self.plot2DInfo))
					print 'why is this a thing???'
					self.close()
					
					
			else:
				pass
		else:
			pass
		
		
	def closeWindow(self):
		self.close()

	def closeEvent(self, e):
		self.close()

class editDataInfo(QtGui.QDialog, Ui_EditDataInfo):
	def __init__(self, reactor, parent = None):
		super(editDataInfo, self).__init__(parent)

		self.reactor = reactor
		self.setupUi(self)
		self.window = window
		self.dv = self.window.dv
		self.dataSet = str(self.window.currentFile.text())
		self.ok.clicked.connect(self.updateComments)
		self.cancel.clicked.connect(self.exitEdit)
		self.name.setWordWrap(True)
		self.currentComs.setReadOnly(True)

		self.setupTags(self)

	@inlineCallbacks
	def setupTags(self, c):
		name = yield self.dv.get_name()
		params = yield self.dv.get_parameters()
		coms = yield self.dv.get_comments()
		self.name.setText(name)
		self.name.setStyleSheet("QLabel#name {color: rgb(131,131,131);}")
		self.parameters.setText(str(params))
		self.parameters.setStyleSheet("QLabel#parameters {color: rgb(131,131,131);}")
		if str(coms) == '[]':
			self.currentComs.setText("(None)")
		else:
			s = ""
			for i in coms:
				s += str(i[2]) + "\n\n" 
			self.currentComs.setText(str(s))

	@inlineCallbacks
	def updateComments(self, c):
		coms = str(self.comments.toPlainText())
		if coms == '':
			pass
		else:
			yield self.dv.add_comment(coms)
		self.close()
	def exitEdit(self):
		self.close()

class dirExplorer(QtGui.QDialog, Ui_DirExp):
	def __init__(self, reactor, status, parent = None):
		super(dirExplorer, self).__init__(parent)
		QtGui.QDialog.__init__(self)

		self.reactor = reactor
		self.setupUi(self)
		self.moveDefault()
		
		self.mainWin = parent
		self.status = status
		
		self.connect(self.reactor)
		

		self.selectedFile = ''
		self.selectedDir = ['']
		self.currentDir = ['']

		self.dirList.itemDoubleClicked.connect(self.updateDirs)
		self.back.clicked.connect(lambda: self.backUp(self.reactor))
		self.home.clicked.connect(lambda: self.goHome(self.reactor))
		self.addDir.clicked.connect(lambda: self.makeDir(self.reactor))
		self.select.clicked.connect(lambda: self.selectFile(self.reactor))
		self.cancel.clicked.connect(self.closeWindow)
		
		
	def moveDefault(self):
		self.move(400,25)


	@inlineCallbacks
	def connect(self, c = None):
		from labrad.wrappers import connectAsync
		try:
			self.cxn = yield connectAsync(name = 'dirExplorer')
			self.dv = yield self.cxn.data_vault
		except:
			print 'Either no LabRad connection or DataVault connection.'
		self.popDirs(self.reactor)
		

	@inlineCallbacks
	def popDirs(self, c = None):
		self.dirList.clear()
		self.fileList.clear()
		l = yield self.dv.dir()
		for i in l[0]:
			self.dirList.addItem(i)
			self.dirList.item(self.dirList.count() - 1).setTextColor(QtGui.QColor(131,131,131))
		for i in l[1]:
			self.fileList.addItem(i)
			self.fileList.item(self.fileList.count() - 1).setTextColor(QtGui.QColor(131,131,131))
		if self.currentDir[-1] == '':
			
			self.dirName.setText('Root')
			self.dirName.setStyleSheet("QLabel#dirName {color: rgb(131,131,131);}")
		else:
			
			self.dirName.setText(self.currentDir[-1])
			self.dirName.setStyleSheet("QLabel#dirName {color: rgb(131,131,131);}")
		if self.currentDir[-1] != '':
			self.currentDrc.setText(self.currentDir[-1])
		else:
			self.currentDrc.setText('(Root)')
		

	@inlineCallbacks
	def updateDirs(self, subdir):
		subdir = str(subdir.text())
		self.currentDir.append(subdir)
		yield self.dv.cd(subdir, False)
		yield self.popDirs(self.reactor)

	@inlineCallbacks
	def backUp(self, c = None):
		if self.currentDir[-1] == '':
			pass
		else:
			direct = yield self.dv.cd()
			back = direct[0:-1]
			self.currentDir.pop(-1)
			yield self.dv.cd(back)
			yield self.popDirs(self.reactor)

	@inlineCallbacks
	def goHome(self, c = None):
		yield self.dv.cd('')
		self.currentDir = ['']
		yield self.popDirs(self.reactor)

	@inlineCallbacks
	def makeDir(self, c = None):
		direct, ok = QtGui.QInputDialog.getText(self, "Make directory", "Directory Name: " )
		if ok:
			yield self.dv.mkdir(str(direct))
			yield self.popDirs(self.reactor)
			
			
	@inlineCallbacks
	def selectFile(self, c = None):
		self.mainWin.setListenDir(self.currentDrc.text(), self.currentDir)
		yield self.sleep(0.5)
		yield self.mainWin.initListener(self.reactor)
		self.close()
		
	def sleep(self,secs):
		d = Deferred()
		self.reactor.callLater(secs,d.callback,'Sleeping')
		return d

		
		
	def closeWindow(self):
		if self.status == False:
			self.mainWin.listen.setEnabled(True)
		else:
			self.mainWin.changeDir.setEnabled(True)
		self.close()

	def closeEvent(self, e):
		if self.status == False:
			self.mainWin.listen.setEnabled(True)
		else:
			self.mainWin.changeDir.setEnabled(True)

class dataVaultExplorer(QtGui.QDialog, Ui_DataVaultExp):
	def __init__(self, reactor, source, parent = None):
		super(dataVaultExplorer, self).__init__(parent)
		QtGui.QDialog.__init__(self)

		self.reactor = reactor
		self.source = source
		self.setupUi(self)
		self.moveDefault()
		
		self.mainWin = parent


		self.connect(self.reactor)
		

		self.selectedFile = ''
		self.selectedDir = ['']
		self.currentDir = ['']

		self.dirList.itemDoubleClicked.connect(self.updateDirs)
		self.fileList.itemClicked.connect(self.fileSelect)
		self.fileList.itemDoubleClicked.connect(lambda: self.displayInfo(self.reactor))
		self.back.clicked.connect(lambda: self.backUp(self.reactor))
		self.home.clicked.connect(lambda: self.goHome(self.reactor))
		self.addDir.clicked.connect(lambda: self.makeDir(self.reactor))
		self.select.clicked.connect(self.selectFile)
		self.cancel.clicked.connect(self.closeWindow)
		
	def moveDefault(self):
		self.move(400,25)

	@inlineCallbacks
	def connect(self, c = None):
		from labrad.wrappers import connectAsync
		try:
			self.cxn = yield connectAsync(name = 'dvExplorer')
			self.dv = yield self.cxn.data_vault
		except:
			print 'Either no LabRad connection or DataVault connection.'
		self.popDirs(self.reactor)

	@inlineCallbacks
	def popDirs(self, c = None):
		self.dirList.clear()
		self.fileList.clear()
		l = yield self.dv.dir()
		for i in l[0]:
			self.dirList.addItem(i)
			self.dirList.item(self.dirList.count() - 1).setTextColor(QtGui.QColor(131,131,131))
		for i in l[1]:
			self.fileList.addItem(i)
			self.fileList.item(self.fileList.count() - 1).setTextColor(QtGui.QColor(131,131,131))
		if self.currentDir[-1] == '':
			
			self.dirName.setText('Root')
			self.dirName.setStyleSheet("QLabel#dirName {color: rgb(131,131,131);}")
		else:
			
			self.dirName.setText(self.currentDir[-1])
			self.dirName.setStyleSheet("QLabel#dirName {color: rgb(131,131,131);}")


	@inlineCallbacks
	def updateDirs(self, subdir):
		subdir = str(subdir.text())
		self.currentDir.append(subdir)
		yield self.dv.cd(subdir, False)
		yield self.popDirs(self.reactor)

	@inlineCallbacks
	def backUp(self, c = None):
		if self.currentDir[-1] == '':
			pass
		else:
			direct = yield self.dv.cd()
			back = direct[0:-1]
			self.currentDir.pop(-1)
			yield self.dv.cd(back)
			yield self.popDirs(self.reactor)

	@inlineCallbacks
	def goHome(self, c = None):
		yield self.dv.cd('')
		self.currentDir = ['']
		yield self.popDirs(self.reactor)

	@inlineCallbacks
	def makeDir(self, c = None):
		direct, ok = QtGui.QInputDialog.getText(self, "Make directory", "Directory Name: " )
		if ok:
			yield self.dv.mkdir(str(direct))
			yield self.popDirs(self.reactor)

	@inlineCallbacks
	def displayInfo(self, c = None):
		dataSet = str(self.currentFile.text())
		yield self.dv.open(str(dataSet))
		self.editDataInfo = editDataInfo(c)
		self.editDataInfo.show()

	def fileSelect(self):
		file = self.fileList.currentItem()
		self.selectedFile = file.text()
		
		self.selectedDir = self.currentDir
		self.currentFile.setText(file.text())
		
	def selectFile(self):
		if self.source == 'saved':
			if self.selectedFile != '':
				savedPlot = plotSetup(self.reactor,self.selectedFile, self.selectedDir, self.cxn, self.dv, 2, self.mainWin)
				self.hide()
				savedPlot.show()
			else:
				pass
		elif self.source == 'live':
			if self.selectedFile != '':
				livePlot = plotSetup(self.reactor,self.selectedFile, self.selectedDir, self.cxn, self.dv, 1, self.mainWin)
				self.hide()
				livePlot.show()
			else:
				pass
		else:
			pass
			
	def closeWindow(self):
		self.close()

	def closeEvent(self, e):
		self.close()

if __name__ == "__main__":
	app = QtGui.QApplication([])
	from qtreactor import pyqt4reactor
	pyqt4reactor.install()
	from twisted.internet import reactor
	window = dvPlotter(reactor)
	window.show()
	reactor.run()



'''
#Print Error
try:
	yield 'something'
except Exception as inst:
	print type(inst)
	print inst.args
	print inst
'''