from dataclasses import dataclass, field, InitVar
from gettext import gettext as _
from typing import List, Dict, Optional, Union
from inspect import signature

from msghandle.models import TextMessageEventObject
from extutils.checker import param_type_ensure
from extutils import is_empty_string
from extutils.logger import LoggerSkeleton

logger = LoggerSkeleton("sys.botcmd", logger_name_env="BOT_CMD")


@dataclass
class CommandParameter:
    name: str
    annotation: type


@dataclass
class CommandUsageDoc:
    usage: str
    description: str


@dataclass
class CommandFunction:
    arg_count: int
    arg_help: InitVar[List[str]]
    fn: callable
    cmd_node: 'CommandNode'
    description: str
    prm_keys: List[CommandParameter] = field(init=False)

    def __post_init__(self, arg_help):
        # List of parameters for future reference
        self.prm_keys = [CommandParameter(name, prm.annotation) for name, prm in signature(self.fn).parameters.items()]

        # Attach arguments help text to description
        self.description = f"{self.description}\n\n"

        for i in range(1, self.arg_count + 1):
            self.description += f"- `{self.prm_keys[i].name}` (`{self.prm_keys[i].annotation.__name__}`): " \
                                f"{arg_help[i - 1] if arg_help[i - 1] else 'N/A'}"

        self.description = self.description.strip()

    # Dynamically construct `usage` because `cmd_node.splittor` is required. Command structure wasn't ready
    # when executing __post_init__().

    @property
    def usage(self) -> str:
        s = self.cmd_node.get_usage(False)

        for i in range(1, self.arg_count + 1):
            s += self.cmd_node.splittor + f"({self.prm_keys[i].name})"

        return s


