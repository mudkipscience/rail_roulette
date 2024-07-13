import json
import os
import random
import re
from rich.console import Console

# Enhanced console output functionality provided by Rich
console = Console(highlight=False)
# Line colours. Enhanced are more accurate to official PTV branding whereas native uses the terminal's defined colours instead.
colour_store = {
    'enhanced': {
        # Group/line colours
        'Alamein': '#F2F2F2 on #094c8d',
        'Belgrave': '#F2F2F2 on #094c8d',
        'Glen Waverley': '#F2F2F2 on #094c8d',
        'Lilydale': '#F2F2F2 on #094c8d',
        'Cranbourne': '#0C0C0C on #16b4e8',
        'Pakenham': '#0C0C0C on #16b4e8',
        'Hurstbridge': '#F2F2F2 on #b1211b',
        'Mernda': '#F2F2F2 on #b1211b',
        'Craigieburn': 'black on #ffb531',
        'Sunbury': '#0C0C0C on #ffb531',
        'Upfield': '#0C0C0C on #ffb531',
        'Flemington Racecourse': '#0C0C0C on #909295',
        'Frankston': '#F2F2F2 on #159943',
        'Stony Point': '#F2F2F2 on #159943',
        'Werribee': '#F2F2F2 on #159943',
        'Williamstown': '#F2F2F2 on #159943',
        'Sandringham': '#0C0C0C on #fc7fbb',
    },
    'native': {
        # Line colours
        'Alamein': 'black on bright_blue',
        'Belgrave': 'black on bright_blue',
        'Glen Waverley': 'black on bright_blue',
        'Lilydale': 'black on bright_blue',
        'Cranbourne': 'black on bright_cyan',
        'Pakenham': 'black on bright_cyan',
        'Hurstbridge': 'black on bright_red',
        'Mernda': 'black on bright_red',
        'Craigieburn': 'black on bright_yellow',
        'Sunbury': 'black on bright_yellow',
        'Upfield': 'black on bright_yellow',
        'Flemington Racecourse': 'black on white',
        'Frankston': 'black on green',
        'Stony Point': 'black on green',
        'Werribee': 'black on green',
        'Williamstown': 'black on green',
        'Sandringham': 'black on bright_magenta',
    },
}
# What the program actually reads. Just an un-nested version of whatever is set in datastore.json config
colours = colour_store['enhanced']


# Runs OS-specific shell command to clear console
def clear():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


# Load saved, visited and unvisited stations from datastore.json, which should be in the same directory. Not bothering with error handling.
def read():
    # I kind of understand how this works? Basically with is shorthand for a try/except/finally statement and I think there are some benefits beyond that too? I dunno.
    #  Either way I'm opening a file! - Update 10/07/2024: Apparently what I said is NOT how it works. Guess I'll have to look into it further...
    with open('datastore.json', 'r') as file:
        return json.load(file)


# Write modified .json to datastore.json
def write(data):
    with open('datastore.json', 'w') as file:
        json.dump(data, file, indent=4, sort_keys=True)


# Generates a string of options the user can select from. ops is an array of names we want to give to each option.
def print_menu(ops):
    index = 1
    menu = ''

    for entry in ops:
        menu += f'{index}) {entry}\n'
        index += 1

    return menu


# Prints a rail-styled title like seen in the main menu. args: txt (title text: str) txr_clr (colour to print txt as) rail_clr (colour to print the "rails" as)
def print_title(txt, txt_clr='default', rail_clr='bright_black'):
    title_txt = list(txt)

    for i in range(len(title_txt)):
        if title_txt[i] != ' ':
            title_txt[i] = f'[{txt_clr}]{title_txt[i]}[/{txt_clr}]'

    title_rails = f'[{rail_clr}] {"+-" * (len(title_txt) + 2)}+'
    title_txt = (
        f'[{rail_clr}] | |{"[" + rail_clr + "]" + "|".join(title_txt)}[{rail_clr}]| |'
    )

    return f'{title_rails}\n{title_txt}\n{title_rails}\n'


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
        else:
            print(
                '\nInvalid choice. Please select one of the listed options above by typing the number next to the option.\n'
            )


