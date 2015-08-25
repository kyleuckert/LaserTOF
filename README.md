# LaserTOF
<b>Description:</b><br>
<p>
This program will convert mass spectra from the time domain to the mass domain.
</p>

<b>Operation:</b><br>
<p>
<i>Open a file:</i>
<ul>
<li>file-> Open-> navigate to file</li>
<li>currently only .txt files are supported</li>
<li>files may be comma, space, or tab delimited</li>
</ul></p>

<p>
<i>Convert spectrum from time to mass domain:</i><br>
<ul>
<b>start new calibration</b>
<li>Calibration -> Start New Calibration</li>
<li>zoom into desired region (magnifying glass tool)</li>
<li>Click "Add Calibration Point"</li>
<li>click point on graph corresponding to peak</li>
<li>add the mass value of this peak in the dialog box</li>
<li>zoom/pan to new area, repeat (from <i>Click "Add Calibration Point"</i> step)</li>
<li>Click "Finish Calibration"</li>
<ul>
<li>calibration includes (0,0)</li>
</ul>
</ul>
<ul>
<b>import old calibration</b>
<li>Calibration-> Open calibration file</li>
<li>open previously saved calibration file<br></li>
</ul>
<ul>
<b>save calibration</b>
<li>Calibration->Save calibration</li>
</ul></p>

<p>
<i>Smooth Spectrum:</i><br>
<ul>
<li>applies a <a href="http://docs.scipy.org/doc/scipy-dev/reference/generated/scipy.signal.savgol_filter.html#scipy.signal.savgol_filter">Savitsky-Golay Smoothing filter</a> to the data</li>
<li>click "Smooth" button</li>
<li>enter values in dialog box:</li>
<li>Window Length: length of filter window</li>
<ul>
<li>must be positive odd integer</li>
<li>suggested value: 51</li>
</ul>
<li>Polynomial Order: order of polynomial to used to fit samples</li>
<ul>
<li>must be less than window length</li>
<li>suggested value: 3</li>
</ul></ul></p>

<p>
<i>Save Figure</i>
<ul>
<li>click Save icon</li>
</ul></p>

<p>
<i>Save spectrum as ASCII file</i>
<ul>
<li>File->Export File</li>
<li>saves current spectrum (in mass or time domain, which ever is displayed)</li>
</ul></p>

<b>Future Plans:</b>
<ul>
<li>Include MSMS calibration capability</li>
<li>Allow user to label peaks
<li>Allow for binary file input</li>
</ul>

<b>Installation:</b>
<p>
<ul>
<li>Install Python using the <a href="http://continuum.io/downloads">Anaconda distribution</a>, which includes several useful scientific packages that will be necessary for the program to run.</li>
<li>Follow the installation instructions, select the default installation configuration.</li>
<li>Open the "Anaconda Command Prompt".</li>
<li>Type the following commands:</li></ul></p>
	conda install matplotlib
	conda install numpy
	conda install scipy

<p>
<ul>
<li>Download this github repository (<a href="https://github.com/kyleuckert/LaserTOF/archive/master.zip">Download ZIP button</a>).</li>
<li>Start the program by double-clicking the LaserTOF_main.py file within the LaserTOF folder. If this is the first time you are running a .py file, you may need to set .py to open using Python 2.7 by default:</li>
<ul>
<li>right click .py file, click "properties"</li>
<li>opens with -> change</li>
<li>browse to: Computer/C://Users/yourusername/Anaconda/python</li>
