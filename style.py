import matplotlib as mpl

# Color cycle is a very slightly modified Seaborn Muted palette (removed the grey color)
mplstyle = {'normal': {'axes.edgecolor': '#000000', 'xtick.color': '#000000', 'ytick.color': '#000000',
                       'axes.facecolor': '#FDFDFF', 'axes.labelcolor': '#000000', 'figure.facecolor': '#FDFDFF',
                       'grid.color': '#000000', 'figure.frameon': False, 'legend.facecolor': '#fdfdfd',
                       'text.color': '#050505', 'lines.color': '#02020B',
                       'axes.prop_cycle': mpl.cycler(color=['#191919', '#4878d0', '#ee864a', '#6acc64', '#d65f5f',
                                                            '#956cb4', '#8c613c', '#dc7ec0', '#d5bb67', '#82c6e2'])},
            'dark': {'axes.edgecolor': '#F5F5F5', 'xtick.color': '#F5F5F5', 'ytick.color': '#F5F5F5',
                     'axes.facecolor': '#191919', 'axes.labelcolor': '#F5F5F5', 'figure.facecolor': '#202020',
                     'grid.color': '#F5F5F5', 'lines.color': '#F5F5F5', 'figure.frameon': False,
                     'text.color': '#F5F5F5',
                     'axes.prop_cycle': mpl.cycler(color=['#F5F5F5', '#4878d0', '#ee864a', '#55A868', '#C44E52',
                                                          '#8172B3', '#B27B4C', '#DA8BC3', '#CCB974', '#64B5CD']),
                     'legend.facecolor': '#191919'}}

