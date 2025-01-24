@echo off

if exist venv\Scripts\activate (
    call venv\Scripts\activate
) else (
    echo Virtual environment not found in the current folder.
    pause
    exit /b 1
)

python src/library.py
pause