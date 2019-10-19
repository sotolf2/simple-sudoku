# simple-sudoku
A simple python tkinter sudoku program

![screenshot](https://raw.githubusercontent.com/sotolf2/simple-sudoku/master/Skjermbildenew.PNG)

## What is this

Basically I've been tinkering around with python, but never really made anything worth thinking about. I've been into solving sudoku
lately, so I was thinking that making something that works for that would be cool, so it's a small pet project of mine, to learn some
more python, and maybe also some more about sudoku stuff. In addition it would be cool to make something visual as well.

## How do I use this thing.

### Get a puzzle to solve

Here you have some possibilities, you can get simple-sudoku to generate a puzzle for you, there are 5 difficulty ratings to choose between, all these puzzles are solveable, and have only one solution. 

    Puzzle -> Generate -> Difficulty

A second posibility is to import a puzzle from a 81 character puzzle string such as this one:

    76.......53.896.......1.2..1....248.....8.....296....1..3.2.......751.36.......12
    
Copy the code into your clipboard and then you can import the puzzle from

    File -> Import from clipboard
    
Simple sudoku can also import a puzzle collection from a \*.sdm file, and you can solve these

    File -> Open file
    
You can then solve the current puzzle, and use the menu or the << and >> buttons to jump to the previous or next puzzle, or you can go to a specific numbered puzzle from

    Collection -> Go to specific puzzle

sdm files are quite a standard for puzzle collectios and you can grab some at
http://sudocue.net/download.php for example, or you can make your own, sdm files are basically the same as the single
line imports shown further up just put one after another on their own line.

If you just have an image to work from, you can just add the given clues into the empty grid, and then use them as a puzzle

    Puzzle -> Set Origin

### Solving a puzzle

So after you have imported a puzzle you can start solving, simple sudoku are basically keyboard driven, at least until someone finds a comfortable way to do it with a mouse. 

The Program uses modes and the cursor (square marking the current cell) will change colour depending on which mode you're in. There are currently 4 modes that you can be in, it changes what happens when you press one of the number keys:

* Solution - Red - Will set the current cell
* Candidate - Blue - Will let you toggle candidates for the current cell
* Cell Colouring - Green - Will colour the cell in a colour
* Candidate Colouring - Yellow will let you set the colour for candidates.

If you are confused why your cursor is in a specific colour, tapping the space bar will change you to candidate mode, which is the mode that you will probably spend the most time in.

You can change the highlighting of cells by pressing a number on a cell that belongs to the puzzle (black big numbers).

Don't be too afraid of doing something wrong as there is an undo function.

A box will pop up congratulating you when you have solved the puzzle correctly.

### Keyboard shortcuts

* wasd or Arrow keys (move cursor around)
* Space toggle candidate mode
* c - Calculate candidates
* F1-F9 Highlight cells
* q - toggle Cell colouring mode
* f - toggle candidate colouring
* e - remove all colouring
* u - undo

### How do I use Candidate colouring?

This is the mode that is the hardest to grasp, basically in this mode you can't use higlightning, and the ways that you usually use to change the highlightning will change the colour that you are currently having, this selected colour will now be used to paint the candidate in your current cell with this colour.

It may not be optimal yet, but it's the most comfortable way to use it that I've found so far.

This is how a puzzle can look while colouring:

![Colouring](https://raw.githubusercontent.com/sotolf2/simple-sudoku/master/colouring.PNG)
