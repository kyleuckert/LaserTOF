import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backend_bases import MouseEvent
from matplotlib.figure import Figure

#not sure what this package is/was for
#Tim will need to download this package if it is necessary
#from mpldatacursor import datacursor

import numpy as np

import scipy as scipy
from scipy.optimize import curve_fit
from scipy import signal

from Tkinter import *
from ttk import *
import tkFileDialog

#import labTOF_plot
import sys

import warnings

import read_lecroy_binary

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
		self.fig = Figure(figsize=(12,8), dpi=100)
		#fig = Figure(facecolor='white', edgecolor='white')
		self.fig.subplots_adjust(bottom=0.15, left=0.13, right=0.95, top=0.95)

		self.canvas = FigureCanvasTkAgg(self.fig, self)
		self.toolbar = NavigationToolbar2TkAgg(self.canvas, self)
		self.toolbar.pack(side=TOP)
		#canvas.get_tk_widget().pack(side=BOTTOM, fill=BOTH, expand=True) 

		#frame for buttons (at bottom)
		#buttons are arranged on grid, not pack
		self.frame_button = Frame(self)
		self.frame_button.pack(side = 'bottom', fill=BOTH, expand=1)
		
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
		#list containing calibration values
		self.cal_time=[]
		self.cal_mass=[]
		self.label_mass=[]
		self.label_time=[]
		self.label_intensity=[]
		self.label_size = float(10)
		self.label_format = "%.0f"
		self.digits_after = 0
		self.label_offset = 0.0
		#calibration point id
		self.cid=-99
		self.initUI()
		#zero mass corresponds to ~40% of parent mass time
		self.MSMS_zero_time=0.40838#0.4150#0.4082

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
		fileMenu.add_command(label="Export Data (ASCII file)", command=self.onExport)
		fileMenu.add_command(label="Quit", command=self.quit_destroy)

		#contains calibration menu items
		#"self" is needed to access items later (to change state)
		#default state for save calibration is disabled
		#state is enabled once a file is loaded
		self.calMenu=Menu(menubar, tearoff=0)     
		menubar.add_cascade(label="Calibration", menu=self.calMenu)        
		self.MScalMenu=Menu(menubar, tearoff=0)
		self.calMenu.add_cascade(label="MS Calibration", menu=self.MScalMenu, state=DISABLED)
		self.MScalMenu.add_command(label="Start New Calibration: include (0,0)", command=self.onCalStartInclude)
		self.MScalMenu.add_command(label="Start New Calibration: exclude (0,0)", command=self.onCalStartExclude)
		self.MScalMenu.add_command(label="Open Calibration File", command=self.onOpenCal)
		
		self.MSMScalMenu=Menu(menubar, tearoff=0)
		self.calMenu.add_cascade(label="MSMS Calibration", menu=self.MSMScalMenu, state=DISABLED)
		self.MSMScalMenu.add_command(label="Start New Calibration", command=self.onMSMSCalStart)
		self.MSMScalMenu.add_command(label="Open Calibration File", command=self.onMSMSOpenCal)

		#default state for save calibration is disabled
		#state is enabled once a calibration is defined
		self.calMenu.add_command(label="Save Calibration File", command=self.onSaveCal, state=DISABLED)


		#generate figure (no data at first)
		self.generate_figure([0,1], [[],[]], ' ')


		#calibration
		Label(self.frame_button, text="Calibration").grid(row=0, column=0, padx=5, pady=5, sticky=W)		
		#create instance of the button widget
		#command specifies the method to be called
		#identify parent peak in MSMS
		self.parentButton = Button(self.frame_button, text="Identify Parent Peak", command = self.calibrate_parent, state=DISABLED)
		#self.parentButton.pack(side=LEFT, padx=5, pady=5)
		self.parentButton.grid(row=0, column=1, padx=5, pady=5, sticky=W)

		#identify half-parent peak in MSMS
		self.halfparentButton = Button(self.frame_button, text="Identify Half-Parent Peak", command = self.calibrate_halfparent, state=DISABLED)
		#self.parentButton.pack(side=LEFT, padx=5, pady=5)
		self.halfparentButton.grid(row=0, column=2, padx=5, pady=5, sticky=W)
		
		#add calibration point
		self.calibrateButton = Button(self.frame_button, text="Add Calibration Point", command = self.calibrate, state=DISABLED)
		#self.calibrateButton.pack(side=LEFT, padx=5, pady=5)
		self.calibrateButton.grid(row=0, column=3, padx=5, pady=5, sticky=W)

		#set MSMS calibration constant MSMS
		self.constantButton = Button(self.frame_button, text="Set MSMS Constant", command = self.calibration_constant, state=DISABLED)
		#self.parentButton.pack(side=LEFT, padx=5, pady=5)
		self.constantButton.grid(row=0, column=4, padx=5, pady=5, sticky=W)

		#finish calibration and convert to mass domain
		self.finishcalButton = Button(self.frame_button, text="Finish Calibration", command = self.finish_calibrate, state=DISABLED)
		#self.finishcalButton.pack(side=LEFT, padx=5, pady=5)
		self.finishcalButton.grid(row=0, column=5, padx=5, pady=5, sticky=W)


		Label(self.frame_button, text="Label Spectrum").grid(row=1, column=0, padx=5, pady=5, sticky=W)

		#label peaks in figure
		self.labelButton = Button(self.frame_button, text="Label Peak", command = self.label_peaks, state=DISABLED)
		#self.labelButton.pack(side=RIGHT, padx=5, pady=5)
		self.labelButton.grid(row=1, column=1, padx=5, pady=5, sticky=W)

		self.deletelabelButton = Button(self.frame_button, text="Remove Labels", command = self.delete_labels, state=DISABLED)
		#self.deletelabelButton.pack(side=RIGHT, padx=5, pady=5)
		self.deletelabelButton.grid(row=1, column=2, padx=5, pady=5, sticky=W)

		self.formatelabelButton = Button(self.frame_button, text="Format Label", command = self.format_labels)
		self.formatelabelButton.grid(row=1, column=3, padx=5, pady=5, sticky=W)


		Label(self.frame_button, text="Smooth Spectrum").grid(row=2, column=0, padx=5, pady=5, sticky=W)

		#smooth spectrum
		self.smoothButton = Button(self.frame_button, text="Smooth", command = self.smooth_data, state=DISABLED)
		#self.smoothButton.pack(side=RIGHT, padx=5, pady=5)
		self.smoothButton.grid(row=2, column=1, padx=5, pady=5, sticky=W)


		Label(self.frame_button, text="Convert Domain").grid(row=3, column=0, padx=5, pady=5, sticky=W)

		#convert to time domain
		self.timeButton = Button(self.frame_button, text="Time Domain", command = self.time_domain)
		#timeButton.pack(side=RIGHT, padx=5, pady=5)
		self.timeButton.grid(row=3, column=1, padx=5, pady=5, sticky=W)

		#convert to mass domain
		self.massButton = Button(self.frame_button, text="Mass Domain", command = self.mass_domain)
		#self.massButton.pack(side=RIGHT, padx=5, pady=5)
		self.massButton.grid(row=3, column=2, padx=5, pady=5, sticky=W)

		self.quitButton = Button(self.frame_button, text="Quit", command = self.quit_destroy)
		#quitButton.place(x=50, y=50)
		#quitButton.pack(side=RIGHT, padx=5, pady=5)
		self.quitButton.grid(row=3, column=6, padx=5, pady=5, sticky=E)


	#plot figure
	def generate_figure(self, data, label, xaxis_title):
		#clear figure
		plt.clf()
		ax = self.fig.add_subplot(111)
		#clear axis
		ax.cla()
		spectrum=ax.plot(data[0],data[1])
		ax.set_xlabel(xaxis_title)#, fontsize=6)
		ax.set_ylabel('intensity (V)')#, fontsize=6)
		#ax.tick_params('both', length=4, width=1, which='major')
		#ax.tick_params('both', length=2, width=0.5, which='minor')
		#for tick in ax.xaxis.get_major_ticks():
			#tick.label.set_fontsize(6)
		#for tick in ax.yaxis.get_major_ticks():
			#tick.label.set_fontsize(6)
		#add peak labels
		for index, label_x in enumerate(label[0]):
			#ax.text(0.94*label_x, 1.05*label[1][index], str("%.1f" % label_x))
			#ax.annotate(str("%.1f" % label_x), xy=(label_x, label[1][index]), xytext=(1.1*label_x, 1.1*label[1][index]), arrowprops=dict(facecolor='black', shrink=0.1),)
			#ax.annotate(str("%.1f" % label_x), xy=(label_x, label[1][index]), xytext=(1.0*label_x, 1.2*label[1][index]),)
			#I could separate format, offset, precision into an array for each label
			an1 = ax.annotate(str(self.label_format % round(label_x + self.label_offset, int(self.digits_after))), xy=(label_x, label[1][index]), xytext=(label_x, label[1][index]), fontsize=self.label_size)
			an1.draggable(state=True)
			#need to retrieve new label position and update position array
			#self.label_mass[index]=(event.xdata)
			#self.label_intensity[index]=(event.ydata)
			#self.label_time[index]=(event.xdata)
		
		#remove self.label_time values
		#set label_peaks to generate figure again with loop that allows peak labeling (datacursor()) - set flag, reset flag in loop
		##otherwise label will appear when selecting peaks for calibration
		#have Tim download mpldatacursor package with pip?
		#need to figure out how to remove labels
		##canvas.delete("all") in function with a redraw function?
		#datacursor(spectrum, display='multiple', draggable=True, formatter='{x:.1f}'.format, bbox=None)
		
		self.canvas.show()
		#self.canvas.get_tk_widget().pack(side=BOTTOM)
		self.canvas.get_tk_widget().pack(side=BOTTOM, fill=BOTH, expand=True)
		#self.can.grid(row=1, column=0, columnspan=6, rowspan=3, padx=5, sticky=E+W+S+N)

		self.toolbar.update()
		#self.canvas._tkcanvas.pack(side=TOP)
		self.canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=True)

	#def delete_figure(self):
		#Canvas.delete("all")
		#.destroy()

	#open file
	def onOpen(self):
		#displays .txt files in browser window
		#only reads time domain data files
		ftypes = [('binary files', '*.trc'), ('txt files', '*.txt')]
		dlg = tkFileDialog.Open(self, filetypes = ftypes)
		fl = dlg.show()
		
		if fl != '':
			if fl[-3:] == 'trc':
				self.time, self.intensity = read_lecroy_binary.read_timetrace(fl)
				#plots data in time domain
				if self.time_mass_flag==0:
					self.time_domain()
				#plots data in mass domain
				elif self.time_mass_flag==1:
					self.mass_domain()

			elif fl[-3:] == 'txt':
				data = self.readFile(fl)
				self.intensity=data[1]
				#self.intensity = [x+0.00075 for x in data[1]]
				if self.time_mass_flag==0:
					self.time=data[0]
					self.time_domain()
				elif self.time_mass_flag==1:
					self.mass=data[0]
					self.mass_domain()
			self.labelButton.config(state=NORMAL)
			self.deletelabelButton.config(state=NORMAL)
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
			savefile.write('\r\n')
		savefile.close()

	#convert to mass domain
	#disabled until calibration is defined
	def mass_domain(self):
		self.time_mass_flag=1
		self.generate_figure([self.mass,self.intensity], [self.label_mass, self.label_intensity], 'mass (Da)')
	
	#convert to time domain	
	def time_domain(self):
		self.time_mass_flag=0
		#plot in micro seconds
		self.generate_figure([[1E6*x for x in self.time],self.intensity], [self.label_time, self.label_intensity], 'time ($\mu$s)')
		
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

	#format labels
	def format_labels(self):
		self.FormatLabelDialog(self.parent)
		#wait for dialog to close
		self.top.wait_window(self.top)
		self.label_size = float(self.label_size)
		self.label_format = "%."+self.digits_after+"f"

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

	#called when "Start New Calibration" is selected from MS cascade
	def onCalStartInclude(self):
		#sets MSMS flag for finish_calibrate routine
		self.MSMS_flag=0
		#reset calibration points
		self.cal_time=[]
		self.cal_mass=[]
		#sets (0,0) as default
		self.cal_time.append(0)
		self.cal_mass.append(0)
		#plot data in time domain (reset plot)
		self.time_domain()
		#set calibration buttons (add new, finish) to enabled state
		self.calibrateButton.config(state=NORMAL)
		self.finishcalButton.config(state=DISABLED)
		self.counter=1

	#called when "Start New Calibration" is selected from MS cascade
	def onCalStartExclude(self):
		#sets MSMS flag for finish_calibrate routine
		self.MSMS_flag=0
		#reset calibration points
		self.cal_time=[]
		self.cal_mass=[]
		#sets (0,0) as default
		#self.cal_time.append(0)
		#self.cal_mass.append(0)
		#plot data in time domain (reset plot)
		self.time_domain()
		#set calibration buttons (add new, finish) to enabled state
		self.calibrateButton.config(state=NORMAL)
		self.finishcalButton.config(state=DISABLED)
		self.counter=0

	#called when "Start New Calibration" is selected in MSMS mode
	def onMSMSCalStart(self):
		#sets MSMS flag for finish_calibrate routine
		self.MSMS_flag=1
		#reset calibration points
		self.cal_time=[]
		self.cal_mass=[]
		#plot data in time domain (reset plot)
		self.time_domain()
		#set calibration button (ID parent peak, finish) to enabled state
		self.parentButton.config(state=NORMAL)
		self.halfparentButton.config(state=DISABLED)
		self.constantButton.config(state=NORMAL)
		self.finishcalButton.config(state=DISABLED)


	#called when click is made in plotting environment during calibration
	def on_click(self, event):	
		temp_len=len(self.cal_time)
		#when the click is made within the plotting window
		if event.inaxes is not None:
			#print 'clicked: ', event.xdata, event.ydata
			self.cal_time.append(event.xdata*1E-6)
			#sets up dialog box for user to enter mass value
			self.MassDialog(self.parent)
		#if click is outside plotting window
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
		self.w.insert(0, '151')
		self.w.grid(row=0, column=1, padx=5, pady=5)

		#polynomial order
		#must be less than window length (3)
		Label(top, text="Polynomial Order:").grid(row=1, column=0, sticky=W, padx=5, pady=5)
		self.p=Entry(top)
		self.p.insert(0, '3')
		self.p.grid(row=1, column=1, padx=5, pady=5)
		
		#calls DialogSmoothOK to set these values
		b=Button(top, text="OK", command=self.DialogSmoothOK)
		b.grid(row=2, column=1, padx=5, pady=5)

	def FormatLabelDialog(self, parent):
		top = self.top = Toplevel(self.parent)
		#font size
		Label(top, text="Font Size:").grid(row=0, column=0, sticky=W, padx=5, pady=5)
		self.fs=Entry(top)
		self.fs.insert(0, '10')
		self.fs.grid(row=0, column=1, padx=5, pady=5)
		
		#Precision
		Label(top, text="Digits After Decimal:").grid(row=1, column=0, sticky=W, padx=5, pady=5)
		self.dg=Entry(top)
		self.dg.insert(0, '0')
		self.dg.grid(row=1, column=1, padx=5, pady=5)
		
		#label offset
		Label(top, text="Label Offset:").grid(row=2, column=0, sticky=W, padx=5, pady=5)
		self.lo=Entry(top)
		self.lo.insert(0, '0.0')
		self.lo.grid(row=2, column=1, padx=5, pady=5)
		
		#calls DialogLabelOK to set these values
		b=Button(top, text="OK", command=self.DialogLabelOK)
		b.grid(row=3, column=1, padx=5, pady=5)

	#called from smooth dialog box within smooth routine
	def DialogLabelOK(self):
		#sets user-defined font size
		self.label_size=float(self.fs.get())
		#sets user-defined precision
		self.digits_after=str(self.dg.get())
		#sets user-defined label offset
		self.label_offset=float(self.lo.get())
		self.top.destroy()

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
		self.counter=self.counter+1
		if self.counter > 1:
			self.finishcalButton.config(state=NORMAL)
		
	#called from MSMS calibration routine
	#stores user-selected point in cid	
	def calibrate_parent(self):
		#user selects point
		self.cid=self.canvas.mpl_connect('button_press_event', self.on_click)
		self.parentButton.config(state=DISABLED)
		self.finishcalButton.config(state=NORMAL)
		self.halfparentButton.config(state=NORMAL)
		#self.calibrateButton.config(state=NORMAL)

	#called from MSMS calibration routine
	#stores user-selected point in cid	
	def calibrate_halfparent(self):
		#user selects point
		self.cid=self.canvas.mpl_connect('button_press_event', self.on_click)
		self.halfparentButton.config(state=DISABLED)
		self.finishcalButton.config(state=NORMAL)
		#self.calibrateButton.config(state=NORMAL)
		
	#user defined calibration constant
	def calibration_constant(self):
		self.ConstantDialog(self.parent)
		#wait for dialog to close
		self.top.wait_window(self.top)
		#recompute time-mass conversion
		#if len(self.cal_time) > 0:
			#self.finishcalButton.config(state=NORMAL)

	
	def ConstantDialog(self, parent):
		top = self.top = Toplevel(self.parent)
		Label(top, text="MSMS Calibration Constant:").grid(row=0, column=0, sticky=W, padx=5, pady=5)
		self.c=Entry(top)
		self.c.insert(0, self.MSMS_zero_time)
		self.c.grid(row=0, column=1, padx=5, pady=5)
		#calls DialogConstantOK to set these values
		b=Button(top, text="OK", command=self.DialogConstantOK)
		b.grid(row=2, column=1, padx=5, pady=5)

	def DialogConstantOK(self):
		#sets user-defined calibration constant
		self.MSMS_zero_time=float(self.c.get())
		self.top.destroy()
		
		
	#called from calibration routine after "finish" button is pressed
	def finish_calibrate(self):
		#disables buttons until "start new calibration" is selected
		self.calibrateButton.config(state=DISABLED)
		self.finishcalButton.config(state=DISABLED)
		self.parentButton.config(state=DISABLED)
		self.halfparentButton.config(state=DISABLED)
		self.constantButton.config(state=DISABLED)
		#allows plotting in mass domain
		self.massButton.config(state=NORMAL)
		#for MSMS calibration
		if self.MSMS_flag==1:
			#add second calibration time point equal to some percentage of parent peak time if necessary
			#if cal_time has only one value:
			if len(self.cal_time) == 1:
				self.cal_time.append(self.cal_time[0]*self.MSMS_zero_time)
				self.cal_mass.append(0)

		#if MS mode (regular)
		if self.MSMS_flag==0:
			#fit quadratic fuction through cal points
			popt, pcov = curve_fit(func_quad, self.cal_time, self.cal_mass)
			#convert time to mass
			self.mass[:] = [popt[0]*(x**2)*(1E10) + popt[1] for x in self.time]

		#if MSMS mode
		elif self.MSMS_flag==1:
			#fit quadratic fuction through cal points
			popt, pcov = curve_fit(func_lin, self.cal_time, self.cal_mass)
			#convert time to mass
			self.mass[:] = [popt[0]*x*(1E10) + popt[1] for x in self.time]
			#discard all data below 0 mass
			mass_temp=self.mass
			int_temp=self.intensity
			time_temp=self.time
			self.mass=[]
			self.intensity=[]
			self.time=[]
			for index, mass in enumerate(mass_temp):
				if mass > 0:
					self.mass.append(mass)
					self.intensity.append(int_temp[index])
					self.time.append(time_temp[index])
			
		#allows user to save calibration file
		self.calMenu.entryconfig("Save Calibration File", state=NORMAL)
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

	#function to label peaks on figure in order to save figure as an image file with labels
	def label_peaks(self):
		#ask for peak (on_click_label)
		self.cid=self.canvas.mpl_connect('button_press_event', self.on_click_label)
	
	#remove peak labels when button is selected
	def delete_labels(self):
		#deletes peak label arrays
		self.label_time=[]
		self.label_mass=[]
		self.label_intensity=[]
		#if time flag is set
		if self.time_mass_flag==0:
			self.time_domain()
		elif self.time_mass_flag==1:
			self.mass_domain()
		
	#called when click is made to label peak
	def on_click_label(self, event):
		temp_len=len(self.label_intensity)
		#if time flag is set
		if self.time_mass_flag==0:
			#temp_len=len(self.label_time)
			#when the click is made within the plotting window
			if event.inaxes is not None:
				#print 'clicked: ', event.xdata, event.ydata
				self.label_time.append(event.xdata)
				self.label_intensity.append(event.ydata)
				#print 'time: ', self.label_time
				#print 'intensity: ', self.label_intensity
				self.time_domain()
			#if click is outside plotting window
			else:
				print 'Clicked ouside axes bounds but inside plot window'		
		#if the mass flag is set
		elif self.time_mass_flag==1:
			#temp_len=len(self.label_mass)
			#when the click is made within the plotting window
			if event.inaxes is not None:
				#print 'clicked: ', event.xdata, event.ydata
				self.label_mass.append(event.xdata)
				self.label_intensity.append(event.ydata)
				#print 'mass: ', self.label_mass
				#print 'intensity: ', self.label_intensity
				self.mass_domain()
			#if click is outside plotting window
			else:
				print 'Clicked ouside axes bounds but inside plot window'		
		#self.peak_intensity=event.ydata
		#plot label
		
		#disconnect from click event when a new peak label value is set
		if temp_len < len(self.label_intensity):
			self.canvas.mpl_disconnect(self.cid)


	#need to destroy parent before quitting, otherwise python crashes on Windows
	def quit_destroy(self):
		self.parent.destroy()
		self.parent.quit()

#quadratic function for time to mass conversion
def func_quad(x, a, b):
	return (1E10)*a*(x**2)+b

def func_lin(x, a, b):
	return (1E10)*a*x+b


def main():
	warnings.filterwarnings("ignore")
	#the root window is created
	root = Tk()

	#The geometry() method sets a size for the window and positions it on the screen.
	#The first two parameters are width and height of the window.
	#The last two parameters are x and y screen coordinates. 
	root.geometry("1000x700+100+30")
	
	#create the instance of the application class
	app = labTOF(root)
	
	#enter the main loop
	root.mainloop()  

if __name__ == '__main__':
	main()  