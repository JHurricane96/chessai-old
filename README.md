Chess AI
========

About
-----

A chess artificial intelligence using the MTD-f algorithm for move selection and that can  
learn from old games. It uses the python-chess library for board representation, move generation,  
zobrist hashing and reading .pgn files.

Building
--------

1. Clone the repo.
2. Install python and virtualenv.
3. Download pypy binary ([Link here](http://pypy.org/download.html)).
4. Run `virtualenv -p <pypy location here> <virtual environment name here>` to set up your virtual environment.
5. Run `source <name of env>/bin/activate` to activate your virtual environment.
6. Run `pip install python-chess` to install the python-chess library.
7. Run `pypy learn.py` to learn. It takes a couple of days to learn from around 10000 games.
8. Run `pypy main.py` to play against the AI.