@ECHO OFF

ECHO Checking Flake8 error...
flake8 . --config .flake8-error --benchmark || ECHO ERROR && PAUSE && EXIT /b

ECHO Checking Flake8 style...
flake8 . --config .flake8-style --benchmark || ECHO ERROR && PAUSE && EXIT /b

ECHO Checking pydocstyle...
pydocstyle bot doc extdiscord extline extutils --count || ECHO ERROR && PAUSE && EXIT /b

ECHO Checking pylint...
pylint bot doc extdiscord extline extutils || ECHO ERROR && PAUSE && EXIT /b

ECHO Running tests (pytest)...
pytest || ECHO ERROR && PAUSE && EXIT /b

ECHO.
ECHO.
ECHO.
ECHO =============================================
ECHO ============== GREEN TO COMMIT ==============
ECHO =============================================
ECHO.
ECHO.
ECHO.
