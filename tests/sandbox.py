from extutils import exec_timing_ns
import asyncio
from dateutil import parser
import requests
from dotmap import DotMap


def f():
    print("87")


async def run():
    f()


@exec_timing_ns
def wrap():
    asyncio.run(run())


@exec_timing_ns
def wrap2():
    pass


if __name__ == "__main__":
    wrap()
    wrap2()
