import time


class Sudoku:
    def __init__(self, initial_values):
        self.cells = {}
        self.parse_puzzle(initial_values)
        self.set_relations()
        self.print_()

    def parse_puzzle(self, initial_values):
        cells = {}

        if initial_values is None:
            for r in range(1, 10):
                for c in range(1, 10):
                    cells.update({(r, c): Cell(r, c, 0)})
        else:
            initial_values = list(initial_values)
            assert len(initial_values) == 81
            for r in range(1, 10):
                for c in range(1, 10):
                    initial_val = initial_values[(((r - 1) * 9) + (c - 1))]
                    cells.update({(r, c): Cell(r, c, int(initial_val))})
        self.cells = cells

    def set_relations(self):
        self.set_classic_relations()

    def check_relatives(self, cell, solver):
        return cell.check_relatives(solver)

    def set_classic_relations(self):
        for r in range(1, 10):
            for c in range(1, 10):
                cell = self.cells.get((r, c))
                for i in range(1, 10):
                    # belonging row
                    cell.relatives.add(self.cells.get((r, i)))
                    # belonging column
                    cell.relatives.add(self.cells.get((i, c)))

                # belonging 3x3
                belonging_3x3_r = int((r - 1) / 3)
                belonging_3x3_c = int((c - 1) / 3)
                for rr in range(belonging_3x3_r * 3 + 1, belonging_3x3_r * 3 + 4):
                    for cc in range(belonging_3x3_c * 3 + 1, belonging_3x3_c * 3 + 4):
                        cell.relatives.add(self.cells.get((rr, cc)))

                cell.relatives.remove(cell)

    def print_(self):
        for r in range(1, 10):
            for c in range(1, 10):
                print ("%s%s" % (self.cells.get((r, c)).current_value, " " if c % 3 == 0 else "")),
            if r % 3 == 0:
                print("")
            print("")
        print("-------------------")
        return self


class KillerRelation:
    def __init__(self, total_value, cells):
        self.total_value = total_value
        self.relatives = cells

    def have_relation(self, cell):
        return cell in self.relatives

    def check_relations(self, cell, solver):
        if self.have_relation(cell):
            assigned_relatives = [c for c in self.relatives if c.current_value != 0]
            if len(self.relatives) == len(assigned_relatives):
                if sum([v.current_value for v in self.relatives]) != self.total_value:
                    return False
                else:
                    return True
            if len(self.relatives) > len(assigned_relatives):
                if sum([v.current_value for v in self.relatives]) >= self.total_value:
                    return False
        return True


class KillerSudoku(Sudoku):
    def __init__(self, initial_values):
        self.killer_relations = []
        Sudoku.__init__(self, initial_values)
        self.verify_relatives()

    def parse_puzzle(self, (initial_values, killer_relations)):
        Sudoku.parse_puzzle(self, initial_values)
        for killer_relation in killer_relations:
            total_value, relatives = killer_relation
            self.killer_relations.append(KillerRelation(total_value, [self.cells.get(c_id) for c_id in relatives]))

    def check_relatives(self, cell, solver):
        if cell.current_value:
            if Sudoku.check_relatives(self, cell, solver):
                for killer_relation in self.killer_relations:
                    if not killer_relation.check_relations(cell, solver):
                        return False
                return True
        return False

    def verify_relatives(self):
        all = set([])
        for killer_relation in self.killer_relations:
            for relative in killer_relation.relatives:
                all.add(relative)
        print(len(all))
        assert len(all) == 81


class Solver:
    def __init__(self, sudoku):
        self.sudoku = sudoku
        self.compare_count = 0
        self.back_track_count = 0

    def get_next_cell(self, cell):
        return self.sudoku.cells.get((cell.row, cell.col + 1) if cell.col < 9 else (cell.row + 1, 1))

    @staticmethod
    def get_next_value(cell):
        return cell.set_next_value()

    def solve(self):
        start = time.clock()
        result = self.solve_r(self.sudoku.cells.get((1, 1)))
        t = time.clock() - start
        self.sudoku.print_()
        if result:
            print ("SUCCEEDED in %s secs with %s backtrack and %s compare in total" % (t,
                                                                                       self.back_track_count,
                                                                                       self.compare_count))
        else:
            print ("FAILED")
        print("")
        return t

    def solve_r(self, cell=None):
        while True:
            if cell is None or self.sudoku.check_relatives(cell, self):
                next_cell = self.get_next_cell(cell)
                if next_cell:
                    if self.solve_r(next_cell):
                        return True
                    else:
                        if not self.get_next_value(cell):
                            break
                else:
                    return True
            else:
                if not self.get_next_value(cell):
                    break
        self.back_track_count += 1
        cell.reset_values()
        return False


