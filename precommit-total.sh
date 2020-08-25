#!/bin/sh

# ------ Variables

# Colors to be used

CLR_RED=[31m
CLR_GREEN=[32m
CLR_YELLOW=[33m
CLR_MAGENTA=[35m
CLR_CYAN=[36m
CLR_NC=[0m

# Linted modules
linted_modules="bot doc extdiscord extline extutils flags"

# ------ Functions

# Execute a django test of the module $1.
exec_django_test() {
  echo
  echo "${CLR_YELLOW}Running tests ($1)...${CLR_NC}"
  echo
  run_cmd_exit_on_err "py manage.py test $1 --failfast" "Django test ($1) - try run the tests using IDE"
}

# Runs command $1.
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

# Print the intro output
print_intro() {
  echo
  echo "${CLR_CYAN}Checking the whole project...${CLR_NC}"
  echo
}

# Check for errors with flake8
check_flake8_error() {
  echo
  echo "${CLR_YELLOW}Checking Flake8 error...${CLR_NC}"
  echo
  run_cmd_exit_on_err "flake8 $linted_modules --config .flake8-error --benchmark" "flake8 error check"
}

# Check for stylistic errors with flake8
check_flake8_style() {
  echo
  echo "${CLR_YELLOW}Checking Flake8 style...${CLR_NC}"
  echo
  run_cmd_exit_on_err "flake8 $linted_modules --config .flake8-style --benchmark" "flake8 style check"
}

# Lint with pydocstyle
check_pydocstyle() {
  echo
  echo "${CLR_YELLOW}Checking pydocstyle...${CLR_NC}"
  echo
  run_cmd_exit_on_err "pydocstyle $linted_modules --count" "pydocstyle check"
}

# Lint with pylint
check_pylint() {
  echo
  echo "${CLR_YELLOW}Checking pylint...${CLR_NC}"
  echo
  run_cmd_exit_on_err "pylint $linted_modules" "pylint check"
}

# Check translations
check_translations() {
  echo
  echo "${CLR_YELLOW}Checking translations...${CLR_NC}"
  echo
  run_cmd_exit_on_err "py script_check_trans.py" "translations check - incomplete translation"
}

# Django test - unit
django_test_unit() {
  exec_django_test "tests.unit"
}

# Django test - integration
django_test_integration() {
  exec_django_test "tests.integration"
}

# Django test - system
django_test_system() {
  exec_django_test "tests.system"
}

# Print the passing message
print_pass_message() {
  echo "${CLR_GREEN}Project check PASSED${CLR_NC}"
}

# ------ Main

# Intro
print_intro

# Code linting
check_flake8_error
check_flake8_style
check_pydocstyle
check_pylint
check_translations

# Tests
django_test_unit
django_test_integration
django_test_system

# Outro
print_pass_message
