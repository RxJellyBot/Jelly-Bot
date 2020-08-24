@ECHO OFF

REM - Colors to be used
SET RED=[31m
SET GREEN=[32m
SET YELLOW=[33m
SET BG_CYAN=[46m
SET NC=[0m

SET LINTED=bot doc extdiscord extline extutils flags

:intro

ECHO.
ECHO =========================================
ECHO = %BG_CYAN%Performing total check on the project%NC% =
ECHO =========================================
ECHO.

:main

SET MSG=Checking Flake8 error...
ECHO.
ECHO %YELLOW%%MSG%%NC%
ECHO.
flake8 . --config .flake8-error --benchmark || GOTO fail

SET MSG=Checking Flake8 style...
ECHO.
ECHO %YELLOW%%MSG%%NC%
ECHO.
flake8 . --config .flake8-style --benchmark || GOTO fail

SET MSG=Checking pydocstyle...
ECHO.
ECHO %YELLOW%%MSG%%NC%
ECHO.
pydocstyle %LINTED% --count || GOTO fail

SET MSG=Checking pylint...
ECHO.
ECHO %YELLOW%%MSG%%NC%
ECHO.
pylint %LINTED% || GOTO fail

SET MSG=Checking translations...
ECHO.
ECHO %YELLOW%%MSG%%NC%
ECHO.
py script_check_trans.py || GOTO fail

SET MSG=Running tests (unit)...
ECHO.
ECHO %YELLOW%%MSG%%NC%
ECHO.
py manage.py test tests.unit || GOTO fail

SET MSG=Running tests (integration)...
ECHO.
ECHO %YELLOW%%MSG%%NC%
ECHO.
py manage.py test tests.integration || GOTO fail

SET MSG=Running tests (system)...
ECHO.
ECHO %YELLOW%%MSG%%NC%
ECHO.
py manage.py test tests.system || GOTO fail

:pass

ECHO.
ECHO ==========================================
ECHO ============== %GREEN%CHECK PASSED%NC% ==============
ECHO ==========================================
ECHO.

GOTO end

:fail

ECHO.
ECHO ==========================================
ECHO %RED%FAILED @ %MSG%%NC%
ECHO ==========================================
ECHO.
EXIT /B 1

:end
