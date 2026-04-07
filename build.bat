@echo off
setlocal

REM Build Windows executable with assets included
py -m pip install --upgrade pyinstaller
if errorlevel 1 goto :error

py -m PyInstaller --noconfirm --clean --onefile --windowed --name SpaceInvaders --add-data "assets;assets" main.py
if errorlevel 1 goto :error

echo.
echo Build completed successfully.
echo Executable: dist\SpaceInvaders.exe
goto :end

:error
echo.
echo Build failed. Check the errors above.
exit /b 1

:end
endlocal
