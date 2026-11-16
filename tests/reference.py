"""Independent brute-force BSQ solver used to check ../ex00/bsq.

Usage: python3 reference.py <map_file>   -> prints the expected solution
       python3 reference.py --random <seed> <dir> <count>  -> writes random maps
"""
import os
import random
import sys


def solve(path):
    with open(path, "rb") as f:
        data = f.read().decode("latin-1")
    header, _, body = data.partition("\n")
    empty, obstacle, full = header[-3], header[-2], header[-1]
    rows = body.split("\n")[:-1]
    h, w = len(rows), len(rows[0])
    # 2D prefix sums of obstacles: blocked[r][c] = obstacles in rows[:r], cols[:c]
    blocked = [[0] * (w + 1) for _ in range(h + 1)]
    for r in range(h):
        for c in range(w):
            blocked[r + 1][c + 1] = (blocked[r][c + 1] + blocked[r + 1][c]
                                     - blocked[r][c] + (rows[r][c] == obstacle))
    best = (0, 0, 0)
    for r in range(h):
        for c in range(w):
            size = best[0] + 1
            while r + size <= h and c + size <= w:
                count = (blocked[r + size][c + size] - blocked[r][c + size]
                         - blocked[r + size][c] + blocked[r][c])
                if count:
                    break
                best = (size, r, c)
                size += 1
    size, top, left = best
    grid = [list(row) for row in rows]
    for r in range(top, top + size):
        for c in range(left, left + size):
            grid[r][c] = full
    sys.stdout.write("".join("".join(row) + "\n" for row in grid))


def random_maps(seed, directory, count):
    rng = random.Random(seed)
    printable = [chr(c) for c in range(32, 127)]
    for i in range(count):
        h, w = rng.randint(1, 40), rng.randint(1, 40)
        density = rng.choice([0.0, 0.02, 0.1, 0.3, 0.6, 1.0])
        empty, obstacle, full = rng.sample(printable, 3)
        lines = ["".join(obstacle if rng.random() < density else empty
                         for _ in range(w)) for _ in range(h)]
        with open(os.path.join(directory, "random_%03d" % i), "w", newline="\n") as f:
            f.write("%d%s%s%s\n" % (h, empty, obstacle, full))
            f.write("".join(line + "\n" for line in lines))


if __name__ == "__main__":
    if sys.argv[1] == "--random":
        random_maps(int(sys.argv[2]), sys.argv[3], int(sys.argv[4]))
    else:
        solve(sys.argv[1])
