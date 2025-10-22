@echo off
setlocal

:: detect user directory dynamically
set "USER_DIR=%USERPROFILE%\GGD\Compiler"

python "%USER_DIR%\ggd.py" %*

endlocal
