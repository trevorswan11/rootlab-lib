@echo off
rmdir /s /q doc dist

pdoc -o doc -d markdown rootlab_lib
python -m build

twine upload dist/*
