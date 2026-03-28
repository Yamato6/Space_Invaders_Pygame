# main.py - Game entry point
# OOP note: this module keeps entry logic encapsulated in main(),
# and delegates behavior to Game without exposing internal game details.

from game import Game


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()