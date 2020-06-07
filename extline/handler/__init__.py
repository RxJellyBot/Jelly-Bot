"""
Contains various functions for handling different type of event.
"""

from .main import handle_main
from .message import handle_msg_main
from .default import handle_default
from .error import handle_error
from .self import handle_self_main
from .member import handle_member_main
