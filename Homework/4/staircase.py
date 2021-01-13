def naive_climb_stairs(n: int) -> int:
    if n in (0, 1):
        return 1
    else:
        return naive_climb_stairs(n - 1) + naive_climb_stairs(n - 2)


def normal_climb_stairs(n: int) -> int:
    if n in (0, 1):
        return 1
    else:
        prev, cur = 1, 1

        for _ in range(1, n):
            cur, prev = cur + prev, cur

        return cur
