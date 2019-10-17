################################################################################################################################################################
# Simple Sudoku
# MIT Liscense:
################################################################################################################################################################
# Copyright 2019 Sotolf Flasskjegg 
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
################################################################################################################################################################

import argparse
from tkinter import Tk, Canvas, Frame, Button, BOTH, TOP, BOTTOM, LEFT, RIGHT
from textwrap import wrap
from enum import Enum

MARGIN =  20 # Pixels around the board
SIDE = 50 # Height of each board cell
WIDTH = HEIGHT = MARGIN * 2 + SIDE * 9 # Width and height of the whole board
# Highlight colours
HLANSWER = "light goldenrod"
HLCAND = "light blue"

class Mode(Enum):
    solution = 1
    candidate = 2

class SudokuError(Exception):
    """
    An application specific error.
    """
    pass

class SudokuBoard(object):
    """
    Sudoku Board Representation
    """
    def __init__(self, puzzle_string):
        self.board = self.__create_board(puzzle_string)
    
    def __create_board(self, puzzle_string):
        rows = wrap(puzzle_string, 9)
        rows = [row.replace('.', '0') for row in rows]
        board = [ [int(ch) for ch in row] for row in rows ]
        return board

class SudokuGame(object):
    """
    A Sudoku game, in charge of storing the state of the board and checking
    whether the puzzle is completed.
    """

    def __init__(self):
        self.puzzle = [[ 0 for x in range(9)] for y in range(9)]
        self.start_puzzle = [[ 0 for x in range(9)] for y in range(9)]
        self.candidates = [[[False for z in range(10)] for x in range(9)] for y in range(9)]
        self.null_board()
        self.current_to_origin()

    def start(self):
        self.game_over = False
        self.puzzle = []
        for i in range(9):
            self.puzzle.append([])
            for j in range(9):
                self.puzzle[i].append(self.start_puzzle[i][j])
    
    def get_cell(self, row, col):
        return self.puzzle[row][col]
    
    def set_cell(self, row, col, val):
        self.puzzle[row][col] = val
    
    def calculate_candidates(self, row, col):
        if self.puzzle[row][col] == 0:
            candidates = list(set(range(10)).difference(self.__set_buddies(row, col)))
            for candidate in candidates:
                self.add_candidate(row, col, candidate)


    def get_candidates(self, row, col):
        candidates = []
        for i in range(1,10):
            if self.candidates[row][col][i]:
                candidates.append(i)
        return candidates
    
    def toggle_candidate(self, row, col, val):
        self.candidates[row][col][val] = not self.candidates[row][col][val]
    
    def remove_candidate(self, row, col, val):
        self.candidates[row][col][val] = False
    
    def add_candidate(self, row, col, val):
        self.candidates[row][col][val] = True

    def get_origin(self, row, col):
        return self.start_puzzle[row][col]
    
    def update_candidates(self, row, col):
        answer = self.puzzle[row][col]
        buddies = self.__find_buddies(row, col)
        for r, c in buddies:
            self.remove_candidate(r, c, answer)

    def __find_buddies(self, row, col):
        buddies = [] 
        # Row buddies
        buddies.extend([(row, c) for c in range(9)])
        # Column buddies
        buddies.extend([(r, col) for r in range(9)])
        # Box buddies
        box_row = row // 3
        box_col = col // 3
        buddies.extend([
                (r, c)
                for r in range(box_row * 3, (box_row + 1) * 3)
                for c in range(box_col * 3, (box_col + 1) * 3)
        ])
        return buddies

    def current_to_origin(self):
        self.game_over = False
        self.start_puzzle = []
        for i in range(9):
            self.start_puzzle.append([])
            for j in range(9):
                self.start_puzzle[i].append(self.puzzle[i][j])
    
    def null_board(self):
        for i in range(9):
            for j in range(9):
                self.start_puzzle[i][j] = 0
        self.start()
                
    def from_string(self, puzzle_string):
        self.start_puzzle = SudokuBoard(puzzle_string).board
        self.start()
    
    def check_win(self):
        for row in range(9):
            if not self.__check_row(row):
                return False
        for column in range(9):
            if not self.__check_column(column):
                return False
        for row in range(3):
            for column in range(3):
                if not self.__check_square(row, column):
                    return False
        self.game_over = True
        return True

    def __check_group(self, block):
        return set(block) == set(range(1,10))

    def __check_row(self, row):
        return self.__check_group(self.puzzle[row])

    def __set_row(self, row):
        return set(self.puzzle[row])

    def __check_column(self, col):
        return self.__check_group(
            [self.puzzle[row][col] for row in range(9)]
        )
    
    def __set_column(self, col):
        return set([self.puzzle[row][col] for row in range(9)])

    def __check_square(self, row, col):
        return self.__check_group(
            [
                self.puzzle[r][c]
                for r in range(row * 3, (row + 1) * 3)
                for c in range(col * 3, (col + 1) * 3)
            ]
        )
    
    def __set_square(self, box_row, box_col):
        return set(
            [
                self.puzzle[r][c]
                for r in range(box_row * 3, (box_row + 1) * 3)
                for c in range(box_col * 3, (box_col + 1) * 3)
            ]
        )
    
    def __set_buddies(self, row, col):
        return self.__set_row(row).union(self.__set_column(col), self.__set_square(row // 3, col // 3))

    
class SudokuUI(Frame):
    """
    The Tkinter UI, responsible for drawing the board and accepting user input.
    """
    def __init__(self, parent, game):
        self.game = game
        self.parent = parent
        Frame.__init__(self, parent)

        self.row, self.col = 0, 0
        self.mode = Mode.solution
        self.highlight = 0

        self.__initUI()

    def __initUI(self):
        self.parent.title("Simple Sudoku")
        self.pack(fill=BOTH, expand=1)
        self.canvas = Canvas(self, width=WIDTH, height=HEIGHT)
        self.canvas.pack(fill=BOTH, side=TOP)
        self.buttons = Frame(self)
        reset_button = Button(self.buttons, text="Reset", command=self.__clear_answers)
        reset_button.grid(row=0, column=0)
        clear_button = Button(self.buttons, text="Clear", command=self.__null_board)
        clear_button.grid(row=0, column=1)
        to_origin_button = Button(self.buttons, text="Set Origin", command=self.__to_origin)
        to_origin_button.grid(row=0, column=2)
        from_clip = Button(self.buttons, text="From clipboard", command=self.__from_clip)
        from_clip.grid(row=0, column=3)
        calculate_candidates = Button(self.buttons, text="Calculate candidates", command=self.__calculate_candidates)
        calculate_candidates.grid(row=0, column=4)
        self.buttons.pack(fill=BOTH, side=BOTTOM)

        self.__draw_grid()
        self.__draw_puzzle()
        self.__draw_cursor()
        self.canvas.focus_set()

        self.canvas.bind("<Button-1>", self.__cell_clicked)
        self.canvas.bind("<Key>", self.__key_pressed)
        self.canvas.bind("<Left>", self.__cursor_left)
        self.canvas.bind("<Right>", self.__cursor_right)
        self.canvas.bind("<Up>", self.__cursor_up)
        self.canvas.bind("<Down>", self.__cursor_down)
        self.canvas.bind("<F1>", self.__toggle_highlight)
        self.canvas.bind("<F2>", self.__toggle_highlight)
        self.canvas.bind("<F3>", self.__toggle_highlight)
        self.canvas.bind("<F4>", self.__toggle_highlight)
        self.canvas.bind("<F5>", self.__toggle_highlight)
        self.canvas.bind("<F6>", self.__toggle_highlight)
        self.canvas.bind("<F7>", self.__toggle_highlight)
        self.canvas.bind("<F8>", self.__toggle_highlight)
        self.canvas.bind("<F9>", self.__toggle_highlight)
    
    def __calculate_candidates(self):
        for row in range(9):
            for column in range(9):
                self.game.calculate_candidates(row, column)
        self.__draw_puzzle()

    def __toggle_highlight(self, event):
        number = int(event.keysym[1])
        if self.highlight == number:
            self.highlight = 0
        else:
            self.highlight = number
        
        self.__draw_puzzle()

    def __null_board(self):
        self.game.null_board()
        self.__draw_puzzle()

    def __to_origin(self):
        self.game.current_to_origin()
        self.__draw_puzzle()

    def __from_clip(self):
        puzzle_string = self.clipboard_get()
        self.game.from_string(puzzle_string)
        self.__draw_puzzle()

    def __draw_grid(self):
        """
        Draws grid divided with blue lines into 3x3 squares
        """
        for i in range(10):
            color = "gray22" if i % 3 == 0 else "gray70"

            x0 = MARGIN + i * SIDE
            y0 = MARGIN
            x1 = MARGIN + i * SIDE
            y1 = HEIGHT - MARGIN
            self.canvas.create_line(x0, y0, x1, y1, fill=color, width=1)

            x0 = MARGIN
            y0 = MARGIN + i * SIDE
            x1 = WIDTH - MARGIN
            y1 = MARGIN + i * SIDE
            self.canvas.create_line(x0, y0, x1, y1, fill=color, width=1)
    
    def __draw_puzzle(self):
        self.canvas.delete("numbers")
        self.canvas.delete("candidates")
        self.canvas.delete("highlights")
        for i in range(9):
            for j in range(9):
                x0 = MARGIN + j * SIDE + 1
                y0 = MARGIN + i * SIDE + 1
                x1 = MARGIN + (j + 1) * SIDE - 1
                y1 = MARGIN + (i + 1) * SIDE - 1
                answer = self.game.get_cell(i,j)
                candidates = self.game.get_candidates(i,j)
                # First draw the highlight or else the candidates won't be visible
                if self.highlight != 0 and answer == self.highlight: 
                    self.canvas.create_rectangle(x0, y0, x1, y1, tags="highlights", fill=HLANSWER, outline=HLANSWER)
                elif self.highlight !=0 and self.highlight in candidates and answer == 0:
                    self.canvas.create_rectangle(x0, y0, x1, y1, tags="highlights", fill=HLCAND, outline=HLCAND)
                
                if answer != 0:
                    # Draw big character
                    x = MARGIN + j * SIDE + SIDE / 2
                    y = MARGIN + i * SIDE + SIDE / 2
                    original = self.game.get_origin(i, j)
                    color = "black" if answer == original else "olive drab"
                    self.canvas.create_text(x,y, text=answer, tags="numbers", fill=color, font=("Arial",24))
                else:
                    # Draw candidates
                    for candidate in candidates:
                        self.__draw_candidate(i, j, candidate)

    def __draw_candidate(self, row, col, candidate):
        diff = 15
        cx = MARGIN + col * SIDE + SIDE / 2
        cy = MARGIN + row * SIDE + SIDE / 2
        if candidate == 1:
            x = cx - diff
            y = cy - diff
        elif candidate == 2:
            x = cx 
            y = cy - diff
        elif candidate == 3:
            x = cx + diff
            y = cy - diff
        elif candidate == 4:
            x = cx - diff
            y = cy
        elif candidate == 5:
            x = cx
            y = cy
        elif candidate == 6:
            x = cx + diff
            y = cy
        elif candidate == 7:
            x = cx - diff
            y = cy + diff
        elif candidate == 8:
            x = cx
            y = cy + diff
        elif candidate == 9:
            x = cx + diff
            y = cy + diff

        self.canvas.create_text(x,y, text=candidate, tags="candidates", fill="gray", font=("Arial", 10))
    
    def __clear_answers(self):
        self.game.start()
        self.canvas.delete("victory")
        self.__draw_puzzle()

    def __cell_clicked(self, event):
        if self.game.game_over:
            return

        x, y = event.x, event.y
        if(MARGIN < x < WIDTH - MARGIN and MARGIN < y < HEIGHT - MARGIN):
            self.canvas.focus_set()

            # get row and col numbers from x,y coordinates
            row, col = (y - MARGIN) // SIDE, (x - MARGIN) // SIDE

            # if cell was selected already - deselect it
            if (row, col) == (self.row, self.col):
                self.row, self.col = -1, -1
            elif self.game.get_origin(row,col) == 0:
                self.row, self.col = row, col
        else:
            self.row, self.col = -1, -1

        self.__draw_cursor()

    def __cursor_left(self, event):
        self.canvas.delete("cursor")
        if self.__deselected():
            self.row = 0
            self.col = 8
        else:
            if self.col == 0:
                self.col = 8
            else:
                self.col -= 1
        self.__draw_cursor()
    
    def __cursor_right(self, event):
        self.canvas.delete("cursor")
        if self.__deselected():
            self.row = 0
            self.col = 0
        else:
            if self.col == 8:
                self.col = 0
            else:
                self.col += 1
        self.__draw_cursor()

    def __cursor_up(self, event):
        self.canvas.delete("cursor")
        if self.__deselected():
            self.row = 8
            self.col = 0
        else:
            if self.row == 0:
                self.row = 8
            else:
                self.row -= 1
        self.__draw_cursor()

    def __cursor_down(self, event):
        self.canvas.delete("cursor")
        if self.__deselected():
            self.row = 0
            self.col = 0
        else:
            if self.row == 8:
                self.row = 0
            else:
                self.row += 1
        self.__draw_cursor()

    def __deselected(self):
        if self.row == -1 and self.col == -1:
            return True
        else:
            return False

    def __draw_cursor(self):
        self.canvas.delete("cursor")
        if self.row >= 0 and self.col >= 0:
            x0 = MARGIN + self.col * SIDE + 1
            y0 = MARGIN + self.row * SIDE + 1
            x1 = MARGIN + (self.col + 1) * SIDE - 1
            y1 = MARGIN + (self.row + 1) * SIDE - 1
            color = ""
            if self.mode is Mode.candidate:
                color = "blue"
            elif self.mode is Mode.solution:
                color = "red"
            else:
                color = "pink"
            self.canvas.create_rectangle(x0, y0, x1, y1, outline=color, tags="cursor", width=3)

    def __key_pressed(self, event):
        if self.game.game_over:
            return

        if self.row >= 0 and self.col >= 0 and event.char in "1234567890":
            if self.mode is Mode.solution:
                self.game.set_cell(self.row, self.col, int(event.char))
                self.game.update_candidates(self.row, self.col)
            elif self.mode is Mode.candidate:
                self.game.toggle_candidate(self.row, self.col, int(event.char))
            self.__draw_puzzle()
            self.__draw_cursor()
            if self.game.check_win():
                self.__draw_victory()
        elif event.char == " ":
            self.__toggle_mode_candidate()
            self.__draw_cursor()
        else:
            self.__draw_puzzle()
            self.__draw_cursor()
            return
    
    def __toggle_mode_candidate(self):
        if self.mode is Mode.candidate:
            self.mode = Mode.solution
        else:
            self.mode = Mode.candidate

    def __draw_victory(self):
        # create an oval
        x0 = y0 = MARGIN + SIDE * 2
        x1 = y1 = MARGIN + SIDE * 7
        self.canvas.create_oval(x0, y0, x1, y1, tags="victory", fill="dark orange", outline="orange")

        # create text
        x = y = MARGIN + 4 * SIDE + SIDE / 2
        self.canvas.create_text(x, y, text="You win!", tags="victory", fill="white", font=("Arial", 32))


if __name__ == '__main__':
    game = SudokuGame()
    game.start()

    root = Tk()
    SudokuUI(root,game)
    root.geometry("{}x{}".format(WIDTH, HEIGHT + 40))
    root.mainloop()