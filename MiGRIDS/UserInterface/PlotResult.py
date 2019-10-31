from PyQt5 import QtWidgets, QtGui
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from matplotlib.figure import Figure
import matplotlib.pyplot as plt

#plot widget
class PlotResult(FigureCanvas):
    def __init__(self,parent, data, title = None):
        fig = Figure(figsize=(5, 6), dpi=100)

        self.axes = fig.add_subplot(111)
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        self.title = title
        self.figure = fig
        FigureCanvas.setSizePolicy(self,QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)

         #make plot
        self.makePlot(data)



    def makePlot(self, data):
        '''Plots all the x, y values in data on a single plot
        :param data is a dictionary with x, y for each key. Series labels are keys. '''
        ax = self.axes
        ax.clear()
        if data is not None:

            #data can have more than 1 series to display
            for k in data.keys():
                if (data[k]['x'] is not None) & (data[k]['y'] is not None):
                    ax.plot(data[k]['x'],data[k]['y'], label=k)

        ax.set_title(self.title)
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles,labels)
        #refresh the plot
        self.draw()
        return

