#http://zetcode.com/gui/tkinter/dialogs/
#http://pythonprogramming.net/how-to-embed-matplotlib-graph-tkinter-gui/

#canvas layout
#http://stackoverflow.com/questions/20149483/python-canvas-and-grid-tkinter

#to do:
#add message display status/errors
#clean source
##natcdf (export using matlab function)
#label peaks
#create executable
#install on lab computer

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backend_bases import MouseEvent
from matplotlib.figure import Figure

import numpy as np

import scipy as scipy
from scipy.optimize import curve_fit
from scipy import signal

from Tkinter import *
from ttk import *
import tkFileDialog

#import labTOF_plot
import sys


class labTOF(Frame):

	#define parent window
	def __init__(self, parent):
		#from Tkinter frame:
		#Frame.__init__(self, parent, background="white")   
		#from ttk frame:
		Frame.__init__(self, parent)

		#save a reference to the parent widget
		self.parent = parent

		#delegate the creation of the user interface to the initUI() method
		#self.parent.title("Lab TOF")
		#self.pack(fill=BOTH, expand=1)
		#self.data=[[1,2,3,4,5,6,7,8],[5,6,1,3,8,9,3,5]]
		self.fig = Figure(figsize=(4,4), dpi=100)
		self.fig.subplots_adjust(bottom=0.15, left=0.15)
		#fig.clf()
		#fig = Figure(facecolor='white', edgecolor='white')
		#self.ax = self.fig.add_subplot(111)
		#plt.clf()
		#self.ax.plot(self.data[0],self.data[1])

		self.canvas = FigureCanvasTkAgg(self.fig, self)
		self.toolbar = NavigationToolbar2TkAgg(self.canvas, self)
		#canvas.show()
		#canvas.get_tk_widget().pack(side=BOTTOM, fill=BOTH, expand=True) 
		self.time=[]
		self.mass=[]
		#time flag=0
		#mass flag=1
		self.time_mass_flag=0
		self.intensity=[]
		self.cal_time=[0.0]
		self.cal_mass=[0.0]
		self.cid=-99
		self.initUI()
        
        
	#container for other widgets
	def initUI(self):
		#set the title of the window using the title() method
		self.parent.title("Lab TOF")
		
		#apply a theme to widget
		self.style = Style()
		self.style.theme_use('default')
		
		#the Frame widget (accessed via the delf attribute) in the root window
		#it is expanded in both directions
		self.pack(fill=BOTH, expand=1)

		menubar = Menu(self.parent)
		self.parent.config(menu=menubar)
		
		fileMenu = Menu(menubar)
		fileMenu.add_command(label="Open", command=self.onOpen)
		fileMenu.add_command(label="Export File", command=self.onExport)
		fileMenu.add_command(label="Quit", command=self.quit)
		menubar.add_cascade(label="File", menu=fileMenu)

		self.calMenu=Menu(menubar)     
		self.calMenu.add_command(label="Start New Calibration", command=self.onCalStart)
		self.calMenu.add_command(label="Open Calibration File", command=self.onOpenCal)
		self.calMenu.add_command(label="Save Calibration File", command=self.onSaveCal, state=DISABLED)
		menubar.add_cascade(label="Calibration", menu=self.calMenu)        

		
		#self.columnconfigure(1, weight=1)
		#self.columnconfigure(3, pad=7)
		#self.rowconfigure(3, weight=1)
		#self.rowconfigure(5, pad=7)

		self.generate_figure([0,1], ' ')
		
		#create instance of the button widget
		#command specifies the method to be called
		quitButton = Button(self, text="Quit", command = self.quit)
		#quitButton.place(x=50, y=50)
		quitButton.pack(side=RIGHT, padx=5, pady=5)
		#quitButton.grid(row=5, column=5, padx=5)

		timeButton = Button(self, text="Time Domain", command = self.time_domain)
		#convertButton.grid(row=5, column=4, padx=5)
		timeButton.pack(side=RIGHT, padx=5, pady=5)

		self.massButton = Button(self, text="Mass Domain", command = self.mass_domain, state=DISABLED)
		self.massButton.pack(side=RIGHT, padx=5, pady=5)

		self.smoothButton = Button(self, text="Smooth", command = self.smooth_data, state=DISABLED)
		self.smoothButton.pack(side=RIGHT, padx=5, pady=5)

		self.peakButton = Button(self, text="Label Peaks", command = self.label_peaks, state=DISABLED)
		self.peakButton.pack(side=RIGHT, padx=5, pady=5)

		self.calibrateButton = Button(self, text="Add Calibration Point", command = self.calibrate, state=DISABLED)
		self.calibrateButton.pack(side=LEFT, padx=5, pady=5)

		self.finishcalButton = Button(self, text="Finish Calibration", command = self.finish_calibrate, state=DISABLED)
		self.finishcalButton.pack(side=LEFT, padx=5, pady=5)
		#self.entrytext=StringVar()
		#self.xaxisText = Entry(textvariable=self.entrytext)
		#self.xaxisText.pack(side=RIGHT, padx=5, pady=5)

		#xaxisLabel = Label(self, text="x range")
		#xaxisLabel.pack(side=RIGHT, padx=5, pady=5)
		

	def mass_domain(self):
		self.time_mass_flag=1
		self.generate_figure([self.mass,self.intensity], 'mass (Da)')
		
	def time_domain(self):
		self.time_mass_flag=0
		self.generate_figure([[1E6*x for x in self.time],self.intensity], 'time ($\mu$s)')
		#self.generate_figure([self.time,self.intensity], 'time ($\mu$s)')
		
	def smooth_data(self):
		#smooth self.time/mass/int variables - permanant
		#probably not a good idea
		#purpose of smoothing function: to display smoothed plot
		self.SmoothDialog(self.parent)
		#wait for dialog to close
		self.top.wait_window(self.top)
		smoothed_signal = scipy.signal.savgol_filter(self.intensity,self.window,self.poly)
		#self.intensity=smoothed_signal.T
		#self.intensity=self.intensity.tolist()
		#self.mass=np.array(self.mass)
		#self.time=np.array(self.time)
		#print 'smoothed: ', len(smoothed_signal), type(smoothed_signal), type(smoothed_signal.tolist())
		self.intensity=smoothed_signal.tolist()
		#print 'intensity: ', len(self.intensity), type(self.intensity)
		if self.time_mass_flag == 1:
			#print 'mass: ', len(self.mass), type(self.mass)
			self.mass_domain()
		else:
			#print 'time: ', len(self.time), type(self.time)
			self.time_domain()


	def generate_figure(self, data, xaxis_title):
		#if i!=0:
			#fig.clf()
			#canvas.get_tk_widget().delete("all")
		#fig = Figure(figsize=(4,4), dpi=100)
		#fig.clf()
		#fig = Figure(facecolor='white', edgecolor='white')
		plt.clf()
		ax = self.fig.add_subplot(111)
		ax.cla()
		ax.plot(data[0],data[1])
		ax.set_xlabel(xaxis_title)
		ax.set_ylabel('intensity')
		#self.canvas.get_tk_widget().delete("all")
		#self.canvas = FigureCanvasTkAgg(self.fig, self)
		#self.canvas._tkcanvas.delete()
		self.canvas.show()
		self.canvas.get_tk_widget().pack(side=BOTTOM, fill=BOTH, expand=True)
		#self.can=Canvas(self.root, width=500, height=250)
		#self.can.grid(row=1, column=0, columnspan=6, rowspan=3, padx=5, sticky=E+W+S+N)
		#self.can(f)

		self.toolbar.update()
		self.canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=True)

	#def delete_figure(self):
		#Canvas.delete("all")
		#.destroy()


	def onOpen(self):

		ftypes = [('txt files', '*.txt')]
		dlg = tkFileDialog.Open(self, filetypes = ftypes)
		fl = dlg.show()

		if fl != '':
			data = self.readFile(fl)
			#self.delete_figure()
			#self.fig.clf()
			self.time=data[0]
			#self.mass=map(lambda x: 1.742E12*(x ** 2), self.time)
			self.intensity=data[1]
			self.time_domain()
			#self.peakButton.config(state=NORMAL)
			self.smoothButton.config(state=NORMAL)
			#self.generate_figure([self.time, self.intensity], 'time')
			#self.txt.insert(END, data)

	def onExport(self):
		savefile = tkFileDialog.asksaveasfile(mode='wb', defaultextension=".txt")
		# asksaveasfile return `None` if dialog closed with "cancel".
		if savefile is None:
			return
		if self.time_mass_flag == 0:
			x=self.time
		else:
			x=self.mass
		y=self.intensity
		
		for i in range(len(x)):
			savefile.write(str(x[i]))
			savefile.write(' ')
			savefile.write(str(y[i]))
			savefile.write('\n')
