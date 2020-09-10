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

ECHO %CLR_CYN%Resetting the Git head to origin...%CLR_NIL%
git reset --hard origin

ECHO %CLR_CYN%Pulling the code from Github...%CLR_NIL%
git pull

ECHO %CLR_CYN%Installing/Upgrading the requirements...%CLR_NIL%
pip install -r requirements.txt --upgrade

ECHO %CLR_CYN%Executing post deployment script...%CLR_NIL%
py script_deploy.py

ECHO %CLR_GRN%Done deploying.%CLR_NIL%
PAUSE
