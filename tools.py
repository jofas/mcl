import random

class Point:
    def __init__(self, x, y, dir):
        self.x = x; self.y = y; self.dir = dir

    def __getitem__(self, i):
        if i == 0: return self.x
        if i == 1: return self.y
        if i == 2: return self.dir
        raise IndexError

    def __setitem__(self, i, val):
        if   i == 0: self.x   = val
        elif i == 1: self.y   = val
        elif i == 2: self.dir = val
        else: raise IndexError

def gen_rnd_points(amount, street):
    for i in range(amount):
        x = random.uniform(street[0][0], street[1][0])
        y = random.uniform(street[0][1], street[1][1])
        dir = "+" if random.randint(0,1) == 0 else "-"
        yield Point( x, y, dir )

def min_max(l):
    mn = l[0];mx = l[0]
    for item in l:
        if item < mn: mn = item
        if item > mx: mx = item
    return mn, mx
