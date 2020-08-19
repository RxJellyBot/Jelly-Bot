@ECHO OFF

SET LINTED=bot doc extdiscord extline extutils flags

:main

SET MSG=Checking Flake8 error...
ECHO %MSG%
flake8 . --config .flake8-error --benchmark || GOTO error

SET MSG=Checking Flake8 style...
ECHO %MSG%
flake8 . --config .flake8-style --benchmark || GOTO error

SET MSG=Checking pydocstyle...
ECHO %MSG%
pydocstyle %LINTED% --count || GOTO error

SET MSG=Checking pylint...
ECHO %MSG%
pylint %LINTED% || GOTO error

SET MSG=Running tests (unit)...
ECHO %MSG%
py manage.py test tests.unit || GOTO error

SET MSG=Running tests (integration)...
ECHO %MSG%
py manage.py test tests.integration || GOTO error

SET MSG=Running tests (system)...
ECHO %MSG%
py manage.py test tests.system || GOTO error

:pass

ECHO.
ECHO.
ECHO.
ECHO =============================================
ECHO ============== GREEN TO COMMIT ==============
ECHO =============================================
ECHO.
ECHO.
ECHO.

GOTO end

:error

ECHO ERROR @ %MSG%
PAUSE
EXIT /b

:end
