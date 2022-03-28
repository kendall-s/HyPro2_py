import pyqtgraph as pg
from PyQt5 import QtGui
from PyQt5.QtCore import QPointF, QRectF

"""
Provides the wrapper for the pyqt graph which is used to draw the nutrient peaks. This is customised and optimised such
that the peak windows are drawn as one continuous line, but where the windows don't exist the line width goes to zero.
"""


class TracePlotter(pg.GraphicsObject):
    """
    This is a pyqtgraph implementation of the trace plot for nutrient data. This was built to replace
    the matplotlib version, which is not very performant.
    The pyqt version is much more performant and been tested with 10000 peak windows
    """

    def __init__(self, time_values, ad_values, flag_values):
        pg.GraphicsObject.__init__(self)

        pg.setConfigOptions(antialias=True)

        self.time_values = time_values
        self.ad_values = ad_values
        self.flag_values = flag_values
        self.width = 2
        self.FLAG_COLORS = {1: '#68C968', 2: '#45D4E8', 3: '#C92724', 4: '#3CB6C9', 5: '#C92724', 6: '#DC9530',
                            91: '#9CCDD6', 92: '#F442D9', 8: '#3CB6C9'}

        self.generatePicture()

    def generatePicture(self):
        """
        Create the lines for the plot. Updates the pen for each peak depending on the flag value
        :return:
        """
        self.picture = QtGui.QPicture()
        p = QtGui.QPainter(self.picture)
        p.setRenderHint(QtGui.QPainter.Antialiasing)

        for i, time_vals in enumerate(self.time_values):
            if i == 0:
                p.setPen(pg.mkPen(color=self.FLAG_COLORS[self.flag_values[i]], width=4))

            for sm_i, point in enumerate(self.ad_values[i]):
                if sm_i > 0:
                    p.drawLine(QPointF(self.time_values[i][sm_i - 1], self.ad_values[i][sm_i - 1]),
                               QPointF(self.time_values[i][sm_i], self.ad_values[i][sm_i]))

                p.setPen(pg.mkPen(color=self.FLAG_COLORS[self.flag_values[i]], width=4))

            p.setPen(pg.mkPen(width=0))

    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QRectF(self.picture.boundingRect())
