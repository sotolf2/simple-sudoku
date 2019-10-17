# simple-sudoku
A simple python tkinter sudoku program

## What is this

Basically I've been tinkering around with python, but never really made anything worth thinking about. I've been into solving sudoku
lately, so I was thinking that making something that works for that would be cool, so it's a small pet project of mine, to learn some
more python, and maybe also some more about sudoku stuff. In addition it would be cool to make something visual as well.

## How do I use this thing.

Yeah, so interfaces and stuff aren't completely my thing, but a short explanation of how to work this program.

At least until now I haven't implemented creating/generating puzzles so for now I've made it simpl as simple as found to import one into
the program. For now I'm only supporting 81 char codes, but I may do something more interesting with that later when I find out how to 
really make a bit more of a user interface.

So you can use a code like:

    76.......53.896.......1.2..1....248.....8.....296....1..3.2.......751.36.......12
    
Just copy the code from hodoku for example, or you can copy lines from the sudoku collection files that you can find under
http://sudocue.net/download.php for example and click the button From clipboard to load the puzzle into simple sudoku.

For the Program itself if the cursor is red it means you will be entering big numbers, pressing the spacebar will change you over to
candidate mode, and the program will indicate this by turning your cursor blue. You can move the cursor by using the arrow keys, or
just clicking the cell with the mouse.

Use the F-Buttons (F1-F9) To highlight, the candidates and numbers.

If you just have a picture of a sudoku that you want to add to the program, you can just add the givens from the puzzle manually
into the blank startup grid, and push the button set origin, this will turn the clues into real clues and make it so that you can't
overwrite them.

Pressing the reset button will remove all of the numbers that you have been manually adding (green).

If you click the button "Calculate candidates" the program will add all candidates that are possible to each of the cells.

