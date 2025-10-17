@echo off
set "USER_DIR=%USERPROFILE%"
set "GGD_PATH=%USER_DIR%\GGD\Compiler"
python "%GGD_PATH%\ggd.py" %*
