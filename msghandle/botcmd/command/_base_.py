from abc import ABC
from typing import List, Dict, Optional

from extutils import decorator_wrap


# FIXME: [SSSHP] Command parsing process is a tree


class CommandClassHolder:
    def __init__(self):
        self._cmd_holder: Dict[str, BotCommand] = {}
        self._fn_holder: Dict[str, callable] = {}

    def _register_cmd_(self, cmd_cls):
        aliases = cmd_cls.get_aliases()
        if any(alias in self._cmd_holder for alias in aliases):
            # Warn that duplication of command alias detected
            pass
        self._cmd_holder.update({name: cmd_cls for name in aliases})

    def _register_exec_fn_(self, fn, arg_count):
        self._fn_holder[arg_count] = fn

    def register_cmd(self, cmd_cls=None):
        if cmd_cls:
            self._register_cmd_(cmd_cls)
            return cmd_cls
        else:
            def wrapper(cmd_cls_in):
                self._register_cmd_(cmd_cls_in)
                return cmd_cls_in
            return wrapper

    def get_cmd(self, cmd_code: str):
        return self._cmd_holder.get(cmd_code)

    def register_exec_fn(self, fn=None, arg_count: int = 0):
        if fn:
            self._register_exec_fn_(fn, arg_count)
            return fn
        else:
            def wrapper(fn_in):
                self._register_exec_fn_(fn_in, arg_count)
                return fn_in
            return wrapper

    def get_exec_fn(self, arg_count: int):
        return self._fn_holder.get(arg_count)


class BotCommand(ABC):
    alias: List[str] = []
    fn_holder: CommandClassHolder = None

    @classmethod
    def get_fn_holder(cls):
        if not cls.fn_holder:
            cls.fn_holder = CommandClassHolder()
        return cls.fn_holder

    @classmethod
    def get_aliases(cls) -> List[str]:
        return cls.alias + [cls.__name__.lower()]

    @classmethod
    def __subcommands__(cls):
        return cls.__subclasses__()

    @classmethod
    def register_exec_fn(cls, fn=None, arg_count: int = 0):
        return cls.get_fn_holder().register_exec_fn(fn, arg_count)

    @classmethod
    def parse_args(cls, args_list: list) -> str:
        return ""
        cls.get_fn_holder().get_cmd(args_list[0])


class CommandHandler:
    def __init__(self, holder: CommandClassHolder):
        self._cmd_cls_holder = holder

    def handle(self, s: str) -> str:
        s = s.split(" ")
        cmd_code, cmd_args = s[0], s[1:]
        cmd_cls: Optional[BotCommand] = self._cmd_cls_holder.get_cmd(cmd_code)
        if cmd_cls:
            return cmd_cls.parse_args(cmd_args)
        return ""


main_cmd_holder = CommandClassHolder()
cmd_handler = CommandHandler(main_cmd_holder)


@main_cmd_holder.register_cmd
class UserIntegrate(BotCommand):
    alias = ["uintg"]

    @main_cmd_holder.register_exec_fn
    def issue_token(self):
        # FIXME: [SHP] Await implementation
        return "Issue Token."


@main_cmd_holder.register_cmd()
class Transform(BotCommand):
    @BotCommand.register_exec_fn(arg_count=1)
    def utf8(self, content):
        return repr(content.encode("utf-8"))


class TransformNewline(Transform):
    @Transform.register_exec_fn(arg_count=1)
    def newline_replace(self, content):
        return content.replace("\n", "\\n")


class TransformUtf8Encode(Transform):
    @Transform.register_exec_fn(arg_count=1)
    def utf8encode(self, content):
        return repr(content.encode("utf-8"))


class TransformReplace(Transform):
    @Transform.register_exec_fn(arg_count=1)
    def replace_single(self, end):
        return "".join(range(end))

    @Transform.register_exec_fn(arg_count=2)
    def replace_double(self, start, end):
        return "".join(range(start, end))


if __name__ == '__main__':
    # Imaginary scene:
    #   /uintg
    #   /userintegrate
    #   /t rp 1
    #   /t rp 1 5
    #   /t nl A\nS
    #   /t u8 AS

    test_pairs = [
        ("uintg", "Issue Token."),
        ("userintegrate", "Issue Token."),
        ("t rp 1", "01"),
        ("t rp 1 5", "012345"),
        ("t nl A\nS", "A\\nS"),
        ("t u8 AS", repr("AS".encode("utf-8")))
    ]
    for src, result in test_pairs:
        assert cmd_handler.handle(src) == result
