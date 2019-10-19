import random
from collections import deque
from copy import deepcopy
from tkinter import Tk, Canvas, Frame, Button, Menu, filedialog, simpledialog, messagebox, BOTH, TOP, BOTTOM, LEFT, RIGHT
from textwrap import wrap
from enum import Enum


MARGIN =  20 # Pixels around the board
SIDE = 50 # Height of each board cell
WIDTH = HEIGHT = MARGIN * 2 + SIDE * 9 # Width and height of the whole board
# Highlight colours
HLANSWER = "light goldenrod"
HLCAND = "light blue"
COLOURS = [None, "pale green", "sienna1", "khaki1", "cornflower blue", "mediumpurple1", "peachpuff2", "tomato", "sandy brown", "hot pink"]

class Mode(Enum):
    solution = 1
    candidate = 2
    colour = 3
    colour_candidate = 4

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
        self.__create_board(puzzle_string)
    
    def update(self, puzzle_string):
        self.__create_board(puzzle_string)
    
    def get(self):
        return self.board[:]

    def set_board(self, board):
        self.board = board
    
    def __create_board(self, puzzle_string):
        rows = wrap(puzzle_string, 9)
        rows = [row.replace('.', '0') for row in rows]
        self.board = [ [int(ch) for ch in row] for row in rows ]

    def generate(self, difficulty):
        file_name = difficulty + ".seed"
        with open(file_name) as file:
            puzzles = [line.strip() for line in file]
            self.__create_board(random.choice(puzzles)) 
        
        # Rotate puzzle between 0 to 3 times
        for i in range(random.randint(0,3)):
            self.rotate90()
        
        # Either don't flip or do flips
        i = random.randint(0,3)

        if i == 0:
            self.flip_hor()
        elif i == 1:
            self.flip_vert()
        elif i == 2:
            self.flip_hor()
            self.flip_vert()
        
        self.translate()
    
    def rotate90(self):
        new_board = [[0 for y in range(9)] for x in range(9)]
        for i in range(9):
            for j in range(9):
                new_board[j][8-i] = self.board[i][j]
        self.board = new_board

    def flip_hor(self):
        new_board = [[0 for y in range(9)] for x in range(9)]
        for i in range(9):
            for j in range(9):
                new_board[8-i][j] = self.board[i][j]
        self.board = new_board

    def flip_vert(self):
        new_board = [[0 for y in range(9)] for x in range(9)]
        for i in range(9):
            for j in range(9):
                new_board[i][8-j] = self.board[i][j]
        self.board = new_board
        
    def translate(self):
        numbers = [1,2,3,4,5,6,7,8,9]
        random.shuffle(numbers)
        new_board = [[0 for y in range(9)] for x in range(9)]
        for i in range(9):
            for j in range(9):
                if self.board[i][j] != 0:
                    new_board[i][j] = numbers[self.board[i][j] - 1]
                else:
                    new_board[i][j] = 0
        self.board = new_board