stylesheet = {'normal': """
/* -------------------------------- QMainWindow-----------

---------------------------------------------------------- */
QMainWindow[ProcessingMenu=true] {
    background-color: #ebeff2;
    border: 0px;
}

QMainWindow[NutrientProcessing=true] {
    background-color: #ebeff2;
    border: 0px;
    
}

QMainWindow {
    font-family: Segoe UI;
    background-color: #EBEFF2;
}



/* ---------------------------- QGraphicsDropShadow ------

---------------------------------------------------------- */
QGraphicsDropShadow {
    color: #e1e6ea;
   
}

/* -------------------------------- QLineEdit  -----------

---------------------------------------------------------- */

QLineEdit {
    font: 14px Segoe UI;
}
QLineEdit:hover {
    font: 14px;
    border: 1px solid #41ADD4;
}



/* ----------------------------------- QLabel ------------

---------------------------------------------------------- */
QLabel {
    font: 14px Segoe UI;
}
QLabel[dashboardText=true] {
    color: #222222;
    font: 15px;
    padding: 10px; 
}
QLabel[sideHeaderHeading=true] {   
    font: 22px;
    color: #FFFFFF;
}
QLabel[sideBarText=true] {
    font: 14px;
    color: #FFFFFF;
}
QLabel[nutrientHeader=true] {
    font: 22px;
    color: #FFFFFF;
}

QLabel[headerText=true] {
    min-width: 60px;
    min-height:20px;
    font: 24px;
    color: #ffffff;
    font-weight: bold;
}
QLabel[headerLogo=true] {
    padding-left: 33px
}


/* --------------------------------- QListWidget ---------

---------------------------------------------------------- */
QListWidget {
    font: 14px Segoe UI;
}


/* --------------------------------- QPushButton ---------

---------------------------------------------------------- */
QPushButton {
    font: 14px Segoe UI;
}
QPushButton[sideBarButton=true] {
    border: 1px solid #4e546c;
    color: #ffffff;
    font: 14px;
    height: 25px;
}
QPushButton[sideBarButton=true]:hover {
    border: 1px solid #4e546c;
    color: #ccd5e0;
}
QPushButton[sideBarButton=true]:pressed {
    border: 1px solid #4e546c;
    color: #6bb7ff;
    border-radius: 1px;
}
QPushButton[nutrientControls=true] {
    color: #222222;
    border: 1px solid #EDEDED;
    border-radius: 5px;
    font: 15px;
}
QPushButton[nutrientControls=true]:hover {
    border: 2px solid #C7E6FF;
    background-color: #E0F0FF;
}
QPushButton[nutrientControls=true]:pressed {
    border: 1px solid #8F98A9;
    background-color: #78C6FF;
    border-style: inset;
}
QPushButton[msgBox=true] {
    width: 85px;
}

QPushButton[procButton=true] {
    color: #222222;
    border: 1px solid #ededed;
    border-radius: 5px;
    background: #ededed;
    font: 14px;
    padding-left: 30px;
    padding-right: 30px;
    padding-top: 5px;
    padding-bottom: 5px;
}
QPushButton[procButton=true]:hover {
    color: #222222;
    border: 1px solid #f7f7f7;
    background: #f7f7f7;
    font: 14px;
}
QPushButton[procButton=true]:pressed{
    border: 1px solid #8f98a8;
    color: #222222;
    background-color: #f7f7f7;
    font: 14px;
    border-style: inset;
}
QPushButton[stealth=true] {
    text-align: left;
    font: 15px;
    color: #222222;
    padding: 10px;
    background-color: #f4f8ff;
    border: 0px;   
}
QPushButton[stealth=true]:hover {
    font: 15px;
    color: #6bb7ff;
    padding: 10px;
    background-color: #f4f8ff;
    border: 0px;
}
QPushButton[stealth=true]:pressed {
    font: 15px;
    color: #086ece;
    padding: 10px;
    background-color: #f4f8ff;
    border: 0px;
}


/* ---------------------------------- QComboBox ---------

---------------------------------------------------------- */
QComboBox {
    font: 14px Segoe UI;
}


/* ---------------------------------- QCheckBox ----------

---------------------------------------------------------- */
QCheckBox {
    font: 14px Segoe UI;
}
QCheckBox[survey_checkbox=true]:indicator {
    width: 50px;
    height: 50px;
}

QCheckBox[sideBarCheckbox=true] {
    font: 14px;
    color: #ffffff;
}


/* --------------------------------- QListWidget ---------

---------------------------------------------------------- */
QListWidget {
    font: 14px;
}


/* --------------------------------- QTabWidget ----------

---------------------------------------------------------- */
QTabWidget QWidget {
    font: 14px Segoe UI;
}


/* --------------------------------- QTableWidget ---------

---------------------------------------------------------- */
QTableWidget {
    font: 14px Segoe UI;
}
QHeaderView {
    font: 14px Segoe UI;
}


/* -------------------------------- QPlainTextEdit---------

---------------------------------------------------------- */
QPlainTextEdit[output=true]{
    font: 14px;
    border: 0px;
    padding-bottom: 3px;
}



/* ----------------------------------- QFrame ------------

---------------------------------------------------------- */

QFrame[dashboardFrame=true] {
    background-color: #f7faff;
}
QFrame[sideBarFrame=true] {
    background-color: #4e546c;
    border-radius: 1px;
}
QFrame[topBarFrame=true] {
    background-color: #ddeaff;
}
QFrame[sideHeaderFrame=true] {
    background-color: #555c78;
    border-radius: 1px;
}
QFrame[nutrientFrame=true] {
    background-color: #F9FCFF;
}
QFrame[nutrientFrame2=true] {
    background-color: #F9FCFF;
    padding: 20px;
}
QFrame[nutrientHeadFrame=true] {
    background-color: #DDEAFF;
}
QFrame[nutrientButtonFrame=true] {
    background-color:#F9FCFF;
    border: 1px solid #DDEAFF;
    border-radius: 3px;
}


/* --------------------------------- QScrollBar ---------

---------------------------------------------------------- */
QScrollBar:vertical {
    width: 6px;
    border: 0px solid #888888;
    background: white;
    border-radius: 3px;
    margin: 0px 0px 0px 0px;
    min-height: 6px;
}
QScrollBar:handle:vertical::pressed {
    background: #555c78;
    border-radius: 3px;    
}
QScrollBar::handle:vertical {
    background: #4e546c;
    min-height: 0px;
    border-radius: 3px;
    min-height: 20px;
}  
QScrollBar::add-line:vertical {
    background: #999999;
    height: 0px;
    subcontrol-position: bottom;
    subcontrol-origin: margin;
} 
QScrollBar::sub-line:vertical {
    background: #999999;
    height: 0px;
    subcontrol-position: top;
    subcontrol-origin:margin;
}

/* --------------------------------------- QMenu ---------

---------------------------------------------------------- */

QMenu {
    font: 13px Segoe UI;
}
QMenuBar {
    font: 13px Segoe UI;
}

/* --------------------------------------- QToolTip ---------

---------------------------------------------------------- */

QToolTip {
    font: 15px Segoe UI;
}
"""

'''
****************************************************************************************************

  Dark theme

  Note font color in dark theme is to be F5F5F5, white can be too harsh of a contrast and actually makes dark mode
  not that nice to use. The very slight off white color is more pleasing on the eyes. Doesn't 'dazzle' as bad

*****************************************************************************************************
'''
              
,'dark': """
/* --------------------------------- QTitleBar -----------

---------------------------------------------------------- */
QTitleBar {
    font-family: Segoe UI;
    background-color: #000000;
}


/* --------------------------------- QMainWindow ---------

---------------------------------------------------------- */
QMainWindow {
    background-color: #0F0F0F;
}


/* ---------------------------- QGraphicsDropShadow ------

---------------------------------------------------------- */
QGraphicsDropShadow {
    color: #191919;
}


/* ---------------------------------- QDialog ------------

---------------------------------------------------------- */
QDialog {
    background-color: #202020;
    font: 14px Segoe UI;
}


/* ------------------------------- QMessageBox ------------

---------------------------------------------------------- */
QMessageBox {
    background-color: #202020;
    background-color: #2C2C2C;
}
QDialogButtonBox {
    background-color: #50E62D;
}




/* ----------------------------------- QLabel ------------

---------------------------------------------------------- */
QLabel {
    font: 14px Segoe UI;
    color: #F5F5F5;
}
QLabel[dashboardText=true] {
    color: #F5F5F5;
    font: 15px;
    padding: 10px; 
}
QLabel[sideHeaderHeading=true] {   
    font: 22px;
    color: #F5F5F5;
}
QLabel[sideBarText=true] {
    font: 14px;
    color: #F5F5F5;
}

QLabel[headerText=true] {
    min-width: 60px;
    min-height:20px;
    font: 24px;
    color: #ffffff;
    font-weight: bold;
}
QLabel[headerLogo=true] {
    padding-left: 33px
}


/* --------------------------------- QPushButton ---------

---------------------------------------------------------- */
QPushButton {
    font: 14px Segoe UI;
    color: #F5F5F5;
    border: 3px solid #333333;
    background-color: #333333;
}
QPushButton:hover {
    border: 2px solid #858585;
}
QPushButton:pressed {
    background-color: #666666;
}
QPushButton[sideBarButton=true] {
    border: 0px solid #4e546c;
    background-color: None;
    color: #F5F5F5;
    font: 14px;
    height: 25px;
}
QPushButton[sideBarButton=true]:hover {
    color: #ccd5e0;
    border: 1px solid #6C676A;
}
QPushButton[sideBarButton=true]:pressed {
    color: #6bb7ff;
}
QPushButton[msgBox=true] {
    width: 85px;
}
QPushButton[nutrientControls=true] {
    border: 1px solid #858585;
    background-color: #333333;
    border-radius: 2px;
}
QPushButton[nutrientControls=true]:hover {
    color: #ccd5e0;
    border: 1px solid #6C676A;
}
QPushButton[nutrientControls=true]:pressed {
    color: #6bb7ff;
    background-color: #3A3A3A;
}

QPushButton[procButton=true] {
    color: #FAFAFA;
    border: 1px solid #272822;
    border-radius: 5px;
    background: #3C3F41;
    font: 14px;
    padding-left: 30px;
    padding-right: 30px;
    padding-top: 5px;
    padding-bottom: 5px;
}
QPushButton[procButton=true]:hover {
    color: #FAFAFA;
    border: 1px solid #82898D;
    background: #5F6467;
}
QPushButton[procButton=true]:pressed{
    border: 1px solid #82898D;
    color: #FAFAFA;
    background-color: #5F6467;
    border-style: inset;
}

QPushButton[stealth=true] {
    text-align: left;
    font: 15px;
    color: #FAFAFA;
    padding: 10px;
    background-color: #202020;
    border: 0px;   
}
QPushButton[stealth=true]:hover {
    font: 15px;
    color: #6bb7ff;
    padding: 10px;
    background-color: #202020;
    border: 0px;
}
QPushButton[stealth=true]:pressed {
    font: 15px;
    color: #086ece;
    padding: 10px;
    background-color: #202020;
    border: 0px;
}

/* ---------------------------------- QComboBox ----------

---------------------------------------------------------- */
QComboBox {
    font: 14px Segoe UI;
    color: #F5F5F5;
    border: 1px solid #666666;
    background-color: #000000;
}
QComboBox:hover {
    border: 2px solid #999999;
}
QComboBox:drop-down {
    border: 0px;
    background-color: #191919;
    color: white;
}
QComboBox QAbstractItemView {
    background-color: #191919;
    color: white;
    selection-background-color: #4D4D4D;    
}
QComboBox:down-arrow {
    image: url(:/assets/dark_mode_drop_arrow.png);
    border: 0px;
    width: 14px;
}


/* --------------------------------- QCheckBox ---------

---------------------------------------------------------- */
QCheckBox {
    font: 14px Segoe UI;
    color: white;
}


/* --------------------------------- QTabWidget ----------

---------------------------------------------------------- */
QTabWidget QWidget {
    font: 14px Segoe UI;
    color: white;
    background-color: #202020;
}
QTabWidget:pane {
    background-color: #191919;
}   
QTabBar:tab {
    background-color: #333333;
}
QTabBar:tab:selected {
    background-color: #666666;
}
QTabBar:tab:hover {
    border: 2px solid #666666;
}




/* --------------------------------- QLineEdit -----------

---------------------------------------------------------- */
QLineEdit {
    border: 1px solid #666666;
    font: 14px Segoe UI;
    color: white;
    background-color: #191919;
}
QLineEdit:hover {
    border: 1px solid #9C9C9C;
}
QLineEdit:focus {
    border: 1px solid #999999;
}


/* ---------------------------------- QListWidget -------

---------------------------------------------------------- */
QListWidget {
    font: 14px Segoe UI;
    color: #F5F5F5;
    background-color: #191919;
    selection-background-color: #4D4D4D;    
}
QListView:item:hover {
    background-color: #2B2B2B;
    color: white;
    
}
QListView:item:selected {
    background-color: #666666;
}



/* --------------------------------- QTableWidget ---------

---------------------------------------------------------- */
QTableWidget {
    font: 14px Segoe UI;
    background-color: #191919;
    color: white;
    gridline-color: #666666;
}
QHeaderView {
    font: 14px Segoe UI;
    background-color: #4D4D4D;
    color: white;
}
QHeaderView:section {
    background-color: #202020;
    gridline-color: #666666;
}



/* --------------------------------- QScrollBar ---------

---------------------------------------------------------- */
QScrollBar:vertical {
    width: 6px;
    border: 0px solid transparent;
    background: transparent;
    border-radius: 3px;
    margin: 0px 0px 0px 0px;
    min-height: 6px;
}
QScrollBar:handle:vertical::pressed {
    background: #8F8F8F;
    border-radius: 3px;    
}
QScrollBar::handle:vertical {
    background: #717171;
    border-radius: 3px;
}  
QScrollBar::add-line:vertical {
    background: none;
    height: 0px;
    subcontrol-position: bottom;
    subcontrol-origin: margin;
} 
QScrollBar::sub-line:vertical {
    background: none;
    height: 0px;
    subcontrol-position: top;
    subcontrol-origin:margin;
}
QScrollBar:add-page:vertical {
    background: none;
}
QScrollBar:sub-page:vertical {
    background: none;
}


/* -------------------------------- QPlainTextEdit---------

---------------------------------------------------------- */
QPlainTextEdit[output=true]{
    font: 14px Segoe UI;
    color: #F5F5F5;
    background-color: #191919;
    selection-background-color: #4D4D4D;  
    border: 0px;
    padding-bottom: 3px;
}


/* ----------------------------------- QGroupBox ----------

---------------------------------------------------------- */
QGroupBox {
    font: 14px Segoe UI;
    font-weight: bold;
}



/* ------------------------------------- QFrame ----------

---------------------------------------------------------- */
QFrame[frameShape="4"][frameShadow="48"] {
    background-color: #D5D5D5;
    border: 1px solid #141414;
}

QFrame[dashboardFrame=true] {
    background-color: #202020;
}
QFrame[sideBarFrame=true]{
    background-color: #202020;
    border-radius: 1px;
}
QFrame[topBarFrame=true]{
    background-color: #202020;
}
QFrame[sideHeaderFrame=true]{
    background-color: #1C1C1C;
    border-radius: 1px;
}
QFrame[nutrientButtonFrame=true] {
    background-color:#191919;
    border: 1px solid #141414;
    border-radius: 3px;
}




/* --------------------------------------- QMenu ---------

---------------------------------------------------------- */

QMenu {
    font: 13px Segoe UI;
    color: #F5F5F5;
    background-color: #191919;
    selection-background-color: #444444;
}
QMenuBar {
    color: #F5F5F5;
    font: 13px Segoe UI;
    background-color: #191919;
    selection-background-color: #444444;
}
QMenuBar:item:selected {
    background-color: #444444;
}
QMenuBar:item:pressed {
    background-color: #333333;
}


/* --------------------------------------- QToolTip ---------

---------------------------------------------------------- */

QToolTip {
    color: #F5F5F5;
    font: 15px Segoe UI;
    background-color: black;
    border: 1px solid black;
    border-radius 2px;   
}

"""
              }

