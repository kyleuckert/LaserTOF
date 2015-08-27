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
		self.fig = Figure(figsize=(4,4), dpi=100)
		#fig = Figure(facecolor='white', edgecolor='white')
		self.fig.subplots_adjust(bottom=0.15, left=0.15)

		self.canvas = FigureCanvasTkAgg(self.fig, self)
		self.toolbar = NavigationToolbar2TkAgg(self.canvas, self)
		#canvas.get_tk_widget().pack(side=BOTTOM, fill=BOTH, expand=True) 
		
		#list containing time domain values
		self.time=[]
		#list containing mass domain values
		self.mass=[]
		#flag to indicate whether time or mass is displayed
		#time flag=0
		#mass flag=1
		self.time_mass_flag=0
		#flag to indicate MS or MSMS calibration
		#MS = 0
		#MSMS = 1
		self.MSMS_flag=-99
		#list containing intensity values
		self.intensity=[]
		#list containing calibration values. (0,0) is used as a default
		self.cal_time=[0.0]
		self.cal_mass=[0.0]
		#calibration point id
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
		#CHANGE all pack to grid layout
		self.pack(fill=BOTH, expand=1)

		menubar = Menu(self.parent)
		self.parent.config(menu=menubar)
		
		#contains file menu items
		fileMenu = Menu(menubar, tearoff=0)
		menubar.add_cascade(label="File", menu=fileMenu)
		fileMenu.add_command(label="Open", command=self.onOpen)
		fileMenu.add_command(label="Export File", command=self.onExport)
		fileMenu.add_command(label="Quit", command=self.quit_destroy)

		#contains calibration menu items
		#"self" is needed to access items later (to change state)
		#default state for save calibration is disabled
		#state is enabled once a file is loaded
		self.calMenu=Menu(menubar, tearoff=0)     
		menubar.add_cascade(label="Calibration", menu=self.calMenu)        
		self.MScalMenu=Menu(menubar, tearoff=0)
		self.calMenu.add_cascade(label="MS Calibration", menu=self.MScalMenu, state=DISABLED)
		self.MScalMenu.add_command(label="Start New Calibration", command=self.onCalStart)
		self.MScalMenu.add_command(label="Open Calibration File", command=self.onOpenCal)
		
		self.MSMScalMenu=Menu(menubar, tearoff=0)
		self.calMenu.add_cascade(label="MSMS Calibration", menu=self.MSMScalMenu, state=DISABLED)
		self.MSMScalMenu.add_command(label="Start New Calibration", command=self.onMSMSCalStart)
		self.MSMScalMenu.add_command(label="Open Calibration File", command=self.onMSMSOpenCal)

		#default state for save calibration is disabled
		#state is enabled once a calibration is defined
		self.calMenu.add_command(label="Save Calibration File", command=self.onSaveCal, state=DISABLED)


		#generate figure (no data at first)
		self.generate_figure([0,1], ' ')
		
		#create instance of the button widget
		#command specifies the method to be called
		quitButton = Button(self, text="Quit", command = self.quit_destroy)
		#quitButton.place(x=50, y=50)
		quitButton.pack(side=RIGHT, padx=5, pady=5)
		#quitButton.grid(row=5, column=5, padx=5)

		#convert to time domain
		timeButton = Button(self, text="Time Domain", command = self.time_domain)
		timeButton.pack(side=RIGHT, padx=5, pady=5)

		#convert to mass domain
		self.massButton = Button(self, text="Mass Domain", command = self.mass_domain, state=DISABLED)
		self.massButton.pack(side=RIGHT, padx=5, pady=5)

		#smooth spectrum
		self.smoothButton = Button(self, text="Smooth", command = self.smooth_data, state=DISABLED)
		self.smoothButton.pack(side=RIGHT, padx=5, pady=5)

		#label peaks in figure
		self.peakButton = Button(self, text="Label Peaks", command = self.label_peaks, state=DISABLED)
		self.peakButton.pack(side=RIGHT, padx=5, pady=5)

		#calibration
		#add calibration point
		self.calibrateButton = Button(self, text="Add Calibration Point", command = self.calibrate, state=DISABLED)
		self.calibrateButton.pack(side=LEFT, padx=5, pady=5)

		#finish calibration and convert to mass domain
		self.finishcalButton = Button(self, text="Finish Calibration", command = self.finish_calibrate, state=DISABLED)
		self.finishcalButton.pack(side=LEFT, padx=5, pady=5)
		

	#convert to mass domain
	#disabled until calibration is defined
	def mass_domain(self):
		self.time_mass_flag=1
		self.generate_figure([self.mass,self.intensity], 'mass (Da)')
	
	#convert to time domain	
	def time_domain(self):
		self.time_mass_flag=0
		#plot in micro seconds
		self.generate_figure([[1E6*x for x in self.time],self.intensity], 'time ($\mu$s)')
		
	#smooth data
	def smooth_data(self):
		#smooth self.time/mass/int variables - permanant
		#probably not a good idea
		#purpose of smoothing function: to display smoothed plot
		self.SmoothDialog(self.parent)
		#wait for dialog to close
		self.top.wait_window(self.top)
		smoothed_signal = scipy.signal.savgol_filter(self.intensity,self.window,self.poly)
		#convert from array to list
		self.intensity=smoothed_signal.tolist()
		#print 'intensity: ', len(self.intensity), type(self.intensity)
		if self.time_mass_flag == 1:
			#print 'mass: ', len(self.mass), type(self.mass)
			self.mass_domain()
		else:
			#print 'time: ', len(self.time), type(self.time)
			self.time_domain()

	#plot figure
	def generate_figure(self, data, xaxis_title):
		#clear figure
		plt.clf()
		ax = self.fig.add_subplot(111)
		#clear axis
		ax.cla()
		ax.plot(data[0],data[1])
		ax.set_xlabel(xaxis_title)
		ax.set_ylabel('intensity')
		self.canvas.show()
		self.canvas.get_tk_widget().pack(side=BOTTOM, fill=BOTH, expand=True)
		#self.can.grid(row=1, column=0, columnspan=6, rowspan=3, padx=5, sticky=E+W+S+N)

		self.toolbar.update()
		self.canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=True)

	#def delete_figure(self):
		#Canvas.delete("all")
		#.destroy()

	#open file
	def onOpen(self):
		#displays .txt files in browser window
		#only reads time domain data files
		ftypes = [('txt files', '*.txt')]
		dlg = tkFileDialog.Open(self, filetypes = ftypes)
		fl = dlg.show()

		if fl != '':
			data = self.readFile(fl)
			self.time=data[0]
			self.intensity=data[1]
			#plots datat in time domain
			self.time_domain()
			#self.peakButton.config(state=NORMAL)
			#allows for smoothing of data
			self.smoothButton.config(state=NORMAL)
			#allows for calibration
			self.calMenu.entryconfig("MS Calibration", state=NORMAL)
			self.calMenu.entryconfig("MSMS Calibration", state=NORMAL)

	#export data to txt file
	def onExport(self):
		#save header info (date/time, ask user for instrument)?
		#ask for save file name
		savefile = tkFileDialog.asksaveasfile(mode='wb', defaultextension=".txt")
		# asksaveasfile return `None` if dialog closed with "cancel".
		if savefile is None:
			return
		#export mass or time domain data depending on flag (what is plotted)
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
		savefile.close()

	#save calibration file
	def onSaveCal(self):
		#ask for save file name
		savefile = tkFileDialog.asksaveasfile(mode='wb', defaultextension=".txt")
		if savefile is None:
			return
		
		#write header information?
		#date/time, file name
		for i in range(len(self.cal_time)):
			savefile.write(str(self.cal_time[i]))
			savefile.write(' ')
			savefile.write(str(self.cal_mass[i]))
			#\r\n is the newline character for windows
			savefile.write('\r\n')
		savefile.close()
		
	#open previous MS (regular) calibration file
	def onOpenCal(self):
		#display .txt files in browser window
		ftypes = [('txt files', '*.txt')]
		dlg = tkFileDialog.Open(self, filetypes = ftypes)
		filename = dlg.show()

		if filename != '':
			#list with time calibration value
			calt_read=[]
			#list with mass calibration value
			calm_read=[]
			file=open(filename,'r')
			#header=file.readline()
			for line in file:
				#read each row - store data in columns
				temp = line.split(' ')
				calt_read.append(float(temp[0]))
				calm_read.append(float(temp[1].rstrip('/n')))
			#store values in calibration lists
			self.cal_time=calt_read
			self.cal_mass=calm_read
		#sets MSMS flag for finish_calibrate routine
		self.MSMS_flag=0
		#call finish_calibrate method to calibrate and plot data in mass domain
		self.finish_calibrate()

	#open previous MSMS calibration file
	def onMSMSOpenCal(self):
		#display .txt files in browser window
		ftypes = [('txt files', '*.txt')]
		dlg = tkFileDialog.Open(self, filetypes = ftypes)
		filename = dlg.show()

		if filename != '':
			#list with time calibration value
			calt_read=[]
			#list with mass calibration value
			calm_read=[]
			file=open(filename,'r')
			#header=file.readline()
			for line in file:
				#read each row - store data in columns
				temp = line.split(' ')
				calt_read.append(float(temp[0]))
				calm_read.append(float(temp[1].rstrip('/n')))
			#store values in calibration lists
			self.cal_time=calt_read
			self.cal_mass=calm_read
		#sets MSMS flag for finish_calibrate routine
		self.MSMS_flag=1
		#call finish_MSMScalibrate method to calibrate and plot data in mass domain
		self.finish_calibrate()

	#called when "Start New Calibration" is selected
	def onCalStart(self):
		#sets MSMS flag for finish_calibrate routine
		self.MSMS_flag=0
		#plot data in time domain (reset plot)
		self.time_domain()
		#set calibration button (add new, finish) to enabled state
		self.calibrateButton.config(state=NORMAL)
		self.finishcalButton.config(state=NORMAL)

	#called when "Start New Calibration" is selected in MSMS mode
	def onMSMSCalStart(self):
		#sets MSMS flag for finish_calibrate routine
		self.MSMS_flag=1
		#plot data in time domain (reset plot)
		self.time_domain()
		#set calibration button (add new, finish) to enabled state
		self.calibrateButton.config(state=NORMAL)
		self.finishcalButton.config(state=NORMAL)

	#called when click is made in plotting environment during calibration
	def on_click(self, event):	
		temp_len=len(self.cal_time)
		#print 'temp len: ', temp_len
	
		#when the click is made within the plotting window
		if event.inaxes is not None:
			#print 'clicked: ', event.xdata, event.ydata
			self.cal_time.append(event.xdata*1E-6)
			#sets up dialog box for user to enter mass value
			self.MassDialog(self.parent)

		else:
			print 'Clicked ouside axes bounds but inside plot window'		
		#disconnect from calibration click event when a new calibration value is set
		if len(self.cal_time) > temp_len:
			self.canvas.mpl_disconnect(self.cid)

	#called during calibration
	#asks user for mass value associated with time value selected
	def MassDialog(self, parent):
		top = self.top = Toplevel(self.parent)
		Label(top, text="Actual Mass Value:").pack()
		
		self.e=Entry(top)
		self.e.pack(padx=5)
		#calls DialogOK to set mass value to input		
		b=Button(top, text="OK", command=self.DialogOK)
		b.pack(pady=5)
	
	#called when Smooth button is pressed
	#asks user for smooth input data
	def SmoothDialog(self, parent):
		top = self.top = Toplevel(self.parent)
		#window length for smoothing function
		#must be greater than poly value, positive, odd (51)
		Label(top, text="Window Length:").grid(row=0, column=0, sticky=W, padx=5, pady=5)
		self.w=Entry(top)
		self.w.grid(row=0, column=1, padx=5, pady=5)

		#polynomial order
		#must be less than window length (3)
		Label(top, text="Polynomial Order:").grid(row=1, column=0, sticky=W, padx=5, pady=5)
		self.p=Entry(top)
		self.p.grid(row=1, column=1, padx=5, pady=5)
		
		#calls DialogSmoothOK to set these values
		b=Button(top, text="OK", command=self.DialogSmoothOK)
		b.grid(row=2, column=1, padx=5, pady=5)
	
	#called from smooth dialog box within smooth routine
	def DialogSmoothOK(self):
		#sets user-defined window length
		self.window=float(self.w.get())
		#sets user-defined polynomail order
		self.poly=float(self.p.get())
		self.top.destroy()
		
	#called from mass dialog box within calibration routine
	def DialogOK(self):
		#sets user-defined mass calibration value to mass cal list
		self.cal_mass.append(float(self.e.get()))
		#closes dialog box
		self.top.destroy()
	
	#called from calibration routine
	#stores user-selected point in cid	
	def calibrate(self):
		#user selects point
		self.cid=self.canvas.mpl_connect('button_press_event', self.on_click)

	#called from calibration routine after "finish" button is pressed
	def finish_calibrate(self):
		#disables buttons until "start new calibration" is selected
		self.calibrateButton.config(state=DISABLED)
		self.finishcalButton.config(state=DISABLED)
		#allows plotting in mass domain
		self.massButton.config(state=NORMAL)
		#allows user to save calibration file
		self.calMenu.entryconfig("Save Calibration File", state=NORMAL)
		
		#if MS mode (regular)
		if self.MSMS_flag==0:
			#fit quadratic fuction through cal points
			popt, pcov = curve_fit(func_quad, self.cal_time, self.cal_mass)
			#convert time to mass
			self.mass[:] = [popt[0]*(x**2)*(1E10) + popt[1] for x in self.time]
			#plots figure in mass domain
			self.mass_domain()

		#if MSMS mode
		elif self.MSMS_flag==1:
			#fit quadratic fuction through cal points
			popt, pcov = curve_fit(func_lin, self.cal_time, self.cal_mass)
			#convert time to mass
			self.mass[:] = [popt[0]*x*(1E10) + popt[1] for x in self.time]
			#plots figure in mass domain
			self.mass_domain()


	#function for file input
	def readFile(self, filename):
		file=open(filename,'r')
		#there is some extra formatting on the first line - delete this data
		header=file.readline()
		header=file.readline()
		header=file.readline()
		header=file.readline()
		header=file.readline()
		#read each row in the file
		#list for temporary time data
		time=[]
		#list for temporary intensity data
		intensity=[]
		for line in file:
			#check file format:
			if ',' in line:
				#read each row - store data in columns
				temp = line.split(',')
				time.append(float(temp[0]))
				intensity.append(float(temp[1].rstrip('/n')))
			if '\t' in line:
				temp = line.split('\t')
				time.append(float(temp[0]))
				intensity.append(float(temp[1].rstrip('/n')))

		data=[time, intensity]
		return data

	#future function to label peaks on figure in order to save figure as an image file with labels
	def label_peaks(self):
		#something goes here eventually
		print 'this button does not work'
		
	def quit_destroy(self):
		self.parent.destroy()
		self.parent.quit()

#quadratic function for time to mass conversion
def func_quad(x, a, b):
	return (1E10)*a*(x**2)+b

def func_lin(x, a, b):
	return (1E10)*a*x+b


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