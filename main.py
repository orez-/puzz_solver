import collections

import attr


def get_id(side):
    if not side:
        return None
    return side.lstrip('blankt-')


DIRECTION_DELTAS = [
    (0, -1),
    (1, 0),
    (0, 1),
    (-1, 0),
]

ROTATION_MAP = dict(enumerate('NESW'))
ORIENTATION_MAP = dict(map(reversed, ROTATION_MAP.items()))


@attr.s(frozen=True, slots=True)
class Piece:
    id = attr.ib()
    top = attr.ib(convert=get_id)
    right = attr.ib(convert=get_id)
    bottom = attr.ib(convert=get_id)
    left = attr.ib(convert=get_id)

    def _side_order(self):
        return [self.top, self.right, self.bottom, self.left]

    def sides(self, rotation=0):
        directions = collections.deque(DIRECTION_DELTAS)
        directions.rotate(-rotation)
        return [
            (dx, dy, side_id)
            for (dx, dy), side_id
            in zip(directions, self._side_order())
            if side_id
        ]

    def get_rotation(self, side, dx, dy):
        side_idx = self._side_order().index(side)
        dir_idx = DIRECTION_DELTAS.index((dx, dy))
        return (dir_idx - side_idx + 4) % 4


def main():
    adjacencies = collections.defaultdict(set)
    with open('problem.csv', 'r') as file:
        next(file)  # skip header
        for line in file:
            id_, top, right, bottom, left, orientation, row, col = line.split(',')
            piece = Piece(id_, top, right, bottom, left)
            for _, _, side in piece.sides():
                adjacencies[side].add(piece)
            if orientation:
                rotation = ORIENTATION_MAP[orientation]
                seen = {piece}
                solution = {piece.id: (int(col), int(row), rotation, piece)}

    queue = collections.deque(solution.values())

    while queue:
        x, y, rotation, piece = queue.popleft()

        for dx, dy, side in piece.sides(rotation):
            (next_piece,) = adjacencies[side] - {piece}
            if next_piece in seen:
                continue
            seen.add(next_piece)

            next_rotation = next_piece.get_rotation(side, -dx, -dy)
            answer = (x + dx, y + dy, next_rotation, next_piece)
            solution[next_piece.id] = answer
            queue.append(answer)

    write_solution(solution)


def write_solution(solution):
    with open('solution.csv', 'w') as out_file, open('problem.csv', 'r') as in_file:
        out_file.write(next(in_file))
        for line in in_file:
            id_, top, right, bottom, left, *_ = line.split(',')
            col, row, rotation, piece = solution[id_]
            print(
                id_,
                top,
                right,
                bottom,
                left,
                ROTATION_MAP[rotation],
                row,
                col,
                file=out_file,
                sep=',',
            )

# ---


def test_no_sides_rotation():
    piece = Piece(*'01234')
    assert set(piece.sides()) == {
        (0, -1, '1'),
        (1, 0, '2'),
        (0, 1, '3'),
        (-1, 0, '4'),
    }


def test_sides_rotation():
    piece = Piece(*'01234')
    assert set(piece.sides(1)) == {  # EAST - top is facing east, right is south
        (0, 1, '2'),
        (-1, 0, '3'),
        (0, -1, '4'),
        (1, 0, '1'),
    }


def test_get_rotation():
    piece = Piece(*'01234')
    assert piece.get_rotation(
        side='1',
        dx=-1,
        dy=0,
    ) == 3
    assert piece.get_rotation(
        side='1',
        dx=0,
        dy=-1,
    ) == 0
    assert piece.get_rotation(
        side='1',
        dx=1,
        dy=0,
    ) == 1
    assert piece.get_rotation(
        side='1',
        dx=0,
        dy=1,
    ) == 2


if __name__ == '__main__':
    main()
