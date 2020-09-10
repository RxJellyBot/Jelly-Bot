#!/bin/sh

# ------ Variables

CLR_RED=[31m
CLR_NC=[0m

# ------ Functions

run_cmd_exit_on_err() {
  if ! $1; then
    echo "${CLR_RED}Error @ $2${CLR_NC}"
    exit 1
  fi
}

check_rebase() {
  BRANCH_NAME=$(git branch | sed "s/* //")

  if [ "$BRANCH_NAME" = "(no branch)" ]; then
    echo "Rebasing. Skipping the precommit checks."
    exit 0
  fi
}

# ------ Main

# Early terminate if rebasing
check_rebase

# Activate venv
# shellcheck disable=SC2039
source ./../Jelly-Bot-venv/Scripts/activate

# Execute precommit check for files
run_cmd_exit_on_err ./precommit-file.sh "Checks on changed files"

# Execute precommit total check
run_cmd_exit_on_err ./precommit-total.sh "Total check"
