@echo off
setlocal EnableExtensions

set "SCRIPT_DIR=%~dp0"
set "INPUT_DIR=exports"
set "OUTPUT_DIR=out"
set "GLOB=*.xml"
set "RECURSIVE="

:parse_args
if "%~1"=="" goto after_args
if /I "%~1"=="-InputDir" (
    set "INPUT_DIR=%~2"
    shift
    shift
    goto parse_args
)
if /I "%~1"=="-OutputDir" (
    set "OUTPUT_DIR=%~2"
    shift
    shift
    goto parse_args
)
if /I "%~1"=="-Glob" (
    set "GLOB=%~2"
    shift
    shift
    goto parse_args
)
if /I "%~1"=="-Recursive" (
    set "RECURSIVE=--recursive"
    shift
    goto parse_args
)
shift
goto parse_args

:after_args
set "INPUT_PATH=%SCRIPT_DIR%%INPUT_DIR%"
set "OUTPUT_PATH=%SCRIPT_DIR%%OUTPUT_DIR%"
set "DASHBOARD_PATH=%OUTPUT_PATH%\dashboard.html"

if not exist "%INPUT_PATH%" (
    echo Input folder not found: %INPUT_PATH%
    exit /b 1
)

echo Running analysis...
echo Input:  %INPUT_PATH%
echo Output: %OUTPUT_PATH%

python "%SCRIPT_DIR%run_analysis.py" analyze --input "%INPUT_PATH%" --output "%OUTPUT_PATH%" --glob "%GLOB%" %RECURSIVE%
if errorlevel 1 (
    echo Analysis failed.
    exit /b %errorlevel%
)

if exist "%DASHBOARD_PATH%" (
    start "" "%DASHBOARD_PATH%"
)

echo Analysis finished.
endlocal
