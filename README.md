Put the files in a EMPTY folder
Then open administerater CMD and type in
```
setx "C:\Path\To\Your\Folder;%PATH%"
exit
```
then start CMD or PS and type in GGD, if it does not work, you did not follow the instructions correctly.

Also it will best work when you do this in admin CMD:
```
mkdir C:\Users\<Username>\GGD
cd C:\Users\<Username>\GGD
mkdir compiler
cd compiler
git clone https://github.com/GGD-Coding-language/GGD-Command-Line.git
setx "C:\Users\<Username>\GGD\compiler;%PATH"
echo %path%
echo You should see "C:\Users\<Username>\GGD\compiler" in there ↑
echo After this please type in EXIT to confirm you are done,
echo If you do not see "C:\Users\<Username>\GGD\compiler" then please send us a email :)
```
