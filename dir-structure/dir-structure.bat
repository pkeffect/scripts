@echo off
setlocal enabledelayedexpansion

:: --- Configuration ---
set "OUTPUT_FILE=project-structure.txt"
set "SCRIPT_NAME=%~nx0"

echo Generating project structure...

:: --- Create output file with header ---
echo # Project Directory Structure ^& Files > "%OUTPUT_FILE%"

:: Get root directory name
for %%i in (.) do set "ROOT_DIR_NAME=%%~ni"
echo %ROOT_DIR_NAME%/ >> "%OUTPUT_FILE%"

:: --- Start recursive processing ---
call :process_directory "." ""

echo.
echo Project structure successfully saved to %OUTPUT_FILE%
goto :eof


:: --- Recursive function ---
:process_directory
setlocal
set "current_dir=%~1"
set "parent_prefix=%~2"

:: Temporary files for sorting
set "TEMP_FILES=%temp%\files_%random%.txt"
set "TEMP_DIRS=%temp%\dirs_%random%.txt"

:: Get files (exclude hidden/system, script, and output)
dir "%current_dir%" /b /a-d-h-s /o:n 2>nul | findstr /v /i /c:"%SCRIPT_NAME%" /c:"%OUTPUT_FILE%" > "%TEMP_FILES%"

:: Get directories (exclude hidden/system)
dir "%current_dir%" /b /ad-h-s /o:n 2>nul | findstr /v /i /c:"node_modules" /c:"__pycache__" /c:".venv" /c:"venv" > "%TEMP_DIRS%"

:: Count total items
set /a total_files=0
for /f "usebackq" %%f in ("%TEMP_FILES%") do set /a total_files+=1

set /a total_dirs=0
for /f "usebackq" %%f in ("%TEMP_DIRS%") do set /a total_dirs+=1

set /a total_items=!total_files! + !total_dirs!
set /a item_count=0

:: Process files first
for /f "usebackq delims=" %%i in ("%TEMP_FILES%") do (
    set /a item_count+=1
    if !item_count! equ !total_items! (
        echo !parent_prefix!└── %%i>> "%OUTPUT_FILE%"
    ) else (
        echo !parent_prefix!├── %%i>> "%OUTPUT_FILE%"
    )
)

:: Process directories
for /f "usebackq delims=" %%i in ("%TEMP_DIRS%") do (
    set /a item_count+=1
    
    if !item_count! equ !total_items! (
        echo !parent_prefix!└── %%i/>> "%OUTPUT_FILE%"
        call :process_directory "%current_dir%\%%i" "!parent_prefix!    "
    ) else (
        echo !parent_prefix!├── %%i/>> "%OUTPUT_FILE%"
        call :process_directory "%current_dir%\%%i" "!parent_prefix!│   "
    )
)

:: Cleanup
del "%TEMP_FILES%" 2>nul
del "%TEMP_DIRS%" 2>nul
endlocal
goto :eof