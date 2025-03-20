@echo off
REM ======================================================================
REM Docker Compose Startup Helper (Windows Version)
REM 
REM This script automatically finds and runs Docker Compose files with
REM proper error handling and status reporting.
REM
REM Features:
REM - Automatically detects common Docker Compose filenames
REM - Provides clear visual feedback
REM - Handles errors gracefully with descriptive messages
REM ======================================================================

REM ----------------------------------------------------------------------
REM Configuration Options
REM ----------------------------------------------------------------------

setlocal enabledelayedexpansion

REM Set title for the console window
title Docker Compose Startup Helper

REM ----------------------------------------------------------------------
REM Color and formatting setup
REM ----------------------------------------------------------------------

REM Colors for Windows console (using ANSI escape sequences - works in Windows 10+)
set "GREEN=[32m"
set "RED=[31m"
set "YELLOW=[33m"
set "BLUE=[34m"
set "NC=[0m"

REM ----------------------------------------------------------------------
REM Functions (implemented as labels in batch)
REM ----------------------------------------------------------------------

REM Main script execution starts here
goto :main

:print_status
    REM Function to print colored status messages
    REM %~1 = icon, %~2 = message, %~3 = color
    echo %~3%~1 %~2%NC%
    goto :eof

:check_docker
    REM Function to check Docker daemon status
    docker info >nul 2>&1
    if %ERRORLEVEL% neq 0 (
        call :print_status "❌" "Docker daemon is not running! Please start Docker first." "%RED%"
        exit /b 3
    )
    goto :eof

:check_docker_compose
    REM Function to check Docker Compose availability
    docker compose version >nul 2>&1
    if %ERRORLEVEL% neq 0 (
        call :print_status "❌" "Docker Compose is not available. Please install it first." "%RED%"
        exit /b 4
    )
    goto :eof

REM ----------------------------------------------------------------------
REM Main Script
REM ----------------------------------------------------------------------

:main
    REM Display script header
    call :print_status "🐳" "Docker Compose Startup Helper" "%BLUE%"
    echo ---------------------------------------

    REM Check prerequisites
    call :print_status "🔍" "Checking prerequisites..." "%YELLOW%"
    call :check_docker
    if %ERRORLEVEL% neq 0 exit /b %ERRORLEVEL%
    
    call :check_docker_compose
    if %ERRORLEVEL% neq 0 exit /b %ERRORLEVEL%

    REM Array of Docker Compose filenames to check (in order of preference)
    set "compose_files[0]=compose.yaml"
    set "compose_files[1]=compose.yml"
    set "compose_files[2]=docker-compose.yaml"
    set "compose_files[3]=docker-compose.yml"

    REM Get current directory for reference
    set "current_dir=%cd%"
    call :print_status "📂" "Searching for Docker Compose files in: %current_dir%" "%YELLOW%"

    REM Initialize variables
    set "compose_file="
    set "found=false"

    REM Loop through potential filenames and check existence
    for /L %%i in (0,1,3) do (
        if exist "!compose_files[%%i]!" (
            set "compose_file=!compose_files[%%i]!"
            call :print_status "✅" "Found: !compose_file!" "%GREEN%"
            set "found=true"
            goto :found_compose_file
        ) else (
            call :print_status "❌" "Not found: !compose_files[%%i]!" "%RED%"
        )
    )

:found_compose_file
    REM Check if a file was found, exit with error if not
    if "%found%"=="false" (
        call :print_status "❌" "Error: No valid Docker Compose file found in %current_dir%!" "%RED%"
        echo.
        call :print_status "💡" "Tip: Create one of these files: compose.yaml, compose.yml, docker-compose.yaml, docker-compose.yml" "%YELLOW%"
        exit /b 1
    )

    REM Run Docker Compose with error handling
    call :print_status "🚀" "Starting services from %compose_file%..." "%BLUE%"
    echo.

    REM Try to start the services, capture exit code for error handling
    docker compose -f "%compose_file%" up -d
    
    if %ERRORLEVEL% equ 0 (
        echo.
        call :print_status "✅" "Services started successfully!" "%GREEN%"
        
        REM Display running containers for user convenience
        echo.
        call :print_status "📋" "Currently running containers:" "%BLUE%"
        docker compose -f "%compose_file%" ps
    ) else (
        set "exit_code=%ERRORLEVEL%"
        echo.
        call :print_status "❌" "Docker Compose failed with exit code: %exit_code%" "%RED%"
        call :print_status "🔍" "Possible issues:" "%YELLOW%"
        echo   - Check the syntax in %compose_file%
        echo   - Ensure Docker daemon is running properly
        echo   - Verify network connectivity for image pulling
        echo   - Check for port conflicts with existing services
        exit /b 2
    )

    REM Optional pause to view results (useful when running from GUI)
    echo.
    pause
    exit /b 0