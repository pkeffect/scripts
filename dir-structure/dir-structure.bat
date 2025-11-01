@echo off
setlocal enabledelayedexpansion

:: --- Configuration ---
set "OUTPUT_FILE=project-structure.txt"
set "TEMP_OUTPUT=%OUTPUT_FILE%.tmp"
set "SCRIPT_NAME=%~nx0"
set "STATS_FILE=%temp%\dirstats_%random%.txt"

:: Initialize statistics
echo 0>"%STATS_FILE%"
echo 0>>"%STATS_FILE%"
echo 0>>"%STATS_FILE%"

echo Generating project structure...

:: --- Create temp file for tree structure ---
echo. > "%TEMP_OUTPUT%"

:: Get root directory name
for %%i in (.) do set "ROOT_DIR_NAME=%%~ni"
echo %ROOT_DIR_NAME%/ >> "%TEMP_OUTPUT%"

:: --- Start recursive processing ---
call :process_directory "." ""

:: --- Read statistics ---
set /a line_num=0
for /f "usebackq delims=" %%a in ("%STATS_FILE%") do (
    set /a line_num+=1
    if !line_num!==1 set /a TOTAL_DIRS=%%a
    if !line_num!==2 set /a TOTAL_FILES=%%a
    if !line_num!==3 set /a TOTAL_SIZE=%%a
)

:: --- Format size ---
call :format_size !TOTAL_SIZE! FORMATTED_SIZE

:: --- Write final output with stats at top ---
echo # Project Directory Structure ^& Files > "%OUTPUT_FILE%"
echo. >> "%OUTPUT_FILE%"
echo # Statistics >> "%OUTPUT_FILE%"
echo Total Directories: !TOTAL_DIRS! >> "%OUTPUT_FILE%"
echo Total Files: !TOTAL_FILES! >> "%OUTPUT_FILE%"
echo Total Size: !FORMATTED_SIZE! >> "%OUTPUT_FILE%"
echo. >> "%OUTPUT_FILE%"
type "%TEMP_OUTPUT%" >> "%OUTPUT_FILE%"

echo.
echo Project structure successfully saved to %OUTPUT_FILE%
echo Total Directories: !TOTAL_DIRS!
echo Total Files: !TOTAL_FILES!
echo Total Size: !FORMATTED_SIZE!

:: Cleanup
del "%STATS_FILE%" 2>nul
del "%TEMP_OUTPUT%" 2>nul
goto :eof


:: --- Format size function ---
:format_size
setlocal
set /a bytes=%~1
set "result="

if %bytes% equ 0 (
    set "result=0 B"
) else if %bytes% lss 1024 (
    set "result=%bytes% B"
) else if %bytes% lss 1048576 (
    set /a kb=%bytes% / 1024
    set "result=!kb! KB"
) else if %bytes% lss 1073741824 (
    set /a mb=%bytes% / 1048576
    set "result=!mb! MB"
) else (
    set /a gb=%bytes% / 1073741824
    set "result=!gb! GB"
)

endlocal & set "%~2=%result%"
goto :eof


:: --- Recursive function ---
:process_directory
setlocal disabledelayedexpansion
set "current_dir=%~1"
set "parent_prefix=%~2"
setlocal enabledelayedexpansion

:: Temporary files for sorting
set "TEMP_FILES=%temp%\files_%random%.txt"
set "TEMP_DIRS=%temp%\dirs_%random%.txt"

:: Get files (exclude hidden/system, script, and output)
dir "%current_dir%" /b /a-d-h-s /o:n 2>nul | findstr /v /i /c:"%SCRIPT_NAME%" /c:"%OUTPUT_FILE%" > "%TEMP_FILES%"

:: Get directories (exclude hidden/system and common folders)
dir "%current_dir%" /b /ad-h-s /o:n 2>nul | findstr /v /i /c:"node_modules" /c:"__pycache__" /c:".venv" /c:"venv" > "%TEMP_DIRS%"

:: Count items
set /a file_count=0
for /f "usebackq" %%f in ("%TEMP_FILES%") do set /a file_count+=1

set /a dir_count=0
for /f "usebackq" %%f in ("%TEMP_DIRS%") do set /a dir_count+=1

set /a total_items=!file_count! + !dir_count!
set /a current_item=0

:: Process files
for /f "usebackq delims=" %%i in ("%TEMP_FILES%") do (
    set /a current_item+=1
    
    :: Update file count and size in stats file
    set /a line_num=0
    for /f "usebackq delims=" %%a in ("%STATS_FILE%") do (
        set /a line_num+=1
        if !line_num!==1 set /a stat_dirs=%%a
        if !line_num!==2 set /a stat_files=%%a
        if !line_num!==3 set /a stat_size=%%a
    )
    set /a stat_files+=1
    for %%f in ("%current_dir%\%%i") do set /a stat_size+=%%~zf
    
    >"%STATS_FILE%" echo !stat_dirs!
    >>"%STATS_FILE%" echo !stat_files!
    >>"%STATS_FILE%" echo !stat_size!
    
    :: Determine connector
    if !current_item! equ !total_items! (
        set "connector=└── "
    ) else (
        set "connector=├── "
    )
    
    >> "%TEMP_OUTPUT%" echo !parent_prefix!!connector!%%i
)

:: Process directories
for /f "usebackq delims=" %%i in ("%TEMP_DIRS%") do (
    set /a current_item+=1
    
    :: Update directory count in stats file
    set /a line_num=0
    for /f "usebackq delims=" %%a in ("%STATS_FILE%") do (
        set /a line_num+=1
        if !line_num!==1 set /a stat_dirs=%%a
        if !line_num!==2 set /a stat_files=%%a
        if !line_num!==3 set /a stat_size=%%a
    )
    set /a stat_dirs+=1
    
    >"%STATS_FILE%" echo !stat_dirs!
    >>"%STATS_FILE%" echo !stat_files!
    >>"%STATS_FILE%" echo !stat_size!
    
    :: Determine connector and child prefix
    if !current_item! equ !total_items! (
        set "connector=└── "
        set "child_prefix=    "
    ) else (
        set "connector=├── "
        set "child_prefix=│   "
    )
    
    >> "%TEMP_OUTPUT%" echo !parent_prefix!!connector!%%i/
    
    :: Recursive call
    call :process_directory "%current_dir%\%%i" "!parent_prefix!!child_prefix!"
)

:: Cleanup temp files
del "%TEMP_FILES%" 2>nul
del "%TEMP_DIRS%" 2>nul

endlocal
endlocal
goto :eof