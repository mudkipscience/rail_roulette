board = []
set_board_size = 3
plr1_char = 'X'
plr2_char = 'O'

def create_board(size = set_board_size): # Create a board (list of nested lists, all of the same length) taking an int as an argument which is used to generate a larger/smaller board
    global board # So apparently I can't just change a variable declared outside of a function or it will create a NEW local variable that doesn't affect the global one. Unless I do this!
    board = [] # Clear the board so we don't get any funny behaviour when this function is repeatedly called
    for i in range(size):
        row = []
        for i in range(size):
            row.append(' ')
        board.append(row.copy())

def format_board(): # Draws the board by adding a key (numbers on the edge of the X and Y axis so players know what spaces are which) and then joining all lists together, returning a string
    board_size = len(board)
    outp = '  ' # Empty whitespace to pad key so it doesn't look ugly
    
    for p in range(board_size):
        outp += str(p + 1) + ' ' # Generates the key at the top of the board

    for i in range(board_size):
        outp += f"\n{i + 1} {'|'.join(board[i])}" # converts a single "row" inside the board list into a string so it can be displayed
        
        if (i + 1) != board_size: # generates the spacing "-+-+-" between rows, skipping the last one
            outp += '\n  ' + '-+' * (board_size - 1) + '-'

    return(outp)

def process_input(inp_type, valid_inputs = [], invalid_inputs = []): # Takes a list of valid choices as arguments and only allows input of characters found in the array.
    choice = input('> ')

    try:
        choice = inp_type(choice)
    except:
        print('Invalid choice (invalid type).')
        return process_input(inp_type, valid_inputs, invalid_inputs)

    if (choice in valid_inputs or len(valid_inputs) == 0) and choice not in invalid_inputs:
        return choice
    else:
        print('Invalid choice (invalid choice).')
        return process_input(inp_type, valid_inputs, invalid_inputs)

# -+ Win detection logic +-

def row_winner(board): # Checks whether values in a nested list from board are all identical, if they are this is a win!
    for row in board:
        first_run = True
        previous = ''
        
        for i in range(len(row)):
            if ' ' in row: # No point executing the rest of this if I'm just gonna find an empty space in the middle of a row
                break
            
            if first_run == True:
                previous = row[i]
                first_run = False
            
            if row[i] != previous:
                break
            
            if (i + 1) == len(row): # Check if we have reached the final item in the row, and if we've gotten this far we found a match/win!

                return True

    return False

def column_winner(board): # Takes the board and recreates it ([['X', 'O], ['X', ' ']] becomes [['X', 'X'], ['O'], [' ']]) and then calls row_winner() to reuse some code I prepared earlier :3
    c_x = 0
    c_board = []
    
    for i in range(len(board)): # Loop as many times as we need to get through all values on the board
        c_y = 0
        c_row = []
        
        for i in range(len(board)): # Loop through all nested lists (rows) and get value of first index in each row
            c_row.append(board[c_y][c_x])
            c_y += 1
        
        c_board.append(c_row)
        c_x += 1

    return row_winner(c_board) # Is this efficient? I dunno!

def diagonal_winner(board): # Creates two lists containing the values of each nested list in a diagonal line ([0][0], [1][1], [2][2], etc.) and again passes it to row_winner()
    d_row1 = []
    d_row2 = []
    
    for i in range(len(board)):
        d_row1.append(board[i][i]) # Create a new list containing the values of the diagonal board row, top to bottom
    
    for i in range(len(board)):
        d_row2.append(board[-i - 1][i]) # Create a new list containing the values of the diagonal board row, top to bottom. THIS TOOK ME LIME HALF ABN HOUR TO FIGURE OUT AND IT WAS SO SIMPLE I FEEL SO STUPDI ARRRGH

    return row_winner([d_row1, d_row2])

def endgame_reached(): # Checks whether the board still contains any blank spaces, for detecting whether the game is unwinnable
    for row in board:
            if ' ' in row:
                return False

    return True

def check_winner():
    if row_winner(board) or column_winner(board) or diagonal_winner(board):
        print('\nThe game has ended, congratulations to the winner! Type 1 to return to the main menu or type 2 to exit.\n')
        inp = process_input(int, [1, 2])
        if inp == 1:
            main_menu()
        else:
            exit()
    else:
        if endgame_reached():
            print('\n Game has finished in a draw. Type 1 to return to the main menu or type 2 to exit.\n')
            inp = process_input(int, [1, 2])
            if inp == 1:
                main_menu()
            else:
                exit()

# -+ Gameplay logic (taking user inputs and modifying the board, calling the win check functions, etc.)

def play_move(char):
    global board

    print(f'\n{char} to play: (horizontal)\n')
    move_x = process_input(int) - 1

    print(f'\n{char} to play: (vertical)\n')
    move_y = process_input(int) - 1

    if move_x < 0 or move_x >= (len(board)):
        move_x = len(board) - 1

    if move_y < 0 or move_y >= (len(board)):
        move_y = len(board) - 1

    if not board[move_y][move_x]  == ' ':
        print('\nThe specified spot on the board has already been filled, please try again.\n')
        play_move(char)
        return

    board[move_y][move_x] = char

def play_game():
    print(format_board())
    play_move(plr1_char)
    check_winner()

    print(format_board())
    play_move(plr2_char)
    check_winner()

    play_game()

# -+ Menu stuff +-

def ops_menu():
    global plr1_char
    global plr2_char
    global set_board_size

    print('-+ Options +-\n')
    print(f'1) Change board size ({len(board)}x{len(board)})')
    print(f'2) Change player 1 character ({plr1_char})')
    print(f'3) Change player 2 character ({plr2_char})')
    print('4) Return to main menu\n')

    inp = process_input(int, [1, 2, 3, 4])

    if inp == 1: # Change board size
        print('Input a new board size below.\n')
        set_board_size = process_input(int)
    elif inp == 2: # Change the character player 1 is represented as
        print('Input a new character for player 1 below.\n')
        inp = process_input(str, [], [' ', ''])
        plr1_char = inp
    elif inp == 3: # Change the character player 2 is represented as
        print('Input a new character for player 2 below.\n')
        inp = process_input(str, [], [' ', ''])
        plr2_char = inp

    main_menu()

def main_menu():
    create_board()
    print('-+ Tic Tac Toe +-\n')
    print('1) Play')
    print('2) Options\n')
    inp = process_input(int, [1, 2])
    
    if inp == 1:
        play_game()
    else:
        ops_menu()

# -+ Actually start the program +-
main_menu()