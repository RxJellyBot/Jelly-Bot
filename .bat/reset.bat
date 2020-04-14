@ECHO OFF
SET /P commit_revert="# of commits to revert > "
git reset --hard HEAD~%commit_revert%
PAUSE