@echo off
rmdir /s /q doc dist

call gendocs.bat
python -m build

twine upload dist/*
