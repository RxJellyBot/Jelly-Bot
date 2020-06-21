@ECHO OFF

ECHO Checking Flake8 Error...
flake8 . --config .flake8-error || ECHO ERROR && PAUSE && EXIT /b

ECHO Checking Flake8 style...
flake8 . --config .flake8-style || ECHO ERROR && PAUSE && EXIT /b

ECHO Checking pylint...
pylint bot doc extdiscord extline || ECHO ERROR && PAUSE && EXIT /b

ECHO Running tests
py manage.py test tests || ECHO ERROR && PAUSE && EXIT /b

ECHO.
ECHO.
ECHO.
ECHO =============================================
ECHO ============== GREEN TO COMMIT ==============
ECHO =============================================
ECHO.