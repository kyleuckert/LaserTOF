from Tkinter import Tk, RIGHT, RAISED, Label, BOTH, W, N, S, E, Frame, Text, Menu, END
#from ttk import Button, Style, Entry#, Frame
import tkFileDialog

class Example(Frame):

	#define parent window
	def __init__(self, parent):
		#from Tkinter frame:
		#Frame.__init__(self, parent, background="white")   
		#from ttk frame:
		Frame.__init__(self, parent)

		#save a reference to the parent widget
		self.parent = parent

		#delegate the creation of the user interface to the initUI() method
		self.initUI()
		#self.parent.title("Centered window")
		#self.pack(fill=BOTH, expand=1)
		#self.centerWindow()
        
	#container for other widgets
	def initUI(self):
		#set the title of the window using the title() method
		self.parent.title("Simple")
		#the Frame widget (accessed via the delf attribute) in the root window
		#it is expanded in both directions
		self.pack(fill=BOTH, expand=1)
		
		#apply a theme to widget
		#self.style = Style()
		#self.style.theme_use('default')

		menubar = Menu(self.parent)
		self.parent.config(menu=menubar)
		
		fileMenu = Menu(menubar)
		fileMenu.add_command(label="Open", command=self.onOpen)
		menubar.add_cascade(label="File", menu=fileMenu)        

		self.txt = Text(self)
		self.txt.pack(fill=BOTH, expand=1)
		
		#create instance of the button widget
		#command specifies the method to be called
		#quitButton = Button(self, text="Quit", command = self.quit)
		#quitButton.place(x=50, y=50)

		#create a second frame with raised relief
		#the frame pushes the two butons to the bottom
		#frame = Frame(self, relief=RAISED, borderwidth=1)
		#frame.pack(fill=BOTH, expand=1)

		#self.pack(fill=BOTH, expand=1)

		#the buttons are created and placed in a horizontal box
		#side creates a horizontal layout
		#closeButton = Button(self, text="Close", command = self.quit)
		#closeButton.pack(side=RIGHT, padx=5, pady=5)
		#okButton = Button(self, text="OK")
		#okButton.pack(side=RIGHT)

	def onOpen(self):

		ftypes = [('Python files', '*.py'), ('All files', '*')]
		dlg = tkFileDialog.Open(self, filetypes = ftypes)
		fl = dlg.show()

		if fl != '':
			text = self.readFile(fl)
			self.txt.insert(END, text)

	def readFile(self, filename):

		f = open(filename, "r")
		text = f.read()
		return text
        
        
	def centerWindow(self):
		#width/height values of screen window
		w = 290
		h = 150
		#width/height values of screen
		sw = self.parent.winfo_screenwidth()
		sh = self.parent.winfo_screenheight()
		#calculate position of screen
		x = (sw - w)/2
		y = (sh - h)/2
		self.parent.geometry('%dx%d+%d+%d' % (w, h, x, y))

def main():

	#the root window is created
	root = Tk()
	
	#The geometry() method sets a size for the window and positions it on the screen.
	#The first two parameters are width and height of the window.
	#The last two parameters are x and y screen coordinates. 
	ex = Example(root)
	root.geometry("300x250+300+300")

	#create the instance of the application class
	#ex = Example(root)
	
	#enter the main loop
	root.mainloop()  


if __name__ == '__main__':
	main()  