import random
from collections import deque, namedtuple, Counter
from copy import deepcopy
import tkinter as tk
from tkinter import messagebox, filedialog
import tkinter.simpledialog
import itertools as it
from textwrap import wrap
from enum import Enum
import pickle
from typing import List, Dict, Tuple, Callable


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

class SudokuBoard(object):
    """
    Sudoku Board Representation
    """
    def __init__(self, puzzle_string: str):
        self.__create_board(puzzle_string)
    
    def update(self, puzzle_string: str):
        self.__create_board(puzzle_string)
    
    def get(self) -> List[List[int]]:
        return self.board[:]

    def set_board(self, board: List[List[int]]):
        self.board = board
    
    def __create_board(self, puzzle_string: str):
        rows = wrap(puzzle_string, 9)
        rows = [row.replace('.', '0') for row in rows]
        self.board = [ [int(ch) for ch in row] for row in rows ]

    def generate(self, difficulty: str):
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
    
    def board_big_as_string(self) -> str:
        puzzle_string = ""
        for row in range(9):
            for col in range(9):
                given = self.board[row][col]
                given_str = ""
                if given == 0:
                    given_str = "."
                else:
                    given_str = str(given)
                puzzle_string += given_str
        return puzzle_string
    


Hint = namedtuple('Hint', "technique cells1 cells2 good_cands bad_cands text")

