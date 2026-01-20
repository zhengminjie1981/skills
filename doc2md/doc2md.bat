@echo off
REM Doc2Md Portable Launcher for Windows

set SCRIPT_DIR=%~dp0
set PYTHONPATH=%SCRIPT_DIR%;%PYTHONPATH%

REM Try portable Python first, then system Python
if exist "%SCRIPT_DIR%\.venv\Scripts\python.exe" (
    "%SCRIPT_DIR%\.venv\Scripts\python.exe" "%SCRIPT_DIR%\scripts\converter.py" %*
) else (
    python "%SCRIPT_DIR%\scripts\converter.py" %*
)
