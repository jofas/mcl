import threading
import math
import random

import srv
import boundries as bnd
import test_suite as ts
import tools

POINTS    = int(1e2)
THRESHOLD = 0.90
STEP      = 50

BLOCK_SIZE = 50
STREET_X   = (10, 590)
STREET_Y   = 75

# mutate offset x, y
MOX = 5
MOY = 5

# max measurement error
MME = 10

STREET = [
    (STREET_X[0], STREET_Y - MOY),
    (STREET_X[1], STREET_Y + MOY)
]

# TODO: robo protocol -> change main, turn point

def main():

    boundries = bnd.HorizontalBlockBoundries \
        .from_map('map.svg', 50)

    points = \
        [x for x in tools.gen_rnd_points(POINTS, STREET)]

    srv.ResponseBuffer.send(points, "init")

    for i in range(len(ts.OBS)):

        obs = ts.gen_rnd_obs(ts.OBS[i], MME)

        mn, mx = tools.min_max([
            error(obs, boundries.distance(p)) \
                for p in points
        ])

        np = []
        for p in points:
            e = error(obs, boundries.distance(p))
            e_norm = (e - mn) / (mx - mn)
            prob = 1 - e_norm

            if prob >= THRESHOLD:
                np.append(p)

        if len(np) == 0:
            print("NO POINTS ANYMORE")
            break

        diff = POINTS - len(np)
        np += [mutate(random.sample(np, 1)[0]) \
            for _ in range(diff)]

        srv.ResponseBuffer.send(np, "mutated")

        if localized(np, 25.0):
            srv.ResponseBuffer.send(np, "DONE")
            print("DONE")
            return
        else:
            np = [p for p in move(np, boundries)]
            srv.ResponseBuffer.send(np, "moved")

        points = np

    srv.ResponseBuffer.send(points, "FAILED")
    print("FAILED")

def mutate(point):
    return tools.Point(
        random.uniform(point.x - MOX, point.x + MOX),
        random.uniform(STREET_Y - MOY, STREET_Y + MOY),
        point.dir
    )

def move(points, boundries):
    for point in points:
        point.x += STEP if point.dir == '+' else - STEP
        if boundries.contains(point):
            yield point

def error(dist1, dist2):
    return sum([(dist1[k] - dist2[k]) ** 2 \
        for k in dist1])

def localized(points, maximum_distance):
    pivot = points[0]
    max_measured_dist = 0.0

    for point in points[1:]:
        if pivot.dir != point.dir: return False
        distance = math.sqrt( (pivot.x - point.x) ** 2
                            + (pivot.y - point.y) ** 2 )

        if max_measured_dist < distance:
            max_measured_dist = distance

    return max_measured_dist < maximum_distance

if __name__ == '__main__':

    mcl = threading.Thread(target=main)
    mcl.start()

    #s = threading.Thread(target=srv.serve)
    #s.start()
