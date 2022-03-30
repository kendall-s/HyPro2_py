from PyQt5.QtWidgets import (QPushButton, QLabel, QComboBox, QListWidget)
from dialogs.templates.DialogTemplate import hyproDialogTemplate

# TODO: Needs finishing is currently only the starting GUI but possibly superseded by the params/params plot
"""
Might need removing, could be superseded by the param/param plot window
"""


class producePlotsDialog(hyproDialogTemplate):
    def __init__(self):
        super().__init__(380, 400, 'HyPro Plot')

        self.init_ui()

        self.show()

    def init_ui(self):
        plottypeslist = ['Waterfall']

        plottypelabel = QLabel('Plot type: ', self)

        self.plottype = QComboBox()
        self.plottype.addItems(plottypeslist)
        self.plottype.setFixedHeight(25)
        # self.plottype.activated.connect(self.populatefileslist)

        datafileslabel = QLabel('Select data to plot: ', self)

        self.datalist = QListWidget()
        # self.datalist.itemSelectionChanged.connect(self.itemselected)

        deploymentslabel = QLabel('Select deployments:')

        self.deploymentslist = QListWidget()
        # self.deploymentslist.itemSelectionChanged.connect()

        okbut = QPushButton('Produce Plots', self)
        okbut.setFixedWidth(90)

        cancelbut = QPushButton('Cancel', self)
        cancelbut.clicked.connect(self.cancel)

        self.grid_layout.addWidget(plottypelabel, 0, 0)
        self.grid_layout.addWidget(self.plottype, 0, 1, 1, 4)

        self.grid_layout.addWidget(datafileslabel, 1, 0)
        self.grid_layout.addWidget(self.datalist, 1, 1, 1, 4)

        self.grid_layout.addWidget(deploymentslabel, 2, 0)
        self.grid_layout.addWidget(self.deploymentslist, 2, 1, 2, 2)

        self.grid_layout.addWidget(okbut, 5, 1)
        self.grid_layout.addWidget(cancelbut, 5, 2)

    def cancel(self):
        self.close()
