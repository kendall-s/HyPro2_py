stylesheet = {'normal': """
/* -------------------------------- QMainWindow-----------

---------------------------------------------------------- */
QMainWindow[ProcessingMenu = true]{
    background-color: #ebeff2;
    border: 0px;
}


/* ----------------------------------- QLabel ------------

---------------------------------------------------------- */
QLabel {
    font: 14px;
}
QLabel[dashboardText=true]{
    color: #222222;
    font: 14px;
    font-weight: bold;  
}
QLabel[sideHeaderHeading=true] {   
    font: 22px;
    color: #ffffff;
}
QLabel[sideBarText=true] {
    font: 14px;
    color: #ffffff;
}


/* --------------------------------- QListWidget ---------

---------------------------------------------------------- */
QListWidget {
    font: 14px;
}


/* --------------------------------- QPushButton ---------

---------------------------------------------------------- */
QPushButton {
    font: 14px;
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


/* ---------------------------------- QComboBox ---------

---------------------------------------------------------- */
QComboBox {
    font: 14px;
}


/* ---------------------------------- QCheckBox ----------

---------------------------------------------------------- */
QCheckBox {
    font: 14px;
}
QCheckBox[survey_checkbox=true]:indicator {
    width: 50px;
    height: 50px;
}

QCheckBox[sideBarCheckbox=true] {
    font: 14px;
    color: #ffffff;
}


/* ---------------------------------- QTabWidget ---------

---------------------------------------------------------- */
QTabWidget QWidget {
    font: 14px;
}


/* --------------------------------- QLineEdit -----------

---------------------------------------------------------- */
QLineEdit {
    font: 14px;
}


/* --------------------------------- QListWidget ---------

---------------------------------------------------------- */
QListWidget {
    font: 14px;
}

/* --------------------------------- QTableWidget ---------

---------------------------------------------------------- */
QTableWidget {
    font: 14px;
}
QHeaderView {
    font: 14px;
}


/* -------------------------------- QPlainTextEdit---------

---------------------------------------------------------- */
QPlainTextEdit{
    font: 14px;
    border: 0px;
    padding-bottom: 3px;
}



/* ----------------------------------- QFrame ------------

---------------------------------------------------------- */
QFrame[dashboardFrame=true] {
    background-color: #f7faff;
}
QFrame[sideBarFrame=true]{
    background-color: #4e546c;
    border-radius: 1px;
}
QFrame[topBarFrame=true]{
    background-color: #ddeaff;
}
QFrame[sideHeaderFrame=true]{
    background-color: #555c78;
    border-radius: 1px;
}
            



/* --------------------------------- QScrollBar ---------

---------------------------------------------------------- */
QScrollBar:vertical {
    width: 6px;
    border: 0px solid #888888;
    background: white;
    border-radius: 3px;
    margin: 0px 0px 0px 0px;
}
QScrollBar:handle:vertical::pressed {
    background: #555c78;
    border-radius: 3px;    
}
QScrollBar::handle:vertical {
    background: #4e546c;
    min-height: 0px;
    border-radius: 3px;
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



"""

# ********************************************************************************************************************

#   Dark theme

# Note font color in dark theme is to be F5F5F5, white can be too harsh of a contrast and actually make dark mode
# not that nice to use. The very slight off white color is more pleasing on the eyes. Doesn't 'dazzle' as bad

# ********************************************************************************************************************

, 'dark' : """
/* --------------------------------- QTitleBar -----------

---------------------------------------------------------- */
QTitleBar {
    background-color: #000000;
}


/* --------------------------------- QMainWindow ---------

---------------------------------------------------------- */
QMainWindow {
    background-color: #202020;
}


/* ---------------------------------- QDialog ------------

---------------------------------------------------------- */
QDialog {
    background-color: #202020;
}


/* ----------------------------------- QLabel ------------

---------------------------------------------------------- */
QLabel {
    font: 14px;
    color: #F5F5F5;
}
QLabel[sideHeaderHeading=true] {   
    font: 22px;
    color: #F5F5F5;
}
QLabel[sideBarText=true] {
    font: 14px;
    color: #F5F5F5;
}



/* --------------------------------- QPushButton ---------

---------------------------------------------------------- */
QPushButton {
    font: 14px;
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


/* ---------------------------------- QComboBox ----------

---------------------------------------------------------- */
QComboBox {
    font: 14px;
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
    font: 14px;
    color: white;
}


/* --------------------------------- QTabWidget ----------

---------------------------------------------------------- */
QTabWidget QWidget {
    font: 14px;
    color: white;
    background-color: #191919;
    border: 1px #000000;
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
    font: 14px;
    color: white;
    background-color: #191919;
}
QLineEdit:hover {
    border: 2px solid #999999;
}
QLineEdit:focus {
    border: 1px solid #888888;
}


/* ---------------------------------- QListWidget -------

---------------------------------------------------------- */
QListWidget {
    font: 14px;
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
}
QScrollBar:handle:vertical::pressed {
    background: #888888;
    border-radius: 3px;    
}
QScrollBar::handle:vertical {
    background: #666666;
    min-height: 0px;
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
QPlainTextEdit{
    font: 14px;
    color: #F5F5F5;
    background-color: #191919;
    selection-background-color: #4D4D4D;  
    border: 0px;
    padding-bottom: 3px;
}



/* ------------------------------------- QFrame ----------

---------------------------------------------------------- */

QFrame[dashboardFrame=true] {
    background-color: #191919;
}
QFrame[sideBarFrame=true]{
    background-color: #191919;
    border-radius: 1px;
}
QFrame[topBarFrame=true]{
    background-color: #191919;
}
QFrame[sideHeaderFrame=true]{
    background-color: #1C1C1C;
    border-radius: 1px;
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

"""
}