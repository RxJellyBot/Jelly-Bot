from dataclasses import dataclass
from gettext import gettext as _
from typing import List, Dict, Optional, Union

from msghandle.models import TextMessageEventObject
from extutils.checker import param_type_ensure
from extutils import is_empty_string
from extutils.logger import LoggerSkeleton

logger = LoggerSkeleton("sys.botcmd", logger_name_env="BOT_CMD")


@dataclass
class CommandFunction:
    arg_count: int
    description: str
    fn: callable

    @property
    def example(self) -> str:
        # FIXME: [HP] Example string
        pass


class CommandNode:
    # TEST: Test all bot commands
    def __init__(self, codes=None, order_idx=0, name=None, description=None, is_root=False):
        if codes:
            self._codes = CommandNode.parse_code(codes)
        else:
            if not is_root:
                raise ValueError(f"`codes` cannot be `None` if the command node is not root. "
                                 f"(Command Node: {self.__class__.__name__})")
        self._name = name
        self._description = description
        self._is_root = is_root
        self._order_idx = order_idx
        self._child_nodes: Dict[str, CommandNode] = {}  # {<CMD_CODES>: <COMMAND_NODE>}
        self._fn: Dict[int, CommandFunction] = {}  # {<ARG_COUNT>: <FUNCTION>}

    def _register_(self, arg_count: int, fn: CommandFunction):
        if arg_count in self._fn:
            logger.logger.warning(f"A function has already existed in function holder. ({self._fn.__qualname__}) "
                                  f"{fn.__qualname__} is going to replace it.")
        self._fn[arg_count] = fn

    @property
    def is_root(self) -> bool:
        return self._is_root

    @property
    def command_codes(self) -> List[str]:
        return self._codes

    @property
    def main_cmd_code(self) -> str:
        return self.command_codes[0]

    @property
    def aliases(self) -> List[str]:
        return self.command_codes[1:]

    @property
    def order_idx(self) -> int:
        """This property is mainly used for the commands list generation."""
        return self._order_idx

    @property
    def child_nodes(self):
        """
        :rtype: Iterable[CommandNode]
        """
        return sorted(set(self._child_nodes.values()), key=lambda item: item.order_idx)

    @property
    def full_cmd(self) -> str:
        # FIXME: [HP] Full command called already from the root cmd node. For example, "jc uintg", "jc replace"
        pass

    @property
    def name(self) -> Optional[str]:
        return self._name

    @property
    def description(self) -> Optional[str]:
        return self._description

    @property
    def max_arg_count(self) -> int:
        return max(self._fn.keys())

    @property
    def functions(self) -> List[CommandFunction]:
        return [cf for cf in sorted(self._fn.values(), key=lambda item: item.arg_count)]

    def new_child_node(self, codes: Union[str, List[str]], name=None, description=None):
        codes = CommandNode.parse_code(codes)
        new = CommandNode(codes, name, description)
        self.attach_child_node(new)
        return new

    def attach_child_node(self, cmd_node):
        """
        :type cmd_node: CommandNode
        :rtype: CommandNode
        """
        for code in cmd_node.command_codes:
            if code in self._child_nodes:
                logger.logger.warning(f"Code {code} has a corresponding command node ({repr(self._child_nodes[code])}) "
                                      f"registered. This will be replaced by {repr(cmd_node)}")
            self._child_nodes[code] = cmd_node

        return cmd_node

    def get_child_node(self, code):
        """
        :rtype: CommandNode or None
        """
        return self._child_nodes.get(code)

    def command_function(
            self, fn: callable = None, arg_count: int = 0,
            description: str = _("No description provided.")):
        """
        Function to use to decorate the function to execute command.
        """
        # Function argument count check
        if fn:
            self._register_(arg_count, CommandFunction(arg_count, fn, description))
            return fn
        else:
            def wrapper(target_fn):
                self._register_(arg_count, CommandFunction(arg_count, target_fn, description))
                return target_fn
            return wrapper

    def get_fn(self, arg_count: int) -> Optional[callable]:
        if arg_count in self._fn:
            return self._fn[arg_count].fn
        else:
            return None

    def parse_args(self, e: TextMessageEventObject, splittor: str) -> List[str]:
        s = e.content
        args = [] if is_empty_string(s) else s.split(splittor, self.max_arg_count)

        cmd_fn: Optional[callable] = self.get_fn(len(args))
        if cmd_fn:
            ret = param_type_ensure(cmd_fn)(e, *args)
            if not isinstance(ret, str):
                ret = [str(ret)]

            return ret

        if s:
            cmd_code, cmd_args = args[0], args[1:]

            cmd_node: Optional[CommandNode] = self.get_child_node(code=cmd_code)
            if cmd_node:
                return cmd_node.parse_args(s[len(cmd_code):], splittor)

        return []

    @staticmethod
    def parse_code(codes) -> List[str]:
        if isinstance(codes, list):
            return codes
        elif isinstance(codes, str):
            return [codes]
        else:
            raise ValueError(f"Parameter `codes` should be either `List[str]` or `str`. ({codes})")

    def __repr__(self):
        return f"CommandNode #{id(self)} " \
               f"[root={self.is_root}|code={','.join(self._codes)}|sub={len(self._child_nodes)}|fn={len(self._fn)}]"


class CommandHandler:
    def __init__(self, root_cmd_node: CommandNode):
        if not root_cmd_node.is_root:
            raise ValueError("Root Command Node is required for `CommandDispatcher`.")
        self._root = root_cmd_node

    def handle(self, e: TextMessageEventObject, splittor: str) -> List[str]:
        return self._root.parse_args(e, splittor)
