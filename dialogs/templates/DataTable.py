import io
import csv
from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import QSortFilterProxyModel, QEvent

class Datatable(QTableWidget):
    def __init__(self, data):
        super().__init__()
        self._data = data

        self.installEventFilter(self)

        # Set the row and column count
        self.setRowCount(self.row_count())
        self.setColumnCount(self.column_count())

        self.add_data(data)

    def add_data(self, data):
        # Add the data into the table
        for row, x in enumerate(data):
            for col, item in enumerate(x):
                try:
                    # Pretty rough way of rounding the values, should implement something slightly better
                    self.setItem(row, col, QTableWidgetItem(str(round(item, 3))))
                except TypeError:
                    self.setItem(row, col, QTableWidgetItem(str(item)))

    def update_data(self, data):
        self.setRowCount(len(data))
        self.setColumnCount(len(data[0]))

        # Add the data into the table
        for row, x in enumerate(data):
            for col, item in enumerate(x):
                try:
                    # Pretty rough way of rounding the values, should implement something slightly better
                    self.setItem(row, col, QTableWidgetItem(str(round(item, 3))))
                except TypeError:
                    self.setItem(row, col, QTableWidgetItem(str(item)))

    def row_count(self):
        # The length of the outer list.
        return len(self._data)

    def column_count(self):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0])

    def eventFilter(self, source, event):
        """
        Event filter to capture the copy event and add the select fields to the clipboard in tab delimited format
        """
        if (event.type() == QEvent.KeyPress and
                event.matches(QKeySequence.Copy)):
            self.copy_selection()
            return True
        return super(QTableWidget, self).eventFilter(source, event)


    def copy_selection(self, copy_headers=False, header=False):
        """
        Provides functionality for copying data from the table
        """
        selection = self.selectedIndexes()
        if selection:
            rows = sorted(index.row() for index in selection)
            columns = sorted(index.column() for index in selection)
            rowcount = rows[-1] - rows[0] + 1
            colcount = columns[-1] - columns[0] + 1
            table = [[''] * colcount for _ in range(rowcount)]
            for index in selection:
                row = index.row() - rows[0]
                column = index.column() - columns[0]
                table[row][column] = index.data()
            stream = io.StringIO()
            if copy_headers:
                left_most_col = min(columns)
                right_most_col = max(columns)
                csv.writer(stream, delimiter='\t').writerow(header[left_most_col: right_most_col+1])
            csv.writer(stream, delimiter='\t').writerows(table)
            QApplication.clipboard().setText(stream.getvalue())