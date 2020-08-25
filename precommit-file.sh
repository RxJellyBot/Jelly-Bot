#!/bin/sh

# ------ Variables

# Colors to be used

CLR_RED=[31m
CLR_GREEN=[32m
CLR_YELLOW=[33m
CLR_MAGENTA=[35m
CLR_CYAN=[36m
CLR_NC=[0m

# ------ Functions

# This function runs the command $1.
# If it returns error, print "Error @ $2" and exit the script with code 1.
#
# 1st parameter: command to run
# 2nd parameter: text to output if error
run_cmd_exit_on_err() {
  echo "Command to run: ${CLR_MAGENTA}$1${CLR_NC}"
  if ! $1; then
    echo "${CLR_RED}Error @ $2${CLR_NC}"
    exit 1
  fi
}

# ------ Subroutines

# Check for the list of changed files and print it as a list,
# then store it to $changed_files where file names will be separated by spaces.
check_changed_files() {
  changed_files=$(git diff --cached --name-only --diff-filter "d" "*.py" ":!tests" | sed -z "s/\n/ /gm")

  if [ -z "$changed_files" ]; then
    echo
    echo "${CLR_GREEN}No changed files to be checked, skipping the file check.${CLR_NC}"
    echo
    exit 0
  fi

  echo
  echo "${CLR_CYAN}Checking Changed Files...${CLR_NC}"
  echo
  echo "${CLR_YELLOW}Changed Files (to be checked)${CLR_NC}"
  git diff --cached --stat "*.py"
  echo
}

# Check for errors with flake8.
check_flake8_error() {
  echo
  echo "${CLR_YELLOW}Checking Flake8 error...${CLR_NC}"
  echo
  run_cmd_exit_on_err "flake8 $changed_files --config .flake8-error --benchmark" "flake8 error check"
}

# Check for stylistic errors with flake8.
check_flake8_style() {
  echo
  echo "${CLR_YELLOW}Checking Flake8 style...${CLR_NC}"
  echo
  run_cmd_exit_on_err "flake8 $changed_files --config .flake8-style --benchmark" "flake8 style check"
}

# Lint with pydocstyle.
check_pydocstyle() {
  echo
  echo "${CLR_YELLOW}Checking pydocstyle...${CLR_NC}"
  echo
  run_cmd_exit_on_err "pydocstyle $changed_files --count" "pydocstyle check"
}

# Lint with pylint.
check_pylint() {
  echo
  echo "${CLR_YELLOW}Checking pylint...${CLR_NC}"
  echo
  run_cmd_exit_on_err "pylint $changed_files" "pylint check"
}

# Print the passing message
print_pass_message() {
  echo "${CLR_GREEN}Check on changed files PASSED${CLR_NC}"
}

# ------ Main

check_changed_files

check_flake8_error
check_flake8_style
check_pydocstyle
check_pylint

print_pass_message
