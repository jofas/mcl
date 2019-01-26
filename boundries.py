import math
import xml.etree.ElementTree as ET

import tools

class HorizontalBlockBoundries:
    def __init__(self, boundry_map, block_size):
        mn, mx = tools.min_max(list(boundry_map.keys()))
        self.mn = mn; self.mx = mx + block_size;
        self.bm = boundry_map
        self.block_size = block_size

    def contains(self, point):
        if point[0] <= self.mn or point[0] >= self.mx:
            return False
        b = self.__get_boundry(point)
        return b[0][1] < point[1] and point[1] < b[1][1]

    def distance(self, point):
        b = self.__get_boundry(point)
        return {
            "+": math.fabs(point[1] - b[1][1]),
            "-": math.fabs(point[1] - b[0][1])
        } if point[2] == "+" else {
            "+": math.fabs(point[1] - b[0][1]),
            "-": math.fabs(point[1] - b[1][1])
        }

    def __get_boundry(self, point):
        return self.bm[int(point[0]/self.block_size) \
            * self.block_size]

    @staticmethod
    def from_map(path, block_size):
        lc = ET.parse(path).getroot()[0]
        lines = [l for l in _horizontals_min_max_format(
            lc, block_size )]

        res = {}
        for l in lines:
            if l['x_min'] not in res:
                res[l['x_min']] = [[l['x_min'],l['y_min']],
                    [l['x_max'], l['y_min']]]
            else:
                if l['y_min'] < res[l['x_min']][0][1]:
                    res[l['x_min']][0][1] = l['y_min']
                else:
                    res[l['x_min']][1][1] = l['y_min']
        return HorizontalBlockBoundries(res, block_size)

def _horizontals_min_max_format(raw_lines, block_size):
    is_horizontal = lambda x: x['y_min'] == x['y_max']
    x_diff        = lambda x: x['x_max'] - x['x_min']
    needs_split   = lambda x: x_diff(x) > block_size
    splits        = lambda x: int(x_diff(x) / block_size)
    make_split    = lambda l, k, i: l[k] + i * block_size \
        if k == 'x_min' else l['x_min'] + i * block_size  \
                                        + block_size

    for l in raw_lines:
        l = __parse_line(l.attrib)
        if is_horizontal(l):
            if needs_split(l):
                for i in range(splits(l)):
                    yield { k : v if k[0] == 'y' else \
                        make_split(l,k,i) \
                            for k, v in l.items() }
            else:
                yield l

def __parse_line(line):
    cut_px = lambda x: x[:-2]

    line = {k: int(cut_px(v)) for k, v in line.items() if \
        k != 'stroke'}

    return {
        'x_min': min(line['x1'], line['x2']),
        'x_max': max(line['x1'], line['x2']),
        'y_min': min(line['y1'], line['y2']),
        'y_max': max(line['y1'], line['y2']),
    }

