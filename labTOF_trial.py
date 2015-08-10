import numpy as np
import sys
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler

import Tkinter as Tk


#top = tk.Tk()
# Code to add widgets will go here...
#top.mainloop()

#########################################################
#function definitions:

#read in MS data
#store data in array
def read_data_files(data_path, filename, mass, intensity):
	#open filename (list of data files)
	file=open(data_path+filename,'r')
	#there is some extra formatting on the first line - delete this data
	header=file.readline()
	#read each row in the file
	for line in file:
		#read each row - store data in columns
		columns=line.split()
		mass.append(float(columns[0]))
		intensity.append(float(columns[1]))


#########################################################
#main:

#ask for data file

#read data file

#plot data file


#create the root widget
#the root widget is the parent window
root = Tk.Tk()
root.wm_title("matplotlib example")

#w = Tk.Label(root, text="Load file:", pady=10)
#fit the size of the window to the text
#w.pack()


#read data
data_path = '/Users/kyleuckert/Documents/Research/MS/Data/2015JUN29/'
filename = '2935_23.0.txt'
mass=[]
intensity=[]
read_data_files(data_path, filename, mass, intensity)

fig = plt.figure(figsize=(8,4), dpi=100)
ax = fig.add_subplot(111)
ax.plot(mass, intensity, color='k')
plt.xlim(0,250)

# a tk.DrawingArea
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.show()
canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

toolbar = NavigationToolbar2TkAgg( canvas, root )
toolbar.update()
canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

def on_key_event(event):
    print('you pressed %s'%event.key)
    key_press_handler(event, canvas, toolbar)

canvas.mpl_connect('key_press_event', on_key_event)

def _quit():
    root.quit()     # stops mainloop
    root.destroy()  # this is necessary on Windows to prevent
                    # Fatal Python Error: PyEval_RestoreThread: NULL tstate

#quit the program
button = Tk.Button(master=root, text='Quit', command=_quit)
button.pack(side=Tk.BOTTOM)

Tk.mainloop()
