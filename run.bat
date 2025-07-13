@echo off
REM ─────────────────────────────────────────────────────────────
REM 1) Point to your Anaconda install root (adjust if needed)
set "CONDA_ROOT=%USERPROFILE%\anaconda3"

REM 2) Initialize conda commands in this shell and activate env
call "%CONDA_ROOT%\condabin\conda.bat" activate pdfenv

IF ERRORLEVEL 1 (
  echo Failed to activate pdfenv. Check that pdfenv exists.
  pause
  exit /b 1
)

REM 3) Run the analyzer on any arguments (or adjust the default "test_folder")
if "%~1"=="" (
  python "%~dp0analyze.py" "%~dp0pdf_folder" -o "%~dp0report.txt"
) else (
  python "%~dp0analyze.py" %*
)

REM 4) Keep the window open so you see the output
echo.
pause