class CommandNode:
    # TEST: Test all bot commands
    def __init__(self, codes=None, order_idx=None, name=None, description=None,
                 is_root=False, splittor=None, prefix=None, parent=None):
        if codes:
            self._codes = CommandNode.parse_code(codes)
        else:
            if not is_root:
                raise ValueError(f"`codes` cannot be `None` if the command node is not root. "
                                 f"(Command Node: {self.__class__.__name__})")

        if is_root and (not splittor or not prefix):
            raise ValueError("`splittor` and `prefix` must be specified if the command node is root.")

        if not is_root and (splittor or prefix):
            raise ValueError("Specify `splittor` and `prefix` only when the node is root.")

        self._name = name
        self._description = description
        self._is_root = is_root
        self._splittor = splittor
        self._prefix = prefix
        self._order_idx = order_idx or 0
        self._parent = parent
        self._child_nodes: Dict[str, CommandNode] = {}  # {<CMD_CODES>: <COMMAND_NODE>}
        self._fn: Dict[int, CommandFunction] = {}  # {<ARG_COUNT>: <FUNCTION>}

    def _register_(self, arg_count: int, fn: CommandFunction):
        if arg_count in self._fn:
            logger.logger.warning(
                f"A function({self._fn[arg_count].fn.__qualname__}) has already existed in function holder. "
                f"{fn.fn.__qualname__} is going to replace it.")
        self._fn[arg_count] = fn

    @property
    def is_root(self) -> bool:
        return self._is_root

    @property
    def splittor(self) -> str:
        if self.is_root:
            return self._splittor
        elif self.parent:
            return self.parent.splittor
        else:
            raise ValueError(
                "Invalid node. Parent is not available while this node is not the root. "
                f"Make sure this command node ({repr(self)}) is attached to the desired root node.")

    @property
    def prefix(self) -> str:
        if self.is_root:
            return self._prefix
        elif self.parent:
            return self.parent.prefix
        else:
            raise ValueError(
                "Invalid node. Parent is not available while this node is not the root. "
                f"Make sure this command node ({repr(self)}) is attached to the desired root node.")

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
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value

    @property
    def child_nodes(self):
        """
        :rtype: Iterable[CommandNode]
        """
        return sorted(set(self._child_nodes.values()), key=lambda item: item.order_idx)

    def get_usage(self, incl_last_splittor: bool = False) -> str:
        current = self
        s = ""

        while current:
            if current.is_root:
                s = current.prefix + s
                break
            else:
                s = current.splittor + s
                s = current.main_cmd_code + s

            current = current.parent

        if not incl_last_splittor:
            s = s[:-len(self.splittor)]

        return s

    @property
    def name(self) -> Optional[str]:
        return self._name

    @property
    def description(self) -> Optional[str]:
        return self._description

    @property
    def max_arg_count(self) -> int:
        return max(self._fn.keys()) if self._fn else -1

    @property
    def functions(self) -> List[CommandFunction]:
        return [cf for cf in sorted(self._fn.values(), key=lambda item: item.arg_count)]

    @property
    def fn_list_for_doc(self) -> List[CommandUsageDoc]:
        ret = []

        for fn in self.functions:
            ret.append(CommandUsageDoc(fn.usage, fn.description))

        for node in self.child_nodes:
            ret.extend(node.fn_list_for_doc)

        return ret

    def new_child_node(self, codes: Union[str, List[str]], order_idx=None, name=None, description=None):
        codes = CommandNode.parse_code(codes)
        new = CommandNode(codes, order_idx, name, description)
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

        cmd_node.parent = self

        return cmd_node

    def get_child_node(self, code):
        """
        :rtype: CommandNode or None
        """
        return self._child_nodes.get(code)

    def command_function(
            self, fn: callable = None, arg_count: int = 0, arg_help: list = None,
            description: str = _("No description provided.")):
        """
        Function used to decorate the function to be ready to execute command.
        """
        if not arg_help:
            arg_help = []

        # Check the length of arg help and fill it with empty string if len(arg_help) is shorter.
        if len(arg_help) < arg_count:
            arg_help.extend(["" for _ in range(arg_count - len(arg_help))])

        def exec_in(f):
            s = signature(f)
            # This length count needs to include the first parameter - e: TextEventObject for every function
            if len(s.parameters) > arg_count:
                self._register_(arg_count, CommandFunction(arg_count, arg_help, f, self, description))
            else:
                logger.logger.warning(
                    f"Function `{f.__qualname__}` not registered because its argument length is insufficient.")

        if fn:
            exec_in(fn)
            return fn
        else:
            def wrapper(target_fn):
                exec_in(target_fn)
                return target_fn
            return wrapper

    def get_fn(self, arg_count: int) -> Optional[callable]:
        if arg_count in self._fn:
            return self._fn[arg_count].fn
        else:
            return None

    def _split_args_(self, s: str, arg_count: int) -> List[str]:
        if is_empty_string(s):
            return []
        elif arg_count == -1:
            return s.split(self.splittor)
        else:
            return s.split(self.splittor, arg_count - 1)

    def parse_args(self, e: TextMessageEventObject, max_arg_count: int = None) -> List[str]:
        if not max_arg_count:
            max_arg_count = self.max_arg_count

        s = e.content
        args = self._split_args_(s, max_arg_count)

        cmd_fn: Optional[callable] = self.get_fn(len(args))
        if cmd_fn:
            ret = param_type_ensure(cmd_fn)(e, *args)
            if isinstance(ret, str):
                ret = [str(ret)]

            return ret

        if s:
            cmd_code, cmd_args = args[0], args[1:]

            cmd_node: Optional[CommandNode] = self.get_child_node(code=cmd_code)
            if cmd_node:
                e.content = s[len(cmd_code) + len(self.splittor):]
                return cmd_node.parse_args(e, cmd_node.max_arg_count)

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
        return f"CommandNode {hex(id(self))} " \
               f"[ root={self.is_root} | code={'N/A' if self.is_root else self.main_cmd_code} | " \
               f"sub={len(set(self._child_nodes.values()))} | fn={len(self._fn)} ]"


class CommandHandler:
    def __init__(self, root_cmd_node: CommandNode):
        if not root_cmd_node.is_root:
            raise ValueError("Root Command Node is required for `CommandDispatcher`.")
        self._root = root_cmd_node

    def handle(self, e: TextMessageEventObject) -> List[str]:
        # Remove prefix from the string content
        e.content = e.content[len(self._root.prefix):]

        # Parse the command and return the response
        return self._root.parse_args(e)
