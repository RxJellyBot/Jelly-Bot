from extutils import exec_timing_ns
from extutils.utils import to_snake_case


@exec_timing_ns
def wrap():
    for i in range(500000):
        to_snake_case("CamelCase")


if __name__ == "__main__":
    wrap()
    wrap()
    wrap()
