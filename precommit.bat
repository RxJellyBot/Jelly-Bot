@ECHO OFF

REM - Colors to be used
SET RED=[31m
SET GREEN=[32m
SET BG_MAGENTA=[45m
SET NC=[0m

:intro

ECHO.
ECHO ======================================================================
ECHO = %BG_MAGENTA%Invoked precommit checks using main precommit file (precommit.bat)%NC% =
ECHO ======================================================================
ECHO.

:main

precommit-total || GOTO fail

:pass

ECHO.
ECHO =============================================
ECHO ============== %GREEN%GREEN TO COMMIT%NC% ==============
ECHO =============================================
ECHO.

GOTO end

:fail

ECHO.
ECHO ==========================================
ECHO ========= %RED%Precommit check FAILED%NC% =========
ECHO ==========================================
ECHO.
EXIT /B 1

:end