class HintEngine(object):
    """
    Here will be methods that searches hints for solving a sudoku

    Most functions will return Hints
    """
    def __init__(self, game):
        self.hint = None
        self.game = game
        self.techs = [
            self.__naked_single,
            self.__hidden_single,
            self.__naked_pair,
            self.__pointing,
            self.__box_line_reduction,
            self.__naked_triple,
            self.__naked_quad,
            self.__hidden_pair,
            self.__hidden_quad,
            self.__hidden_triple,
        ]

    def get_hint(self) -> Hint:
        for tech in self.techs:
            tech()
            if not self.hint is None:
                break
        
        return self.hint

    def __hidden_pair(self):
        # boxes first
        for box_no in range(1,10):
            coords = self.__get_box_coords(box_no) 
            self.__search_hidden_pair(coords)
            if not self.hint is None:
                return
        # then rows
        for row in range(9):
            coords = self.__get_row_coords(row)
            self.__search_hidden_pair(coords)
            if not self.hint is None:
                return
        
        for col in range(9):
            coords = self.__get_col_coords(col)
            self.__search_hidden_pair(coords)

    def __search_hidden_pair(self, coords: List[Tuple[int, int]]):
        coord_places = self.__get_candidate_positions(coords)
        places = {cand: frozenset(cur_coords) for cand, cur_coords in coord_places.items() if len(cur_coords) == 2 }
        if len(places) < 2:
            return
        place_cands: Dict[frozenset, List[int]] = {}
        for cand, coord_set in places.items():
            if coord_set in place_cands:
                place_cands[coord_set].append(cand)
            else:
                place_cands[coord_set] = [cand]
        
        for cur_coords_set, cands in place_cands.items():
            if len(cands) == 2:
                cur_coords = list(cur_coords_set)
                bad_cands = []
                for row,col in cur_coords:
                    for cand in self.game.get_candidates(row, col):
                        if cand not in cands:
                            bad_cands.append((row, col, cand))
                if not bad_cands:
                    continue
                cells1 = coords
                good_cands = []
                for row,col in cur_coords:
                    for cand in cands:
                        good_cands.append((row, col, cand))
                self.hint = Hint("Hidden pair {} {}".format(cands[0], cands[1]), cells1, None, good_cands, bad_cands, "Hidden pair")
                return
                
    def __hidden_triple(self):
        # boxes first
        for box_no in range(1,10):
            coords = self.__get_box_coords(box_no) 
            self.__search_hidden_triple(coords)
            if not self.hint is None:
                return
        # then rows
        for row in range(9):
            coords = self.__get_row_coords(row)
            self.__search_hidden_triple(coords)
            if not self.hint is None:
                return
        
        for col in range(9):
            coords = self.__get_col_coords(col)
            self.__search_hidden_triple(coords)

    def __search_hidden_triple(self, coords: List[Tuple[int, int]]):
        coord_places = self.__get_candidate_positions(coords)
        places = {cand: frozenset(cur_coords) for cand, cur_coords in coord_places.items() }
        if len(places) < 3:
            return
        all_cands = set()
        for cand_set in places.keys():
            all_cands.add(cand_set)

        place_cands: Dict[int, set] = {}
        for cand, coord_set in places.items():
            if cand in place_cands:
                place_cands[cand].add(coord_set)
            else:
                place_cands[cand] = set(coord_set)

        combinations = [set(combo) for combo in it.combinations(all_cands, 3)]
        for combo in combinations:
            cell_set = set()
            for cand in combo:
                cand_cells = [cell for cell in list(place_cands[cand])]
                for cell in cand_cells:
                    cell_set.add(cell)
            if len(cell_set) == 3:
                containing_cells = list(cell_set)
                cells1 = coords
                good_cands = []
                bad_cands = []
                for row, col in containing_cells:
                    for cand in self.game.get_candidates(row, col):
                        if cand in combo:
                            good_cands.append((row, col, cand))
                        else:
                            bad_cands.append((row, col, cand))
                if not bad_cands:
                    continue
            
                x,y,z = tuple(combo)
                self.hint = Hint("Hidden triple {} {} {}".format(x,y,z), cells1, None, good_cands, bad_cands, "Hidden Triple" )
                return

    def __hidden_quad(self):
        # boxes first
        for box_no in range(1,10):
            coords = self.__get_box_coords(box_no) 
            self.__search_hidden_quad(coords)
            if not self.hint is None:
                return
        # then rows
        for row in range(9):
            coords = self.__get_row_coords(row)
            self.__search_hidden_quad(coords)
            if not self.hint is None:
                return
        
        for col in range(9):
            coords = self.__get_col_coords(col)
            self.__search_hidden_quad(coords)

    def __search_hidden_quad(self, coords: List[Tuple[int, int]]):
        coord_places = self.__get_candidate_positions(coords)
        places = {cand: frozenset(cur_coords) for cand, cur_coords in coord_places.items() }
        if len(places) < 4:
            return
        all_cands = set()
        for cand_set in places.keys():
            all_cands.add(cand_set)

        place_cands: Dict[int, set] = {}
        for cand, coord_set in places.items():
            if cand in place_cands:
                place_cands[cand].add(coord_set)
            else:
                place_cands[cand] = set(coord_set)

        combinations = [set(combo) for combo in it.combinations(all_cands, 4)]
        for combo in combinations:
            cell_set = set()
            for cand in combo:
                cand_cells = [cell for cell in list(place_cands[cand])]
                for cell in cand_cells:
                    cell_set.add(cell)
            if len(cell_set) == 4:
                containing_cells = list(cell_set)
                cells1 = coords
                good_cands = []
                bad_cands = []
                for row, col in containing_cells:
                    for cand in self.game.get_candidates(row, col):
                        if cand in combo:
                            good_cands.append((row, col, cand))
                        else:
                            bad_cands.append((row, col, cand))
                if not bad_cands:
                    continue
            
                w,x,y,z = tuple(combo)
                self.hint = Hint("Hidden quad {} {} {} {}".format(w,x,y,z), cells1, None, good_cands, bad_cands, "Hidden Quad" )
                return

    def __get_candidate_positions(self, coords: List[Tuple[int, int]]) -> Dict[int, List[Tuple[int, int]]]:
        coord_cand = {(row, col): self.game.get_candidates(row, col) for row, col in coords}

        cand_coord: Dict[int, List[Tuple[int, int]]] = {}
        for coord, cands in coord_cand.items():
            for cand in cands:
                if cand in cand_coord:
                    cand_coord[cand].append(coord)
                else:
                    cand_coord[cand] = [coord]
        
        return cand_coord



    def __naked_triple(self):
        # boxes first
        for box_no in range(1,10):
            coords = self.__get_box_coords(box_no)
            triplets = [(frozenset(self.game.get_candidates(row, col)), (row, col)) for row, col in coords if len(self.game.get_candidates(row, col)) <= 3]
            if not triplets:
                continue
            triplet_coords = self.__get_triplet_coords(triplets)
            if not triplet_coords:
                continue
            for triplet, cur_coords in triplet_coords.items():
                x, y, z = tuple(triplet)
                # Affecting row
                rows = set([row for row, col in cur_coords])
                if len(rows) == 1:
                    cells1 = coords + self.__get_row_coords(list(rows)[0])
                    self.__create_triple_hint(x,y,z, cells1, cur_coords)
                    if not self.hint is None:
                        return

                # Affecting column
                cols = set([col for row, col in cur_coords])
                if len(cols) == 1:
                    cells1 = coords + self.__get_col_coords(list(cols)[0])
                    self.__create_triple_hint(x,y,z, cells1, cur_coords)
                    if not self.hint is None:
                        return

                # Only box
                cells1 = coords
                self.__create_triple_hint(x,y,z, cells1, cur_coords)
                if not self.hint is None:
                    return
        
        # Then rows
        for row in range(9):
            coords = self.__get_row_coords(row)
            triplets = [(frozenset(self.game.get_candidates(row, col)), (row, col)) for row, col in coords if len(self.game.get_candidates(row, col)) <= 3]
            if not triplets:
                continue
            triplet_coords = self.__get_triplet_coords(triplets)
            if not triplet_coords:
                continue
            for triplet, cur_coords in triplet_coords.items():
                x, y, z = tuple(triplet)
                cells1 = coords
                self.__create_triple_hint(x,y,z, cells1, cur_coords)
                if not self.hint is None:
                    return


        # Then colums
        for col in range(9):
            coords = self.__get_col_coords(col)
            triplets = [(frozenset(self.game.get_candidates(row, col)), (row, col)) for row, col in coords if len(self.game.get_candidates(row, col)) <= 3]
            if not triplets:
                continue
            triplet_coords = self.__get_triplet_coords(triplets)
            if not triplet_coords:
                continue
            for triplet, cur_coords in triplet_coords.items():
                x, y, z = tuple(triplet)
                cells1 = coords
                self.__create_triple_hint(x,y,z, cells1, cur_coords)
                if not self.hint is None:
                    return

    def __create_triple_hint(self, x: int, y: int, z: int, cells1: List[Tuple[int, int]], cur_coords: List[Tuple[int, int]]):
        good_cands = [(row, col, x) for row, col in cur_coords] + [(row, col, y) for row, col in cur_coords] + [(row, col, z) for row, col in cur_coords]
        bad_x = [(row, col, x) for row, col in cells1 if (row, col) not in cur_coords and x in self.game.get_candidates(row, col)]
        bad_y = [(row, col, y) for row, col in cells1 if (row, col) not in cur_coords and y in self.game.get_candidates(row, col)] 
        bad_z = [(row, col, z) for row, col in cells1 if (row, col) not in cur_coords and z in self.game.get_candidates(row, col)] 
        bad_cands = bad_x + bad_y + bad_z
        if not bad_cands:
            return
        self.hint = Hint("Naked triple {} {} {}".format(x, y, z), cells1, None, good_cands, bad_cands, "Naked triple")
    
    def __get_triplet_coords(self, triplets: List[Tuple[frozenset, Tuple[int, int]]]) -> Dict[frozenset, List[Tuple[int, int]]]:
        triplet_coords = {}
        combinations = it.combinations(triplets, 3)
        for a, b, c in combinations:
            union = a[0].union(b[0], c[0])
            if len(union) == 3:
                triplet_coords[union] = [a[1], b[1], c[1]]

        return triplet_coords

    def __naked_quad(self):
        # boxes first
        for box_no in range(1,10):
            coords = self.__get_box_coords(box_no)
            quads = [(frozenset(self.game.get_candidates(row, col)), (row, col)) for row, col in coords if len(self.game.get_candidates(row, col)) <= 4]
            if not quads:
                continue
            quad_coords = self.__get_quad_coords(quads)
            if not quad_coords:
                continue
            for quad, cur_coords in quad_coords.items():
                x, y, z, a = tuple(quad)
                # Affecting row
                rows = set([row for row, col in cur_coords])
                if len(rows) == 1:
                    cells1 = coords + self.__get_row_coords(list(rows)[0])
                    self.__create_quad_hint(x,y,z,a, cells1, cur_coords)
                    if not self.hint is None:
                        return

                # Affecting column
                cols = set([col for row, col in cur_coords])
                if len(cols) == 1:
                    cells1 = coords + self.__get_col_coords(list(cols)[0])
                    self.__create_quad_hint(x,y,z,a, cells1, cur_coords)
                    if not self.hint is None:
                        return

                # Only box
                cells1 = coords
                self.__create_quad_hint(x,y,z,a, cells1, cur_coords)
                if not self.hint is None:
                    return
        
        # Then rows
        for row in range(9):
            coords = self.__get_row_coords(row)
            quads = [(frozenset(self.game.get_candidates(row, col)), (row, col)) for row, col in coords if len(self.game.get_candidates(row, col)) <= 4]
            if not quads:
                continue
            quad_coords = self.__get_quad_coords(quads)
            if not quad_coords:
                continue
            for quad, cur_coords in quad_coords.items():
                x, y, z, a = tuple(quad)
                cells1 = coords
                self.__create_quad_hint(x,y,z,a, cells1, cur_coords)
                if not self.hint is None:
                    return


        # Then colums
        for col in range(9):
            coords = self.__get_col_coords(col)
            quads = [(frozenset(self.game.get_candidates(row, col)), (row, col)) for row, col in coords if len(self.game.get_candidates(row, col)) <= 4]
            if not quads:
                continue
            quad_coords = self.__get_quad_coords(quads)
            if not quad_coords:
                continue
            for quad, cur_coords in quad_coords.items():
                x, y, z, a = tuple(quad)
                cells1 = coords
                self.__create_quad_hint(x,y,z,a, cells1, cur_coords)
                if not self.hint is None:
                    return

    def __create_quad_hint(self, x: int, y: int, z: int, a: int, cells1: List[Tuple[int, int]], cur_coords: List[Tuple[int, int]]):
        good_cands = [(row, col, x) for row, col in cur_coords] + [(row, col, y) for row, col in cur_coords] + [(row, col, z) for row, col in cur_coords] + [(row, col, a) for row, col in cur_coords]
        bad_x = [(row, col, x) for row, col in cells1 if (row, col) not in cur_coords and x in self.game.get_candidates(row, col)]
        bad_y = [(row, col, y) for row, col in cells1 if (row, col) not in cur_coords and y in self.game.get_candidates(row, col)] 
        bad_z = [(row, col, z) for row, col in cells1 if (row, col) not in cur_coords and z in self.game.get_candidates(row, col)] 
        bad_a = [(row, col, a) for row, col in cells1 if (row, col) not in cur_coords and a in self.game.get_candidates(row, col)] 
        bad_cands = bad_x + bad_y + bad_z + bad_a
        if not bad_cands:
            return
        self.hint = Hint("Naked quad {} {} {} {}".format(x, y, z, a), cells1, None, good_cands, bad_cands, "Naked quad")
    
    def __get_quad_coords(self, quads: List[Tuple[frozenset, Tuple[int, int]]]) -> Dict[frozenset, List[Tuple[int, int]]]:
        quad_coords = {}
        combinations = it.combinations(quads, 4)
        for a, b, c, d in combinations:
            union = a[0].union(b[0], c[0], d[0])
            if len(union) == 4:
                quad_coords[union] = [a[1], b[1], c[1], d[1]]

        return quad_coords

    def __naked_pair(self):
        # boxes first
        for box_no in range(1,10):
            coords = self.__get_box_coords(box_no)
            pairs = [(frozenset(self.game.get_candidates(row, col)), (row, col)) for row, col in coords if len(self.game.get_candidates(row, col)) == 2]
            if not pairs:
                continue
            pair_coords = self.__get_pair_coords(pairs)
            for pair, cur_coords in pair_coords.items():
                x, y = tuple(pair)
                if len(cur_coords) == 2:
                    # Affecting row
                    rows = set([row for row,col in cur_coords])
                    if len(rows) == 1:
                        cells1 = coords + self.__get_row_coords(list(rows)[0])
                        self.__create_pair_hint(x,y,cells1, cur_coords)
                        if not self.hint is None:
                            return

                    # Affecting column
                    cols = set([col for row,col in cur_coords])
                    if len(cols) == 1:
                        cells1 = coords + self.__get_col_coords(list(cols)[0])
                        self.__create_pair_hint(x,y,cells1, cur_coords)
                        if not self.hint is None:
                            return

                    # Only box
                    cells1 = coords
                    self.__create_pair_hint(x,y, cells1, cur_coords)
                    if not self.hint is None:
                        return

        # Then rows
        for row in range(9):
            coords = self.__get_row_coords(row)
            pairs = [(frozenset(self.game.get_candidates(row, col)), (row, col)) for row, col in coords if len(self.game.get_candidates(row, col)) == 2]
            if not pairs:
                continue
            pair_coords = self.__get_pair_coords(pairs)
            for pair, cur_coords in pair_coords.items():
                x, y = tuple(pair)
                if len(cur_coords) == 2:
                    cells1 = coords
                    self.__create_pair_hint(x,y, cells1, cur_coords)
                    if not self.hint is None:
                        return

        # At last columns
        for col in range(9):
            coords = self.__get_col_coords(col)
            pairs = [(frozenset(self.game.get_candidates(row, col)), (row, col)) for row, col in coords if len(self.game.get_candidates(row, col)) == 2]
            if not pairs:
                continue
            pair_coords = self.__get_pair_coords(pairs)
            for pair, cur_coords in pair_coords.items():
                x, y = tuple(pair)
                if len(cur_coords) == 2:
                    cells1 = coords
                    self.__create_pair_hint(x, y, cells1, cur_coords)
                    if not self.hint is None:
                        return
    
    def __create_pair_hint(self, x: int, y: int, cells1: List[Tuple[int, int]], cur_coords: List[Tuple[int, int]]):
        good_cands = [(row, col, x) for row, col in cur_coords] + [(row, col, y) for row, col in cur_coords]
        bad_x = [(row, col, x) for row, col in cells1 if (row, col) not in cur_coords and x in self.game.get_candidates(row, col)]
        bad_y = [(row, col, y) for row, col in cells1 if (row, col) not in cur_coords and y in self.game.get_candidates(row, col)] 
        bad_cands = bad_x + bad_y
        if not bad_cands:
            return
        self.hint = Hint("Naked pair {} {}".format(x, y), cells1, None, good_cands, bad_cands, "Naked pair")

    def __get_pair_coords(self, pairs: List[Tuple[frozenset, Tuple[int, int]]]) -> Dict[frozenset, List[Tuple[int, int]]]:
        pair_coords: Dict[frozenset, List[Tuple[int, int]]] = {}
        for pair, coord in pairs:
            if pair in pair_coords:
                pair_coords[pair].append(coord)
            else:
                pair_coords[pair] = [coord]
        
        return pair_coords

    def __box_line_reduction(self):
        # First check rows
        for row in range(9):
            coords = self.__get_row_coords(row)
            self.__search_bl_reduction(coords)

        if not self.hint is None:
            return
        # Then columns
        for col in range(9):
            coords = self.__get_col_coords(col)
            self.__search_bl_reduction(coords)

    def __search_bl_reduction(self, coords: List[Tuple[int, int]]):
        candidate_coords = self.__get_candidate_coords(coords)

        for candidate in range(1,10):
            cur_coords = candidate_coords.get(candidate, None)

            if cur_coords is None:
                continue

            boxes = set()
            for row, col in cur_coords:
                boxes.add(self.__get_box(row, col))
            
            # Are all of the candidates in the same box?
            if len(boxes) == 1:
                # Do we have any candidates to delete in that box
                box_coords = [cell for cell in self.__get_box_coords(list(boxes)[0]) if cell not in cur_coords]
                bad_cands = [(row, col, candidate) for (row, col) in box_coords if candidate in self.game.get_candidates(row, col)]
                if not bad_cands:
                    continue
                good_cands = [(row, col, candidate) for (row, col) in cur_coords]
                cells1 = coords + box_coords

                self.hint = Hint("Box-line reduction", cells1, None, good_cands, bad_cands, "Box line interaction")
                return


            
    def __get_box(self, row: int, col: int) -> int:
        box_row = row // 3
        box_col = col // 3

        boxes = [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9]
        ]

        return boxes[box_row][box_col]

    def __pointing(self):
        for box_no in range(1,10):
            coords = self.__get_box_coords(box_no)
            candidate_coords = self.__get_candidate_coords(coords)

            # Go through each candidate to see if it is pointing
            for candidate in range(1,10):
                cur_coords = candidate_coords.get(candidate, None)

                if cur_coords is None:
                    continue
                
                # Filter out already answered cells
                # Can only be pointing if 2 or three candidates
                if len(cur_coords) == 2 or len(cur_coords) == 3:
                    # are we row pointing
                    rows = set([row for row, col in cur_coords])
                    if len(rows) == 1:
                        # we are pointing in a row, are we pointing at something that we can delete?
                        row_coords = self.__get_row_coords(list(rows)[0])
                        row_coords = [(row, col) for row, col in row_coords if (row, col) not in cur_coords]
                        bad_cands = [(row, col, candidate) for (row, col) in row_coords if candidate in self.game.get_candidates(row, col)]
                        if not bad_cands:
                            continue
                        good_cands = [(row, col, candidate) for (row, col) in cur_coords]
                        cells1 = coords + row_coords
                        self.hint = Hint("Pointing Pair/Triple (row)", cells1, None, good_cands, bad_cands, "Pointing Pair/Triple reduces row")
                        return

                    cols = set([col for row, col in cur_coords])
                    if len(cols) == 1:
                        # we are pointing in a column, are we pointing at something we can delete?
                        col_coords = self.__get_col_coords(list(cols)[0])
                        col_coords = [(row, col) for row, col in col_coords if (row, col) not in cur_coords]
                        bad_cands = [(row, col, candidate) for (row, col) in col_coords if candidate in self.game.get_candidates(row, col)]
                        if not bad_cands:
                            continue
                        good_cands = [(row, col, candidate) for (row, col) in cur_coords]
                        cells1 = coords + col_coords
                        self.hint = Hint("Pointing Pair/Triple (column)", cells1, None, good_cands, bad_cands, "Pointing Pair/Triple reduces row")
                        return

    def __get_candidate_coords(self, coords: List[Tuple[int, int]]) -> Dict[int, List[Tuple[int, int]]]:
        candidate_coords: Dict[int, List[Tuple[int, int]]] = {}
        # Build list of locations where each candidate can be
        for row, col in coords:
            candidates = self.game.get_candidates(row, col)
            for candidate in candidates:
                if candidate in candidate_coords:
                    candidate_coords[candidate].append((row, col))
                else:
                    candidate_coords[candidate] = [(row, col)]
        return candidate_coords

    def __naked_single(self):
        good_cells = []
        good_cands = []
        for row in range(9):
            for col in range(9):
                cands = self.game.get_candidates(row, col)
                if len(cands) == 1 and self.game.get_cell(row, col) == 0:
                    good_cells.append((row,col))
                    good_cands.append((row,col,cands[0]))
        
        if len(good_cells) > 0:
            self.hint = Hint("Naked single", good_cells, None, good_cands, None, "The only number that can go in this cell is")
    
    def __hidden_single(self):
        searches = [
            self.__hs_search_box,
            self.__hs_search_row,
            self.__hs_search_col
        ]
        for search in searches:
            search()
            if self.hint is None:
                continue
            else:
                return
    
    def __hs_search_box(self):
        for box_no in range(1,10):
            coords = self.__get_box_coords(box_no)
            found, (coord, cand) = self.__hs_search(coords)
            if found:
                row, col = coord
                self.hint = Hint("Hidden single (box)", coords, None, ((row, col, cand),), None, "In the box this is the only cell with this candidate")
                return

    def __hs_search_row(self):
        for row in range(9):
            coords = self.__get_row_coords(row)
            found, (coord, cand) = self.__hs_search(coords)
            if found:
                row, col = coord
                self.hint = Hint("Hidden single (row)", coords, None, ((row, col, cand),), None, "In the row this candidate can only be here" )
                return

    def __hs_search_col(self):
        for col in range(9):
            coords = self.__get_col_coords(col)
            found, (coord, cand) = self.__hs_search(coords)
            if found:
                row, col = coord
                self.hint = Hint("Hidden single (column)", coords, None, ((row, col, cand),), None, "In the column this candidate can only be here" )
                return

    def __hs_search(self, coords: List[Tuple[int, int]]) -> Tuple[bool, Tuple[Tuple[int, int], int]]:
        cnt: Counter = Counter()
        search_coords = [ (row, col) for row, col in coords if self.game.get_cell(row,col) == 0]
        for row, col in search_coords:
            cnt.update(self.game.get_candidates(row, col))
        
        for i in range(1,10):
            if cnt[i] == 1:
                for row, col in search_coords:
                    if i in self.game.get_candidates(row, col):
                        return (True, ((row,col), i))
        return (False, ((0,0), 0))

    def __get_box_coords(self, box_no: int) -> List[Tuple[int, int]]:
        coords: list = [
            ((0,0),(0,0),(0,0),(0,0),(0,0),(0,0),(0,0),(0,0),(0,0)),
            # Box 1
            ((0,0),(0,1),(0,2),(1,0),(1,1),(1,2),(2,0),(2,1),(2,2)),
            # Box 2
            ((0,3),(0,4),(0,5),(1,3),(1,4),(1,5),(2,3),(2,4),(2,5)),
            # Box 3
            ((0,6),(0,7),(0,8),(1,6),(1,7),(1,8),(2,6),(2,7),(2,8)),
            # Box 4
            ((3,0),(3,1),(3,2),(4,0),(4,1),(4,2),(5,0),(5,1),(5,2)),
            # Box 5
            ((3,3),(3,4),(3,5),(4,3),(4,4),(4,5),(5,3),(5,4),(5,5)),
            # Box 6
            ((3,6),(3,7),(3,8),(4,6),(4,7),(4,8),(5,6),(5,7),(5,8)),
            # Box 7
            ((6,0),(6,1),(6,2),(7,0),(7,1),(7,2),(8,0),(8,1),(8,2)),
            # Box 8
            ((6,3),(6,4),(6,5),(7,3),(7,4),(7,5),(8,3),(8,4),(8,5)),
            # Box 9
            ((6,6),(6,7),(6,8),(7,6),(7,7),(7,8),(8,6),(8,7),(8,8)),
        ]
        return [(row, col) for row, col in coords[box_no] if self.game.get_cell(row, col) == 0]

    def __get_row_coords(self, row: int) -> List[Tuple[int, int]]:
        coords = []
        for i in range(9):
            coords.append((row,i))
        return [(row, col) for row, col in coords if self.game.get_cell(row, col) == 0]
    
    def __get_col_coords(self, col: int) -> List[Tuple[int, int]]:
        coords = []
        for i in range(9):
            coords.append((i, col))
        return [(row, col) for row, col in coords if self.game.get_cell(row, col) == 0]

    def get_naked(self) -> Hint:
        self.__naked_single()
        return self.hint

