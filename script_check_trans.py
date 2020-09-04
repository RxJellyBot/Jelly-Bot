"""Script to check if the translations are completed in GitHub Actions."""
import glob
import os
import sys

from django.core.management import call_command


def invalid_found(line_no):
    """
    Method to be called when an invalid line is found.

    This method terminates the program with exit code 1.

    :param line_no: line # of the invalid line
    """
    print(f"[ERROR] Invalid line detected @ Line {line_no}")
    sys.exit(1)


def make_po_file():
    """
    Method to make a po file.

    Will cleanup and retry if the somehow the translation file creation failed and leave a lot of .html.py files.
    """
    # Call Django admin command `makemessages` to create po file
    try:
        call_command("makemessages", all=True)
    except PermissionError:
        print("[WARNING] Error occurred, retry to create po file")

        # Occasionally fails and creates a lot of .html.py dummy file
        for path in glob.glob("*.html.py"):
            os.unlink(path)

        call_command("makemessages", all=True)


def check_po_file():
    """Method to check the po file."""
    in_entry = False
    empty_msgstr = False

    with open("locale/zh_TW/LC_MESSAGES/django.po", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            # `line` will have a `\n` at the end so it needs to be stripped
            line: str = line.strip()

            # Set `in_entry` flag to `True` if found an entry head
            if line.startswith("#: "):
                in_entry = True
            # Set `in_entry` flag to `False` if found an empty line (out/end of entry)
            # Also check if empty msgstr was found and then out of entry
            elif not line:
                if empty_msgstr:
                    invalid_found(line_no)
                in_entry = False

            # Check for fuzzy line
            if line.startswith("#, fuzzy"):
                invalid_found(line_no)

            # Check in-entry empty msgstr
            empty_msgstr = in_entry and line == 'msgstr ""'


def make_mo_file():
    """Method to make mo file."""
    # Call Django admin command `compilemessages` to create mo file
    call_command("compilemessages")


def main():
    """Main execution flow of checking the translation completeness."""
    make_po_file()
    check_po_file()
    make_mo_file()


if __name__ == '__main__':
    main()
