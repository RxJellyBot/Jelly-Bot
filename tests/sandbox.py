from extutils import exec_timing_ns
from extutils.utils import to_snake_case


d = {i: None for i in range(500000)}


@exec_timing_ns
def wrap():
    for k, v in d.items():
        k == 13000


if __name__ == "__main__":
    wrap()
    wrap()
    wrap()