# Cheekily putting this in here for ease.
default_params = {
    "nutrientprocessing": {
        "elementNames": {
            "silicateName": "SILICATE",
            "phosphateName": "PHOSPHATE",
            "nitrateName": "NOx",
            "nitriteName": "NITRITE",
            "ammoniaName": "AMMONIA"
        },
        "processingpars": {
            "silicate": {
                "peakPeriod": 80,
                "washPeriod": 40,
                "windowSize": 37,
                "windowStart": 36,
                "driftCorrType": "Piecewise",
                "baseCorrType": "Piecewise",
                "carryoverCorr": True,
                "calibration": "Linear",
                "calerror": 0.2,
                "sigdigits": 2,
                "duplicateError": 0.2,
            },
            "phosphate": {
                "peakPeriod": 80,
                "washPeriod": 40,
                "windowSize": 29,
                "windowStart": 39,
                "driftCorrType": "Piecewise",
                "baseCorrType": "Piecewise",
                "carryoverCorr": True,
                "calibration": "Linear",
                "calerror": 0.02,
                "sigdigits": 3,
                "duplicateError": 0.02,
            },
            "nitrate": {
                "peakPeriod": 80,
                "washPeriod": 40,
                "windowSize": 22,
                "windowStart": 40,
                "driftCorrType": "Piecewise",
                "baseCorrType": "Piecewise",
                "carryoverCorr": True,
                "calibration": "Linear",
                "calerror": 0.02,
                "sigdigits": 3,
                "duplicateError": 0.6,
            },
            "nitrite": {
                "peakPeriod": 80,
                "washPeriod": 40,
                "windowSize": 29,
                "windowStart": 40,
                "driftCorrType": "Piecewise",
                "baseCorrType": "Piecewise",
                "carryoverCorr": True,
                "calibration": "Linear",
                "calerror": 0.02,
                "sigdigits": 3,
                "duplicateError": 0.02,
            },
            "ammonia": {
                "peakPeriod": 80,
                "washPeriod": 40,
                "windowSize": 28,
                "windowStart": 45,
                "driftCorrType": "Piecewise",
                "baseCorrType": "Piecewise",
                "carryoverCorr": True,
                "calibration": "Linear",
                "calerror": 0.02,
                "sigdigits": 3,
                "duplicateError": 0.02,
            }
        },
        "calibrants": {
            "maxnumber": "7",
            "cal0": "Cal 0",
            "cal1": "Cal 1",
            "cal2": "Cal 2",
            "cal3": "Cal 3",
            "cal4": "Cal 4",
            "cal5": "Cal 5",
            "cal6": "Cal 6"
        },
        "slkcolumnnames": {
            "sampleID": "Sample ID",
            "cupNumbers": "Cup Number",
            "cupTypes": "Cup Type",
            "dateTime": "Date Time Stamp"
        },
        "cupnames": {
            "primer": "PRIM",
            "recovery": "UNKNOWN",
            "drift": "DRIF",
            "baseline": "BASL",
            "calibrant": "CALB",
            "high": "HIGH",
            "low": "LOW ",
            "null": "NULL",
            "end": "END",
            "sample": "SAMP"
        },
        "qcsamplenames": {
            "rmns": "RMNS",
            "mdl": "MDL",
            "bqc": "BQC",
            "internalqc": "IntQC",
            "driftcheck": "Drift Sample Check",
            "underway": "UWY Sample"
        },
        "qcplotted":
            [
                {"formatname": "RMNS", "sampleid": "RMNS"},
                {"formatname": "MDL", "sampleid": "MDL"},
            ]

    },
    "analysisparams": {
        "seal": {
            "filePrefix": "",
            "runFormat": "RRR",
            "activated": False
        },
        "guildline": {
            "filePrefix": "",
            "runFormat": "RRR",
            "activated": False
        },
        "scripps": {
            "filePrefix": "",
            "runFormat": "RRR",
            "activated": False
        },
        "seasave": {
            "filePrefix": "",
            "runFormat": "RRR",
            "activated": False
        },
        "logsheet": {
            "filePrefix": "",
            "runFormat": "RRR",
            "activated": False
        }
    },
    "surveyparams": {
        "default": {
            "guildline": {
                "activated": False,
                "ctdsurvey": True,
                "decodesampleid": False,
                "surveyprefix": "",
                "decodedepfromid": False,
                "depformat": None,
                "usesampleid": False
            },
            "scripps": {
                "activated": False,
                "ctdsurvey": True,
                "decodesampleid": False,
                "surveyprefix": None,
                "decodedepfromid": False,
                "usesampleid": False
            },
            "seal": {
                "activated": False,
                "ctdsurvey": True,
                "decodesampleid": True,
                "surveyprefix": None,
                "decodedepfromid": True,
                "depformat": "DDBB",
                "usesampleid": False
            }
        }
    },
    "rosettedefault": 24
}
