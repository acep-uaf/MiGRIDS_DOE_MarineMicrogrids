from PyQt5 import QtWidgets, QtGui
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from matplotlib.figure import Figure
import matplotlib.pyplot as plt

#plot widget
class PlotCanvas(FigureCanvas):
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
        self.mpl_connect('pick_event',self.onpick)


    def makePlot(self, data):
        '''Plots all the x, y values in data on a single plot
        :param data is a dictionary with x, y for each key. Series labels are keys. '''
        ax = self.axes
        ax.clear()
        if data is not None:

            #data can have more than 1 series to display
            self.lines = {}
            for k in data.keys():
                if (data[k]['x'] is not None) & (data[k]['y'] is not None):
                    if(len(data[k]['x'])) > 1:
                         self.lines[k] = ax.plot(data[k]['x'],data[k]['y'], label=k,c=data[k]['color'])
                    else:
                        self.lines[k] = ax.plot(data[k]['x'], data[k]['y'], 'o',label=k, c=data[k]['color'])


        ax.set_title(self.title)
        handles, labels = ax.get_legend_handles_labels()

        leg = ax.legend(handles,labels,loc='upper left', fancybox=True, shadow=False)
        [l.set_picker(10) for l in leg.get_lines()] #tolerance around legend items
        leg.get_frame().set_alpha(0.4)
        #refresh the plot
        self.draw()
        return

    def onpick(self,event):
        legline = event.artist
        origline = self.lines[legline._label][0]
        vis = not origline.get_visible() #swap the visibility
        origline.set_visible(vis)
        if vis:
            legline.set_alpha(1.0)
        else:
            legline.set_alpha(0.2) #dim if not displayed in plot
        self.draw()
