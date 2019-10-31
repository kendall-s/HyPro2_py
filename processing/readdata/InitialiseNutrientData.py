from PyQt5.QtWidgets import (QWidget, QPushButton, QSlider, QLabel, QGridLayout, QCheckBox, QFrame,
                             QVBoxLayout, QMainWindow, QTabWidget, QDesktopWidget)
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtGui import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from pylab import *
from scipy.stats import linregress
from scipy.interpolate import interp1d
import processing.plotting.QCPlots as qcp
import processing.RefreshFunction
import numpy
from netCDF4 import Dataset
import sys, statistics, logging, json, csv, traceback, sqlite3, os, pprint
import calendar
import hyproicons
from dialogs.TraceSelectionDialog import traceSelection
from processing.algo.HyproComplexities import determineSurvey


# ******************************************************************************************
# Still implemented but very close to getting deleted
# THis is a very messy and bad code example for processing nutrients, it was more written as a proof of concept
# Most of this code is being cleaned up and shifted into better structured code
# ******************************************************************************************
# TODO: migrate nutrient processing to cleaned

class initNutrientData(QMainWindow):

    # Takes in the file, database path, project path, active project and whether processing should be interactive
    def __init__(self, file, database, path, project, interactive, rereading):
        super().__init__()
        self.setWindowIcon(QtGui.QIcon(':/assets/icon.svg'))
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # keys for nutrients
        self.nutrients = ['phosphate', 'nitrate', 'silicate', 'nitrite', 'ammonia']
        self.channels = {'phosphate': 0, 'silicate': 0, 'nitrate': 0, 'nitrite': 0, 'ammonia': 0}

        self.file = file
        self.database = database
        self.currpath = path
        self.currproject = project
        self.filepath = self.currpath + '/' + 'Nutrients' + '/' + self.file

        self.interactive = interactive
        self.rereading = rereading

        self.nutsactive = []

        self.qualityflag = []
        self.dilutionfac = []

        # If peak windows are shifted calibration peak flags are reset to retry fitting curve
        self.resetcalflags = False

        self.tabledoesntexist = True

        self.driftcorrbuffer = []

        self.pressed = False

        self.tabindex = 0

        self.init_ui()

        try:
            self.loadprocsettings()

            self.loadfilesin()

            self.currentnut = self.nutsactive[0]

            self.processingcontainer(self.currentnut)

        except IndexError:
            logging.error(
                'ERROR: This error is most likely caused by not being able to find any nutrients in the file. '
                'The parameters file probably needs updating')
            self.close()

        except Exception:
            logging.error('ERROR: Processing failed for file: ' + str(self.file))
            self.close()

        self.setStyleSheet("""

            QMainWindow {
                background-color: #ebeff2;
                border: 0px solid #bababa;   
            }
            QLabel {
                font: 14px;
            }
            QLabel[hidetheme=true] {
                color: #fefefe;
            }
            QListWidget {
                font: 14px;
            }
            QPushButton {
                font: 14px;
            }
            QPushButton[icons=true] {
                color: #222222;
                border: 1px solid #ededed;
                border-radius: 5px;
                background-color: #ededed;
                font: 15px;   
            }
            QPushButton[icons=true]:hover {
                color: #222222;
                border: 2px solid #ededed;
                background: #f7f7f7;
                font: 15px;
            }
            QPushButton[icons=true]:pressed{
                border: 1px solid #8f98a8;
                color: #222222;
                background-color: #f7f7f7;
                font: 15px;
                border-style: inset;
            }
            QPushButton[clear=true] {
                background-color: #fefefe;
            }
            QTabWidget QWidget {
                font: 14px;
                border: 0px;
                background-color: #f9fcff;
            }
            QCheckBox {
                font: 13px;
            }
            QFrame[dashboardframe=true] {
                background-color: #f9fcff;
            }
            QFrame[dashboardframe2=true] {
                background-color: #f9fcff;
                padding: 20px;
            }
            QFrame[headerframe=true]{
                background-color: #ddeaff;
            }
            QLabel[headertext=true]{
                color: #222222;
                font: 18px;
                font-weight: bold;  
            }
            
                            """)

    def init_ui(self):
        try:
            # A lot of GUI setup here..
            deffont = QFont('Segoe UI')
            self.setFont(deffont)

            self.gridlayout = QGridLayout()
            self.gridlayout.setSpacing(5)

            screenwidth = QDesktopWidget().availableGeometry().width()
            screenheight = QDesktopWidget().availableGeometry().height()

            self.setGeometry(10, 10, screenwidth - (screenwidth * 0.1), screenheight - (screenheight * 0.1))
            qtRectangle = self.frameGeometry()
            centerPoint = QDesktopWidget().availableGeometry().center()
            qtRectangle.moveCenter(centerPoint)
            self.move(qtRectangle.topLeft())
            self.showMaximized()
            self.setWindowModality(QtCore.Qt.WindowModal)

            self.setWindowTitle('HyPro - Process Nutrient Run')

            mainMenu = self.menuBar()
            fileMenu = mainMenu.addMenu('File')
            editMenu = mainMenu.addMenu('Edit')

            # self.windowsplitter = QSplitter(QtCore.Qt.Vertical)

            self.analysistraceLabel = QLabel('Analysis Trace:', self)
            self.analysistraceLabel.setProperty('headertext', True)
            self.analysistraceLabel.setFont(deffont)

            tracelabelframe = QFrame(self)
            tracelabelframe.setProperty('headerframe', True)
            tracelabelframeshadow = QtWidgets.QGraphicsDropShadowEffect()
            tracelabelframeshadow.setBlurRadius(6)
            tracelabelframeshadow.setColor(QtGui.QColor('#e1e6ea'))
            tracelabelframeshadow.setYOffset(2)
            tracelabelframeshadow.setXOffset(3)
            tracelabelframe.setGraphicsEffect(tracelabelframeshadow)

            traceframe = QFrame(self)
            traceframe.setProperty('dashboardframe', True)
            traceframeshadow = QtWidgets.QGraphicsDropShadowEffect()
            traceframeshadow.setBlurRadius(6)
            traceframeshadow.setColor(QtGui.QColor('#e1e6ea'))
            traceframeshadow.setYOffset(2)
            traceframeshadow.setXOffset(3)
            traceframe.setGraphicsEffect(traceframeshadow)

            self.qctabsLabel = QLabel('QC Charts:', self)
            self.qctabsLabel.setProperty('headertext', True)
            self.qctabsLabel.setFont(deffont)

            qclabelframe = QFrame(self)
            qclabelframe.setProperty('headerframe', True)
            qclabelframeshadow = QtWidgets.QGraphicsDropShadowEffect()
            qclabelframeshadow.setBlurRadius(6)
            qclabelframeshadow.setColor(QtGui.QColor('#e1e6ea'))
            qclabelframeshadow.setYOffset(2)
            qclabelframeshadow.setXOffset(3)
            qclabelframe.setGraphicsEffect(qclabelframeshadow)

            self.qctabs = QTabWidget()

            qctabsframe = QFrame(self)
            qctabsframe.setProperty('dashboardframe', True)
            qctabsframeshadow = QtWidgets.QGraphicsDropShadowEffect()
            qctabsframeshadow.setBlurRadius(6)
            qctabsframeshadow.setColor(QtGui.QColor('#e1e6ea'))
            qctabsframeshadow.setYOffset(3)
            qctabsframeshadow.setXOffset(3)
            qctabsframe.setGraphicsEffect(qctabsframeshadow)

            #buttonsframe = QFrame(self)
            #buttonsframe.setMinimumHeight(65)
            #buttonsframe.setProperty('dashboardframe', True)
            #buttonsframeshadow = QtWidgets.QGraphicsDropShadowEffect()
            #buttonsframeshadow.setBlurRadius(6)
            #buttonsframeshadow.setColor(QtGui.QColor('#e1e6ea'))
            #buttonsframeshadow.setYOffset(2)
            #buttonsframeshadow.setXOffset(3)
            #buttonsframe.setGraphicsEffect(buttonsframeshadow)
                      
            self.autosize = QCheckBox('Auto zoom', self)
            self.autosize.setFont(deffont)

            leftonxaxis = QPushButton(self)
            leftonxaxis.setFont(deffont)
            leftonxaxis.clicked.connect(self.shiftleftxaxis)
            leftonxaxis.setIcon(QIcon(':/assets/greenleftarrow.svg'))
            leftonxaxis.setIconSize(QtCore.QSize(33, 33))
            leftonxaxis.setProperty('icons', True)
            #leftonxaxis.setFixedHeight(40)
            #leftonxaxis.setFixedWidth(45)

            rightonxaxis = QPushButton(self)
            rightonxaxis.setFont(deffont)
            rightonxaxis.clicked.connect(self.shiftrightxaxis)
            rightonxaxis.setIcon(QIcon(':/assets/greenrightarrow.svg'))
            rightonxaxis.setIconSize(QtCore.QSize(33, 33))
            rightonxaxis.setProperty('icons', True)
            #rightonxaxis.setFixedHeight(40)
            #rightonxaxis.setFixedWidth(45)

            zoomin = QPushButton(self)
            zoomin.clicked.connect(self.zoomin)
            zoomin.setIcon(QIcon(':/assets/zoomin.svg'))
            zoomin.setIconSize(QtCore.QSize(33, 33))
            zoomin.setProperty('icons', True)
            #zoomin.setFixedHeight(40)
            #zoomin.setFixedWidth(45)

            zoomout = QPushButton(self)
            zoomout.clicked.connect(self.zoomout)
            zoomout.setIcon(QIcon(':/assets/zoomout.svg'))
            zoomout.setIconSize(QtCore.QSize(33, 33))
            zoomout.setProperty('icons', True)
            #zoomout.setFixedHeight(40)
            #zoomout.setFixedWidth(45)

            zoomfit = QPushButton(self)
            zoomfit.clicked.connect(self.zoomfit)
            zoomfit.setIcon(QIcon(':/assets/expand.svg'))
            zoomfit.setIconSize(QtCore.QSize(33, 33))
            zoomfit.setProperty('icons', True)
            #zoomfit.setFixedHeight(40)
            #zoomfit.setFixedWidth(45)

            self.underwayfile = QCheckBox('Find Lat/Longs', self)

            okcanframe = QFrame(self)
            okcanframe.setMinimumHeight(40)
            okcanframe.setProperty('dashboardframe2', True)
            okcanframeshadow = QtWidgets.QGraphicsDropShadowEffect()
            okcanframeshadow.setBlurRadius(6)
            okcanframeshadow.setColor(QtGui.QColor('#e1e6ea'))
            okcanframeshadow.setYOffset(2)
            okcanframeshadow.setXOffset(3)
            okcanframe.setGraphicsEffect(okcanframeshadow)
            
            okbut = QPushButton('Proceed', self)
            okbut.setFont(deffont)
            okbut.setFixedHeight(25)
            okbut.setFixedWidth(95)
            okbut.clicked.connect(self.nextnut)
            okbut.setProperty('icons', True)

            cancelbut = QPushButton('Cancel', self)
            cancelbut.setFont(deffont)
            cancelbut.clicked.connect(self.cancel)
            cancelbut.setProperty('icons', True)
            cancelbut.setFixedHeight(25)
            cancelbut.setFixedWidth(95)

            #self.sidescroll = QSlider(QtCore.Qt.Horizontal)
            #self.sidescroll.setFixedWidth(100)
            #self.sidescroll.setValue(50)
            #self.sidescroll.valueChanged.connect(self.sidescroller)
            #self.sidescroll.sliderReleased.connect(self.setscroller)
            #self.sidescroll.sliderPressed.connect(self.sidescrollerclicked)

            # Initialise the trace figure for plotting to
            self.tracefigure = plt.figure(figsize=(6, 4))
            self.tracefigure.set_tight_layout(tight=True)
            self.tracefigure.set_facecolor('#f9fcff')
            self.tracecanvas = FigureCanvas(self.tracefigure)
            self.tracecanvas.setParent(self)
            self.tracetoolbar = NavigationToolbar(self.tracecanvas, self)
            self.tracetoolbar.locLabel.hide()

            # Setting everything into the layout

            self.gridlayout.addWidget(tracelabelframe, 0, 0, 1, 11)
            self.gridlayout.addWidget(self.analysistraceLabel, 0, 0, 1, 3, QtCore.Qt.AlignCenter)

            self.gridlayout.addWidget(qclabelframe, 0, 11, 1, 5)
            self.gridlayout.addWidget(self.qctabsLabel, 0, 11, 1, 1, QtCore.Qt.AlignCenter)


            self.gridlayout.addWidget(traceframe, 1, 0, 20, 11)
            self.gridlayout.addWidget(self.tracecanvas, 1, 0, 17, 11)
            self.gridlayout.addWidget(self.tracetoolbar, 18, 0, 1, 5)

            self.gridlayout.addWidget(qctabsframe, 1, 11, 19, 5)
            self.gridlayout.addWidget(self.qctabs, 1, 11, 19, 5)

            #self.gridlayout.addWidget(buttonsframe, 19, 0, 2, 11)

            self.gridlayout.addWidget(self.autosize, 20, 0, QtCore.Qt.AlignCenter)

            self.gridlayout.addWidget(leftonxaxis, 19, 3, 2, 1)
            self.gridlayout.addWidget(rightonxaxis, 19, 4, 2, 1)
            self.gridlayout.addWidget(zoomfit, 19, 5, 2, 1)
            self.gridlayout.addWidget(zoomin, 19, 6, 2, 1)
            self.gridlayout.addWidget(zoomout, 19, 7, 2, 1)

            #self.gridlayout.addWidget(self.sidescroll, 11, 3, 1, 3)

            self.gridlayout.addWidget(self.underwayfile, 19, 0, QtCore.Qt.AlignCenter)

            self.gridlayout.addWidget(okcanframe, 20, 11, 1, 5)

            self.gridlayout.addWidget(okbut, 20, 12, 1, 2, QtCore.Qt.AlignJustify)
            self.gridlayout.addWidget(cancelbut, 20, 13, 1, 2, QtCore.Qt.AlignJustify)

            self.centralWidget().setLayout(self.gridlayout)

            self.maintrace = self.tracefigure.add_subplot(111)

            # Connect the mouse interaction to the trace plot so we can click and select peaks on it
            clicker = self.tracefigure.canvas.mpl_connect("button_press_event", self.on_click)

            self.bootup = True

        except Exception:
            print(traceback.print_exc())

    def loadfilesin(self):
        try:
            # Here is the function for reading in the two files, the CHD and the SLK
            # they could be separated but no point really as one is useless without the other.....
            self.runumber = self.file[len(self.params['analysisparams']['seal']['filePrefix']):-4]

            # Start with opening the .slk file
            with open(self.filepath) as fileread:
                read = csv.reader(fileread, delimiter=';')
                readlist = list(read)

            datasection = []
            # Now the .SLK will be parsed, this is messy because there are different 'versions' of the
            # .slk as there isn't a defined standard..
            # THe .slk is essentially a spreadshet and it will be broken up into an array
            for x in readlist:
                if x[0] == 'C' or x[0] == 'F':
                    datasection.append(x)
                    # Get size of spreadsheet to make array to hold data
                if x[0] == 'B':
                    if x[1][0] == 'X':
                        w = int(x[1][1:])
                    if x[2][0] == 'X':
                        w = int(x[2][1:])
                    if x[2][0] == 'Y':
                        h = int(x[2][1:])
                    if x[1][0] == 'Y':
                        h = int(x[1][1:])

            dataarray = [['' for i in range(w)] for j in range(h)]

            row = 0
            col = 0
            for x in datasection:
                try:
                    if x[1][0] == 'Y':
                        row = int(x[1][1:]) - 1
                    if len(x) > 2:
                        if x[2][0] == 'X':
                            col = int(x[2][1:]) - 1
                    if x[1][0] == 'X':
                        col = int(x[1][1:]) - 1
                    if x[0][0] == 'F':
                        if len(x) == 4:
                            if x[3][0] == 'M':
                                fake = 0
                            else:
                                col = int(x[3][1:]) - 1
                        else:
                            if x[1][0] != 'W':
                                col = int(x[3][1:]) - 1

                    dataarray[row][col] = x[-1][1:]
                except Exception as e:
                    print(x)
                    print('len: ' + str(len(x)))

            # By finding where certain headers are the associated data can be found
            findx, findy = self.getindex(dataarray, '"TIME"')
            self.analysistime = dataarray[findx][findy + 1][1:-1]

            findx, findy = self.getindex(dataarray, '"DATE"')
            self.analysisdate = dataarray[findx][findy + 1][1:-1]

            findx, findy = self.getindex(dataarray, '"OPER"')
            self.operator = dataarray[findx][findy + 1][1:-1]

            for x in self.nutrients:
                findx, findy = self.getindex(dataarray, '"' + self.params['nutrientprocessing']['elementNames']
                ['%sName' % x] + '"')
                if findx != 'no':
                    self.nutsactive.append(x)
                    self.channels[x] = dataarray[findx - 1][findy]
                    if x == 'silicate':
                        self.silgain = dataarray[findx + 3][findy]
                        self.silbase = dataarray[findx + 2][findy]
                        self.silicatecalibrants = [row[findy - 1] for row in dataarray[findx + 6:]]
                        self.silicatepeakstarts = [row[findy + 2] for row in dataarray[findx + 6:]]
                    if x == 'phosphate':
                        self.phosgain = dataarray[findx + 3][findy]
                        self.phosbase = dataarray[findx + 2][findy]
                        self.phosphatecalibrants = [row[findy - 1] for row in dataarray[findx + 6:]]
                        self.phosphatepeakstarts = [row[findy + 2] for row in dataarray[findx + 6:]]
                    if x == 'nitrate':
                        self.nitragain = dataarray[findx + 3][findy]
                        self.nitrabase = dataarray[findx + 2][findy]
                        self.nitratecalibrants = [row[findy - 1] for row in dataarray[findx + 6:]]
                        self.nitratepeakstarts = [row[findy + 2] for row in dataarray[findx + 6:]]
                    if x == 'nitrite':
                        self.nitrigain = dataarray[findx + 3][findy]
                        self.nitribase = dataarray[findx + 2][findy]
                        self.nitritecalibrants = [row[findy - 1] for row in dataarray[findx + 6:]]
                        self.nitritepeakstarts = [row[findy + 2] for row in dataarray[findx + 6:]]
                    if x == 'ammonia':
                        self.ammgain = dataarray[findx + 3][findy]
                        self.ammbase = dataarray[findx + 2][findy]
                        self.ammoniacalibrants = [row[findy - 1] for row in dataarray[findx + 6:]]
                        self.ammoniapeakstarts = [row[findy + 2] for row in dataarray[findx + 6:]]

            # THe helpful data from the .slk is pulled out here and put into separated lists
            findx, findy = self.getindex(dataarray,
                                         '"' + self.params['nutrientprocessing']['slkcolumnnames']['sampleID'] + '"')
            self.sampleids = [row[findy][1:-1] for row in dataarray[findx + 1:]]

            findx, findy = self.getindex(dataarray,
                                         '"' + self.params['nutrientprocessing']['slkcolumnnames']['cupNumbers'] + '"')
            self.cupnumbers = [row[findy][1:-1] for row in dataarray[findx + 1:]]

            findx, findy = self.getindex(dataarray,
                                         '"' + self.params['nutrientprocessing']['slkcolumnnames']['cupTypes'] + '"')
            self.cuptypes = [row[findy][1:-1] for row in dataarray[findx + 1:]]

            findx, findy = self.getindex(dataarray,
                                         '"' + self.params['nutrientprocessing']['slkcolumnnames']['dateTime'] + '"')
            datetime = [row[findy][1:-1] for row in dataarray[findx + 1:]]

            format = '%d/%m/%Y %I:%M:%S %p'
            structtime = [time.strptime(x, format) for x in datetime]
            self.epochtime = [calendar.timegm(x) for x in structtime]

            # Open and load in CHD file, this is much simpler and easier, thankfully
            with open(self.filepath[:-3] + 'CHD') as fileread:
                read = csv.reader(fileread, delimiter=';')
                readlist = list(read)
            for x in self.nutsactive:
                if x == 'silicate':
                    self.silicatechd = [int(row[int(self.channels['silicate'])]) for row in readlist]
                if x == 'phosphate':
                    self.phosphatechd = [int(row[int(self.channels['phosphate'])]) for row in readlist]
                if x == 'nitrate':
                    self.nitratechd = [int(row[int(self.channels['nitrate'])]) for row in readlist]
                if x == 'nitrite':
                    self.nitritechd = [int(row[int(self.channels['nitrite'])]) for row in readlist]
                if x == 'ammonia':
                    self.ammoniachd = [int(row[int(self.channels['ammonia'])]) for row in readlist]

            # Make flagging and dilution list for all samples, defaulting for both at 1
            self.qualityflag = [1] * len(self.sampleids)
            self.dilutionfac = [1] * len(self.sampleids)

        except ValueError:
            logging.error(
                'ERROR: A number in the slk file is formatted as text, I can not convert it, you will have to')
            self.close()
        except IndexError:
            logging.error('ERROR: Issue with .CHD file most likely')
            self.close()
        except TypeError:
            logging.error("ERROR: Couldn't find something in the SLK file, some name is wrong or missing...")
            self.close()

        except Exception:
            logging.error(traceback.print_exc())
            self.close()

    # This function aims to line up the relevant AD data from the CHD file with the peaks from the SLK file
    def matchpeaksgetadvals(self, nutrient):
        self.qctabs.clear()
        try:
            # Assign the settings from the parameters file
            nutrient = nutrient
            self.peakPeriod = self.params['nutrientprocessing']['processingpars'][nutrient]['peakPeriod']
            self.washPeriod = self.params['nutrientprocessing']['processingpars'][nutrient]['washPeriod']
            self.windowSize = self.params['nutrientprocessing']['processingpars'][nutrient]['windowSize']
            self.windowStart = self.params['nutrientprocessing']['processingpars'][nutrient]['windowStart']

            self.peakLength = int(self.peakPeriod) + int(self.washPeriod)

            # Find the AD values for each peak using the default peak windows
            self.chdvalues = 0
            if nutrient == 'silicate':
                self.peakstarts = self.silicatepeakstarts
                self.chdvalues = self.silicatechd
            if nutrient == 'phosphate':
                self.peakstarts = self.phosphatepeakstarts
                self.chdvalues = self.phosphatechd
            if nutrient == 'nitrate':
                self.peakstarts = self.nitratepeakstarts
                self.chdvalues = self.nitratechd
            if nutrient == 'nitrite':
                self.peakstarts = self.nitritepeakstarts
                self.chdvalues = self.nitritechd
            if nutrient == 'ammonia':
                self.peakstarts = self.ammoniapeakstarts
                self.chdvalues = self.ammoniachd

            # Pull out the values for each peak in the peak period
            self.windowvals = [[0 for x in range(int(self.windowSize))] for y in
                               range(len(self.peakstarts))]
            self.timevals = [[0 for x in range(int(self.windowSize))] for y in range(len(self.peakstarts))]

            # Gets the AD values for the window range for each peak, will also give a peak a 'bad' flag if
            # the peak start value in the SLK file starts with a #hash, this is a manual control
            # implemented for getting rid of bad data
            for i, x in enumerate(range(len(self.peakstarts) - 1)):
                if self.peakstarts[x][1] == '#':
                    self.qualityflag[i] = 3
                for y in range(int(self.windowSize)):
                    if self.peakstarts[x][1] == '#':
                        self.windowvals[x][y] = self.chdvalues[
                            (int(self.peakstarts[x][2:-1]) + int(self.windowStart) + y)]
                        self.timevals[x][y] = (int(self.peakstarts[x][2:-1]) + int(self.windowStart) + y)
                    else:
                        self.windowvals[x][y] = self.chdvalues[(int(self.peakstarts[x]) + int(self.windowStart) + y)]
                        self.timevals[x][y] = (int(self.peakstarts[x]) + int(self.windowStart) + y)

            # Peak shape QC, uses slope fitting to measure whether a peak shape is good or bad, can implement
            # gui for setting custom values for this. This is good as it works well on small peaks, right up until
            # they are close to the baseline, which is why there is the <4000 cutoff
            slopes = []
            slope2 = []
            for x in self.windowvals:
                med = median(x)
                normed = [y / med for y in x]
                fit = polyfit(range(len(x)), normed, 2)
                slopes.append(fit[0])
                slope2.append(fit[1])
            for i, x in enumerate(slopes):
                if abs(x) > 0.005:
                    self.qualityflag[i] = 6
                if abs(slope2[i]) > 0.009:
                    self.qualityflag[i] = 6
            for i, x in enumerate(self.windowvals):
                if median(x) < 4000:
                    self.qualityflag[i] = 1

            # Window ad medians
            self.windowadmedians = [statistics.median(self.windowvals[x]) for x in range(len(self.windowvals))]
            self.windowadmedians[-1] = 1

            # Set label to say what nutrient we are processing
            self.analysistraceLabel.setText('Analysis Trace for %s:' % nutrient.capitalize())

            # On initial start up set the boundries for the trace plot
            if self.bootup:
                self.xmin = 0
                self.xmax = (len(self.chdvalues) + 10)
                self.ymin = 2000
                self.ymax = 60000
                self.drawtrace('all')
                self.bootup = False
            else:
                self.drawtrace('notall')

            self.tracecanvas.draw()

            self.show()

        except ValueError:
            logging.error('ERROR: Problem with SLK file formatting, a column is missing or out of place')

        except Exception as e:
            logging.error(traceback.print_exc())

    # Function to draw the trace and the peak windows on top, coloured differently depending on flag
    def drawtrace(self, amount):
        try:
            self.maintrace.cla()

            self.maintrace.set_facecolor('#fcfdff')
            self.maintrace.grid(color="#0a2b60", alpha=0.1)
            self.maintrace.set_xlim(self.xmin, self.xmax)
            self.maintrace.set_ylim(self.ymin, self.ymax)
            self.maintrace.set_xlabel('Time (s)')
            self.maintrace.set_ylabel('A/D Value')

            if amount == 'all':
                traceplot = self.maintrace.plot(range(len(self.chdvalues)), self.chdvalues, color='#1b2535',
                                                linewidth=0.75)

                for x in range(len(self.peakstarts) - 1):
                    if self.qualityflag[x] == 1:
                        self.win, = self.maintrace.plot(self.timevals[x], self.windowvals[x], color="#16bc4b",
                                                        linewidth=2)
                    if self.qualityflag[x] == 2:
                        self.win, = self.maintrace.plot(self.timevals[x], self.windowvals[x], color="#63d0ff",
                                                        linewidth=2)
                    if self.qualityflag[x] == 6:
                        self.win, = self.maintrace.plot(self.timevals[x], self.windowvals[x], color="#DB977A",
                                                        linewidth=2)
                    if self.qualityflag[x] == 3 or self.cuptypes[x] == 'NULL':
                        self.win, = self.maintrace.plot(self.timevals[x], self.windowvals[x], color="#f44253",
                                                        linewidth=2)


            else:

                traceplot = self.maintrace.plot(range(len(self.chdvalues)), self.chdvalues, color='#1b2535',
                                                linewidth=0.75)
                for x in range(len(self.peakstarts) - 1):
                    if self.qualityflag[x] == 1:
                        self.win, = self.maintrace.plot(self.timevals[x], self.windowvals[x], color="#16bc4b",
                                                        linewidth=2)
                    if self.qualityflag[x] == 2:
                        self.win, = self.maintrace.plot(self.timevals[x], self.windowvals[x], color="#63d0ff",
                                                        linewidth=2)
                    if self.qualityflag[x] == 6:
                        self.win, = self.maintrace.plot(self.timevals[x], self.windowvals[x], color="#DB977A",
                                                        linewidth=2)
                    if self.qualityflag[x] == 3 or self.cuptypes[x] == 'NULL':
                        self.win, = self.maintrace.plot(self.timevals[x], self.windowvals[x], color="#f44253",
                                                        linewidth=2)


                baselineplot = self.maintrace.plot(self.basepeakstarts, self.bmedians, linewidth=1, color="#d69f20")
                driftplot = self.maintrace.plot(self.driftpeakstarts, self.dmedians, linewidth=1, color="#c6c600")

                self.tracecanvas.draw()

            for x in self.maintrace.get_xticklabels():
                x.set_fontname('Segoe UI Symbol')
            for y in self.maintrace.get_yticklabels():
                y.set_fontname('Segoe UI Symbol')

        except Exception:
            logging.error(traceback.print_exc())
            self.close()

    # Function for calculation the baseline correction across the run
    def baselinecorrection(self, nutrient, windowadmedians):
        try:
            self.bindexes = [i for i, j in enumerate(self.cuptypes) if j == self.params['nutrientprocessing']
            ['cupnames']['baseline']]
            baseindexes = [i for i, j in enumerate(self.cuptypes) if j == self.params['nutrientprocessing']
            ['cupnames']['baseline']]

            self.bmedians = [windowadmedians[x] for x in baseindexes]
            self.bmedians.insert(0, self.bmedians[0])
            baseadmedians = [windowadmedians[x] for x in baseindexes]

            # Makes a baseline (same as first baseline) at the very start of the run
            if baseindexes[0] != '0':
                baseindexes.insert(0, 0)
                baseadmedians.insert(0, baseadmedians[0])

            # Makes a baseline at the very end of the run
            if baseindexes[-1] != len(self.cuptypes):
                baseindexes.insert(-1, len(self.cuptypes) - 1)
                baseindexes.sort()
                baseadmedians.insert(-1, baseadmedians[-1])
            self.baseadmedians = baseadmedians
            self.baseindexs = baseindexes

            # Does a baseline correction based on the type specified for the nutrient
            if self.params['nutrientprocessing']['processingpars'][nutrient]['baseCorrType'] == 'Piecewise':
                # Interpolates the correction factor between each of the drifts to apply across the run

                baseinterp = interp1d(baseindexes, baseadmedians)

                self.basecorrectedmedians = [x - baseinterp(windowadmedians.index(x)) for x in
                                             windowadmedians]
                self.basepeakstarts = [0]
                for x in self.bindexes:
                    if nutrient == 'silicate':
                        self.basepeakstarts.append(float(self.silicatepeakstarts[x]))
                    if nutrient == 'phosphate':
                        self.basepeakstarts.append(float(self.phosphatepeakstarts[x]))
                    if nutrient == 'nitrate':
                        self.basepeakstarts.append(float(self.nitratepeakstarts[x]))
                    if nutrient == 'nitrite':
                        self.basepeakstarts.append(float(self.nitritepeakstarts[x]))
                    if nutrient == 'ammonia':
                        self.basepeakstarts.append(float(self.ammoniapeakstarts[x]))

            self.maintrace.plot(self.basepeakstarts, self.bmedians, linewidth=1, color="#d69f20")
            self.tracecanvas.draw()

            return self.basecorrectedmedians

        except Exception:
            print(traceback.print_exc())

    # Function for calculating carryover correction
    def carryovercorrection(self, basecorrectedmedians):
        try:
            # Get carryover peak indexes
            highindex = self.cuptypes.index(self.params['nutrientprocessing']['cupnames']['high'])
            highadmedian = basecorrectedmedians[highindex]
            lowindex = [i for i, j in enumerate(self.cuptypes) if
                        j == self.params['nutrientprocessing']['cupnames']['low']]
            lowadmedians = [basecorrectedmedians[x] for x in lowindex]
            # k = (B - C) / (A - B)
            self.carryovercorrectioncoef = (lowadmedians[0] - lowadmedians[1]) / (highadmedian - lowadmedians[0])
            correctedbuffer = [m - ((m - 1) * self.carryovercorrectioncoef) for m in basecorrectedmedians]
            self.carryovercorrectedmedians = correctedbuffer
            # self.carryovercorrectedmedians = self.basecorrectedmedians

            return self.carryovercorrectedmedians

        except ValueError:
            logging.error(
                'ERROR: Cannot find high/low carryover in run, not applying carryover correction for file: %s' % self.file)
            self.carryovercorrectioncoef = 1
            return basecorrectedmedians

        except Exception:
            print(traceback.print_exc())

    def driftcorrection(self, nutrient, carryovercorrectedmedians):
        try:
            self.driftcorrbuffer = []
            # Get indexes of drift cups
            self.driftindexes = [i for i, j in enumerate(self.cuptypes) if j == self.params['nutrientprocessing']
            ['cupnames']['drift']]
            if self.driftindexes:
                self.dmedians = [self.windowadmedians[x] for x in self.driftindexes]

                # Get drift values
                driftadmedians = [carryovercorrectedmedians[x] for x in self.driftindexes]
                # Makes a drift (same as first drift) at the very start of the run, makes it easier to interp
                if self.driftindexes[0] != '0':
                    self.driftindexes.insert(0, 0)
                    driftadmedians.insert(0, driftadmedians[0])
                    self.dmedians.insert(0, self.dmedians[0])
                # Makes a drift at the very end of the run equal to last actual drift
                if self.driftindexes[-1] != len(self.cuptypes):
                    self.driftindexes.insert(-1, len(self.cuptypes) - 1)
                    self.driftindexes.sort()
                    driftadmedians.insert(-1, driftadmedians[-1])
                    self.dmedians.insert(-1, self.dmedians[-1])

                self.driftpeakstarts = []
                for x in self.driftindexes:
                    if nutrient == 'silicate':
                        self.driftpeakstarts.append(float(self.silicatepeakstarts[x]))
                    if nutrient == 'phosphate':
                        self.driftpeakstarts.append(float(self.phosphatepeakstarts[x]))
                    if nutrient == 'nitrate':
                        self.driftpeakstarts.append(float(self.nitratepeakstarts[x]))
                    if nutrient == 'nitrite':
                        self.driftpeakstarts.append(float(self.nitritepeakstarts[x]))
                    if nutrient == 'ammonia':
                        self.driftpeakstarts.append(float(self.ammoniapeakstarts[x]))

                self.maintrace.plot(self.driftpeakstarts, self.dmedians, linewidth=1, color="#c6c600")

                # Works out the correction factor to apply between each drift, compared to the overall mean drift
                meanbuffer = statistics.mean(driftadmedians[1:-1])
                for x in driftadmedians:
                    self.driftcorrbuffer.append((meanbuffer / x))

                if self.params['nutrientprocessing']['processingpars'][nutrient]['driftCorrType'] == 'Piecewise':
                    # Interpolates the correction factor between each of the drifts to apply across the run
                    driftinterp = interp1d(self.driftindexes, self.driftcorrbuffer)

                    self.driftcorrectedmedians = [x * driftinterp(carryovercorrectedmedians.index(x)) for x in
                                                  carryovercorrectedmedians]

                    return self.driftcorrectedmedians
            else:
                return carryovercorrectedmedians

        except Exception as e:
            print(traceback.print_exc())
            return carryovercorrectedmedians

    # Function that makes the calibration curve and calculates the final concentrations for the run
    def applycalibration(self, nutrient, driftcorrectedmedians):
        try:
            calibrantindexes = [i for i, j in enumerate(self.cuptypes) if
                                j == self.params['nutrientprocessing']['cupnames']['calibrant']]
            calconcs = 0
            if nutrient == 'silicate':
                calconcs = self.silicatecalibrants
            if nutrient == 'phosphate':
                calconcs = self.phosphatecalibrants
            if nutrient == 'nitrate':
                calconcs = self.nitratecalibrants
            if nutrient == 'nitrite':
                calconcs = self.nitritecalibrants
            if nutrient == 'ammonia':
                calconcs = self.ammoniacalibrants

            calibrantconcentrations = [float(calconcs[x]) for x in calibrantindexes]
            calibrantadvaluemedians = [driftcorrectedmedians[x] for x in calibrantindexes]
            calibrantids = [self.sampleids[x] for x in calibrantindexes]

            # Get quality flags to check if cal should be used in calibration
            self.calibrantflags = [self.qualityflag[x] for x in calibrantindexes]

            # Reset bad cal flags to restart the calibration iteration
            if self.resetcalflags:
                for i, x in enumerate(self.calibrantflags):
                    if x == 6:
                        self.calibrantflags[i] = 1
                self.resetcalflags = False

            # Gets rid of cal 6 values that don't matter for some channels
            # if calibrantconcentrations[-1] == 0.0:
            #    calibrantindexes = calibrantindexes[:-2]
            #    calibrantconcentrations = calibrantconcentrations[:-2]
            #    calibrantadvaluemedians = calibrantadvaluemedians[:-2]
            #    self.calibrantflags = self.calibrantflags[:-2]

            # Takes the cal 0 mean ad value, subtracts it from all the calibrants

            calzeroads = []
            zeroid = self.params['nutrientprocessing']['calibrants']['cal0']
            for i, x in enumerate(calibrantids):
                if x == zeroid:
                    calzeroads.append(calibrantadvaluemedians[i])
            calzeroaverage = statistics.mean(calzeroads)
            calibrantadvaluemediansminuszero = [x - calzeroaverage for x in calibrantadvaluemedians]

            # Make the final ad vals and concs available for plotting etc
            self.finalcaladvals = [x - calzeroaverage for x in calibrantadvaluemedians]
            self.cc = [x for x in calibrantconcentrations]

            # Set the weightings of each calibrant, gives cal zero a tighter weighting to point the curve more to zero
            weightings = []
            calsubsetindexes = []
            for i, x in enumerate(calibrantconcentrations):
                calsubsetindexes.append(i)
                if x == 0.0:
                    # Give cal zero a better weighting to make the calibration more likely to pass through zero
                    weightings.append(0.5)
                else:
                    # Give everything else an equal weighting of 1
                    weightings.append(1)

            # Linear calibration
            if self.params['nutrientprocessing']['processingpars'][nutrient]['calibration'] == 'Linear':
                toproc = True
                it = 0
                while toproc:
                    it += 1
                    procchange = False
                    caladfit = []
                    calconcfit = []
                    weightfit = []
                    for i, x in enumerate(self.calibrantflags):
                        if x == 1 or x == 2 or x == 6:
                            caladfit.append(calibrantadvaluemediansminuszero[i])
                            calconcfit.append(calibrantconcentrations[i])
                            weightfit.append(weightings[i])

                    coeff, resids, rank, singvals, rcond = polyfit(caladfit,
                                                                   calconcfit, 1, w=weightfit,
                                                                   full=True)
                    # Function of fit
                    p = numpy.poly1d(coeff)
                    yhat = p(caladfit)  # or [p(z) for z in x]
                    ybar = numpy.sum(calconcfit) / len(caladfit)  # or sum(y)/len(y)
                    ssreg = numpy.sum((yhat - ybar) ** 2)  # or sum([ (yihat - ybar)**2 for yihat in yhat])
                    sstot = numpy.sum((calconcfit - ybar) ** 2)
                    rsq = ssreg / sstot

                    # Determine residuals for each point in curve
                    calresiduals = []
                    for i, x in enumerate(calconcfit):
                        calresiduals.append(x - p(caladfit[i]))

                    # Check the worst fitted point, if outside error increase weighting or flag
                    worstcalindex = calresiduals.index(max(calresiduals))

                    if max(calresiduals) > float(
                            self.params['nutrientprocessing']['processingpars'][nutrient]['calerror']):
                        if max(calresiduals) < float(
                                self.params['nutrientprocessing']['processingpars'][nutrient]['calerror']) * 2:
                            # Cal error only suspect, marked suspect and given less weighting
                            weightings[worstcalindex] = 3
                            self.calibrantflags[worstcalindex] = 2
                            procchange = True
                        else:
                            # Cal error too great - marked bad
                            self.calibrantflags[worstcalindex] = 6
                            procchange = True

                    # Calibrate repeat if there was an out of place point
                    if procchange:
                        toproc = True
                    else:
                        toproc = False
                    # Iterative cap
                    if it > 10:
                        toproc = False

                    for i, x in enumerate(calibrantindexes):
                        self.qualityflag[x] = self.calibrantflags[i]

                # Get final residuals for plotting
                finalcalresiduals = []
                for i, x in enumerate(calibrantconcentrations):
                    finalcalresiduals.append(p(calibrantadvaluemediansminuszero[i]) - x)

                self.calerrors = finalcalresiduals

                # The poly1d fit that can be plotted
                self.fittoplot = poly1d(polyfit(calibrantadvaluemediansminuszero, calibrantconcentrations, 1))

                # Calibrate the data
                self.calibrateddata = [(k * coeff[0] + coeff[1]) for k in driftcorrectedmedians]

                slope, intercept, self.r_value, p_value, std_err = linregress(calibrantadvaluemediansminuszero,
                                                                              calibrantconcentrations)

            if self.params['nutrientprocessing']['processingpars'][nutrient]['calibration'] == 'Quadratic':
                fit = polyfit(calibrantadvaluemediansminuszero, calibrantconcentrations, 2)
                self.calibrateddata = [(k ^ 2 * fit[0] + k * fit[1] + fit[2]) for k in driftcorrectedmedians]

            self.drawtrace('notall')

        except statistics.StatisticsError:
            logging.error('Could not perform some stats, could be lack of Cal 0')

        except Exception:
            logging.error(traceback.print_exc())

    # Little function to load up the parameters, catches the exception if it can't find it...
    def loadprocsettings(self):
        try:
            with open(self.currpath + '/' + '%sParams.json' % self.currproject, 'r') as file:
                self.params = json.loads(file.read())
        except Exception as e:
            logging.error('ERROR: Could not load project parameters file, this should live within the project folder')

    # Reverse to save params file to disk
    def saveprocsettings(self):
        try:
            with open(self.currpath + '/' + '%sParams.json' % self.currproject, 'w') as file:
                json.dump(self.params, file)
        except Exception as e:
            logging.error(
                'ERROR: Could not save to project parameters file, this should live within the project folder')

    def getindex(self, arr, searchitem):
        for i, x in enumerate(arr):
            for j, y in enumerate(x):
                if y == searchitem:
                    return i, j
        return 'no', 'no'

    # The function that cycles through the nutrients as each one is processed
    # here the calibrated data is put into the project database file
    def nextnut(self):
        try:
            runnumlist = []
            peaknums = []
            survey = []
            deps = []
            rps = []
            testflags = []
            testdilution = []
            for i, x in enumerate(self.calibrateddata):
                runnumlist.append(self.runumber)
                peaknums.append(i+1)
                sid = self.sampleids[i]
                if self.cuptypes[i] != self.params['nutrientprocessing']['cupnames']['sample']:
                    deps.append('calibration')
                    rps.append('calibration')
                    survey.append('calibration')
                else:
                    try:
                        dephold, rphold, surveyhold = determineSurvey(self.database, self.params, 'seal', sid)
                        deps.append(dephold)
                        rps.append(rphold)
                        survey.append(surveyhold)
                    except TypeError:
                        deps.append('NoIdea')
                        rps.append('NoIdea')
                        survey.append('NoIdea')

            finaldata = tuple(zip(runnumlist, self.cuptypes, self.sampleids, peaknums, self.windowadmedians,
                                  self.driftcorrectedmedians, self.calibrateddata, survey, deps, rps, self.qualityflag,
                                  self.dilutionfac, self.epochtime))

            conn = sqlite3.connect(self.database)
            c = conn.cursor()
            c.executemany('INSERT OR REPLACE INTO %sData VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)' % self.currentnut, finaldata)
            conn.commit()
            conn.close()

            if self.currentnut == 'phosphate':
                phosstart = self.windowStart
                phossize = self.windowSize
                phoscarry = self.carryovercorrectioncoef
            if self.currentnut == 'nitrate':
                nitrastart = self.windowStart
                nitrasize = self.windowSize
                nitracarry = self.carryovercorrectioncoef
            if self.currentnut == 'nitrite':
                nitristart = self.windowStart
                nitrisize = self.windowSize
                nitricarry = self.carryovercorrectioncoef
            if self.currentnut == 'silicate':
                silstart = self.windowStart
                silsize = self.windowSize
                silcarry = self.carryovercorrectioncoef
            if self.currentnut == 'ammonia':
                ammstart = self.windowStart
                ammsize = self.windowSize
                ammcarry = self.carryovercorrectioncoef

            # To match up lat/lons if the nutrient file is from the underway
            if self.underwayfile.isChecked():
                self.findlatlons()

            # Save fresh processing settings in the json file
            self.saveprocsettings()

            # Go to the next nutrient that is active and process it
            indexthrough = self.nutsactive.index(self.currentnut)
            if indexthrough < len(self.nutsactive) - 1:
                # self.qualityflag = [1 for x in self.sampleids]
                # self.dilutionfac = [1 for x in self.sampleids]
                self.bootup = True
                self.qctabs.clear()
                plt.clf()
                self.currentnut = self.nutsactive[indexthrough + 1]

                self.processingcontainer(self.currentnut)

            else:

                # Save all useful information to put into the header table in the db
                # Is used to reprocess if necessary, could also apply same processing settings as
                # another file, TODO: add feature to process file based on another file

                # First convert analysis time in the file to epoch time in seconds
                format = '%d/%m/%Y %I:%M:%S %p'
                structtime = time.strptime(self.analysisdate + ' ' + self.analysistime, format)
                self.analepochtime = calendar.timegm(structtime)

                conn = sqlite3.connect(self.database)
                c = conn.cursor()

                # header = tuple(
                #    zip(self.file, self.analepochtime, self.operator, self.nitragain, self.nitrabase, nitrastart,
                #        nitrasize, nitracarry, self.phosgain, self.phosbase, phosstart, phossize, phoscarry,
                #        self.silgain, self.silbase, silstart, silsize, silcarry, self.nitrigain, self.nitribase,
                #        nitristart, nitrisize, nitricarry, self.ammbase, self.ammgain, ammstart, ammsize, ammcarry))

                # Make a record of the file processed and its modified time to check when it has been updated
                modifiedtime = float(os.path.getmtime(self.filepath))
                holder = ((self.file, modifiedtime),)
                conn = sqlite3.connect(self.database)
                c = conn.cursor()
                c.executemany('INSERT OR REPLACE INTO nutrientFilesProcessed VALUES(?,?)', holder)
                conn.commit()
                conn.close()

                # Close it out...
                plt.clf()
                self.close()
                logging.info('Nutrient file - ' + str(self.file) + ' successfully processed')
                if not self.rereading:
                    self.refreshing = processing.RefreshFunction.refreshFunction(self.currpath, self.currproject,
                                                                                 self.interactive)

        except Exception:
            print(traceback.print_exc())

    def cancel(self):
        self.close()

    # Function that moves the 'camera' along the trace
    def shiftleftxaxis(self):
        xmin, xmax = self.maintrace.get_xbound()
        tenpercent = xmax * 0.1
        if xmin > 0 - 100:
            self.maintrace.set_xlim(xmin - tenpercent, xmax - tenpercent)
            self.tracecanvas.draw()
        if self.autosize.isChecked():
            self.zoomfit()

    def shiftrightxaxis(self):
        xmin, xmax = self.maintrace.get_xbound()
        tenpercent = xmax * 0.1
        if xmax < len(self.chdvalues) + 100:
            self.maintrace.set_xlim(xmin + tenpercent, xmax + tenpercent)
            self.tracecanvas.draw()
        if self.autosize.isChecked():
            self.zoomfit()

    # Function for zooming in on the trace
    def zoomin(self):
        ymin, ymax = self.maintrace.get_ybound()
        xmin, xmax = self.maintrace.get_xbound()
        ytenpercent = ymax * 0.1
        xtenpercent = (xmax - xmin) * 0.15
        if ymax > min(self.chdvalues) * 2 and xtenpercent < (xmax - xmin) / 2:
            self.maintrace.set_ylim(ymin, ymax - ytenpercent)
            self.maintrace.set_xlim(xmin + xtenpercent, xmax - xtenpercent)
        self.tracecanvas.draw()

    # Function for zooming out on trace
    def zoomout(self):
        ymin, ymax = self.maintrace.get_ybound()
        xmin, xmax = self.maintrace.get_xbound()
        ytenpercent = ymax * 0.1
        xtenpercent = (xmax - xmin) * 0.15
        if ymax < max(self.chdvalues) + 500:
            self.maintrace.set_ylim(ymin, ymax + ytenpercent)
            self.maintrace.set_xlim(xmin - xtenpercent, xmax + xtenpercent)
        else:
            if xmin > 0 and xmax < len(self.chdvalues):
                self.maintrace.set_xlim(xmin - xtenpercent, xmax + xtenpercent)
        self.tracecanvas.draw()

    # Fits height bounds to match tallest peak
    def zoomfit(self):
        try:
            ymin, ymax = self.maintrace.get_ybound()
            xmin, xmax = self.maintrace.get_xbound()
            maxheight = max(self.chdvalues[int(xmin): int(xmax)])
            self.maintrace.set_ylim(ymin, maxheight * 1.02)
            self.tracecanvas.draw()
        except Exception as e:
            print(e)

    # Manages the clicking
    def on_click(self, event):
        tb = get_current_fig_manager().toolbar
        if event.button == 1 and event.inaxes and tb.mode == '':
            xaxistime = int(event.xdata)
            x = 'trace'
            self.matchclicktopeak(x, xaxistime)

    # Manages the key pressing
    def keyPressEvent(self, event):
        # print(event.key())
        if event.key() == 65:
            self.shiftleftxaxis()
        if event.key() == 68:
            self.shiftrightxaxis()
        if event.key() == 87:
            self.zoomin()
        if event.key() == 88:
            self.zoomout()
        if event.key() == 83:
            self.zoomfit()
        if event.key() == 81:
            if self.autosize.isChecked():
                self.autosize.setChecked(False)
            else:
                self.autosize.setChecked(True)

    # Function that finds the corresponding peak to what was clicked on the trace
    def matchclicktopeak(self, plot, xdata):
        try:
            if plot == 'trace':
                for i, x in enumerate(self.peakstarts):
                    if i + 1 < len(self.peakstarts):
                        if x[1] == '#':
                            point = x[2:-1]
                        else:
                            point = x

                        if self.peakstarts[i + 1][1] == '#':
                            pointplusone = self.peakstarts[i + 1][2:-1]
                        else:
                            pointplusone = self.peakstarts[i + 1]

                        if xdata > int(point) and xdata < int(pointplusone):
                            sampleid = self.sampleids[i]
                            admedian = self.windowadmedians[i]
                            conc = self.calibrateddata[i]
                            flag = self.qualityflag[i]
                            dil = self.dilutionfac[i]
                            cup = self.cuptypes[i]
                            index = i
                            peaknumber = i + 1
                            self.tracedialog = traceSelection(sampleid, cup, peaknumber, admedian, conc, flag, dil,
                                                              'Trace')
                            self.tracedialog.show()
                            self.tracedialog.setStart.connect(lambda: self.movepeakstart(xdata, index))
                            self.tracedialog.setStart.connect(self.tracedialog.close)
                            self.tracedialog.setEnd.connect(lambda: self.movepeakend(xdata, index))
                            self.tracedialog.setEnd.connect(self.tracedialog.close)
                            self.tracedialog.saveSig.connect(lambda: self.updatefromtracedialog(index))
                            self.tracedialog.peakShiftRight.connect(lambda: self.shiftpeaks(xdata, 'right'))
                            self.tracedialog.peakShiftLeft.connect(lambda: self.shiftpeaks(xdata, 'left'))

        except Exception:
            logging.error(traceback.print_exc())

    # Everything needs to be reprocessed if something changes in the dialog
    def updatefromtracedialog(self, index):
        self.cuptypes[index] = self.tracedialog.peakcupline.text()
        self.dilutionfac[index] = float(self.tracedialog.dilutionline.text())
        if self.tracedialog.flagbox.currentText() == 'Good':
            self.qualityflag[index] = 1
        if self.tracedialog.flagbox.currentText() == 'Suspect':
            self.qualityflag[index] = 2
        if self.tracedialog.flagbox.currentText() == 'Bad':
            self.qualityflag[index] = 3

        self.resetcalflags = True

        # Reprocess it all now yeowww
        self.xmin, self.xmax = self.maintrace.get_xbound()  # Keep same trace bounds after re-draw
        self.ymin, self.ymax = self.maintrace.get_ybound()
        self.tabindex = self.qctabs.currentIndex()  # Also keep same tab, more user friendly..
        self.processingcontainer(self.currentnut)  # Contains eqtns to proc data

    # Function that actually deletes AD data, due to hydraulic effects sometimes peaks can become
    # out of sync, not being where they should be, this allows a manual method for shifting them back into place
    def shiftpeaks(self, clickxdata, direction):
        if direction == 'right':
            for i in range(3):
                self.chdvalues.insert(clickxdata, 0)
        if direction == 'left':
            for i in range(3):
                self.chdvalues.pop(clickxdata)

        # Reprocess it all now
        self.xmin, self.xmax = self.maintrace.get_xbound()  # Keep same trace bounds after re-draw
        self.ymin, self.ymax = self.maintrace.get_ybound()
        self.tabindex = self.qctabs.currentIndex()  # Also keep same tab, more user friendly..
        self.processingcontainer(self.currentnut)  # Contains eqtns to proc data

    # Moves a peak window start position
    def movepeakstart(self, clickxdata, peakindex):
        try:
            currentwindowvals = self.timevals[peakindex]
            if clickxdata < max(currentwindowvals):
                if clickxdata < min(currentwindowvals):
                    differential = min(currentwindowvals) - clickxdata
                    # Find the new start point on the peak
                    newstart = int(self.params['nutrientprocessing']['processingpars'][self.currentnut][
                                       'windowStart']) - differential
                    self.params['nutrientprocessing']['processingpars'][self.currentnut]['windowStart'] = newstart
                    # Window size will now be bigger, find the correct window size to apply
                    newlength = max(currentwindowvals) - clickxdata
                    self.params['nutrientprocessing']['processingpars'][self.currentnut][
                        'windowSize'] = newlength

                if clickxdata > min(currentwindowvals) and clickxdata < max(currentwindowvals):
                    # Find the new start point on the peak
                    differential = clickxdata - min(currentwindowvals)
                    newstart = int(self.params['nutrientprocessing']['processingpars'][self.currentnut][
                                       'windowStart']) + differential
                    self.params['nutrientprocessing']['processingpars'][self.currentnut][
                        'windowStart'] = newstart
                    # Make the window size smaller now
                    newlength = max(currentwindowvals) - clickxdata
                    self.params['nutrientprocessing']['processingpars'][self.currentnut][
                        'windowSize'] = newlength

                self.resetcalflags = True

                # Reprocess it all now
                self.xmin, self.xmax = self.maintrace.get_xbound()  # Keep same trace bounds after re-draw
                self.ymin, self.ymax = self.maintrace.get_ybound()
                self.tabindex = self.qctabs.currentIndex()  # Also keep same tab, more user friendly..
                self.processingcontainer(self.currentnut)  # Contains eqtns to proc data

        except Exception:
            logging.error(traceback.print_exc())

    # Moves a peak window end position
    def movepeakend(self, clickxdata, peakindex):
        try:
            currentwindowvals = self.timevals[peakindex]
            if clickxdata > min(currentwindowvals):
                if clickxdata < max(currentwindowvals):
                    differential = max(currentwindowvals) - clickxdata
                    newend = int(self.params['nutrientprocessing']['processingpars'][self.currentnut][
                                     'windowSize']) - differential
                    self.params['nutrientprocessing']['processingpars'][self.currentnut][
                        'windowSize'] = newend

                if clickxdata > max(currentwindowvals):
                    differential = clickxdata - max(currentwindowvals)
                    newend = int(self.params['nutrientprocessing']['processingpars'][self.currentnut][
                                     'windowSize']) + differential
                    self.params['nutrientprocessing']['processingpars'][self.currentnut][
                        'windowSize'] = newend

                self.resetcalflags = True

                # Reprocess it all now
                self.xmin, self.xmax = self.maintrace.get_xbound()
                self.ymin, self.ymax = self.maintrace.get_ybound()
                self.tabindex = self.qctabs.currentIndex()
                self.processingcontainer(self.currentnut)

        except Exception:
            logging.error(traceback.print_exc())

    # Small container for going through the necessary processing functions
    def processingcontainer(self, nut):

        # This changes any temporary 'bad' flags for the cals back to good so they are re-used in calibration
        for i, x in enumerate(self.qualityflag):
            if x == 6:
                self.qualityflag[i] = 1

        self.matchpeaksgetadvals(nut)

        basecorrectedadmedians = self.baselinecorrection(nut, self.windowadmedians)

        carryovercorrectedadmedians = self.carryovercorrection(basecorrectedadmedians)

        driftcorrectedadmedians = self.driftcorrection(nut, carryovercorrectedadmedians)

        self.applycalibration(nut, driftcorrectedadmedians)

        if not self.interactive:
            self.nextnut()
        else:
            self.qctabscreate()

    # The QC tabs on the right of the screen are produced from within here, this function essentially prepares the data
    # then calls upon QCPlots.py to produce the plots
    def qctabscreate(self):
        try:

            # Calibration curve plot creation
            self.calcurvetab = QWidget()
            self.qctabs.addTab(self.calcurvetab, 'Cal Curve')
            self.calcurvetab.layout = QVBoxLayout()
            self.calcurveplotted = qcp.calibrationCurve(self.currentnut, self.finalcaladvals, self.cc,
                                                        self.fittoplot, self.r_value, self.calibrantflags)
            self.calcurvetab.layout.addWidget(self.calcurveplotted)
            self.calcurvetab.setLayout(self.calcurvetab.layout)

            # Calibration error plot creation
            calpeaknums = []
            for i, id in enumerate(self.cuptypes):
                if id == self.params['nutrientprocessing']['cupnames']['calibrant']:
                    calpeaknums.append(i)
            self.calerrortab = QWidget()
            self.qctabs.addTab(self.calerrortab, 'Cal Error')
            self.calerrortab.layout = QVBoxLayout()
            self.calerrorplotted = qcp.calibrationError(self.currentnut, calpeaknums, self.calerrors,
                                                        self.params['nutrientprocessing']['processingpars'][
                                                            self.currentnut]['calerror'], self.calibrantflags)
            self.calerrortab.layout.addWidget(self.calerrorplotted)
            self.calerrortab.setLayout(self.calerrortab.layout)

            # Baseline correction plot creation
            maxcalibrantad = max(self.finalcaladvals)
            basepercentage = [x / maxcalibrantad for x in self.baseadmedians]
            self.basecorrtab = QWidget()
            self.qctabs.addTab(self.basecorrtab, 'Baseline Correction')
            self.basecorrtab.layout = QGridLayout()
            type = 'baseline'
            self.baselinecorrplotted = qcp.driftBase(self.baseindexs, basepercentage, self.windowadmedians, type,
                                                     self.qualityflag)
            self.basecorrtab.layout.addWidget(self.baselinecorrplotted)
            self.basecorrtab.setLayout(self.basecorrtab.layout)

            # Drift correction plot creation
            self.driftcorrtab = QWidget()
            self.qctabs.addTab(self.driftcorrtab, 'Drift Correction')
            self.driftcorrtab.layout = QGridLayout()
            type = 'drift'
            self.driftcorrplotted = qcp.driftBase(self.driftindexes, self.driftcorrbuffer,
                                                  self.windowadmedians, type, self.qualityflag)
            self.driftcorrtab.layout.addWidget(self.driftcorrplotted)
            self.driftcorrtab.setLayout(self.driftcorrtab.layout)

            # Determine QC plots that are needed
            for x in self.params['nutrientprocessing']['qcsamplenames'].keys():
                inrun = False
                qc = self.params['nutrientprocessing']['qcsamplenames'][x]
                qcindex = []
                for i, id in enumerate(self.sampleids):
                    if qc in id:
                        qcindex.append(i)
                        inrun = True

                if inrun:
                    if x == 'rmns':
                        # Need to figure out what RMNS and if multiple
                        ids = [self.sampleids[x] for x in qcindex]
                        alllots = [self.sampleids[x][len(qc) + 1:len(qc) + 3] for x in qcindex]
                        lots = set(alllots)
                        splitindexes = []
                        for y in lots:
                            peaknum = []
                            conc = []
                            for i, z in enumerate(alllots):
                                if y == z:
                                    peaknum.append(qcindex[i])
                                    conc.append(self.calibrateddata[qcindex[i]])

                            self.rmnstab = QWidget()
                            self.qctabs.addTab(self.rmnstab, 'RMNS %s' % y)
                            self.rmnstab.layout = QVBoxLayout()
                            self.rmnsplotted = qcp.rmnsPlot(y, self.currentnut, peaknum, conc)
                            self.rmnstab.layout.addWidget(self.rmnsplotted)
                            self.rmnstab.setLayout(self.rmnstab.layout)

                    elif x == 'mdl':
                        mdladmedians = [self.calibrateddata[x] for x in qcindex]
                        self.mdltab = QWidget()
                        self.qctabs.addTab(self.mdltab, 'MDL')
                        self.mdltab.layout = QVBoxLayout()
                        self.mdlplotted = qcp.mdlPlot(qcindex, mdladmedians)
                        self.mdltab.layout.addWidget(self.mdlplotted)
                        self.mdltab.setLayout(self.mdltab.layout)

                    else:
                        self.newtab = QWidget()
                        self.qctabs.addTab(self.newtab, '%s' % qc)

            self.qctabs.setCurrentIndex(self.tabindex)

        except Exception:
            print(traceback.print_exc())

    # Little function used for matching the ships lat longs to analysis time stamps, used for underway processing
    # Can ignore for general use
    def findlatlons(self):
        # uwync = Dataset(self.currpath + '/in2018_v04uwy.nc')
        uwync = Dataset(self.currpath + '/' + self.currproject + 'uwy.nc')
        epochdate = uwync.Epoch
        datetoconvert = epochdate[-22:-3]
        uwyformat = '%Y-%m-%d %H:%M:%S'
        ts = time.strptime(datetoconvert, uwyformat)
        epochtimestamp = calendar.timegm(ts)
        starttime = epochtimestamp + float(epochdate[0:8])
        uwylon = uwync.variables['longitude'][:]
        uwylat = uwync.variables['latitude'][:]
        uwytime = []
        uwytime.append(starttime)
        for i, x in enumerate(uwylon):
            uwytime.append(uwytime[i] + 5)

        sampleepochtimes = []
        pickedconcentrations = []
        for i, x in enumerate(self.cuptypes):
            if x == self.params['nutrientprocessing']['cupnames']['sample']:
                if self.qualityflag[i] == 1 or self.qualityflag[i] == 6:
                    sampleepochtimes.append(self.epochtime[i])
                    pickedconcentrations.append(self.calibrateddata[i])

        startingsampletime = min(sampleepochtimes)
        endingsampletime = max(sampleepochtimes)
        uwytimestartindex = 0
        uwytimeendindex = 0
        for i, x in enumerate(uwytime):
            if abs(x - startingsampletime) < 3:
                uwytimestartindex = i
            if abs(x - endingsampletime) < 4:
                uwytimeendindex = i
                break

        print(uwytimestartindex)
        print(uwytimeendindex)

        subsetuwytime = uwytime[uwytimestartindex: uwytimeendindex]
        subsetuwylat = uwylat[uwytimestartindex: uwytimeendindex]
        subsetuwylon = uwylon[uwytimestartindex: uwytimeendindex]
        uwyindex = []
        for i, x in enumerate(subsetuwytime):
            for o, m in enumerate(sampleepochtimes):
                if abs(x - m) < 5:
                    uwyindex.append(i)

        matchlat = [float(subsetuwylat[x]) for x in uwyindex]
        matchlon = [float(subsetuwylon[x]) for x in uwyindex]
        file = [self.file for x in uwyindex]

        print(len(matchlat))
        print(len(matchlon))
        print(len(pickedconcentrations))

        uwydata = tuple(zip(matchlat, matchlon, sampleepochtimes, pickedconcentrations, file))

        conn = sqlite3.connect(self.database)
        c = conn.cursor()

        if self.tabledoesntexist:
            c.executemany(
                'INSERT OR REPLACE INTO underwayNutrients(latitude, longitude, time, %s, file) VALUES(?,?,?,?,?)' % self.currentnut,
                uwydata)
            self.tabledoesntexist = False
        else:
            uwytime = tuple(zip(pickedconcentrations, sampleepochtimes))
            c.executemany('UPDATE underwayNutrients SET %s=? WHERE time=?' % self.currentnut, uwytime)

        conn.commit()
        conn.close()

    def sidescrollerclicked(self):
        self.pressed = True
        # scrollerthread = threading.Thread(self.sidescroller)
        # scrollerthread.daemon = True
        # scrollerthread.start()

    def sidescroller(self):
        value = self.sidescroll.value()
        percentageslide = value / 50
        xmin, xmax = self.maintrace.get_xbound()
        if percentageslide < 1:
            self.maintrace.set_xlim(xmin - (5 * (1 + percentageslide)), xmax - (5 * (1 + percentageslide)))
            self.tracecanvas.draw()
        if percentageslide > 1:
            self.maintrace.set_xlim(xmin + (5 * (1 + percentageslide)), xmax + (5 * (1 + percentageslide)))
            self.tracecanvas.draw()
            # self.sidescroll.sliderReleased.connect(self.setscroller)

    def setscroller(self):
        self.pressed = False
        self.sidescroll.setValue(50)

