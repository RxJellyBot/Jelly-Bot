import json

import math
from django.test import Client
from django.urls import reverse

from extutils import exec_timing_ns

d = {i: None for i in range(500000)}


@exec_timing_ns
def wrap():
    pass


@exec_timing_ns
def wrap2():
    pass


if __name__ == "__main__":
    wrap()
    wrap2()
