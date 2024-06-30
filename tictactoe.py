board = []
set_board_size = 3
plr1_char = 'X'
plr2_char = 'O'

# Create a board (list of nested lists, all of the same length) taking an int as an argument which is used to generate a larger/smaller board
def create_board(size = set_board_size): 
    # So apparently I can't just change a variable declared outside of a function or it will create a NEW local variable that doesn't affect the global one. Unless I do this!
    global board 
    # Clear the board so we don't get any funny behaviour when this function is repeatedly called
    board = [] 
    for i in range(size):
        row = []
        for i in range(size):
            row.append(' ')
        # Copy the row instead of appending the row itself. In Python default behaviour is to create a reference to an existing variable instead of a separate one, so any changes made to row will propogate to ALL rows. If that makes sense.
        board.append(row.copy())

# Draws the board by adding a key (numbers on the edge of the X and Y axis so players know what spaces are which) and then joining all lists together, returning a string
def format_board():
    board_size = len(board)
    outp = '  '
    
    # Generates the key at the top of the board
    for p in range(board_size):
        outp += str(p + 1) + ' '
    
    # converts a single "row" inside the board list into a string so it can be displayed
    for i in range(board_size):
        outp += f"\n{i + 1} {'|'.join(board[i])}"
    
        # generates the spacing "-+-+-" between rows, skipping the last one
        if (i + 1) != board_size: 
            outp += '\n  ' + '-+' * (board_size - 1) + '-'

    return(outp)

# Takes a list of valid choices as arguments and only allows input of characters found in the array.
def process_input(inp_type, valid_inputs = [], invalid_inputs = []):
    choice = input('> ')
    
    try:
        choice = inp_type(choice)
    except ValueError:
        print('Invalid choice (invalid type).')
        return process_input(inp_type, valid_inputs, invalid_inputs)

    if inp_type is int and choice < 1:
        print('Invalid choice (out of range).')
        return process_input(inp_type, valid_inputs, invalid_inputs)

    if (choice in valid_inputs or len(valid_inputs) == 0) and choice not in invalid_inputs:
        return choice
    else:
        print('Invalid choice (invalid choice).')
        return process_input(inp_type, valid_inputs, invalid_inputs)

# -+ Win detection logic +-

# Checks whether values in a nested list from board are all identical, if they are this is a win!
def row_winner(board): 
    for row in board:
        first_run = True
        previous = ''
        
        for i in range(len(row)):
            # No point executing the rest of this if I'm just gonna find an empty space in the middle of a row
            if ' ' in row: 
                break
            
            if first_run:
                previous = row[i]
                first_run = False
            
            if row[i] != previous:
                break
            
            # Check if we have reached the final item in the row, and if we've gotten this far someone has won!
            if (i + 1) == len(row):

                return row[0]

    return

# Takes the board and recreates it ([['X', 'O], ['X', ' ']] becomes [['X', 'X'], ['O'], [' ']]) and then calls row_winner() to reuse some code I prepared earlier :3
def column_winner(board):
    c_x = 0
    c_board = []
    
        # Loop as many times as we need to get through all values on the board
    for i in range(len(board)):
        c_y = 0
        c_row = []
        
        # Loop through all nested lists (rows) and get value of first index in each row
        for i in range(len(board)):
            c_row.append(board[c_y][c_x])
            c_y += 1
        
        c_board.append(c_row)
        c_x += 1

    return row_winner(c_board)

# Creates two lists containing the values of each nested list in a diagonal line ([0][0], [1][1], [2][2], etc.) and again passes it to row_winner()
def diagonal_winner(board):
    d_row1 = []
    d_row2 = []
    
    # Create a new list containing the values of the diagonal board row, top to bottom
    for i in range(len(board)):
        d_row1.append(board[i][i])
    
    # Create a new list containing the values of the diagonal board row, top to bottom. THIS TOOK ME LIME HALF ABN HOUR TO FIGURE OUT AND IT WAS SO SIMPLE I FEEL SO STUPDI ARRRGH
    for i in range(len(board)):
        d_row2.append(board[-i - 1][i]) 

    return row_winner([d_row1, d_row2])

# Checks whether the board still contains any blank spaces, for detecting whether the game is unwinnable
def draw():
    for row in board:
            if ' ' in row:
                return False

    return True

# Ends the game if win/draw detected or continues if no win found and the board still has free space
def check_winner():
    winner = row_winner(board) or column_winner(board) or diagonal_winner(board)

    if winner is not None:
        print(format_board())
        print(f'\n{winner} has won the game, congratulations! Type 1 to return to the main menu or type 2 to exit.\n')
        inp = process_input(int, [1, 2])
        if inp == 1:
            main_menu()
        else:
            exit()
    else:
        if draw():
            print(format_board())
            print('\nIt\'s a draw!. Type 1 to return to the main menu or type 2 to exit.\n')
            inp = process_input(int, [1, 2])
            if inp == 1:
                main_menu()
            else:
                exit()

# -+ Gameplay logic (taking user inputs and modifying the board, calling the win check functions, etc.)

def play_move(char):
    global board

    print(f'{char} to play: (horizontal)\n')
    move_x = process_input(int) - 1

    print(f'{char} to play: (vertical)\n')
    move_y = process_input(int) - 1
    
    # If move is out of range, reduce it to the length of the board (the max)
    if move_x < 0 or move_x >= (len(board)):
        move_x = len(board) - 1

    if move_y < 0 or move_y >= (len(board)):
        move_y = len(board) - 1

    # Make sure the spot the player wants to fill is not taken
    if not board[move_y][move_x]  == ' ':
        print('The specified spot on the board has already been filled, please try again.\n')
        play_move(char)
        return
    
    # Replaces the blank spot on the board with the players character
    board[move_y][move_x] = char

# Calls all the functions needed for the game to... function
def play_game():
    print(format_board() + '\n')
    play_move(plr1_char)
    check_winner()

    print(format_board() + '\n')
    play_move(plr2_char)
    check_winner()

    play_game()

# -+ Menu stuff +-

def main_menu():
    create_board(set_board_size)
    print('-+ Tic Tac Toe +-\n')
    print('1) Play')
    print('2) Options\n')
    inp = process_input(int, [1, 2])
    
    if inp == 1:
        play_game()
    else:
        ops_menu()

def ops_menu():
    global plr1_char
    global plr2_char
    global set_board_size

    print('-+ Options +-\n')
    print(f'1) Change board size ({set_board_size}x{set_board_size})')
    print(f'2) Change player 1 character ({plr1_char})')
    print(f'3) Change player 2 character ({plr2_char})')
    print('4) Return to main menu\n')

    inp = process_input(int, [1, 2, 3, 4])

    # Change board size
    if inp == 1:
        print('Input a new board size below.\n')
        new_size = process_input(int)
        if new_size > 9:
            print('Board sizes over 9 will cause bugs with how the game board is drawn. Do you wish to continue? (y/n)\n')
            inp = process_input(str, ['y', 'n'])
            if inp.lower() == 'y':
                set_board_size = new_size
            else:
                main_menu()
        set_board_size = new_size
        
    # Change the character player 1 is represented as
    elif inp == 2:
        print('Input a new character for player 1 below.\n')
        inp = process_input(str, [], [' ', ''])
        plr1_char = inp
    # Change the character player 2 is represented as
    elif inp == 3:
        print('Input a new character for player 2 below.\n')
        inp = process_input(str, [], [' ', ''])
        plr2_char = inp

    main_menu()

main_menu()
