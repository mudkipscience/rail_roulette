board = []
plr1_char = 'X'
plr2_char = 'O'

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

def winner(board): # Don't feel the need to explain this one
    return row_winner(board) or column_winner(board) or diagonal_winner(board)

def endgame_reached(board): # Checks whether the board still contains any blank spaces, for detecting whether the game is unwinnable
    for row in board:
            if ' ' in row:
                return False
            
    return True

def process_input(valid_inputs): # Takes a list of valid choices as arguments and only allows input of characters found in the array. Only works with integers
    choice = int(input('> '))
    if choice in valid_inputs or len(valid_inputs) == 0:
        return choice
    else:
        print(str(choice) + ' is not a valid choice.')
        process_input(valid_inputs)

def create_board(size = 3): # Create a board (list of nested lists, all of the same length) taking an int as an argument which is used to generate a larger/smaller board
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

def ops_menu():
    print('-+ Options +-')
    print()
    print(f'1) Change board size ({len(board)}x{len(board)})')
    print(f'2) Change player 1 character ({plr1_char})')
    print(f'3) Change player 2 character ({plr2_char})')
    print()
    inp = process_input([1, 2, 3])
    if inp == 1: # Change board size
        print('Input a new board size below.')
        print()
        inp = process_input([])
        create_board(inp)
        main_menu()
    elif inp == 2: # Change the character player 1 is represented as
        ...
    else: # Change the character player 2 is represented as
        ...

def main_menu():
    print('-+ Tic Tac Toe +-')
    print()
    print('1) Play')
    print('2) Options')
    print()
    inp = process_input([1, 2])
    if inp == 1:
        print(format_board())
    else:
        ops_menu()

# -+ Actual stuff the user sees begins here, the above was all just logic +-
create_board()
main_menu()