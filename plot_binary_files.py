import numpy as np

path = '/Users/kyleuckert/Google Drive/LaserTOF/'
filename = 'RawDataACMatric_pos.trc'

f = open(path+filename, "rb")
try:
    byte = f.read(1)
    mass=[]
    intensity=[]
    while byte != "":
        # Do stuff with byte.
        byte = f.read(1)
        for line in f:
			#read each row - store data in columns
			columns=line.split()
			mass.append(float(columns[0]))
			intensity.append(float(columns[1]))
finally:
    f.close()
    
print byte