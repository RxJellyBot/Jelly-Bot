from collections import defaultdict
from dataclasses import dataclass, field
from time import monotonic
from typing import List, Dict, Optional, Union, Callable, Tuple
from inspect import signature

from bson import ObjectId
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from flags import CommandScopeCollection, CommandScope, ChannelType, BotFeature
from msghandle.models import TextMessageEventObject, HandledMessageEventText
from mongodb.factory import BotFeatureUsageDataManager
from JellyBot.systemconfig import HostUrl
from extutils.checker import param_type_ensure, NonSafeDataTypeConverter, TypeCastingFailed
from extutils.logger import LoggerSkeleton
from extutils.strtrans import type_translation

logger = LoggerSkeleton("sys.botcmd", logger_name_env="BOT_CMD")


@dataclass
class CommandParameter:
    name: str
    annotation_name: str


@dataclass
class CommandFunction:
    arg_count: int
    arg_help: List[str]
    fn: callable
    cmd_node: 'CommandNode'
    cmd_feature: BotFeature
    description: str
    scope: CommandScope
    cooldown_sec: int
    last_call: Dict[ObjectId, float] = field(init=False)
    prm_keys: List[CommandParameter] = field(init=False)

    def __post_init__(self):
        # List of parameters for future reference
        self.prm_keys = [CommandParameter(name, prm.annotation.__name__)
                         for name, prm in signature(self.fn).parameters.items()]
        self.last_call = defaultdict(lambda: -self.cooldown_sec)
        self._cache = {}

    # Dynamically construct `usage` because `cmd_node.splitter` is required. Command structure wasn't ready
    # when executing __post_init__().
    @property
    def usage(self) -> str:
        k = "usage"

        if k not in self._cache:
            s = self.cmd_node.get_usage()

            for i in range(1, self.arg_count + 1):
                s += self.cmd_node.main_splitter + f"({self.prm_keys[i].name})"

            self._cache[k] = s.strip()

        return self._cache[k]

    @property
    def all_usage(self) -> List[str]:
        k = "all_usage"

        if k not in self._cache:
            ret = []

            for usage in self.cmd_node.get_all_usage():
                for i in range(1, self.arg_count + 1):
                    usage += self.cmd_node.main_splitter + f"({self.prm_keys[i].name})"

                ret.append(usage.strip())

            self._cache[k] = ret

        return self._cache[k]

    @property
    def parallel_param_list(self) -> Tuple[CommandParameter, str]:
        for i in range(1, self.arg_count + 1):
            yield self.prm_keys[i], self.arg_help[i - 1]

    @property
    def function_id(self) -> int:
        # For documentation uniqueness identifying use
        return id(self.fn)

    def can_be_called(self, channel_oid: ObjectId) -> bool:
        return (monotonic() - self.last_call[channel_oid]) > self.cooldown_sec

    def cd_sec_left(self, channel_oid: ObjectId) -> float:
        return max(self.cooldown_sec - (monotonic() - self.last_call[channel_oid]), 0)

    @property
    def has_cooldown(self) -> int:
        return self.cooldown_sec > 0

    def record_called(self, channel_oid: ObjectId):
        self.last_call[channel_oid] = monotonic()

    def __eq__(self, other):
        return self.function_id == other.function_id

    def __hash__(self):
        return self.function_id


