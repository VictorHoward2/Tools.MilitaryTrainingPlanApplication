@echo off
REM Build script for Military Training Plan Application
REM Usage: build_exe.bat [onefile]

setlocal enabledelayedexpansion

echo.
echo ================================
echo Military Training Plan - Build Script
echo ================================
echo.

REM Check if PyInstaller is installed
echo Checking if PyInstaller is installed...
pip list | findstr /C:"pyinstaller" >nul
if %errorlevel% neq 0 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
    if %errorlevel% neq 0 (
        echo Failed to install PyInstaller
        pause
        exit /b 1
    )
) else (
    echo PyInstaller found!
)

REM Check if main.spec exists
if not exist "main.spec" (
    echo Error: main.spec not found!
    echo Make sure you run this script from the project root directory
    pause
    exit /b 1
)

REM Clean previous builds
echo.
echo Cleaning previous builds...
if exist "build" (
    rmdir /s /q "build"
    echo Removed ./build
)
if exist "dist" (
    rmdir /s /q "dist"
    echo Removed ./dist
)

REM Build
echo.
echo Building .exe file...
if "%1"=="onefile" (
    echo Mode: One-file (--onefile)
    pyinstaller main.spec --onefile
) else (
    echo Mode: One-dir ^(default^)
    pyinstaller main.spec
)

REM Check if build was successful
echo.
if exist "dist\MilitaryTrainingPlan.exe" (
    echo.
    echo ================================
    echo Build completed successfully!
    echo ================================
    echo.
    echo Executable location:
    echo   .\dist\MilitaryTrainingPlan.exe
    echo.
    echo To run the application:
    echo   .\dist\MilitaryTrainingPlan.exe
    echo.
    echo Default login:
    echo   Username: admin
    echo   Password: admin
    echo.
    echo.
) else if exist "dist\MilitaryTrainingPlan\MilitaryTrainingPlan.exe" (
    echo.
    echo ================================
    echo Build completed successfully!
    echo ================================
    echo.
    echo Executable location:
    echo   .\dist\MilitaryTrainingPlan\MilitaryTrainingPlan.exe
    echo.
    echo To run the application:
    echo   .\dist\MilitaryTrainingPlan\MilitaryTrainingPlan.exe
    echo.
    echo Default login:
    echo   Username: admin
    echo   Password: admin
    echo.
    echo.
) else (
    echo.
    echo Build failed!
    echo Check the error messages above
    echo.
    pause
    exit /b 1
)

pause
