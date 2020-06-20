flake8 . --config .flake8-error || ECHO ERROR && PAUSE && EXIT /b
flake8 . --config .flake8-style || ECHO ERROR && PAUSE && EXIT /b
pylint rxtoolbox || ECHO ERROR && PAUSE && EXIT /b
py -m unittest tests || ECHO ERROR && PAUSE && EXIT /b