# game entrance

from source import tools
from source.states import main_menu, load_screen, level

def main():
    state_dictionary = {
        'main_menu': main_menu.Main_menu(),
        'load_screen': load_screen.LoadScreen(),
        'level': level.Level(),
        'level2': level.Level2(),
        'load_level2': load_screen.Load_level2(),
        'level3': level.Level3(),
        'load_level3': load_screen.Load_level3(),
        'level4': level.Level4(),
        'load_level4': load_screen.Load_level4(),
        'TOBEDONE': main_menu.TOBEDONE(),
        'game_over': load_screen.GameOver(),
        'game_win':main_menu.GameWin()
    }
    game = tools.Game(state_dictionary, 'main_menu')
    game.run()


if __name__ == '__main__':
    main()
