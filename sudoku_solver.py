import time


class SudokuSolver:
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