#		text2save = str(self.intensity)
#		savefile.write(text2save)
		savefile.close()

	def onSaveCal(self):
		savefile = tkFileDialog.asksaveasfile(mode='wb', defaultextension=".txt")
		if savefile is None:
			return

		for i in range(len(self.cal_time)):
			savefile.write(str(self.cal_time[i]))
			savefile.write(' ')
			savefile.write(str(self.cal_mass[i]))
			savefile.write('\n')
#		text2save = str(self.intensity)
#		savefile.write(text2save)
		savefile.close()
		
	def onOpenCal(self):
		ftypes = [('txt files', '*.txt')]
		dlg = tkFileDialog.Open(self, filetypes = ftypes)
		filename = dlg.show()

		if filename != '':
			calt_read=[]
			calm_read=[]
			file=open(filename,'r')
			#header=file.readline()
			for line in file:
				#read each row - store data in columns
				temp = line.split(' ')
				#print temp
				calt_read.append(float(temp[0]))
				calm_read.append(float(temp[1].rstrip('/n')))
			self.cal_time=calt_read
			self.cal_mass=calm_read
		self.finish_calibrate()

	def onCalStart(self):
		self.time_domain()
		self.calibrateButton.config(state=NORMAL)
		self.finishcalButton.config(state=NORMAL)

	def on_click(self, event):	
		temp_len=len(self.cal_time)
		#print 'temp len: ', temp_len
	
		if event.inaxes is not None:
			#print 'clicked: ', event.xdata, event.ydata
			#calibration=[event.xdata, event.ydata]
			#return calibration
			self.cal_time.append(event.xdata*1E-6)
			self.MassDialog(self.parent)

		else:
			print 'Clicked ouside axes bounds but inside plot window'		
		if len(self.cal_time) > temp_len:
			self.canvas.mpl_disconnect(self.cid)
		#print 'len cal: ', len(self.calx)

	def MassDialog(self, parent):
		top = self.top = Toplevel(self.parent)
		Label(top, text="Actual Mass Value:").pack()
		
		self.e=Entry(top)
		self.e.pack(padx=5)
		
		b=Button(top, text="OK", command=self.DialogOK)
		b.pack(pady=5)
	
	def SmoothDialog(self, parent):
		top = self.top = Toplevel(self.parent)
		Label(top, text="Window Length:").grid(row=0, column=0, sticky=W, padx=5, pady=5)
		self.w=Entry(top)
		self.w.grid(row=0, column=1, padx=5, pady=5)

		Label(top, text="Polynomial Order:").grid(row=1, column=0, sticky=W, padx=5, pady=5)
		self.p=Entry(top)
		self.p.grid(row=1, column=1, padx=5, pady=5)
		
		b=Button(top, text="OK", command=self.DialogSmoothOK)
		b.grid(row=2, column=1, padx=5, pady=5)
		
	def DialogSmoothOK(self):
		self.window=float(self.w.get())
		self.poly=float(self.p.get())
		self.top.destroy()
		
	def DialogOK(self):
		self.cal_mass.append(float(self.e.get()))
		self.top.destroy()
		
	def calibrate(self):
		#user selects point
		self.cid=self.canvas.mpl_connect('button_press_event', self.on_click)

	
	def finish_calibrate(self):
		self.calibrateButton.config(state=DISABLED)
		self.finishcalButton.config(state=DISABLED)
		self.massButton.config(state=NORMAL)
		self.calMenu.entryconfig("Save Calibration File", state=NORMAL)
		
		#fit line through cal points
		popt, pcov = curve_fit(func, self.cal_time, self.cal_mass)
		#convert time to mass
		#self.mass=map(lambda x: (popt[0]*(x ** 2))+popt[1], self.time)
		self.mass[:] = [popt[0]*(x**2)*(1E10) + popt[1] for x in self.time]
		self.mass_domain()

	def readFile(self, filename):

		#f = open(filename, "r")
		#text = f.read()
		file=open(filename,'r')
		#there is some extra formatting on the first line - delete this data
		header=file.readline()
		header=file.readline()
		header=file.readline()
		header=file.readline()
		header=file.readline()
		#read each row in the file
		time=[]
		intensity=[]
		for line in file:
			#check file format:
			if ',' in line:
				#read each row - store data in columns
				#columns=line.split()
				#mass.append(float(columns[0]))
				#intensity.append(float(columns[1]))
				temp = line.split(',')
				time.append(float(temp[0]))
				intensity.append(float(temp[1].rstrip('/n')))
			if '\t' in line:
				temp = line.split('\t')
				time.append(float(temp[0]))
				intensity.append(float(temp[1].rstrip('/n')))

		data=[time, intensity]
		return data

	def label_peaks(self):
		#something goes here eventually
		print 'this button does not work'


def func(x, a, b):
	return (1E10)*a*(x**2)+b



def main():

	#the root window is created
	root = Tk()
	
	#The geometry() method sets a size for the window and positions it on the screen.
	#The first two parameters are width and height of the window.
	#The last two parameters are x and y screen coordinates. 
	root.geometry("900x500+200+50")
	
	#create the instance of the application class
	app = labTOF(root)
	
	#enter the main loop
	root.mainloop()  


if __name__ == '__main__':
	main()  