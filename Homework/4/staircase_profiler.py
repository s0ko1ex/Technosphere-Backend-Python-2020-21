#!/usr/bin/env python3
import cProfile
import pstats
import io
import sys
from staircase import naive_climb_stairs, normal_climb_stairs

for i in sys.argv[1:]:
    print(f"n = {i}\n-------")
    pr = cProfile.Profile()
    pr.enable()
    naive_climb_stairs(int(i))
    pr.disable()

    s = io.StringIO()
    sortby = 'cumulative'
    s.write("Naive implementation\n--------------------")
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()

    s.write("Normal implementation\n---------------------")
    pr.clear()
    pr.enable()
    normal_climb_stairs(int(i))
    pr.disable()

    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print(s.getvalue(), "\n")
