board = [
        [' ', ' ', ' '],
        [' ', ' ', ' '],
        [' ', ' ', ' ']
    ]
    
plr1_char = 'X'
plr2_char = 'O'
b_size = len(board)
b_range = range(b_size)


def row_winner(board):
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

def column_winner(board):
    c_x = 0
    c_board = []
    
    for i in b_range: # Loop as many times as we need to get through all values on the board
        c_y = 0
        c_row = []
        
        for i in b_range: # Loop through all nested lists (rows) and get value of first index in each row
            c_row.append(board[c_y][c_x])
            c_y += 1
        
        c_board.append(c_row)
        c_x += 1
    
    return row_winner(c_board) # Reuse some code I prepared earlier :3

def diagonal_winner(board):
    d_row1 = []
    d_row2 = []
    
    for i in b_range:
        d_row1.append(board[i][i]) # Create a new list containing the values of the diagonal board row, top to bottom
    
    for i in b_range:
        d_row2.append(board[-i - 1][i]) # Create a new list containing the values of the diagonal board row, top to bottom. THIS TOOK ME LIME HALF ABN HOUR TO FIGURE OUT AND IT WAS SO SIMPLE I FEEL SO STUPDI ARRRGH
        
        
    return row_winner([d_row1, d_row2]) # Is this efficient? I dunno!

def winner(board):
    return row_winner(board) or column_winner(board) or diagonal_winner(board)

def endgame_reached(board):
    for row in board:
            if ' ' in row:
                return False
            
    return True

def process_input(valid_inputs):
    choice = int(input('> '))
    if choice in valid_inputs:
        return choice
    else:
        print(str(choice) + ' is not a valid choice.')
        process_input(valid_inputs)
        

def format_board(): 
    board_size = len(board)
    
    top = '  ' # Empty whitespace to pad key so it doesn't look ugly
    
    for p in range(board_size):
        top += str(p + 1) + ' ' # Generates the key at the top of the board
    
    print(top)
    
    for i in range(board_size):
        print(f"{i + 1} {'|'.join(board[i])}") # converts a single "row" inside the board list into a string so it can be displayed
        
        if (i + 1) != board_size: # generates the spacing "-+-+-" between rows, skipping the last one
            print('  ' + '-+' * (board_size - 1) + '-')

def ops_menu():
    print('-+ Options +-')
    print()
    print(f'1) Change board size ({b_size}x{b_size})')
    print(f'2) Change player 1 character ({plr1_char})')
    print(f'3) Change player 2 character ({plr2_char})')
    print()
    inp = process_input([1, 2, 3])

def main_menu():
    print('-+ Tic Tac Toe +-')
    print()
    print('1) Play')
    print('2) Options')
    print()
    inp = process_input([1, 2])
    if inp == 1:
        format_board()
    else:
        ops_menu()

main_menu()