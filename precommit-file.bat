@ECHO OFF

REM - Colors to be used
SET RED=[31m
SET GREEN=[32m
SET YELLOW=[33m
SET BG_CYAN=[46m
SET NC=[0m

:intro

ECHO.
ECHO ==========================
ECHO = %BG_CYAN%Checking Changed Files%NC% =
ECHO ==========================
ECHO.
ECHO %YELLOW%Changed Files%NC%
ECHO %~1

:main

SET MSG=Checking Flake8 error...
ECHO.
ECHO %YELLOW%%MSG%%NC%
ECHO.
flake8 %~1 --config .flake8-error --benchmark || GOTO fail

SET MSG=Checking Flake8 style...
ECHO.
ECHO %YELLOW%%MSG%%NC%
ECHO.
flake8 %~1 --config .flake8-style --benchmark || GOTO fail

SET MSG=Checking pydocstyle...
ECHO.
ECHO %YELLOW%%MSG%%NC%
ECHO.
pydocstyle %~1 --count || GOTO fail

SET MSG=Checking pylint...
ECHO.
ECHO %YELLOW%%MSG%%NC%
ECHO.
pylint %~1 || GOTO fail

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
