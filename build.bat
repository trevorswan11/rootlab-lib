@echo off
echo "This is only for initial deployments, are you sure?"
PAUSE
python -m build
twine upload --repository-url https://upload.pypi.org/legacy/ dist/*
