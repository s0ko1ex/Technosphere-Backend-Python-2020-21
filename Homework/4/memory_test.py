#!/usr/bin/env python3
from memory_profiler import profile
from staircase import naive_climb_stairs, normal_climb_stairs
import sys


@profile(precision=4)
def naive_call(n: int) -> int:
    naive_climb_stairs(n)


@profile(precision=4)
def normal_call(n: int) -> int:
    normal_climb_stairs(n)


if __name__ == "__main__":
    for i in sys.argv[1:]:
        print(f"n = {i}\n-------")
        print("Naive implementation\n--------------------")
        naive_call(int(i))
        print("Normal implementation\n---------------------")
        normal_call(int(i))
        print()
