TITLE WIN FILE SCAN/FIX
@ECHO OFF
CLS
color 0e
:MENU
CLS
ECHO # WINDOWS FILE SCAN AND FIX
FOR /F "tokens=2" %%i in ('date /t') do set mydate=%%i
SET mytime=%time%
ECHO # CURRENT TIME: %mydate%:%mytime%
ECHO.
ECHO 1.  CheckHealth - DISM /Online /Cleanup-Image /CheckHealth
ECHO 2.  ScanHealth - DISM /Online /Cleanup-Image /ScanHealth
ECHO 3.  RestoreHealth - DISM /Online /Cleanup-Image /RestoreHealth 
ECHO 4.  System File Checker - SFC /scannow 
ECHO 5.  Run all in order
ECHO.
ECHO # PRESS 'Q' TO QUIT
ECHO.
SET INPUT=
SET /P INPUT=Please select a number from above:
IF /I '%INPUT%'=='1' GOTO Selection1
IF /I '%INPUT%'=='2' GOTO Selection2
IF /I '%INPUT%'=='3' GOTO Selection3
IF /I '%INPUT%'=='4' GOTO Selection4
IF /I '%INPUT%'=='5' GOTO Selection5
IF /I '%INPUT%'=='m' GOTO Menu
IF /I '%INPUT%'=='q' GOTO Quit
CLS
ECHO # INVALID INPUT
ECHO -------------------------------------
ECHO Please select a number from the Main
echo Menu [1-5] or select 'Q' to quit.
ECHO -------------------------------------
ECHO # PRESS ANY KEY TO CONTINUE
PAUSE > NUL
GOTO MENU
:Selection1
DISM /Online /Cleanup-Image /CheckHealth
PAUSE
:Selection2
DISM /Online /Cleanup-Image /ScanHealth
PAUSE
:Selection3
DISM /Online /Cleanup-Image /RestoreHealth 
PAUSE
:Selection4
SFC /scannow 
PAUSE
:Selection5
DISM /Online /Cleanup-Image /CheckHealth && DISM /Online /Cleanup-Image /ScanHealth && DISM /Online /Cleanup-Image /RestoreHealth && SFC /scannow && PAUSE > NULL
GOTO MENU
:Quit
EXIT