# Check whether a station name has been written to to_visit dict. If yes, prompt the user whether they want to mark it as visited & continue or return/exit
def check_to_visit(data):
    clear()

    if len(data['to_visit']) > 0:
        to_visit = data['to_visit']
        print(
            f'Attention! {to_visit} Station has already been chosen as your next station to visit. What would you like to do?\n'
        )
        print(print_menu(['Mark as visited', 'Get a new station', 'Main menu']))

        while True:
            choice = input('> ')
            if choice == '1':
                # Insert the dict associated with the randomly chosen station into visited after grabbing it from unvisited with get()
                data['visited'].update(
                    {data['to_visit']: data['unvisited'].get(data['to_visit'])}
                )
                # Add on the date the station was visited to the station dict
                data['visited'][data['to_visit']].update(
                    {'date_visited': assign_date(data['to_visit'])}
                )
                # Now that we've copied over the station dict into visited, we can remove it from unvisited with pop()
                data['unvisited'].pop(data['to_visit'])
                # Reset to_visit to be an empty string again. We do this for option 2 below as well.
                data['to_visit'] = ''
                # Write changes to datastore.json so the program remembers them when reopened
                write(data)

                roll_station(data)

                break
            elif choice == '2':
                data['to_visit'] = ''
                write(data)

                roll_station(data)

                break
            elif choice == '3':
                break
            else:
                print(
                    '\nInvalid choice. Please select one of the listed options above by typing the number next to the option.\n'
                )
    else:
        roll_station(data)


# Asks for a date from the user, checks to make sure it is valid and formatted as DD/MM/YYYY then returns it
def assign_date(stn_name) -> str:
    # Regular expression that checks for a valid DD/MM/YYYY format (I don't think I need to worry about MM/DD/YYYY freaks given this is a Melbourne-specific program)
    regex = '(0[1-9]|[12][0-9]|3[01])\\/(0[1-9]|1[0,1,2])\\/(20)\\d{2}'

    print(
        f'\nType in the date you visited {stn_name} Station in the format of DD/MM/YYYY below.\n'
    )

    while True:
        raw_date = input('> ')

        # Check to make sure the length is valid before running regex checks
        if len(raw_date) != 10:
            print('\nInvalid date. Please enter a date in the format of DD/MM/YYYY.\n')
        else:
            # Use regex to validate the user input
            date = re.search(regex, raw_date)

            if date:
                return raw_date
            else:
                print(
                    '\nInvalid date. Please enter a date in the format of DD/MM/YYYY. Year must be between 2000 and 2099.\n'
                )