class Cell:
    def __init__(self, row, col, init_value):
        self.row = row
        self.col = col
        self.current_value = init_value
        self.tested_values = []
        self.available_values = [] if init_value != 0 else [1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.relatives = set([])

    def get_index(self):
        return self.row, self.col

    def set_next_value(self):
        if len(self.available_values) > 0:
            self.tested_values.append(self.current_value)
            self.current_value = self.available_values.pop()
            return True
        return False

    def reset_values(self):
        for i in range(len(self.tested_values)):
            self.available_values.append(self.current_value)
            self.current_value = self.tested_values.pop()

    def check_relatives(self, solver):
        if self.current_value:
            for relative in self.relatives:
                solver.compare_count += 1
                if self.current_value == relative.current_value:
                    return False
                if len(relative.available_values) == 0 and self.current_value in relative.available_values:
                    return False
            return True
        return False

    def __str__(self):
        print_elems = [('row', self.row),
                       ('col', self.col),
                       ('current_value', self.current_value),
                       ('available_values', self.available_values),
                       ('tested_values', self.tested_values)]
        return ', '.join("%s: %s" % item for item in print_elems)

    def __repr__(self):
        return self.__str__()


if __name__ == '__main__':
    easy_sudoku = list([])
    easy_sudoku.append('003020600900305001001806400008102900700000008006708200002609500800203009005010300')

    hard_sudoku = list([])
    hard_sudoku.append('000070020800000006010205000905400008000000000300008501000302080400000009070060000')
    hard_sudoku.append('850002400720000009004000000000107002305000900040000000000080070017000000000036040')
    hard_sudoku.append('005300000800000020070010500400005300010070006003200080060500009004000030000009700')
    hard_sudoku.append('120040000005069010009000500000000070700052090030000002090600050400900801003000904')
    hard_sudoku.append('000570030100000020700023400000080004007004000490000605042000300000700900001800000')
    hard_sudoku.append('700152300000000920000300000100004708000000060000000000009000506040907000800006010')
    hard_sudoku.append('100007090030020008009600500005300900010080002600004000300000010040000007007000300')
    hard_sudoku.append('100034080000800500004060021018000000300102006000000810520070900006009000090640002')
    hard_sudoku.append('000920000006803000190070006230040100001000700008030029700080091000507200000064000')
    hard_sudoku.append('060504030100090008000000000900050006040602070700040005000000000400080001050203040')
    hard_sudoku.append('700000400020070080003008079900500300060020090001097006000300900030040060009001035')
    hard_sudoku.append('000070020800000006010205000905400008000000000300008501000302080400000009070060000')


    killer_sudoku = (None, [
        (3, [(1, 1), (1, 2)]),
        (15, [(1, 3), (1, 4), (1, 5)]),
        (22, [(1, 6), (2, 5), (2, 6), (3, 5)]),
        (4, [(1, 7), (2, 7)]),
        (16, [(1, 8), (2, 8)]),
        (15, [(1, 9), (2, 9), (3, 9), (4, 9)]),
        (25, [(2, 1), (2, 2), (3, 1), (3, 2)]),
        (17, [(2, 3), (2, 4)]),
        (9, [(3, 3), (3, 4),(4,4)]),
        (8, [(3, 6), (4, 6), (5, 6)]),
        (20, [(3, 7), (3, 8), (4, 7)]),
        (6, [(4, 1), (5, 1)]),
        (14, [(4, 2), (4, 3)]),
        (17, [(4, 5), (5, 5), (6, 5)]),
        (17, [(4, 8), (5, 7), (5, 8)]),
        (13, [(5, 2), (5, 3), (6, 2)]),
        (20, [(5, 4), (6, 4), (7, 4)]),
        (12, [(5, 9), (6, 9)]),
        (27, [(6, 1), (7, 1), (8, 1), (9, 1)]),
        (6, [(6, 3), (7, 2), (7, 3)]),
        (20, [(6, 6), (7, 6), (7, 7)]),
        (6, [(6, 7), (6, 8)]),
        (10, [(7, 5), (8, 4), (8, 5), (9, 4)]),
        (14, [(7, 8), (7, 9), (8, 8), (8, 9)]),
        (8, [(8, 2), (9, 2)]),
        (16, [(8, 3), (9, 3)]),
        (15, [(8, 6), (8, 7)]),
        (13, [(9, 5), (9, 6), (9, 7)]),
        (17, [(9, 8), (9, 9)]),
    ])

    Solver(KillerSudoku(killer_sudoku)).solve()

    exit()
    for sudoku in easy_sudoku:
        Solver(Sudoku(sudoku)).solve()

    for sudoku in hard_sudoku:
        Solver(Sudoku(sudoku)).solve()
