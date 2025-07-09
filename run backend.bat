@echo off
title Start CBSE Bot Backend
echo Loading environment and launching backend...

:: STEP 1: GO TO YOUR BACKEND FOLDER
cd /d "C:\Users\vforf\OneDrive\Desktop\Law bot\Backend"

:: STEP 2: OPTIONAL - ACTIVATE VENV IF YOU HAVE ONE
:: call venv\Scripts\activate

:: STEP 3: RUN THE APP (it will load .env automatically if you're using python-dotenv)
python app.py

pause