# Selects a random station from the data['unvisited'] dictionary/object by doing (sparkles) magic (sparkles)
def roll_station(data):
    # Check whether there are any stations left to visit (the function we call here is just a screen that congratulates the user and gives options to return to main menu or exit)
    if len(data['unvisited']) == 0:
        no_unvisited()
        return

    # Get the name's of all stations by converting the dictionary keys (the names) into a list. I know I don't need to include keys() but it makes it more readable for me.
    stations = list(data['unvisited'].keys())

    # dictionary of arrays that lists what group a line is apart of
    line_groups = {
        'Burnley': ['Alamein', 'Belgrave', 'Glen Waverley', 'Lilydale'],
        'Caufield': ['Cranbourne', 'Pakenham'],
        'Clifton Hill': ['Hurstbridge', 'Mernda'],
        'Northern': ['Craigieburn', 'Sunbury', 'Upfield'],
        'Cross City': ['Frankston', 'Werribee', 'Williamstown'],
    }

    # Used for converting the time int assigned to each station in datastore.json into something that actually makes sense when you read it.
    int_to_timerange = {
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

        # Takes a list and mutates it to add colour to each line/group, as well as adding commas and ' and ' to make nicer and readable when we join it into a string later on.
        def prettify_list(items):
            # Adds rich styling (colours here) to each group/station. Found using this syntax was easier over using enumerate() as I need the index of the item anyway.
            for i, item in enumerate(items):
                colour = colours.get(item) or colours.get(line_groups[item][0])
                items[i] = f'[{colour}] {item} [/{colour}]'

            # Inserts ' and ' into the second last place in the list.
            if len(items) > 1:
                items.insert(-1, ' and ')

            # Loop to add commas into each odd index. Checking to see if len > 3 instead of > 2 because we inserted ' and ' above.
            if len(items) > 3:
                for i, stn in enumerate(items):
                    # Break if we encounter ' and ' in the list - if we do we do not need any more commas
                    if stn == ' and ':
                        break

                    # Only add a comma if the index is odd
                    if i % 2:
                        items.insert(i, ', ')

        # Pick a random station name from our list made above
        station = random.choice(stations)
        station_info = data['unvisited'][station]
        station_groups_list = []
        # Make a copy of the line info because if we mutated it we would end up writing those changes to datastore.json
        station_lines_list = station_info['line'].copy()

        # This codeblock checks if all lines in a group serve the station, and if so removes the individual lines and adds the group to reduce clutter.
        # Loop through each group
        for group in line_groups:
            group_lines = line_groups[group]
            matched_lines = []

            # Loop through each line in the group
            for line in group_lines:
                # Check if the station is served by the group line. If yes append to matched_lines
                if line in data['unvisited'][station]['line']:
                    matched_lines.append(line)

            # Convert the lists to sets (sets are unordered so this makes the order not matter for comparision) and check if the two sets contain identical items
            if set(matched_lines) == set(group_lines):
                # If they do, append the group name to be displayed later
                station_groups_list.append(group)

                # And then remove each line that is apart of that group
                for line in station_lines_list.copy():
                    if line in matched_lines:
                        station_lines_list.remove(line)

        if len(station_groups_list) != 0:
            # prettify_list() adds colour to each line/group + adds commas and 'and' between list items. Check above to see the full function.
            prettify_list(station_groups_list)

            if len(station_groups_list) == 1:
                station_groups_list.append(' group')
            else:
                station_groups_list.append(' groups')

        if len(station_lines_list) != 0:
            # Explained this a few lines up
            prettify_list(station_lines_list)

            if len(station_lines_list) == 1:
                station_lines_list.append(' line')
            else:
                station_lines_list.append(' lines')

        # If the station is served by both lines and groups, put ', and by the ' between the list of groups and lines to make it more readable
        if len(station_groups_list) > 0 and len(station_lines_list) > 0:
            station_groups_list.append(', and by the ')

        console.print(f"Looks like you're heading to... [bold]{station}!\n")
        console.print(
            f'- [bold]{station}[/bold] is served by the {''.join(station_groups_list)}{''.join(station_lines_list)}.'
        )
        console.print(
            f'- [bold]{station}[/bold] is {station_info["distance"]}km from Southern Cross.'
        )
        console.print(
            f'- Journeys to [bold]{station}[/bold] take {int_to_timerange[station_info["time"]]} minutes on average.\n'
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


# Statistics page. Currently contains info on how many stations have been visited in total and for each group/line.
def stats(data):
    clear()

    visited = {}
    unvisited = {}
    for line in colours:
        visited.update({line: []})
        unvisited.update({line: []})

    for v in data['visited']:
        for line in data['visited'][v]['line']:
            visited[line].append(v)

    for unv in data['unvisited']:
        for line in data['unvisited'][unv]['line']:
            unvisited[line].append(unv)

    burnley = {
        'visited': len(visited['Alamein'])
        + len(visited['Belgrave'])
        + len(visited['Glen Waverley'])
        + len(visited['Lilydale']),
        'total': (
            len(visited['Alamein'])
            + len(visited['Belgrave'])
            + len(visited['Glen Waverley'])
            + len(visited['Lilydale'])
        )
        + (
            len(unvisited['Alamein'])
            + len(unvisited['Belgrave'])
            + len(unvisited['Glen Waverley'])
            + len(unvisited['Lilydale'])
        ),
    }
    caufield = {
        'visited': len(visited['Cranbourne']) + len(visited['Pakenham']),
        'total': len(visited['Cranbourne'])
        + len(visited['Pakenham'])
        + len(unvisited['Cranbourne'])
        + len(unvisited['Pakenham']),
    }
    clifton = {
        'visited': len(visited['Mernda']) + len(visited['Hurstbridge']),
        'total': (len(visited['Mernda']) + len(visited['Hurstbridge']))
        + (len(unvisited['Mernda']) + len(unvisited['Hurstbridge'])),
    }
    northern = {
        'visited': len(visited['Craigieburn'])
        + len(visited['Sunbury'])
        + len(visited['Upfield']),
        'total': len(visited['Craigieburn'])
        + len(visited['Sunbury'])
        + len(visited['Upfield'])
        + len(unvisited['Craigieburn'])
        + len(unvisited['Sunbury'])
        + len(unvisited['Upfield']),
    }
    cross_city = {
        'visited': len(visited['Frankston'])
        + len(visited['Werribee'])
        + len(visited['Williamstown']),
        'total': len(visited['Frankston'])
        + len(visited['Werribee'])
        + len(visited['Williamstown'])
        + len(unvisited['Frankston'])
        + len(unvisited['Werribee'])
        + len(unvisited['Williamstown']),
    }

    console.print(f"""
    -+ Statistics +-

    [bold]You have visited {len(data["visited"])} out of {len(data["visited"]) + len(data["unvisited"])} stations. Breakdown:[/bold]

    - You\'ve visited {burnley["visited"]} out of {burnley["total"]} [{colours["Alamein"]}] Burnley [/{colours["Alamein"]}] group stations:
      - {len(visited["Alamein"])} out of {len(visited["Alamein"]) + len(unvisited["Alamein"])} stations on the Alamein line.
      - {len(visited["Belgrave"])} out of {len(visited["Belgrave"]) + len(unvisited["Belgrave"])} stations on the Belgrave line.
      - {len(visited["Glen Waverley"])} out of {len(visited["Glen Waverley"]) + len(unvisited["Glen Waverley"])} stations on the Glen Waverley line.
      - {len(visited["Lilydale"])} out of {len(visited["Lilydale"]) + len(unvisited["Lilydale"])} stations on the Lilydale line.

    - You\'ve visited {caufield["visited"]} out of {caufield["total"]} [{colours["Cranbourne"]}] Caufield [/{colours["Cranbourne"]}] group stations:
      - {len(visited["Cranbourne"])} out of {len(visited["Cranbourne"]) + len(unvisited["Cranbourne"])} stations on the Cranbourne line.
      - {len(visited["Pakenham"])} out of {len(visited["Pakenham"]) + len(unvisited["Pakenham"])} stations on the Pakenham line.

    - You\'ve visited {clifton["visited"]} out of {clifton["total"]} [{colours["Mernda"]}] Clifton Hill [/{colours["Mernda"]}] group stations.
      - {len(visited["Hurstbridge"])} out of {len(visited["Hurstbridge"]) + len(unvisited["Hurstbridge"])} stations on the Hurstbridge line.
      - {len(visited["Mernda"])} out of {len(visited["Mernda"]) + len(unvisited["Mernda"])} stations on the Mernda line.

    - You\'ve visited {northern["visited"]} out of {northern["total"]} [{colours["Sunbury"]}] Northern [/{colours["Sunbury"]}] group stations:
      - {len(visited["Craigieburn"])} out of {len(visited["Craigieburn"]) + len(unvisited["Craigieburn"])} stations on the Craigieburn line.
      - {len(visited["Sunbury"])} out of {len(visited["Sunbury"]) + len(unvisited["Sunbury"])} stations on the Sunbury line.
      - {len(visited["Upfield"])} out of {len(visited["Upfield"]) + len(unvisited["Upfield"])} stations on the Upfield line.

    - You\'ve visited {cross_city["visited"]} out of {cross_city["total"]} [{colours["Frankston"]}] Cross City [/{colours["Frankston"]}] group stations:
      - {len(visited["Frankston"])} out of {len(visited["Frankston"]) + len(unvisited["Frankston"])} stations on the Frankston line.
      - {len(visited["Werribee"])} out of {len(visited["Werribee"]) + len(unvisited["Werribee"])} stations on the Werribee line.
      - {len(visited["Williamstown"])} out of {len(visited["Williamstown"]) + len(unvisited["Williamstown"])} stations on the Williamstown line.

    - You\'ve visited {len(visited["Flemington Racecourse"])} out of {len(visited["Flemington Racecourse"]) + len(unvisited["Flemington Racecourse"])} stations on the [{colours["Flemington Racecourse"]}] Flemington Racecourse [/{colours["Flemington Racecourse"]}] line.
    - You\'ve visited {len(visited["Stony Point"])} out of {len(visited["Stony Point"]) + len(unvisited["Stony Point"])} stations on the [{colours["Stony Point"]}] Stony Point [/{colours["Stony Point"]}] line.
    - You\'ve visited {len(visited["Sandringham"])} out of {len(visited["Sandringham"]) + len(unvisited["Sandringham"])} stations on the [{colours["Sandringham"]}] Sandringham [/{colours["Sandringham"]}] line.
    """)
    print(print_menu(['Main menu', 'Exit']))

    while True:
        choice = input('> ')

        if choice == '1':
            break
        elif choice == '2':
            exit()
        else:
            print(
                '\nInvalid choice. Please select one of the listed options above by typing the number next to the option.\n'
            )


def ops_menu(data):
    clear()

    print('\n -+ Options +-\n')
    print(
        print_menu(
            [
                'Colour mode',
                'Mark station as visited',
                'Reset visited stations',
                'Main menu',
            ]
        )
    )

    while True:
        choice = input('> ')

        if choice == '1':
            colour_mode(data)
            break
        elif choice == '2':
            mark_visited(data)
            break
        elif choice == '3':
            reset_stations(data)
            break
        elif choice == '4':
            break
        else:
            print(
                '\nInvalid choice. Please select one of the listed options above by typing the number next to the option.\n'
            )


def mark_visited(data):
    clear()

    print(
        "To mark a station as visited, type in it's full name below. Type nothing to return to the main menu.\n"
    )

    station = None
    visited = False

    while True:
        user_input = input('> ')
        stn_name = user_input.title()
        if len(user_input) == 0:
            break
        else:
            station = data['unvisited'].get(stn_name)

            if not station:
                station = data['visited'].get(stn_name)

                if station:
                    visited = True
                else:
                    print('\nStation not found, recheck spelling.\n')

        if station:
            if visited is True:
                print(
                    '\nThis station is already marked as visited. Do you wish to set it back to being unvisited? (y/n)\n'
                )
                while True:
                    user_input = input('> ')
                    user_input = user_input.lower()

                    if user_input == 'n':
                        print(
                            '\nOperation aborted. Press enter to return to the main menu.'
                        )
                        input()
                        return

                    elif user_input == 'y':
                        break

                    else:
                        print(
                            '\nInvalid choice. Please select one of the listed options above by typing the number next to the option.\n'
                        )

            if visited is False:
                # Insert the dict associated with the user provided station into visited after grabbing it from unvisited with get(). Vice versa for the else statement.
                data['visited'].update({stn_name: station})
                # Add on the date the station was visited to the station dict
                data['visited'][stn_name].update(
                    {'date_visited': assign_date(stn_name)}
                )
                # Now that we've copied over the station dict into visited, we can remove it from unvisited with pop(). Vice versa for the else statement.
                data['unvisited'].pop(stn_name)
            else:
                data['unvisited'].update({stn_name: station})
                # Remove the date_visited key from the station dict
                data['unvisited'][stn_name].pop('date_visited')
                data['visited'].pop(stn_name)

            # If the station provided by the user was queued in to_visit, clear to_visit
            if data['to_visit'] == stn_name:
                data['to_visit'] = ''

            # Write changes to datastore.json so the program remembers them when reopened
            write(data)

            print(
                '\nOperation completed successfully. Press enter to return to the main menu.'
            )
            input()

            break


def colour_mode(data):
    global colours
    current_mode = 'Enhanced'

    if data['config']['use_enhanced_colours'] is False:
        current_mode = 'Native'

    clear()

    print(
        'Configure how line colours are displayed by selecting one of the two modes. Accurate will use colours similar to the actual line colours; Native will use the colours defined by your terminal emulator.\n'
    )

    print(f'Current mode: {current_mode}\n')

    print(print_menu(['Use accurate colours', 'Use native colours', 'Main menu']))

    while True:
        choice = input('> ')
        if choice == '1':
            colours = colour_store['enhanced']

            data['config']['use_enhanced_colours'] = True
            write(data)

            break
        elif choice == '2':
            colours = colour_store['native']

            data['config']['use_enhanced_colours'] = False
            write(data)

            break
        elif choice == '3':
            break
        else:
            print(
                '\nInvalid choice. Please select one of the listed options above by typing the number next to the option.\n'
            )


def reset_stations(data):
    clear()

    console.print(
        'Warning! you are about to reset [bold underline]ALL VISITED STATIONS![/bold underline] Data that will be lost includes which stations have been visited and on what date you visited them. Type "I know what I\'m doing!" to reset all visited stations, or type anything else to return to the main menu.\n'
    )

    user_input = input('> ')

    if user_input == "I know what I'm doing!":
        visited = data['visited']
        # Get all keys (station names) in data['visited'] and turn it into a list so we know which stations we need to reset
        station_names = list(visited.keys())

        # reset data['to_visit'] if it contains a value
        if len(data['to_visit']) > 0:
            data['to_visit'] = ''

        # Iterate over every key we got from data['visited'], remove any data that needs to be reset (like visited dates) then move the entire dict back to data['unvisited]
        for name in station_names:
            date_visited = visited[name].get('date_visited')

            if date_visited:
                visited[name].pop('date_visited')

            data['unvisited'].update({name: visited[name]})
            data['visited'].pop(name)

        write(data)

        input(
            '\nOperation succeeded - all visited stations have been reset. Press enter to return to the main menu.'
        )
    else:
        input('\nOperation cancelled. Press enter to return to the main menu.')


# Main program
def main():
    data = read()
    use_enhanced_colours = data['config']['use_enhanced_colours']

    if use_enhanced_colours is False:
        global colours
        colours = colour_store['native']

    while True:
        clear()

        console.print(print_title('Rail Roulette', 'bright_blue'))

        print(print_menu(['Get next station', 'Statistics', 'Options', 'Exit']))

        choice = input('> ')

        if choice == '1':
            check_to_visit(data)
        elif choice == '2':
            stats(data)
        elif choice == '3':
            ops_menu(data)
        elif choice == '4':
            exit()
        else:
            print(
                '\nInvalid choice. Please select one of the listed options above by typing the number next to the option.\n'
            )


if __name__ == '__main__':
    main()
