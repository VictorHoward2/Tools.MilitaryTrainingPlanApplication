# Build script for Military Training Plan Application
# Usage: .\build_exe.ps1 [--onefile]

param(
    [switch]$onefile = $false
)

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Military Training Plan - Build Script" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if PyInstaller is installed
Write-Host "Checking if PyInstaller is installed..." -ForegroundColor Yellow
$pyinstaller = pip list | Select-String "pyinstaller"
if ($null -eq $pyinstaller) {
    Write-Host "PyInstaller not found. Installing..." -ForegroundColor Yellow
    pip install pyinstaller
}
else {
    Write-Host "PyInstaller found!" -ForegroundColor Green
}

# Check if main.spec exists
if (-not (Test-Path ".\main.spec")) {
    Write-Host "Error: main.spec not found!" -ForegroundColor Red
    Write-Host "Make sure you run this script from the project root directory" -ForegroundColor Red
    exit 1
}

# Clean previous builds
Write-Host ""
Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path ".\build") {
    Remove-Item -Recurse -Force ".\build"
    Write-Host "Removed ./build" -ForegroundColor Green
}
if (Test-Path ".\dist") {
    Remove-Item -Recurse -Force ".\dist"
    Write-Host "Removed ./dist" -ForegroundColor Green
}

# Build
Write-Host ""
Write-Host "Building .exe file..." -ForegroundColor Yellow

if ($onefile) {
    Write-Host "Mode: One-file (--onefile)" -ForegroundColor Cyan
    pyinstaller main.spec --onefile
}
else {
    Write-Host "Mode: One-dir (default)" -ForegroundColor Cyan
    pyinstaller main.spec
}

# Check if build was successful
Write-Host ""
if ((Test-Path ".\dist\MilitaryTrainingPlan.exe") -or (Test-Path ".\dist\MilitaryTrainingPlan\MilitaryTrainingPlan.exe")) {
    Write-Host "================================" -ForegroundColor Green
    Write-Host "Build completed successfully!" -ForegroundColor Green
    Write-Host "================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Executable location:" -ForegroundColor Cyan
    if (Test-Path ".\dist\MilitaryTrainingPlan.exe") {
        Write-Host "  .\dist\MilitaryTrainingPlan.exe" -ForegroundColor Green
    }
    else {
        Write-Host "  .\dist\MilitaryTrainingPlan\MilitaryTrainingPlan.exe" -ForegroundColor Green
    }
    Write-Host ""
    Write-Host "To run the application:" -ForegroundColor Cyan
    Write-Host "  .\dist\MilitaryTrainingPlan.exe" -ForegroundColor White
    Write-Host ""
    Write-Host "Default login:" -ForegroundColor Cyan
    Write-Host "  Username: admin" -ForegroundColor White
    Write-Host "  Password: admin" -ForegroundColor White
}
else {
    Write-Host "Build failed!" -ForegroundColor Red
    Write-Host "Check the error messages above" -ForegroundColor Red
    exit 1
}