class CommandNode:
    def __init__(self, *, codes=None, order_idx=None, name=None, description=None, brief_description=None,
                 is_root=False, splitters=None, prefix=None, parent=None, case_insensitive=True):
        if codes:
            self._codes = CommandNode.parse_code(codes)
        else:
            if not is_root:
                raise ValueError(f"`codes` cannot be `None` if the command node is not root. "
                                 f"(Command Node: {self.__class__.__name__})")

        if is_root and (not splitters or not prefix):
            raise ValueError("`splitters` and `prefix` must be specified if the command node is root.")

        if not is_root and (splitters or prefix):
            raise ValueError("Specify `splitters` and `prefix` only when the node is root.")

        self._name = name
        self._description = description
        self._brief_description = brief_description or description
        self._is_root = is_root
        self._splitters = splitters
        self._prefix = prefix
        self._order_idx = order_idx or 0
        self._parent = parent
        self._child_nodes: Dict[str, CommandNode] = {}  # {<CMD_CODES>: <COMMAND_NODE>}
        self._fn: Dict[int, CommandFunction] = {}  # {<ARG_COUNT>: <FUNCTION>}
        self._case_insensitive = case_insensitive
        self._fn_cache = {}

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
    def splitters(self) -> List[str]:
        return self._splitters

    @property
    def main_splitter(self) -> str:
        if self.is_root:
            return self._splitters[0]
        elif self.parent:
            return self.parent.main_splitter
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

    @property
    def case_insensitive(self) -> bool:
        return self._case_insensitive

    def get_usage(self) -> str:
        current = self
        s = ""

        while current:
            if current.is_root:
                s = current.prefix + current.main_splitter + s
                break
            else:
                s = current.main_splitter + s
                s = current.main_cmd_code + s

            current = current.parent

        s = s[:-len(self.main_splitter)]

        return s

    def _get_usage_all_code_(self, node, suffix):
        if node.is_root:
            return [str(node.prefix + node.main_splitter + suffix)]
        else:
            ret = []

            for code in node.command_codes:
                ret.extend(self._get_usage_all_code_(node.parent, code + node.main_splitter + suffix))

            return ret

    def get_all_usage(self) -> List[str]:
        return self._get_usage_all_code_(self, "")

    @property
    def name(self) -> Optional[str]:
        return self._name

    @property
    def description(self) -> Optional[str]:
        return self._description

    @property
    def brief_description(self) -> Optional[str]:
        return self._brief_description

    @property
    def max_arg_count(self) -> int:
        return max(self._fn.keys()) if self._fn else -1

    @property
    def functions(self) -> List[CommandFunction]:
        return [cf for cf in sorted(self._fn.values(), key=lambda item: item.arg_count)]

    @property
    def functions_incl_child(self) -> List[CommandFunction]:
        ret = self.functions

        for node in self.child_nodes:
            ret.extend(node.functions)

        return ret

    def new_child_node(self, *, codes: Union[str, List[str]], order_idx=None, name=None, description=None):
        codes = CommandNode.parse_code(codes)
        new = CommandNode(codes=codes, order_idx=order_idx, name=name, description=description)
        self.attach_child_node(new)
        return new

    def attach_child_node(self, cmd_node):
        """
        :type cmd_node: CommandNode
        :rtype: CommandNode
        """
        for code in cmd_node.command_codes:
            if code in self._child_nodes and id(self._child_nodes[code]) != id(cmd_node):
                logger.logger.warning(f"Code {code} has a corresponding command node ({repr(self._child_nodes[code])}) "
                                      f"registered. This will be replaced by {repr(cmd_node)}")

            if self._case_insensitive:
                code = code.lower()

            self._child_nodes[code] = cmd_node

        cmd_node.parent = self

        return cmd_node

    def get_child_node(self, code):
        """
        :rtype: CommandNode or None
        """
        if self._case_insensitive:
            code = code.lower()

        return self._child_nodes.get(code)

    def command_function(
            self, fn: Callable = None, *, arg_count: int = 0, arg_help: List[str] = None,
            description: str = _("No description provided."),
            scope: CommandScope = CommandScopeCollection.NOT_RESTRICTED,
            feature_flag: BotFeature = BotFeature.UNDEFINED, cooldown_sec: int = 0):
        """
        Function used to decorate the function to be ready to execute command.

        :param fn: No need to specify as the decorator will automatically use it.
        :param arg_count: The count of the arguments indicating when will the `fn` be executed.
        :param arg_help: Help of each arguments.
        :param description: Description of the command function.
        This will be replaced by the description of `feature_flag` even if specified.
        :param scope: Usable scope of the command function.
        :param feature_flag: Feature flag of the command function.
        """
        if not arg_help:
            arg_help = []

        if feature_flag != BotFeature.UNDEFINED:
            description = feature_flag.description

        # Check the length of arg help and fill it with empty string if len(arg_help) is shorter.
        if len(arg_help) < arg_count:
            arg_help.extend(["" for _ in range(arg_count - len(arg_help))])

        def exec_in(f):
            s = signature(f)
            # This length count needs to include the first parameter - e: TextEventObject for every function
            if len(s.parameters) > arg_count:
                self._register_(
                    arg_count, CommandFunction(
                        arg_count, arg_help, f, self, feature_flag, description, scope, cooldown_sec))
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

    def get_fn_obj(self, arg_count: int) -> Optional[CommandFunction]:
        if arg_count in self._fn:
            return self._fn[arg_count]
        else:
            return None

    @staticmethod
    def _split_args_(s: str, splitter: str, arg_count: int) -> List[str]:
        if not s:
            return []

        ret = []
        in_quote = False
        proc_s = ""

        def is_quote(c_):
            return c_ in ("'", "\"", "“", "”")

        for idx, c in enumerate(s):
            is_splitter = c == splitter
            if (not in_quote and is_splitter) or (in_quote and is_quote(c)):
                ret.append(proc_s)

                if arg_count != -1 and len(ret) >= arg_count:
                    break

                proc_s = ""
            elif is_quote(c):
                in_quote = True
            elif not(not in_quote and is_splitter):
                """
                In quote, is splitter, append string
                0 0 1
                0 1 0
                1 0 1
                1 1 1
                """
                proc_s += c

        if proc_s:
            ret.append(proc_s)

        return ret

    @staticmethod
    def _sanitize_args_(args_list: List[str]):
        return [arg.strip() for arg in args_list if arg]

    @staticmethod
    def _merge_overlength_args_(args_list: List[str], splitter: str, max_count: int):
        if 0 < max_count < len(args_list):
            idx = max_count - 1
            args_list[idx] = splitter.join(args_list[idx:])

        if max_count > 0:
            return args_list[:max_count]
        else:
            return args_list

    def parse_args(
            self, e: TextMessageEventObject, splitter, max_arg_count: int = None,
            args: List[str] = None, is_sub=False) \
            -> List[HandledMessageEventText]:
        if not max_arg_count:
            max_arg_count = self.max_arg_count

        if args is None:
            args = self._split_args_(e.content, splitter, max_arg_count)
            args = self._sanitize_args_(args)

        args = self._merge_overlength_args_(args, splitter, max_arg_count)

        cmd_fn: Optional[CommandFunction] = self.get_fn_obj(len(args))
        if cmd_fn:
            ret: List[HandledMessageEventText]

            # checks
            if not cmd_fn.scope.is_in_scope(e.channel_type):
                ret = [
                    HandledMessageEventText(
                        content=CommandSpecialResponse.out_of_scope(e.channel_type, cmd_fn.scope.available_ctypes))]
            elif not cmd_fn.can_be_called(e.channel_oid):
                ret = [
                    HandledMessageEventText(
                        content=_("Command is in cooldown. Call the command again after {:.2f} secs.").format(
                            cmd_fn.cd_sec_left(e.channel_oid)))]
            else:
                BotFeatureUsageDataManager.record_usage(cmd_fn.cmd_feature, e.channel_oid, e.user_model.id)
                try:
                    ret = param_type_ensure(fn=cmd_fn.fn, converter=NonSafeDataTypeConverter)(e, *args)
                    cmd_fn.record_called(e.channel_oid)
                except TypeCastingFailed as e:
                    ret = [HandledMessageEventText(
                        content=_("Incorrect type of data: `{}`.\n"
                                  "Expected type: `{}` / Actual type: `{}`").format(
                            e.data, type_translation(e.expected_type), type_translation(e.actual_type)
                        ))]

            if isinstance(ret, str):
                ret = [HandledMessageEventText(content=ret)]
            elif isinstance(ret, list):
                ret = [HandledMessageEventText(content=txt) if isinstance(txt, str) else txt for txt in ret]

            return ret

        if args:
            cmd_code, cmd_args = args[0], args[1:]

            cmd_node: Optional[CommandNode] = self.get_child_node(code=cmd_code)
            if cmd_node:
                return cmd_node.parse_args(e, splitter, cmd_node.max_arg_count, args=cmd_args, is_sub=True)

        if is_sub:
            return [HandledMessageEventText(
                content=_("Executable command not found.\nVisit {}{} for more information.").format(
                    HostUrl, reverse("page.doc.botcmd.main")))]
        else:
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


class CommandSpecialResponse:
    @staticmethod
    def out_of_scope(current: ChannelType, allowed: List[ChannelType]) -> str:
        return _("Command not allowed to use under this channel type: {}\n"
                 "Please use the command under either one of these channel types: {}").format(
            current.key, " / ".join([str(ctype.key) for ctype in allowed]))


class CommandHandler:
    def __init__(self, root_cmd_node: CommandNode):
        if not root_cmd_node.is_root:
            raise ValueError("Root Command Node is required for `CommandDispatcher`.")
        self._root = root_cmd_node

    def handle(self, e: TextMessageEventObject) -> List[HandledMessageEventText]:
        # Remove prefix from the string content
        e.content = e.content[len(self._root.prefix):]

        # Check what splitter to apply
        splitter = None
        for spltr in self._root.splitters:
            if e.content.startswith(spltr):
                splitter = spltr
                break

        if splitter:
            # Remove splitter from the string content
            e.content = e.content[len(splitter):]

            # Parse the command and return the response
            return self._root.parse_args(e, splitter)
        else:
            return []