class SudokuGame(object):
    """
    A Sudoku game, in charge of storing the state of the board and checking
    whether the puzzle is completed.
    """

    def __init__(self):
        self.board = SudokuBoard("0" * 81)
        self.puzzle = self.board.get()
        self.start_puzzle = self.board.get()
        self.candidates = [[[False for z in range(10)] for x in range(9)] for y in range(9)]
        self.undostack = deque()
        self.null_board()
        self.current_to_origin()

    def start(self):
        self.game_over = False
        self.candidates = [[[False for z in range(10)] for x in range(9)] for y in range(9)]
        self.puzzle = []
        for i in range(9):
            self.puzzle.append([])
            for j in range(9):
                self.puzzle[i].append(self.start_puzzle[i][j])
        self.board.set_board(self.puzzle)
        self.__save_undo_state()
    
    def __save_undo_state(self):
        self.undostack.append((deepcopy(self.puzzle), deepcopy(self.start_puzzle), deepcopy(self.candidates)))
    
    def undo(self):
        self.puzzle, self.start_puzzle, self.candidates = self.undostack.pop()

    def get_cell(self, row, col):
        return self.puzzle[row][col]
    
    def set_cell(self, row, col, val):
        self.puzzle[row][col] = val
        self.update_candidates(row, col, undo=False)
        self.__save_undo_state()
    
    def calculate_all_candidates(self):
        for row in range(9):
            for col in range(9):
                self.calculate_candidates(row, col, undo=False)
        self.__save_undo_state()

    def calculate_candidates(self, row, col, undo=True):
        if self.puzzle[row][col] == 0:
            candidates = list(set(range(10)).difference(self.__set_buddies(row, col)))
            for candidate in candidates:
                self.add_candidate(row, col, candidate, undo=False)
        
        if undo:
            self.__save_undo_state()


    def get_candidates(self, row, col):
        candidates = []
        for i in range(1,10):
            if self.candidates[row][col][i]:
                candidates.append(i)
        return candidates
    
    def toggle_candidate(self, row, col, val, undo=True):
        self.candidates[row][col][val] = not self.candidates[row][col][val]
        if undo:
            self.__save_undo_state()
    
    def remove_candidate(self, row, col, val, undo=True):
        self.candidates[row][col][val] = False
        if undo:
            self.__save_undo_state()
    
    def add_candidate(self, row, col, val, undo=True):
        self.candidates[row][col][val] = True
        if undo:    
            self.__save_undo_state()

    def get_origin(self, row, col):
        return self.start_puzzle[row][col]
    
    def update_candidates(self, row, col, undo=True):
        answer = self.puzzle[row][col]
        buddies = self.__find_buddies(row, col)
        for r, c in buddies:
            self.remove_candidate(r, c, answer, undo=False)
        if undo:
            self.__save_undo_state()

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
        self.__save_undo_state()
    
    def null_board(self):
        for i in range(9):
            for j in range(9):
                self.start_puzzle[i][j] = 0
        self.start()
                
    def load_puzzle(self, file_name, line_number):
        with open(file_name) as file:
            puzzles = [line.strip() for line in file]
            self.from_string(puzzles[line_number])
        self.__save_undo_state()

    def generate(self, difficulty):
        self.board.generate(difficulty)
        self.start_puzzle = self.board.get()
        self.start()
    
    def rotate90(self):
        self.board.rotate90()
        self.start_puzzle = self.board.get()
        self.start()

    def flip_hor(self):
        self.board.flip_hor()
        self.start_puzzle = self.board.get()
        self.start()

    def flip_vert(self):
        self.board.flip_vert()
        self.start_puzzle = self.board.get()
        self.start()

    def translate(self):
        self.board.translate()
        self.start_puzzle = self.board.get()
        self.start()

    def load_random_puzzle(self, file_name):
        with open(file_name) as file:
            puzzles = [line.strip() for line in file]
            self.from_string(random.choice(puzzles))
        self.__save_undo_state()

    def from_string(self, puzzle_string):
        self.board.update(puzzle_string)
        self.start_puzzle = self.board.get()
        self.start()
        self.__save_undo_state()
    
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
        self.puzzle_num = 0
        self.file_name = ""
        self.colours = [[None for i in range(9)] for j in range(9)]

        self.__initUI()

    def __initUI(self):
        self.parent.title("Simple Sudoku")
        self.pack(fill=BOTH, expand=1)

        # Menubar
        menubar = Menu(self.parent)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.__from_file)
        filemenu.add_command(label="Import from clipboard", command=self.__from_clip)
        menubar.add_cascade(label="File", menu=filemenu)
        puzzlemenu = Menu(menubar, tearoff=0)
        puzzlemenu.add_command(label="Reset", command=self.__clear_answers)
        puzzlemenu.add_command(label="Clear", command=self.__null_board)
        puzzlemenu.add_command(label="Set Origin", command=self.__to_origin)
        generatemenu = Menu(puzzlemenu, tearoff=0)
        generatemenu.add_command(label="Easy", command=self.__generate_easy)
        generatemenu.add_command(label="Medium", command=self.__generate_medium)
        generatemenu.add_command(label="Hard", command=self.__generate_hard)
        generatemenu.add_command(label="Unfair", command=self.__generate_unfair)
        generatemenu.add_command(label="Extreme", command=self.__generate_extreme)
        puzzlemenu.add_cascade(label="Generate", menu=generatemenu)
        menubar.add_cascade(label="Puzzle", menu=puzzlemenu)
        collectionmenu = Menu(menubar, tearoff=0)
        collectionmenu.add_command(label="Next Puzzle", command=self.__next_puzzle)
        collectionmenu.add_command(label="Previous Puzzle", command=self.__previous_puzzle)
        collectionmenu.add_command(label="Go to specific Puzzle...", command=self.__goto_puzzle)
        collectionmenu.add_command(label="Random Puzzle", command=self.__random_from_file)
        menubar.add_cascade(label="Collection", menu=collectionmenu)
        debugmenu = Menu(menubar, tearoff=0)
        debugmenu.add_command(label="rotate90", command=self.__rotate90)
        debugmenu.add_command(label="flip horizontal", command=self.__flip_hor)
        debugmenu.add_command(label="flip vertical", command=self.__flip_vert)
        debugmenu.add_command(label="translate", command=self.__translate)
        menubar.add_cascade(label="Debug", menu=debugmenu)
        self.parent.config(menu=menubar)

        self.canvas = Canvas(self, width=WIDTH, height=HEIGHT)
        self.canvas.pack(fill=BOTH, side=TOP)
        self.buttons = Frame(self)
        calculate_candidates = Button(self.buttons, text="Calculate candidates", command=self.__calculate_candidates)
        calculate_candidates.grid(row=0, column=4)
        previous_puzzle = Button(self.buttons, text="<<", command=self.__previous_puzzle)
        previous_puzzle.grid(row=0, column=6)
        next_puzzle = Button(self.buttons, text=">>", command=self.__next_puzzle)
        next_puzzle.grid(row=0, column=7)
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
        
        self.canvas.bind("<a>", self.__cursor_left)
        self.canvas.bind("<d>", self.__cursor_right)
        self.canvas.bind("<w>", self.__cursor_up)
        self.canvas.bind("<s>", self.__cursor_down)
        
        self.canvas.bind("<u>", self.__undo)
        self.canvas.bind("<q>", self.__toggle_mode_colouring)
        self.canvas.bind("<e>", self.__erase_colouring)

        self.canvas.bind("<F1>", self.__toggle_highlight)
        self.canvas.bind("<F2>", self.__toggle_highlight)
        self.canvas.bind("<F3>", self.__toggle_highlight)
        self.canvas.bind("<F4>", self.__toggle_highlight)
        self.canvas.bind("<F5>", self.__toggle_highlight)
        self.canvas.bind("<F6>", self.__toggle_highlight)
        self.canvas.bind("<F7>", self.__toggle_highlight)
        self.canvas.bind("<F8>", self.__toggle_highlight)
        self.canvas.bind("<F9>", self.__toggle_highlight)
    
    def __erase_colouring(self, event):
        self.colours = [[None for i in range(9)] for j in range(9)]
        self.__draw_puzzle()
    
    def __undo(self, event):
        self.game.undo()
        self.__draw_puzzle()

    def __generate_easy(self):
        self.game.generate("Easy")
        self.file_name = "Easy.seed"
        self.puzzle_num = 0
        self.__draw_puzzle()

    def __generate_medium(self):
        self.game.generate("Medium")
        self.file_name = "Medium.seed"
        self.puzzle_num = 0
        self.__draw_puzzle()

    def __generate_hard(self):
        self.game.generate("Hard")
        self.file_name = "Hard.seed"
        self.puzzle_num = 0
        self.__draw_puzzle()

    def __generate_unfair(self):
        self.game.generate("Unfair")
        self.file_name = "Unfair.seed"
        self.puzzle_num = 0
        self.__draw_puzzle()

    def __generate_extreme(self):
        self.game.generate("Extreme")
        self.file_name = "Extreme.seed"
        self.puzzle_num = 0
        self.__draw_puzzle()

    def __rotate90(self):
        self.game.rotate90()
        self.__draw_puzzle()

    def __flip_hor(self):
        self.game.flip_hor()
        self.__draw_puzzle()

    def __flip_vert(self):
        self.game.flip_vert()
        self.__draw_puzzle()

    def __translate(self):
        self.game.translate()
        self.__draw_puzzle()

    def __from_file(self):
        self.file_name = filedialog.askopenfilename(title="Open puzzle file")
        self.puzzle_num = 0
        self.game.load_puzzle(self.file_name, self.puzzle_num)
        self.__draw_puzzle()

    def __goto_puzzle(self):
        in_num = simpledialog.askinteger("Go to puzzle", "Go to which puzzle number")
        if in_num is not None:
            self.puzzle_num = in_num - 1
            self.game.load_puzzle(self.file_name, self.puzzle_num)
            self.__draw_puzzle()
        
    def __previous_puzzle(self):
        if self.puzzle_num != 0:
            self.puzzle_num -= 1
        self.game.load_puzzle(self.file_name, self.puzzle_num)
        self.__draw_puzzle()

    def __next_puzzle(self):
        self.puzzle_num += 1
        self.game.load_puzzle(self.file_name, self.puzzle_num)
        self.__draw_puzzle()

    def __random_from_file(self):
        self.game.load_random_puzzle(self.file_name)
        self.__draw_puzzle()
    
    def __calculate_candidates(self):
        self.game.calculate_all_candidates()
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
        self.canvas.delete("puzzleinfo")
        self.canvas.delete("cellcolouring")
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

                # Then draw cell colouring
                colour = self.colours[i][j]
                if not colour is None:
                    self.canvas.create_rectangle(x0, y0, x1, y1, tags="cellcolouring", fill=colour , outline=colour)
                
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
        
        # Write puzzle info in the middle bottom of the puzzle
        pix = WIDTH / 2
        piy = HEIGHT - MARGIN / 2
        puzzle_info = ""
        if self.file_name != "":
            collection_name = self.file_name.split("/")[-1].split(".")[-2]
            if self.puzzle_num == 0:
                puzzle_info = collection_name
            else:
                puzzle_info = "{}: {}".format(collection_name, self.puzzle_num + 1)
        self.canvas.create_text(pix, piy, text=puzzle_info, tags="puzzleinfo", fill="gray", font=("Arial", 12))

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
            elif self.mode is Mode.colour:
                color = "green"
            else:
                color = "pink"
            self.canvas.create_rectangle(x0, y0, x1, y1, outline=color, tags="cursor", width=3)

    def __key_pressed(self, event):
        if self.game.game_over:
            return

        if self.row >= 0 and self.col >= 0 and event.char in "1234567890":
            if self.mode is Mode.solution and self.game.get_origin(self.row,self.col) == 0:
                self.game.set_cell(self.row, self.col, int(event.char))
            elif self.mode is Mode.solution:
                self.highlight = int(event.char)
            elif self.mode is Mode.candidate:
                self.game.toggle_candidate(self.row, self.col, int(event.char))
            elif self.mode is Mode.colour:
                self.colours[self.row][self.col] = COLOURS[int(event.char)]
            self.__draw_puzzle()
            self.__draw_cursor()
            if self.game.check_win():
                #self.__draw_victory()
                messagebox.showinfo("Completed", "Congratulations, you solved the puzzle!")
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
        self.__draw_cursor()

    def __toggle_mode_colouring(self, event):
        if self.mode is Mode.colour:
            self.mode = Mode.solution
        else:
            self.mode = Mode.colour
        self.__draw_cursor()

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
