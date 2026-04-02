@echo off
setlocal EnableExtensions

set "SCRIPT_DIR=%~dp0"
set "HOST=127.0.0.1"
set "PORT=8765"
set "DATA_DIR=web_jobs"
set "OPEN_BROWSER=--open-browser"
set "MA2_AI_PROVIDER=ollama"
set "MA2_AI_MODEL=llama3.1:8b"
set "MA2_AI_BASE_URL=http://127.0.0.1:11434"
set "PYTHON_EXE=python"

if exist "%SCRIPT_DIR%.venv\Scripts\python.exe" set "PYTHON_EXE=%SCRIPT_DIR%.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" if exist "%SCRIPT_DIR%.venv-2\Scripts\python.exe" set "PYTHON_EXE=%SCRIPT_DIR%.venv-2\Scripts\python.exe"
if not exist "%PYTHON_EXE%" if exist "%SCRIPT_DIR%.venv-1\Scripts\python.exe" set "PYTHON_EXE=%SCRIPT_DIR%.venv-1\Scripts\python.exe"

:parse_args
if "%~1"=="" goto after_args
if /I "%~1"=="-Host" (
    set "HOST=%~2"
    shift
    shift
    goto parse_args
)
if /I "%~1"=="-Port" (
    set "PORT=%~2"
    shift
    shift
    goto parse_args
)
if /I "%~1"=="-DataDir" (
    set "DATA_DIR=%~2"
    shift
    shift
    goto parse_args
)
if /I "%~1"=="-NoBrowser" (
    set "OPEN_BROWSER="
    shift
    goto parse_args
)
shift
goto parse_args

:after_args
"%PYTHON_EXE%" "%SCRIPT_DIR%run_web_app.py" --host "%HOST%" --port "%PORT%" --data-dir "%SCRIPT_DIR%%DATA_DIR%" %OPEN_BROWSER%
endlocal