class SudokuGame(object):
    """
    A Sudoku game, in charge of storing the state of the board and checking
    whether the puzzle is completed.
    """

    def __init__(self):
        self.board = SudokuBoard("0" * 81)
        self.puzzle = self.board.get()
        self.start_puzzle = self.board.get()
        self.candidates = [[set() for x in range(9)] for y in range(9)]
        self.undostack = deque()
        self.null_board()
        self.current_to_origin()
        self.colours = [[0 for i in range(9)] for j in range(9)]
        self.candidate_colours = [[[0 for x in range(10)] for y in range(9)] for z in range(9)]

    def start(self):
        self.game_over = False
        self.candidates = [[set() for x in range(9)] for y in range(9)]
        self.puzzle = []
        self.colours = [[0 for i in range(9)] for j in range(9)]
        self.candidate_colours = [[[0 for x in range(10)] for y in range(9)] for z in range(9)]

        for i in range(9):
            self.puzzle.append([])
            for j in range(9):
                self.puzzle[i].append(self.start_puzzle[i][j])
        self.board.set_board(self.puzzle)
        self.save_undo_state()
    
    def save_undo_state(self):
        self.undostack.append((deepcopy(self.puzzle), deepcopy(self.start_puzzle), deepcopy(self.candidates),deepcopy(self.colours), deepcopy(self.candidate_colours)))

    def hint(self) -> str:
        self.reset_colours()
        hint = HintEngine(self).get_hint()

        if hint is None:
            return

        if not hint.cells1 is None:
            for cell in hint.cells1:
                row, col = cell
                self.colours[row][col] = 3

        if not hint.cells2 is None:
            for cell in hint.cells2:
                row, col = cell
                self.colours[row][col] = 4

        if not hint.good_cands is None:
            for cand in hint.good_cands:
                row, col, cand = cand
                self.candidate_colours[row][col][cand] = 1

        if not hint.bad_cands is None:
            for cand in hint.bad_cands:
                row, col, cand = cand
                self.candidate_colours[row][col][cand] = 2
        
        return hint.technique

    def undo(self):
        self.puzzle, self.start_puzzle, self.candidates, self.colours, self.candidate_colours = self.undostack.pop()

    def get_state(self) -> str:
        state = ""
        return state

    def get_cell(self, row: int, col: int) -> int:
        return self.puzzle[row][col]
    
    def set_cell(self, row: int, col: int, val: int, undo=True):
        self.puzzle[row][col] = val
        self.update_candidates(row, col, undo=False)
        if undo:
            self.save_undo_state()
    
    def calculate_all_candidates(self):
        for row in range(9):
            for col in range(9):
                self.calculate_candidates(row, col, undo=False)
        self.save_undo_state()

    def calculate_candidates(self, row: int, col: int, undo=True):
        if self.puzzle[row][col] == 0:
            candidates = list(set(range(10)).difference(self.__set_buddies(row, col)))
            for candidate in candidates:
                self.add_candidate(row, col, candidate, undo=False)
        
        if undo:
            self.save_undo_state()


    def get_candidates(self, row: int, col: int) -> List[int]:
        return list(self.candidates[row][col])
    
    def get_candidate_set(self, row: int, col: int) -> List[int]:
        return self.candidates
    
    def get_cell_colour(self, row: int, col: int) -> str:
        return COLOURS[self.colours[row][col]]
    
    def get_candidate_colour(self, row: int, col: int, candidate: int) -> str:
        return COLOURS[self.candidate_colours[row][col][candidate]]
    
    def set_candidate_colour(self, row: int, col: int, candidate: int, colour_number: int, undo=True):
        self.candidate_colours[row][col][candidate] = colour_number
        if undo:
            self.save_undo_state()
    
    def set_cell_colour(self, row: int, col: int, colour_number: int, undo=True):
        self.colours[row][col] = colour_number
        if undo:
            self.save_undo_state()


    def toggle_candidate(self, row: int, col: int, val: int, undo=True):
        if val not in self.candidates[row][col]:
            self.candidates[row][col].add(val)
        else:
            self.candidates[row][col].remove(val)
        if undo:
            self.save_undo_state()

    def reset_colours(self):
        self.colours = [[0 for i in range(9)] for j in range(9)]
        self.candidate_colours = [[[0 for x in range(10)] for y in range(9)] for z in range(9)]
    
    def remove_candidate(self, row: int, col: int, val: int, undo=True):
        self.candidates[row][col].discard(val)
        if undo:
            self.save_undo_state()
    
    def add_candidate(self, row: int, col: int, val: int, undo=True):
        self.candidates[row][col].add(val)
        if undo:    
            self.save_undo_state()

    def get_origin(self, row: int, col: int) -> int:
        return self.start_puzzle[row][col]
    
    def get_puzzle_string(self) -> str:
        self.board.set_board(self.start_puzzle)
        return self.board.board_big_as_string()

    def set_forum_string(self, forum_string: str):
        new_origin = [[0 for col in range(9)] for row in range(9)]
        new_candidates: List[List[set]] = [[set() for x in range(9)] for y in range(9)]
        tmp_cands = []
        for line in forum_string.splitlines():
            line.strip()
            if not line or not line[0] == "|":
                continue
            line = line.replace("|", "")
            row_str = line.split()
            new_row: List[List[int]] = []
            for col in range(9):
                new_row[col] = [int(char) for char in row_str[col]]
            tmp_cands.append(new_row)
            
            
        for row in range(9):
            for col in range(9):
                cur_cands = tmp_cands[row][col]
                if len(cur_cands) == 1:
                    new_origin[row][col] = cur_cands[0]
                else:
                    new_candidates[row][col].update(set(cur_cands))
        
        self.start_puzzle = new_origin
        self.puzzle = new_origin
        self.candidates = new_candidates

    def get_forum_string(self) -> str:
        forum_string = ""
        # Build up candidate diagram
        col_widths = [0 for col in range(9)]
        candidates: List[List[List[int]]] = [[[] for col in range(9)] for row in range(9)]
        for row in range(9):
            for col in range(9):
                cur = self.get_cell(row, col)
                if cur != 0:
                    candidates[row][col] = [cur]
                else:
                    candidates[row][col] = self.get_candidates(row, col)
                
                width = len(candidates[row][col])
                if width > col_widths[col]:
                    col_widths[col] = width

        # Prettyprint it
        spacing = "-" * 4
        header = "."
        header += "-" * (col_widths[0] + col_widths[1] + col_widths[2])
        header += spacing
        header += "."
        header += "-" * (col_widths[3] + col_widths[4] + col_widths[5])
        header += spacing
        header += "."
        header += "-" * (col_widths[6] + col_widths[7] + col_widths[8])
        header += spacing
        header += "."
        header += "\n"
        
        footer = "'"
        footer += "-" * (col_widths[0] + col_widths[1] + col_widths[2])
        footer += spacing
        footer += "'"
        footer += "-" * (col_widths[3] + col_widths[4] + col_widths[5])
        footer += spacing
        footer += "'"
        footer += "-" * (col_widths[6] + col_widths[7] + col_widths[8])
        footer += spacing
        footer += "'"

        spacer = ":"
        spacer += "-" * (col_widths[0] + col_widths[1] + col_widths[2])
        spacer += spacing
        spacer += "+"
        spacer += "-" * (col_widths[3] + col_widths[4] + col_widths[5])
        spacer += spacing
        spacer += "+"
        spacer += "-" * (col_widths[6] + col_widths[7] + col_widths[8])
        spacer += spacing
        spacer += ":"
        spacer += "\n"

        forum_string += header
        forum_string += self.__cand_row_to_string(candidates[0], col_widths)
        forum_string += self.__cand_row_to_string(candidates[1], col_widths)
        forum_string += self.__cand_row_to_string(candidates[2], col_widths)
        forum_string += spacer
        forum_string += self.__cand_row_to_string(candidates[3], col_widths)
        forum_string += self.__cand_row_to_string(candidates[4], col_widths)
        forum_string += self.__cand_row_to_string(candidates[5], col_widths)
        forum_string += spacer
        forum_string += self.__cand_row_to_string(candidates[6], col_widths)
        forum_string += self.__cand_row_to_string(candidates[7], col_widths)
        forum_string += self.__cand_row_to_string(candidates[8], col_widths)
        forum_string += footer

        return forum_string
    
    def __cand_row_to_string(self, cands: List[List[int]], col_widths: List[int]) -> str:
        candstrings = ["".join(["".join(str(cand2)) for cand2 in cand]) for cand in cands]

        for col in range(9):
            candstrings[col] += " " * (col_widths[col] - len(candstrings[col]))

        result = ""
        result += "| "
        result += candstrings[0]
        result += " "
        result += candstrings[1]
        result += " "
        result += candstrings[2]
        result += " | "
        result += candstrings[3]
        result += " "
        result += candstrings[4]
        result += " "
        result += candstrings[5]
        result += " | "
        result += candstrings[6]
        result += " "
        result += candstrings[7]
        result += " "
        result += candstrings[8]
        result += " |\n"

        return result

    def update_candidates(self, row: int, col: int, undo=True):
        answer = self.puzzle[row][col]
        buddies = self.__find_buddies(row, col)
        for r, c in buddies:
            self.remove_candidate(r, c, answer, undo=False)
        if undo:
            self.save_undo_state()

    def __find_buddies(self, row: int, col: int) -> List[Tuple[int, int]]:
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
        self.save_undo_state()
    
    def null_board(self):
        for i in range(9):
            for j in range(9):
                self.start_puzzle[i][j] = 0
        self.start()
                
    def load_puzzle(self, file_name: str, line_number: int):
        with open(file_name) as file:
            puzzles = [line.strip() for line in file]
            self.from_string(puzzles[line_number])
        self.save_undo_state()

    def generate(self, difficulty: str):
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

    def load_random_puzzle(self, file_name: str):
        with open(file_name) as file:
            puzzles = [line.strip() for line in file]
            self.from_string(random.choice(puzzles))
        self.save_undo_state()

    def from_string(self, puzzle_string: str):
        self.board.update(puzzle_string)
        self.start_puzzle = self.board.get()
        self.start()
        self.save_undo_state()
    
    def check_win(self) -> bool:
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

    def __check_group(self, block: List[int]) -> bool:
        return set(block) == set(range(1,10))

    def __check_row(self, row: int) -> bool:
        return self.__check_group(self.puzzle[row])

    def __set_row(self, row: int) -> set:
        return set(self.puzzle[row])

    def __check_column(self, col: int) -> bool:
        return self.__check_group(
            [self.puzzle[row][col] for row in range(9)]
        )
    
    def __set_column(self, col: int) -> set:
        return set([self.puzzle[row][col] for row in range(9)])

    def __check_square(self, row: int, col: int) -> bool:
        return self.__check_group(
            [
                self.puzzle[r][c]
                for r in range(row * 3, (row + 1) * 3)
                for c in range(col * 3, (col + 1) * 3)
            ]
        )
    
    def __set_square(self, box_row: int, box_col: int) -> set:
        return set(
            [
                self.puzzle[r][c]
                for r in range(box_row * 3, (box_row + 1) * 3)
                for c in range(box_col * 3, (box_col + 1) * 3)
            ]
        )
    
    def __set_buddies(self, row: int, col: int) -> set:
        return self.__set_row(row).union(self.__set_column(col), self.__set_square(row // 3, col // 3))

    
class SudokuUI(tk.Frame):
    """
    The Tkinter UI, responsible for drawing the board and accepting user input.
    """
    def __init__(self, parent: tk.Tk, game: SudokuGame):
        self.game = game
        self.parent = parent
        tk.Frame.__init__(self, parent)

        self.margin =  20 # Pixels around the board
        self.side = 50 # Height of each board cell
        self.width = self.height = self.margin * 2 + self.side * 9 # Width and height of the whole board
        self.cluesize = self.side // 2
        self.candidatesize = self.side // 4
        self.candidatediff = self.side // 3

        self.row, self.col = 0, 0
        self.mode = Mode.solution
        self.highlight = 0
        self.puzzle_num = 0
        self.file_name = ""
        self.technique = ""
        self.autosolve_naked_singles = tk.BooleanVar(value=False)

        self.__initUI()

    def __initUI(self):
        self.parent.title("Simple Sudoku")
        self.pack(fill=tk.BOTH, expand=1)

        # Menubar
        menubar = tk.Menu(self.parent)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open...", command=self.__from_file)
        filemenu.add_command(label="Import from clipboard", command=self.__from_clip)
        filemenu.add_command(label="Import candidates from clipboard", command=self.__from_candidates_clip)
        filemenu.add_command(label="Export givens to clipboard", command=self.__export_givens_clip)
        filemenu.add_command(label="Export candidates to clipboard", command=self.__export_candidates_clip)
        filemenu.add_command(label="Save state as...", command=self.__save_state_as)
        menubar.add_cascade(label="File", menu=filemenu)
        puzzlemenu = tk.Menu(menubar, tearoff=0)
        puzzlemenu.add_command(label="Calculate candidates", command=self.__calculate_candidates)
        puzzlemenu.add_command(label="Get hint", command=self.__hint)
        puzzlemenu.add_checkbutton(label="Autosolve naked singles", onvalue=True, offvalue=0, variable=self.autosolve_naked_singles)
        puzzlemenu.add_command(label="Reset", command=self.__clear_answers)
        puzzlemenu.add_command(label="Clear", command=self.__null_board)
        puzzlemenu.add_command(label="Set Origin", command=self.__to_origin)
        generatemenu = tk.Menu(puzzlemenu, tearoff=0)
        generatemenu.add_command(label="Easy", command=self.__generate_easy)
        generatemenu.add_command(label="Medium", command=self.__generate_medium)
        generatemenu.add_command(label="Hard", command=self.__generate_hard)
        generatemenu.add_command(label="Unfair", command=self.__generate_unfair)
        generatemenu.add_command(label="Extreme", command=self.__generate_extreme)
        puzzlemenu.add_cascade(label="Generate", menu=generatemenu)
        menubar.add_cascade(label="Puzzle", menu=puzzlemenu)
        collectionmenu = tk.Menu(menubar, tearoff=0)
        collectionmenu.add_command(label="Next Puzzle", command=self.__next_puzzle)
        collectionmenu.add_command(label="Previous Puzzle", command=self.__previous_puzzle)
        collectionmenu.add_command(label="Go to specific Puzzle...", command=self.__goto_puzzle)
        collectionmenu.add_command(label="Random Puzzle", command=self.__random_from_file)
        menubar.add_cascade(label="Collection", menu=collectionmenu)
        debugmenu = tk.Menu(menubar, tearoff=0)
        debugmenu.add_command(label="rotate90", command=self.__rotate90)
        debugmenu.add_command(label="flip horizontal", command=self.__flip_hor)
        debugmenu.add_command(label="flip vertical", command=self.__flip_vert)
        debugmenu.add_command(label="translate", command=self.__translate)
        menubar.add_cascade(label="Debug", menu=debugmenu)
        self.parent.config(menu=menubar)

        self.canvas = tk.Canvas(self, width=WIDTH, height=HEIGHT)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.__draw_grid()
        self.__draw_puzzle()
        self.__draw_cursor()
        self.canvas.focus_set()
        
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
        self.canvas.bind("<f>", self.__toggle_mode_colour_candidate)
        self.canvas.bind("<c>", self.__calculate_candidates)
        self.canvas.bind("<h>", self.__hint)

        self.canvas.bind("<F1>", self.__toggle_highlight)
        self.canvas.bind("<F2>", self.__toggle_highlight)
        self.canvas.bind("<F3>", self.__toggle_highlight)
        self.canvas.bind("<F4>", self.__toggle_highlight)
        self.canvas.bind("<F5>", self.__toggle_highlight)
        self.canvas.bind("<F6>", self.__toggle_highlight)
        self.canvas.bind("<F7>", self.__toggle_highlight)
        self.canvas.bind("<F8>", self.__toggle_highlight)
        self.canvas.bind("<F9>", self.__toggle_highlight)

        self.canvas.bind("<Button-1>", self.__cell_clicked)
        self.canvas.bind("<Key>", self.__key_pressed)
        self.canvas.bind("<Configure>", self.__canvas_resize)
    
    def __erase_colouring(self, event):
        self.game.reset_colours()
        self.technique = ""
        self.__draw_puzzle()

    def __hint(self, event=None):
        self.technique = self.game.hint()
        self.highlight = 0
        self.__draw_puzzle()
    
    def __autofill_naked_singles(self):
        hint = HintEngine(self.game).get_naked()
        if hint is None:
            return
        else:
            for row, col, val in hint.good_cands:
                self.game.set_cell(row, col, val, undo=False)

        self.__draw_puzzle()
    
    def __undo(self, event):
        self.game.undo()
        self.__draw_puzzle()

    def __save_state_as(self):
        file = filedialog.asksaveasfile(mode='w', defaultextension=".sdk")
        if file is None:
            return
        content = self.game.get_state()
        file.write(content)
        file.close()

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
    
    def __calculate_candidates(self, event=None):
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
    
    def __export_givens_clip(self):
        self.clipboard_clear()
        self.clipboard_append(self.game.get_puzzle_string())

    def __export_candidates_clip(self):
        self.clipboard_clear()
        self.clipboard_append(self.game.get_forum_string())

    def __from_candidates_clip(self):
        forum_string = self.clipboard_get()
        self.game.set_forum_string(forum_string)
        self.__draw_puzzle()

    def __canvas_resize(self, event):
        base = min(event.width, event.height)

        self.side = (base - 2 * self.margin) // 9 
        self.width = self.height = self.margin * 2 + self.side * 9 # Width and height of the whole board
        self.cluesize = self.side // 2
        self.candidatesize = self.side // 4
        self.candidatediff = self.side // 3

        self.__draw_grid()
        self.__draw_puzzle()
        self.__draw_cursor()

    def __draw_grid(self):
        """
        Draws grid divided with blue lines into 3x3 squares
        """
        self.canvas.delete("grid")
        for i in range(10):
            color = "gray22" if i % 3 == 0 else "gray70"

            x0 = self.margin + i * self.side
            y0 = self.margin
            x1 = self.margin + i * self.side
            y1 = self.height - self.margin
            self.canvas.create_line(x0, y0, x1, y1, fill=color, width=1, tags="grid")

            x0 = self.margin
            y0 = self.margin + i * self.side
            x1 = self.width - self.margin
            y1 = self.margin + i * self.side
            self.canvas.create_line(x0, y0, x1, y1, fill=color, width=1, tags="grid")
    
    def __draw_puzzle(self):
        self.canvas.delete("numbers")
        self.canvas.delete("candidates")
        self.canvas.delete("highlights")
        self.canvas.delete("puzzleinfo")
        self.canvas.delete("cellcolouring")
        self.canvas.delete("candidatecolour")
        self.canvas.delete("hint")
        for i in range(9):
            for j in range(9):
                x0 = self.margin + j * self.side + 1
                y0 = self.margin + i * self.side + 1
                x1 = self.margin + (j + 1) * self.side - 1
                y1 = self.margin + (i + 1) * self.side - 1
                answer = self.game.get_cell(i,j)
                candidates = self.game.get_candidates(i,j)

                # First draw the highlight or else the candidates won't be visible
                do_highlight = True
                if self.highlight == 0 or self.mode is Mode.colour_candidate:
                    do_highlight = False

                if do_highlight and answer == self.highlight: 
                    self.canvas.create_rectangle(x0, y0, x1, y1, tags="highlights", fill=HLANSWER, outline=HLANSWER)
                elif do_highlight and self.highlight in candidates and answer == 0:
                    self.canvas.create_rectangle(x0, y0, x1, y1, tags="highlights", fill=HLCAND, outline=HLCAND)

                # Then draw cell colouring
                colour = self.game.get_cell_colour(i,j)
                if not colour is None and answer == 0:
                    self.canvas.create_rectangle(x0, y0, x1, y1, tags="cellcolouring", fill=colour , outline=colour)
                
                if answer != 0:
                    # Draw big character
                    x = self.margin + j * self.side + self.side / 2
                    y = self.margin + i * self.side + self.side / 2
                    original = self.game.get_origin(i, j)
                    color = "black" if answer == original else "olive drab"
                    self.canvas.create_text(x,y, text=answer, tags="numbers", fill=color, font=("Arial",self.cluesize))
                else:
                    # Draw candidate colouring
                    for candidate in candidates:
                        self.__draw_candidate_colour(i, j, candidate)
                    # Draw candidates
                    for candidate in candidates:
                        self.__draw_candidate(i, j, candidate)
        
        # Write puzzle info in the middle bottom of the puzzle
        pix = self.width / 2
        piy = self.height - self.margin / 2
        puzzle_info = ""
        if self.file_name != "":
            collection_name = self.file_name.split("/")[-1].split(".")[-2]
            if self.puzzle_num == 0:
                puzzle_info = collection_name
            else:
                puzzle_info = "{}: {}".format(collection_name, self.puzzle_num + 1)
        self.canvas.create_text(pix, piy, text=puzzle_info, tags="puzzleinfo", fill="gray", font=("Arial", 12))

        # Write the name of the Technique that was hinted in the top middle
        piy = self.margin / 2
        puzzle_info = "Hint: {}".format(self.technique)
        if self.technique != "":
            self.canvas.create_text(pix, piy, text=puzzle_info, tags="hint", fill="gray", font=("Arial", 12))
        
        # If we're autosolving singles, check once more
        if self.autosolve_naked_singles.get():
            self.__autofill_naked_singles()

    def __get_candidate_pos(self, row: int, col: int, candidate: int) -> Tuple[float, float]:
        diff = self.candidatediff
        cx = self.margin + col * self.side + self.side / 2
        cy = self.margin + row * self.side + self.side / 2
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

        return x, y


    def __draw_candidate(self, row: int, col: int, candidate: int):
        x,y = self.__get_candidate_pos(row, col, candidate)
        self.canvas.create_text(x,y, text=candidate, tags="candidates", fill="gray", font=("Arial", self.candidatesize))

    def __draw_candidate_colour(self, row: int, col: int, candidate: int):
        diff = self.candidatediff / 2 - 1
        colour = self.game.get_candidate_colour(row, col, candidate)
        if colour is None:
            return
        x,y = self.__get_candidate_pos(row, col, candidate)
        x0 = x - diff
        x1 = x + diff
        y0 = y - diff
        y1 = y + diff
        self.canvas.create_oval(x0, y0, x1, y1, tags="candidatecolour", fill=colour, outline=colour)
    
    def __clear_answers(self):
        self.game.start()
        self.canvas.delete("victory")
        self.__draw_puzzle()

    def __cell_clicked(self, event):
        if self.game.game_over:
            return

        x, y = event.x, event.y
        if(self.margin < x < self.width - self.margin and self.margin < y < self.height - self.margin):
            self.canvas.focus_set()

            # get row and col numbers from x,y coordinates
            row, col = (y - self.margin) // self.side, (x - self.margin) // self.side

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

    def __deselected(self) -> bool:
        if self.row == -1 and self.col == -1:
            return True
        else:
            return False

    def __draw_cursor(self):
        self.canvas.delete("cursor")
        if self.row >= 0 and self.col >= 0:
            x0 = self.margin + self.col * self.side + 1
            y0 = self.margin + self.row * self.side + 1
            x1 = self.margin + (self.col + 1) * self.side - 1
            y1 = self.margin + (self.row + 1) * self.side - 1
            color = ""
            if self.mode is Mode.candidate:
                color = "blue"
            elif self.mode is Mode.solution:
                color = "red"
            elif self.mode is Mode.colour:
                color = "green"
            elif self.mode is Mode.colour_candidate:
                color = "yellow3"
            else:
                color = "pink"
            self.canvas.create_rectangle(x0, y0, x1, y1, outline=color, tags="cursor", width=3)

    def __key_pressed(self, event):
        if self.game.game_over:
            return

        if self.row >= 0 and self.col >= 0 and event.char in "1234567890":
            if self.mode is Mode.solution and self.game.get_origin(self.row,self.col) == 0:
                self.game.set_cell(self.row, self.col, int(event.char))
            elif self.game.get_origin(self.row,self.col) != 0:
                self.highlight = int(event.char)
            elif self.mode is Mode.candidate:
                self.game.toggle_candidate(self.row, self.col, int(event.char))
            elif self.mode is Mode.colour:
                self.game.set_cell_colour(self.row, self.col,int(event.char))
            elif self.mode is Mode.colour_candidate and self.game.get_origin(self.row,self.col) != 0:
                self.highlight = int(event.char)
            elif self.mode is Mode.colour_candidate:
                self.game.set_candidate_colour(self.row, self.col, int(event.char), self.highlight)
            self.__draw_puzzle()
            self.__draw_cursor()
            if self.game.check_win():
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
        self.__draw_puzzle()

    def __toggle_mode_colouring(self, event):
        if self.mode is Mode.colour:
            self.mode = Mode.solution
        else:
            self.mode = Mode.colour
        self.__draw_cursor()
        self.__draw_puzzle()
    
    def __toggle_mode_colour_candidate(self, event):
        if self.mode is Mode.colour_candidate:
            self.mode = Mode.solution
        else:
            self.mode = Mode.colour_candidate
        self.__draw_cursor()
        self.__draw_puzzle()


if __name__ == '__main__':
    game = SudokuGame()
    game.start()

    root = tk.Tk()
    SudokuUI(root,game)
    root.geometry("{}x{}".format(WIDTH, HEIGHT))
    root.mainloop()
