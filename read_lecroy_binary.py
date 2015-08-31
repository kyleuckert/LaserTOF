from struct import unpack
import numpy as np
import struct
import array

def read_timetrace(filename):
	'''
	Read binary waveform file (.trc) from LeCroy waverunner
	Based on Matlab file LCREAD.m
	Input:
		filename : filename, string
	Output:
		
	'''
	## Seek offset in the header block
	fid = open(filename, "r")
	data = fid.read(50)
	WAVEDESC = str.find(data,'WAVEDESC')
	##---------------------------------------------------------------------------------------
	## Define the addresses of the various informations in the file
	## These addresses are valid for the template LECROY_2_2 and are subject to change in
	## future revisions of the LeCroy firmware
	##---------------------------------------------------------------------------------------
	TESTED_TEMPLATE = 'LECROY_2_3';

	#Addresses (WAVEDESC + address as stated in the LECROY template)
	aCOMM_TYPE			= WAVEDESC+ 32;
	aCOMM_ORDER			= WAVEDESC+ 34;
	aWAVE_DESCRIPTOR	= WAVEDESC+ 36;	# length of the descriptor block
	aUSER_TEXT			= WAVEDESC+ 40;	# length of the usertext block
	aTRIGTIME_ARRAY     = WAVEDESC+ 48; # length of the TRIGTIME array
	aWAVE_ARRAY_1		= WAVEDESC+ 60;	# length (in Byte) of the sample array

	aVERTICAL_GAIN		= WAVEDESC+ 156;
	aVERTICAL_OFFSET	= WAVEDESC+ 160;

	aHORIZ_INTERVAL		= WAVEDESC+ 176;
	aHORIZ_OFFSET		= WAVEDESC+ 180;
	aSUBARRAY_COUNT		= WAVEDESC+ 144;
	aWAVE_ARRAY_COUNT	= WAVEDESC+ 116;

	#---------------------------------------------------------------------------------------
	## determine the number storage format HIFIRST / LOFIRST 	(big endian / little endian)
	#---------------------------------------------------------------------------------------
	
	fid.seek(aCOMM_ORDER)
	COMM_ORDER = ord(fid.read(1))

	if COMM_ORDER == 0:
	 	## big-endian
		fmt = '>'
	else:
		## little-endian
		fmt = '<'

	COMM_TYPE			= ReadWord(fid, fmt, aCOMM_TYPE)
	WAVE_DESCRIPTOR 	= ReadLong(fid, fmt, aWAVE_DESCRIPTOR)
	USER_TEXT			= ReadLong(fid, fmt, aUSER_TEXT)
	TRIGTIME_array      = ReadLong(fid, fmt, aTRIGTIME_ARRAY)
	WAVE_ARRAY_1		= ReadLong(fid, fmt, aWAVE_ARRAY_1)
	VERTICAL_GAIN		= ReadFloat	(fid, fmt, aVERTICAL_GAIN)
	VERTICAL_OFFSET		= ReadFloat	(fid, fmt, aVERTICAL_OFFSET)
	HORIZ_INTERVAL		= ReadFloat(fid, fmt, aHORIZ_INTERVAL);
	HORIZ_OFFSET		= ReadDouble(fid, fmt, aHORIZ_OFFSET);
	#INSTRUMENT_NAME = ReadString(fid, fmt, aINSTRUMENT_NAME);
	#INSTRUMENT_NUMBER       = ReadLong      (fid, fmt, aINSTRUMENT_NUMBER);
	NBSEGMENTS			= ReadLong(fid, fmt, aSUBARRAY_COUNT);
	WAVE_ARRAY_COUNT    = ReadLong(fid, fmt, aWAVE_ARRAY_COUNT);
	#print VERTICAL_GAIN
	#print VERTICAL_OFFSET
  
	fid.close()
	fid = open(filename, "rb")
        # for sequence mode
        #print NBSEGMENTS
        if NBSEGMENTS > 1:
          # Read contents of TRIGTIME_ARRAY, which is an interleaved array
          #---------------------------------------------------------------------------------------
          # Take from X-Stream oscilloscopes remote control manual, appendix II:
          # <  0>          TRIGGER_TIME: double     ; for sequence acquisitions, 
          #                                         ; time in seconds from first 
          #                                         ; trigger to this one 
          # <  8>          TRIGGER_OFFSET: double   ; the trigger offset is in seconds 
          #                                         ; from trigger to zeroth data point

          #fseek(fid, WAVEDESC + WAVE_DESCRIPTOR + USER_TEXT, 'bof');
          trigtime_array_temp = ReadData(fid, fmt, WAVEDESC + WAVE_DESCRIPTOR + USER_TEXT, 2*NBSEGMENTS, 'b')
          #print len(trigtime_array_temp)
          trigger_time = trigtime_array_temp[::2]
          #print len(trigger_time)
          trigger_offset = trigtime_array_temp[1::2]
          #print trigger_time
          #print trigger_offset
          #print len(trigger_time)
          #print WAVE_ARRAY_COUNT
          #print 2*NBSEGMENTS
          #print TRIGTIME_array
          #print "COMM_TYPE", COMM_TYPE
    
          if COMM_TYPE==0:
            word='b'
          else:
            word='h'

          ally = ReadDataSequence(fid, fmt, WAVEDESC + WAVE_DESCRIPTOR + USER_TEXT + TRIGTIME_array, WAVE_ARRAY_COUNT, NBSEGMENTS,  word)
          #print len(ally[0])
          #print ally[1]
          allxy = []
          for i in range(len(ally)):
            #print trigger_time[i]
            #x = np.arange(1+trigger_time[i], int(WAVE_ARRAY_COUNT)/ int(NBSEGMENTS)+1+trigger_time[i])*HORIZ_INTERVAL + HORIZ_OFFSET
            x = np.arange(1, int(WAVE_ARRAY_COUNT)/ int(NBSEGMENTS)+1)*HORIZ_INTERVAL + HORIZ_OFFSET
            y = (ally[i]*VERTICAL_GAIN -VERTICAL_OFFSET)
            allxy.append((x,y))

	  fid.close()
          return allxy


        else:
          #print TRIGTIME_array,HORIZ_INTERVAL
	
	  y = ReadData(fid, fmt, WAVEDESC + WAVE_DESCRIPTOR + USER_TEXT + TRIGTIME_array, WAVE_ARRAY_1)
	  y = VERTICAL_GAIN * y - VERTICAL_OFFSET
  	  x = np.arange(1,len(y)+1)*HORIZ_INTERVAL + HORIZ_OFFSET
	
	  return x,y

