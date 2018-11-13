# Installation of LISVAP

## System requirements

Currently LISVAP is available on both Linux and 32-bit Windows systems. Either way, the application requires that a recent version of the PCRaster software is available, or at least PCRaster’s ‘pcrcalc’ application and all associated libraries. Unless you are using a ‘sealed’ version of LISVAP (i.e. a version in which the source code is made unreadable), you will also need a licensed version of ‘pcrcalc’. For details on how to install PCRaster the reader is referred to the PCRaster documentation.

## Installation on Windows systems

For Windows users the installation involves unzipping the contents of ‘lisvap_win32.zip’ to the folder in which the LISFLOOD model is installed already (e.g. ‘lisflood’). The Windows version of LISVAP is a Windows executable (byte-code ‘compiled’ using *Py2Exe*). It comprises the following files, which should all be in the same directory:

 

| Files                                | Description                        |
| ------------------------------------ | ---------------------------------- |
| *lisvap.exe*                         | LISVAP executable                  |
| *lisvap.xml*                         | LISVAP master code                 |
| *config.xml*                         | configuration file (*)             |
| *lisvapLib.zip*                      | library of Python source modules   |
| *python25.dll*                       | Python 2.5 interpreter library (*) |
| *w9xpopen.exe*                       | needed on WinXX systems (*)        |
| *zlib.pyd ,bz2.pyd, unicodedata.pyd* | additional libraries  (*)          |

 

All items marked with an asterisk (*) are shared with LISFLOOD. If LISFLOOD is already set up correctly, LISVAP will use the same configuration file and it should work correctly. Further information on the format of the configuration file can be found in the LISFLOOD User Manual (Van der Knijff & De Roo, 2008). <span style="color:red"> (update)</span>

 

The LISVAP executable is a command-line application which can be called from the command prompt (‘DOS’ prompt). To make life easier you may include the full path to ‘lisvap.exe’ in the ’Path’ environment variable. In Windows XP you can do this by selecting ‘settings’ from the ‘Start’ menu; then go to ‘control panel’/’system’ and go to the ‘advanced’ tab. Click on the  ‘environment variables’ button. Finally, locate the ‘Path’ variable in the ‘system variables’ window and click on ‘Edit’ (requires local Administrator priviliges).

## Installation on Linux systems

Under Linux LISVAP requires that the Python interpreter (version 2.4 or more recent) is installed on the system. You can download Python free of any charge from the following location:

 http://www.python.org/

 

The installation process is largely identical to the Windows procedure: unzip the contents of ‘lisvap_linux.zip’ to the LISFLOOD directory. Check if the file ‘lisvap’ is executable. If not, make it executable using:

 ```xml
chmod 755 lisvap
 ```



## Running LISVAP

Type ‘lisvap’ at the command prompt. You should see something like this:

 ```xml
  LISVAP version July 24 2006
  Potential evaporation pre-processor for LISFLOOD

     (C) Institute for Environment and Sustainability
         Joint Research Centre of the European Commission
         TP261, I-21020 Ispra (Va), Italy
  usage (1): lisvap [switches] <InputFile>
  usage (2): lisvap --listoptions (show options only)

   InputFile     : LISVAP input file (see documentation
                   for description of format)
   switches:
             -s  : keep temporary script after simulation
 ```



You can run LISVAP by typing ‘lisvap’ followed by a specially-formatted settings file. The layout of this file is described in Chapter 5. Chapter 4 explains all other input files. <span style="color:red"> (update)</span>