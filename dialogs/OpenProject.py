from PyQt5.QtWidgets import (QPushButton, QLabel, QListWidget)
from time import sleep
import json
from dialogs.templates.DialogTemplate import hyproDialogTemplate


# Small GUI functionality for opening a project and loading it in as the active project
class openProject(hyproDialogTemplate):
    def __init__(self):
        super().__init__(200, 350, 'HyPro - Open Proect')
        
        self.selectedproject = ''

        self.init_ui()

        self.show()

    def init_ui(self):
        selectprojlabel = QLabel('Select an existing project:', self)

        self.selectprojbox = QListWidget(self)
        self.selectprojbox.setProperty('other', True)
        self.selectprojbox.doubleClicked.connect(self.selection)

        self.selectbutton = QPushButton('Select', self)
        self.selectbutton.clicked.connect(self.selection)

        cancelbutton = QPushButton('Cancel', self)
        cancelbutton.clicked.connect(self.cancel)

        projnames = []
        try:
            # Get list of current projects to populate list
            with open('C:/HyPro/hyprosettings.json', 'r') as f:
                self.params = json.load(f)

            for x in self.params['projects'].keys():
                self.selectprojbox.addItem(x)

        except Exception as e:
            print(e)

        self.grid_layout.addWidget(selectprojlabel, 0, 0, 1, 2)
        self.grid_layout.addWidget(self.selectprojbox, 1, 0, 1, 2)
        self.grid_layout.addWidget(self.selectbutton, 2, 0, 1, 1)
        self.grid_layout.addWidget(cancelbutton, 2, 1, 1, 1)

    def selection(self):
        try:
            self.selectedproject = self.selectprojbox.currentItem().text()

            self.params['activeproject'] = self.selectedproject

            with open('C:/HyPro/hyprosettings.json', 'w') as file:
                json.dump(self.params, file)

        except Exception as e:
            print(e)

        sleep(0.3)
        self.close()

    def cancel(self):
        self.close()