def ReadByte(fid,fmt,Addr):
	fid.seek(Addr)
	#s = fid.readline(1)
	s = fid.read(1)
	s = unpack(fmt + 'b', s)
	if(type(s) == tuple):
		return s[0]
	else:
		return s

def ReadWord(fid,fmt,Addr):
	fid.seek(Addr)
	#s = fid.readline(2)
	s = fid.read(2)
	s = unpack(fmt + 'h', s)
	if(type(s) == tuple):
		return s[0]
	else:
		return s	
	
def ReadLong(fid,fmt,Addr):
	fid.seek(Addr)
	#s = fid.readline(4)
	s = fid.read(4)
	s = unpack(fmt + 'l', s)
	if(type(s) == tuple):
		return s[0]
	else:
		return s

def ReadFloat(fid,fmt,Addr):
	fid.seek(Addr)
	#s = fid.readline(4)
	s = fid.read(4)
	s = unpack(fmt + 'f', s)
	if(type(s) == tuple):
		return s[0]
	else:
		return s

def ReadDouble(fid,fmt,Addr):
	fid.seek(Addr)
	#s = fid.readline(8)
	s = fid.read(8)
	s = unpack(fmt + 'd', s)
	if(type(s) == tuple):
		return s[0]
	else:
		return s

def ReadDataSequence(fid, fmt, Addr, datalen, nsegments,  what='b'):
    import time
    start = time.time()
    fid.seek(Addr)
    #m1 = time.time()
    #print datalen
    toread = int(datalen)/int(nsegments)
    fmtl = fmt + str(toread) + what
    nbytes = struct.calcsize(fmtl)
    #print "fmtl", fmtl, nbytes
    #m2 = time.time()
    result = []
    for i in range(nsegments):
      data = fid.read(nbytes)
      wavelenght = np.frombuffer(data, what, toread)
      result.append(wavelenght)

#    result = struct.unpack(fmt, data[0:nbytes])
    #m3 = time.time()
    #print 'M1: %s, M2: %s, M3: %s' % (m1-start,m2-start,m3-start)
    return result

def ReadData(fid, fmt, Addr, datalen, what='2b'):    

	fid.seek(Addr)
	fmtl = fmt + str(datalen) + what
	#fmtl = np.dtype(int)
	#fmtl=fmtl.newbyteorder(fmt)
	#print fmtl
	nbytes = struct.calcsize(fmtl)
	#print nbytes
	data = fid.read(nbytes)
	#data=fid.read()
	dt=np.dtype('int16')
	dt=dt.newbyteorder(fmt)
	#print dt
	#np.frombuffer(buffer, dtype=float, count=-1, offset=0)
	result = np.frombuffer(data, dt, -1)
	#result = np.frombuffer(data, what, 50002)
#	result = struct.unpack(fmtl, data)
#	result=np.array(result)
	#print result[0]
	#print len(result)
#	result = struct.unpack(fmt, data[0:nbytes])
	return result 