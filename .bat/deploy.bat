@ECHO OFF

SET CLR_GRN=[32m
SET CLR_CYN=[36m
SET CLR_NIL=[0m

ECHO %CLR_CYN%Heading to the venv directory...%CLR_NIL%
cd ../../venv/Scripts

ECHO %CLR_CYN%Activating venv...%CLR_NIL%
call activate

ECHO %CLR_CYN%Heading back to the repo root...%CLR_NIL%
cd ../../Jelly-Bot

ECHO %CLR_CYN%Updating the current code to the latest version (1/3)...%CLR_NIL%
git reset --hard origin || GOTO :error

ECHO %CLR_CYN%Updating the current code to the latest version (2/3)...%CLR_NIL%
git pull || GOTO :error

ECHO %CLR_CYN%Updating the current code to the latest version (3/3)...%CLR_NIL%
git reset --hard origin || GOTO :error

ECHO %CLR_CYN%Installing/Upgrading the requirements...%CLR_NIL%
pip install -r requirements.txt --upgrade

ECHO %CLR_CYN%Executing post deployment script...%CLR_NIL%
py script_deploy.py

ECHO %CLR_GRN%Done deploying.%CLR_NIL%
PAUSE
