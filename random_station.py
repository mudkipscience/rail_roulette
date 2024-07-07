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
- Option to manually mark a station as visited
- Log date a station was visited (can take user input for this)
- Look up info on stations (PT connections, nearby stations + other stuff already included in datastore)
- More?
"""

import json
import os
import random

# Library to do fancy text formatting and stuff, including colours. I could just implement colours with ASCII escape characters buuut this is better.
from rich.console import Console


# Enhanced console output functionality provided by Rich
console = Console(highlight=False)


# Line colours. I use them in a couple places so just easier to have as a global variable.
line_colours = {
    'Alamein': 'white on #094c8d',
    'Belgrave': 'white on #094c8d',
    'Glen Waverley': 'white on #094c8d',
    'Lilydale': 'white on #094c8d',
    'Cranbourne': 'black on #16b4e8',
    'Pakenham': 'black on #16b4e8',
    'Hurstbridge': 'white on #b1211b',
    'Mernda': 'white on #b1211b',
    'Craigieburn': 'black on #ffb531',
    'Sunbury': 'black on #ffb531',
    'Upfield': 'black on #ffb531',
    'Flemington Racecourse': 'black on #909295',
    'Frankston': 'black on #159943',
    'Stony Point': 'black on #159943',
    'Werribee': 'black on #159943',
    'Williamstown': 'black on #159943',
    'Sandringham': 'black on #fc7fbb',
}


# Runs OS-specific shell command to clear console
def clear():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


# Generates a string of options the user can select from. ops is an array of names we want to give to each option.
def print_menu(ops):
    index = 1
    menu = ''

    for entry in ops:
        menu += f'{index}) {entry}\n'
        index += 1
    
    return menu


# Load saved, visited and unvisited stations from datastore.json, which should be in the same directory. Not bothering with error handling.
def read():
    # I kind of understand how this works? Basically with is shorthand for a try/except/finally statement and I think there are some benefits beyond that too? I dunno. Either way I'm opening a file!
    with open('datastore.json', 'r') as file:
        return json.load(file)


# Write modified .json to datastore.json
def write(data):
    with open('datastore.json', 'w') as file:
        json.dump(data, file, indent=4, sort_keys=True)


# Check whether a station name has been written to to_visit dict. If yes, prompt the user whether they want to mark it as visited & continue or return/exit
def check_to_visit(data):
    clear()

    if len(data['to_visit']) > 0:
        print("Warning! There's a station queued up for you to visit already!\n")
        print(print_menu(['Mark as visited & continue', 'Main menu', 'Exit']))

        while True:
            choice = input('> ')
            if choice == '1':
                # Insert the dict associated with the randomly chosen station into visited after grabbing it from unvisited with get()
                data['visited'].update(
                    {data['to_visit']: data['unvisited'].get(data['to_visit'])}
                )
                # Now that we've copied over the station dict into visited, we can remove it from unvisited with pop()
                data['unvisited'].pop(data['to_visit'])
                # Reset to_visit to be an empty string again
                data['to_visit'] = ''
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
    # I stored times as an int like this in datastore.json to save myself retyping stuff. This dict just contains what each number correlates to.
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
        lines = ''
        for line in station_info['line']:
            colour = line_colours[line]
            lines += f'[{colour}] {line} [/{colour}]'

            if line != station_info['line'][-1]:
                lines += ', '

        console.print(f"Looks like you're heading to... [bold]{station}!\n")
        console.print(f'- [bold]{station}[/bold] is served by the {lines} line/s.')
        console.print(
            f'- [bold]{station}[/bold] is {station_info["distance"]}km from the CBD.'
        )
        console.print(
            f'- Journeys to [bold]{station}[/bold] take {time_conversion[station_info["time"]]} minutes on average.\n'
        )
        print(print_menu(['Reroll', 'Accept']))

        while True:
            choice = input('> ')
            if choice == '1':
                roll_station(data)
                break
            elif choice == '2':
                # Writes the key/station name to to_visit, a string value in datastore.json. This is so we can retrieve info on this station later. For now, we can leave it in unvisited.
                data['to_visit'] = station
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
    print(print_menu(['Main menu', 'Exit']))

    while True:
        choice = input('> ')

        if choice == '1':
            break
        elif choice == '2':
            exit()


def stats(data):
    clear()

    visited = {}
    unvisited = {}
    for line in line_colours:
        visited.update({line: []})
        unvisited.update({line: []})

    for v in data['visited']:
        for line in data['visited'][v]['line']:
            visited[line].append(v)

    for unv in data['unvisited']:
        for line in data['unvisited'][unv]['line']:
            unvisited[line].append(unv)

    burnley = {
        'visited': len(visited["Alamein"]) + len(visited["Belgrave"]) + len(visited["Glen Waverley"]) + len(visited["Lilydale"]),
        'total': (len(visited["Alamein"]) + len(visited["Belgrave"]) + len(visited["Glen Waverley"]) + len(visited["Lilydale"])) + (len(unvisited["Alamein"]) + len(unvisited["Belgrave"]) + len(unvisited["Glen Waverley"]) + len(unvisited["Lilydale"]))
    }
    caufield = {
        'visited': len(visited["Cranbourne"]) + len(visited["Pakenham"]),
        'total': len(visited["Cranbourne"]) + len(visited["Pakenham"]) + len(unvisited["Cranbourne"]) + len(unvisited["Pakenham"])
    }
    clifton = {
        'visited': len(visited['Mernda']) + len(visited['Hurstbridge']),
        'total': (len(visited['Mernda']) + len(visited['Hurstbridge'])) + (len(unvisited['Mernda']) + len(unvisited['Hurstbridge']))
    }
    northern = {
        'visited': len(visited['Craigieburn']) + len(visited['Sunbury']) + len(visited['Upfield']),
        'total': len(visited['Craigieburn']) + len(visited['Sunbury']) + len(visited['Upfield']) + len(unvisited['Craigieburn']) + len(unvisited['Sunbury']) + len(unvisited['Upfield'])
    }
    cross_city = {
        'visited': len(visited['Frankston']) + len(visited['Werribee']) + len(visited['Williamstown']),
        'total': len(visited['Frankston']) + len(visited['Werribee']) + len(visited['Williamstown']) + len(unvisited['Frankston']) + len(unvisited['Werribee']) + len(unvisited['Williamstown'])
    }

    print('\n -+ Statistics +-\n')
    console.print(
        f'[bold]You have visited {len(data["visited"])} out of {len(data["visited"]) + len(data["unvisited"])} stations. Breakdown:[/bold]\n\n'
        f'- You\'ve visited {burnley["visited"]} out of {burnley["total"]} [{line_colours["Alamein"]}] Burnley [/{line_colours["Alamein"]}] group stations:\n'
        f'  - {len(visited["Alamein"])} out of {len(visited["Alamein"]) + len(unvisited["Alamein"])} stations on the Alamein line.\n'
        f'  - {len(visited["Belgrave"])} out of {len(visited["Belgrave"]) + len(unvisited["Belgrave"])} stations on the Belgrave line.\n'
        f'  - {len(visited["Glen Waverley"])} out of {len(visited["Glen Waverley"]) + len(unvisited["Glen Waverley"])} stations on the Glen Waverley line.\n'
        f'  - {len(visited["Lilydale"])} out of {len(visited["Lilydale"]) + len(unvisited["Lilydale"])} stations on the Lilydale line.\n\n'
        f'- You\'ve visited {caufield["visited"]} out of {caufield["total"]} [{line_colours["Cranbourne"]}] Caufield [/{line_colours["Cranbourne"]}] group stations:\n'
        f'  - {len(visited["Cranbourne"])} out of {len(visited["Cranbourne"]) + len(unvisited["Cranbourne"])} stations on the Cranbourne line.\n'
        f'  - {len(visited["Pakenham"])} out of {len(visited["Pakenham"]) + len(unvisited["Pakenham"])} stations on the Pakenham line.\n\n'
        f'- You\'ve visited {clifton["visited"]} out of {clifton["total"]} [{line_colours["Mernda"]}] Clifton Hill [/{line_colours["Mernda"]}] group stations.\n'
        f'  - {len(visited["Hurstbridge"])} out of {len(visited["Hurstbridge"]) + len(unvisited["Hurstbridge"])} stations on the Hurstbridge line.\n'
        f'  - {len(visited["Mernda"])} out of {len(visited["Mernda"]) + len(unvisited["Mernda"])} stations on the Mernda line.\n\n'
        f'- You\'ve visited {northern["visited"]} out of {northern["total"]} [{line_colours["Sunbury"]}] Northern [/{line_colours["Sunbury"]}] group stations:\n'
        f'  - {len(visited["Craigieburn"])} out of {len(visited["Craigieburn"]) + len(unvisited["Craigieburn"])} stations on the Craigieburn line.\n'
        f'  - {len(visited["Sunbury"])} out of {len(visited["Sunbury"]) + len(unvisited["Sunbury"])} stations on the Sunbury line.\n',
        f'  - {len(visited["Upfield"])} out of {len(visited["Upfield"]) + len(unvisited["Upfield"])} stations on the Upfield line.\n\n'
        f'- You\'ve visited {cross_city["visited"]} out of {cross_city["total"]} [{line_colours["Frankston"]}] Cross-City [/{line_colours["Frankston"]}] group stations:\n'
        f'  - {len(visited["Frankston"])} out of {len(visited["Frankston"]) + len(unvisited["Frankston"])} stations on the Frankston line.\n'
        f'  - {len(visited["Werribee"])} out of {len(visited["Werribee"]) + len(unvisited["Werribee"])} stations on the Werribee line.\n'
        f'  - {len(visited["Williamstown"])} out of {len(visited["Williamstown"]) + len(unvisited["Williamstown"])} stations on the Williamstown line.\n\n'
        f'- You\'ve visited {len(visited["Flemington Racecourse"])} out of {len(visited["Flemington Racecourse"]) + len(unvisited["Flemington Racecourse"])} stations on the [{line_colours["Flemington Racecourse"]}] Flemington Racecourse [/{line_colours["Flemington Racecourse"]}] line.\n\n'
        f'- You\'ve visited {len(visited["Stony Point"])} out of {len(visited["Stony Point"]) + len(unvisited["Stony Point"])} stations on the [{line_colours["Stony Point"]}] Stony Point [/{line_colours["Stony Point"]}] line.\n\n'
        f'- You\'ve visited {len(visited["Sandringham"])} out of {len(visited["Sandringham"]) + len(unvisited["Sandringham"])} stations on the [{line_colours["Sandringham"]}] Sandringham [/{line_colours["Sandringham"]}] line.\n\n'
    )
    print(print_menu(['Main menu', 'Exit']))

    while True:
        choice = input('> ')

        if choice == '1':
            break
        elif choice == '2':
            exit()


# Main program
def main(data):
    while True:
        unmodified_title = ' | |E|v|e|r|y| |M|e|t|r|o| |S|t|a|t|i|o|n| |'
        modified_title = (
            '[grey69] +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+[grey69]\n'
        )

        for i in range(44):
            if unmodified_title[i] == '|':
                modified_title += '[grey69]|[/grey69]'
            # Colour the word "Metro" in the blue they use in their branding
            elif i > 14 and i < 25:
                modified_title += '[#0073cf]' + unmodified_title[i] + '[/#0073cf]'
            else:
                modified_title += (
                    '[light_sky_blue1]' + unmodified_title[i] + '[/light_sky_blue1]'
                )

        modified_title += (
            '\n[grey69] +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+[/grey69]\n'
        )

        clear()

        console.print(modified_title)
        print(
            print_menu(
                ['Get next station', 'Mark station as visited', 'Statistics', 'Exit']
            )
        )

        choice = input('> ')

        if choice == '1':
            check_to_visit(data)
        elif choice == '2':
            pass
        elif choice == '3':
            stats(data)
        elif choice == '4':
            exit()
        else:
            print(
                '\nInvalid choice. Please select one of the listed options above by typing the number next to the option.\n'
            )


main(read())
