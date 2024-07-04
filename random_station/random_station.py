"""
Little program I've made to help me on my quest to visit every Metro station in Melbourne. This program will select a random station name from an imported .json file and
give me the option to select it (which removes it from the selection next time) or roll for another one. I might add more features too, but I thought this would be a fun
project now I've finished up with my tic tac toe program :3

Plan:
- Simple terminal interface (maybe using colours?)
- Import and modify a .json file for data storage
- Options to reroll if I don't like the choice
- Show what line the station is on and it's distance from the CBD/Southern Cross
- Counter for how many stations visited/how many remaining, in total and by line (maybe a small hooray msg if a line is completed)
- Maybe a "queue" that doesn't clear a station until I confirm I visited it?
- Maybe a GUI eventually!
- More?
"""

import json
import os
import random


# Runs OS-specific shell command to clear console
def clear():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


# Load saved, visited and unvisited stations from datastore.json, which should be in the same directory. Not bothering with error handling.
def read():
    # I kind of understand how this works? Basically with is shorthand for a try/except/finally statement and I think there are some benefits beyond that too? I dunno. Either way I'm opening a file!
    with open('datastore.json', 'r') as file:
        return json.load(file)


# Write modified .json to datastore.json
def write(data):
    with open('datastore.json', 'w') as file:
        json.dump(data, file, indent=4)


# Check whether a station dict is present in the to_visit dict. If it is, prompt the user whether they want to mark it as visited & continue or return/exit
def check_to_visit(data):
    clear()

    if len(data['to_visit']) > 0:
        print("Warning! There's a station queued up for you to visit already!\n")
        print('1) Mark as visited and continue')
        print('2) Return to main menu')
        print('3) Exit')

        while True:
            choice = input('> ')
            if choice == '1':
                # Remove the station object/dictionary from the to_visit section and return the value of the remove dict/object
                visited_station = data['to_visit'].popitem()
                # Add the dict we removed from the to_visit section to the visited section
                data['visited'].update({visited_station[0]: visited_station[1]})
                # Write changes to datastore.json so the program remembers them when reopened
                write(data)
                roll_station(data)
                break
            elif choice == '2':
                break
            elif choice == '3':
                exit()
            else:
                print(
                    '\nInvalid choice. Please select one of the listed options above by typing the number next to the option.\n'
                )
    else:
        roll_station(data)


# Selects a random station from the data['unvisited'] dictionary/object by doing (sparkles) magic (sparkles)
def roll_station(data):
    # Check whether there are any stations left to visit (the function we call here is just a screen that congratulates the user and gives options to return to main menu or exit)
    if len(data['unvisited']) == 0:
        no_unvisited()
        return

    # Get the name's of all stations by converting the dictionary keys (the names) into a list
    stations = list(data['unvisited'].keys())
    # I stored time's as an int like this in datastore.json to save myself retyping stuff. This dict just contains what each number correlates to.
    time_conversion = {
        0: 'under 10',
        1: '11 to 20',
        2: '21 to 30',
        3: '31 to 40',
        4: '41 to 50',
        5: '51 to 60',
        6: '61 to 70',
        7: '71 to 80',
        8: '81 to 90',
        9: '91 to 100',
        10: '101 to 110',
    }

    while True:
        clear()
        # Pick a random station name from our list made above
        station = random.choice(stations)
        # Now that we have a station name/key, grab info on the station from data['unvisited'] including line, distance, travel time...
        station_info = data['unvisited'][station]

        print(
            f'Looks like you\'re heading to... {station}, located on the {station_info['line']} line! {station} is {station_info['distance']}km from the CBD. Journeys to {station} on average take {time_conversion[station_info['time']]} minutes.\n'
        )
        print('1) Reroll')
        print('2) Accept\n')

        while True:
            choice = input('> ')
            if choice == '1':
                roll_station(data)
                break
            elif choice == '2':
                # Explained this in more detail above. pop() removes the station from 'unvisited', update() inserts it into the 'to_visit' section and write() writes our changes to datastore.json
                to_visit = data['unvisited'].pop(station)
                data['to_visit'].update({station: to_visit})
                write(data)
                break
            else:
                print(
                    '\nInvalid choice. Please select one of the listed options above by typing the number next to the option.\n'
                )

        break


# We call this when data['unvisited'] has a length of 0 (meaning it contains nothing)
def no_unvisited():
    clear()

    print(
        "There aren't any more stations to visit - you've been to them all! Congratulations!\n"
    )
    print('1) Main menu')
    print('2) Exit\n')

    while True:
        choice = input('> ')

        if choice == '1':
            break
        elif choice == '2':
            exit()


# Main program
def main(data):
    clear()
    print('\n-+ Random-Metro-Station-Choosinator 3000 +-\n')
    print('1) Get next station')
    print('2) View statistics')
    print('3) Exit\n')

    choice = input('> ')

    if choice == '1':
        check_to_visit(data)
    elif choice == '2':
        pass
    elif choice == '3':
        exit()
    else:
        print(
            '\nInvalid choice. Please select one of the listed options above by typing the number next to the option.\n'
        )

    main(data)


main(read())

"""
dict(sorted(data['unvisited_stations'].items()))
"""
