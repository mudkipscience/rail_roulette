import json
import os
import random
import re
from typing import Any
from rich.console import Console

# Enhanced console output functionality provided by Rich
console = Console(highlight=False)
# dictionary of arrays that lists what group a line is apart of
line_groups: dict[str, list[str]] = {
    'Burnley': ['Alamein', 'Belgrave', 'Glen Waverley', 'Lilydale'],
    'Caufield': ['Cranbourne', 'Pakenham'],
    'Clifton Hill': ['Hurstbridge', 'Mernda'],
    'Northern': ['Craigieburn', 'Sunbury', 'Upfield'],
    'Cross City': ['Frankston', 'Werribee', 'Williamstown'],
}
# Line colours. Enhanced are more accurate to official PTV branding whereas native uses the terminal's defined colours instead.
colour_store: dict[str, dict[str, str]] = {
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
colours: dict[str, str] = colour_store['enhanced']


# Runs OS-specific shell command to clear console
def clear() -> None:
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


# Load saved, visited and unvisited stations from datastore.json, which should be in the same directory.
def read() -> dict[str, Any]:
    # I kind of understand how this works? Basically with is shorthand for a try/except/finally statement and I think there are some benefits beyond that too? I dunno.
    #  Either way I'm opening a file! - Update 10/07/2024: Apparently what I said is NOT how it works. Guess I'll have to look into it further...
    with open('datastore.json', 'r') as file:
        return json.load(file)


# Write modified .json to datastore.json
def write(data: dict[str, Any]) -> None:
    with open('datastore.json', 'w') as file:
        json.dump(data, file, indent=4, sort_keys=True)


# Generates a string of options the user can select from. ops is an array of names we want to give to each option.
def print_menu(ops: list[str]) -> str:
    menu: str = ''

    for i, entry in enumerate(ops, 1):
        menu += f'{i}) {entry}\n'

    return menu


# Prints a rail-styled title like seen in the main menu. args: txt (title text: str) txr_clr (colour to print txt as) rail_clr (colour to print the "rails" as)
def print_title(
    txt: str, txt_clr: str = 'default', rail_clr: str = 'bright_black'
) -> str:
    title_txt: list[str] = list(txt)

    for i in range(len(title_txt)):
        if title_txt[i] != ' ':
            title_txt[i] = f'[{txt_clr}]{title_txt[i]}[/{txt_clr}]'

    title_rails: str = f'[{rail_clr}] {"+-" * (len(title_txt) + 2)}+'
    formatted_txt: str = (
        f'[{rail_clr}] | |{"[" + rail_clr + "]" + "|".join(title_txt)}[{rail_clr}]| |'
    )

    return f'{title_rails}\n{formatted_txt}\n{title_rails}\n'


# (for now) this function only searches stations based on a partial string (e.g. "fli" will return Flinders Street, "fern" will return Ferntree Gully and Upper Ferntree Gully, "so cro" will return Southern Cross)
def search_stations(
    data: dict[str, Any], query: str, include_visited: bool = False
) -> list[str]:
    query = query.lower()
    # Use a set to prevent duplicates
    results: set[str] = set()

    # Use a nested function to save me writing almost the same code twice - returns none as this mutates the existing variable results which is accessible from this scope
    def find_results(stations: list[str]) -> None:
        for stn in stations:
            # Basic stuff, if the query (substring) is found to be in the station name, add that station name to the results set
            if query in stn.lower():
                results.add(stn)

        # Does the same thing as above but only if include_visited is True
        if include_visited is True:
            visited_stns = list(data['visited'].keys())
            for stn in visited_stns:
                if query in stn.lower():
                    results.add(stn)

        # Split the words in the query at whitespace (fli st becomes ['fli', st'])
        split_query: list[str] = query.split()

        if len(split_query) > 1:
            for stn in stations:
                matches_found: int = 0

                # Try and match each split query against a station name
                for substr in split_query:
                    if substr in stn.lower():
                        matches_found += 1

                # if matches_found == the length of the split_query list, a match must have been found
                if matches_found == len(split_query):
                    results.add(stn)

    find_results(list(data['unvisited'].keys()))

    if include_visited is True:
        find_results(list(data['visited'].keys()))

    result_list: list[str] = list(results)

    return sorted(result_list)


# We call this when data['unvisited'] has a length of 0 (meaning it contains nothing)
def no_unvisited() -> None:
    clear()

    print(
        "There aren't any more stations to visit - you've been to them all! Congratulations!\n"
    )
    print(print_menu(['Main menu', 'Exit']))

    while True:
        choice: str = input('> ')

        if choice == '1':
            break
        elif choice == '2':
            exit()
        else:
            print(
                '\nInvalid choice. Please select one of the listed options above by typing the number next to the option.\n'
            )


# Check whether a station name has been written to to_visit dict. If yes, prompt the user whether they want to mark it as visited & continue or return/exit
def check_to_visit(data: dict[str, Any]) -> None:
    clear()

    if len(data['to_visit']) > 0:
        to_visit: str = data['to_visit']
        print(
            f'Attention! {to_visit} Station has already been chosen as your next station to visit. What would you like to do?\n'
        )
        print(print_menu(['Mark as visited', 'Get a new station', 'Main menu']))

        while True:
            choice: str = input('> ')
            if choice == '1':
                # Insert the dict associated with the randomly chosen station into visited after grabbing it from unvisited with get()
                data['visited'].update(
                    {data['to_visit']: data['unvisited'].get(data['to_visit'])}
                )

                # If the user provides a date, add on the date the station was visited to the station dict
                date: str | None = assign_date(data['to_visit'])

                if date:
                    data['visited'][data['to_visit']].update({'date_visited': date})

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
def assign_date(stn_name: str) -> str | None:
    # Regular expression that checks for a valid DD/MM/YYYY format (I don't think I need to worry about MM/DD/YYYY freaks given this is a Melbourne-specific program)
    regex: str = '(0[1-9]|[12][0-9]|3[01])\\/(0[1-9]|1[0,1,2])\\/(20)\\d{2}'

    print(
        f'\nType in the date you visited {stn_name} in the format of DD/MM/YYYY below, or type "skip" to skip.\n'
    )

    while True:
        user_input: str = input('> ')

        if user_input == 'skip':
            break

        # Check to make sure the length is valid before running regex checks
        elif len(user_input) != 10:
            print(
                '\nInvalid choice. Please either enter a date in the format of DD/MM/YYYY or type "skip".\n'
            )

        else:
            # Use regex to validate the user input
            date: re.Match[str] | None = re.search(regex, user_input)

            if date:
                return user_input
            else:
                print(
                    '\nInvalid date. Please enter a date in the format of DD/MM/YYYY. Year must be between 2000 and 2099.\n'
                )


# Selects a random station from the data['unvisited'] dictionary/object by doing (sparkles) magic (sparkles)
def roll_station(data: dict[str, Any]) -> None:
    # Check whether there are any stations left to visit (the function we call here is just a screen that congratulates the user and gives options to return to main menu or exit)
    if len(data['unvisited']) == 0:
        no_unvisited()
        return

    # Get the name's of all stations by converting the dictionary keys (the names) into a list.
    stations: list[str] = list(data['unvisited'].keys())

    # Used for converting the time int assigned to each station in datastore.json into something that actually makes sense when you read it.
    int_to_timerange: dict[int, str] = {
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
        def prettify_list(items: list[str]) -> None:
            # Adds rich styling (colours here) to each group/station. Found using this syntax was easier over using enumerate() as I need the index of the item anyway.
            for i, item in enumerate(items):
                colour: str | None = colours.get(item) or colours.get(
                    line_groups[item][0]
                )
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
        station: str = random.choice(stations)
        station_info: dict[str, Any] = data['unvisited'][station]
        station_groups_list: list[str] = []
        # Make a copy of the line info because if we mutated it we would end up writing those changes to datastore.json
        station_lines_list: list[str] = station_info['line'].copy()

        # This codeblock checks if all lines in a group serve the station, and if so removes the individual lines and adds the group to reduce clutter.
        # Loop through each group
        for group in line_groups:
            group_lines = line_groups[group]
            matched_lines: list[str] = []

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
            f'• [bold]{station}[/bold] is served by the {"".join(station_groups_list)}{"".join(station_lines_list)}.'
        )
        console.print(
            f'• [bold]{station}[/bold] is {station_info["distance"]}km from Southern Cross.'
        )
        console.print(
            f'• Journeys to [bold]{station}[/bold] take {int_to_timerange[station_info["time"]]} minutes on average.\n'
        )
        print(print_menu(['Reroll', 'Accept']))

        while True:
            choice: str = input('> ')
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
def stats(data: dict[str, Any]) -> None:
    # Returns the count of unvisited and total unique stations in a group in a list [visited, total]
    def count_unique_stns(group: str) -> list[int]:
        # Get lines associated with a group from line_groups dict defined near the top of the file
        group_lines: list[str] = line_groups[group]
        # Create two sets. Sets cannot contain duplicate values so it's an easy way of removing duplicate stations and returning more accurate numbers
        unvisited_set: set[str] = set()
        visited_set: set[str] = set()

        # Loop through each line in the provided group
        for line in group_lines:
            # Two list comprehensions that create lists containing visited/unvisited stations if they are served by the line we are currently looping through
            unvisited_list = [
                stn
                for stn in data['unvisited']
                if line in data['unvisited'][stn]['line']
            ]
            visited_list = [
                stn for stn in data['visited'] if line in data['visited'][stn]['line']
            ]

            # Combine the newly created lists above with the sets we defined at the start of this func by converting the lists to sets and using union()
            unvisited_set = unvisited_set.union(set(unvisited_list))
            visited_set = visited_set.union(set(visited_list))

        total: int = len(unvisited_set) + len(visited_set)

        # Return the amount of unique stations visited in the group at index 0 and total unique stations in the group
        return [len(visited_set), total]

    # Return the count of visited and total stations on a line
    def count_stations(line: str):
        unvisited_stns = [
            stn for stn in data['unvisited'] if line in data['unvisited'][stn]['line']
        ]
        visited_stns = [
            stn for stn in data['visited'] if line in data['visited'][stn]['line']
        ]

        total: int = len(unvisited_stns) + len(visited_stns)

        return [len(visited_stns), total]

    def group_summary(group: str) -> str:
        group_visited_total: list[int] = count_unique_stns(group)
        group_lines: list[str] = line_groups[group]
        colour: str | None = colours.get(group_lines[0])

        summary_list = [
            f"• You've visited {group_visited_total[0]} out of {group_visited_total[1]} [{colour}] {group} [/{colour}] group stations:"
        ]

        for line in group_lines:
            unvisited_stns = [
                stn
                for stn in data['unvisited']
                if line in data['unvisited'][stn]['line']
            ]

            visited_stns = [
                stn for stn in data['visited'] if line in data['visited'][stn]['line']
            ]

            summary_list.append(
                f'  • {len(visited_stns)} out of {len(visited_stns) + len(unvisited_stns)} stations on the {line} line.'
            )

        return '\n'.join(summary_list)

    clear()

    flemington_count: list[int] = count_stations('Flemington Racecourse')
    stony_count: list[int] = count_stations('Stony Point')
    sandringham_count: list[int] = count_stations('Sandringham')

    console.print(
        f'-+ Statistics +-\n\n[bold]You have visited {len(data["visited"])} out of {len(data["visited"]) + len(data["unvisited"])} stations. Breakdown:[/bold]\n'
    )

    # For each group, print out a group summary (prints out the amount visited and total unique stations in that group + same for each line in each group too)
    for group in line_groups:
        console.print(group_summary(group) + '\n')

    console.print(
        f'• You\'ve visited {flemington_count[0]} out of {flemington_count[1]} stations on the [{colours["Flemington Racecourse"]}] Flemington Racecourse [/{colours["Flemington Racecourse"]}] line.'
    )
    console.print(
        f'• You\'ve visited {stony_count[0]} out of {stony_count[1]} stations on the [{colours["Stony Point"]}] Stony Point [/{colours["Stony Point"]}] line.'
    )
    console.print(
        f'• You\'ve visited {sandringham_count[0]} out of {sandringham_count[1]} stations on the [{colours["Sandringham"]}] Sandringham [/{colours["Sandringham"]}] line.'
    )
    console.print(
        '\n[bright_black italic]Note: Individual line totals will not add up to the group total as duplicate stations are removed when calculating the group total.[/bright_black italic]\n'
    )

    print(print_menu(['Main menu', 'Exit']))

    while True:
        choice: str = input('> ')

        if choice == '1':
            break
        elif choice == '2':
            exit()
        else:
            print(
                '\nInvalid choice. Please select one of the listed options above by typing the number next to the option.\n'
            )


def info_view(data: dict[str, Any]):
    pass


def ops_menu(data: dict[str, Any]) -> None:
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
        choice: str = input('> ')

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


def colour_mode(data: dict[str, Any]) -> None:
    global colours
    current_mode: str = 'Enhanced'

    if data['config']['use_enhanced_colours'] is False:
        current_mode = 'Native'

    clear()

    print(
        'Configure how line colours are displayed by selecting one of the two modes. Accurate will use colours similar to the actual line colours; Native will use the colours defined by your terminal emulator.\n'
    )

    print(f'Current mode: {current_mode}\n')

    print(print_menu(['Use accurate colours', 'Use native colours', 'Main menu']))

    while True:
        choice: str = input('> ')
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


def mark_visited(data: dict[str, Any]) -> None:
    clear()

    print(
        'To mark a station as visited, type in its name below. Type nothing to return to the main menu.\n'
    )

    station: str | None = None

    while True:
        user_input: str = input('> ')
        if len(user_input) == 0:
            break
        else:
            search: list[str] = search_stations(data, user_input, True)

            if len(search) == 0:
                print('\nStation not found, recheck spelling.\n')
            elif len(search) > 5:
                print('\nToo many results, try another query.\n')
            else:
                if len(search) > 1:
                    console.print(
                        'Found multiple stations, please select one from the options below:\n'
                    )

                    print(print_menu(search + ['Return to main menu']))
                    while True:
                        choice: str | int = input('> ')

                        if not choice.isdigit():
                            print('\nError: Input must be a valid whole number.\n')
                        else:
                            choice = int(choice) - 1

                            if choice < 0 or choice > len(search):
                                print(
                                    f'\nError: Input must be between 1 and {len(search) + 1}\n'
                                )
                            elif choice == len(search):
                                return
                            else:
                                station = search[choice]
                                break
                else:
                    station = search[0]

            if station:
                stn_data: dict[str, Any] = data['visited'].get(station) or data[
                    'unvisited'
                ].get(station)

                visited: dict[str, Any] = data['visited'].get(station)

                if visited:
                    print(
                        f'\n{station} has already been marked as visited. Do you wish to set it back to being unvisited? (y/n)\n'
                    )
                    while True:
                        user_input: str = input('> ')
                        user_input = user_input.lower()

                        if user_input == 'n':
                            input(
                                '\nOperation aborted. Press enter to return to the main menu.'
                            )
                            return

                        elif user_input == 'y':
                            break

                        else:
                            print(
                                '\nInvalid choice. Please select one of the listed options above by typing the number next to the option.\n'
                            )

                if not visited:
                    # Insert the dict associated with the user provided station into visited after grabbing it from unvisited with get(). Vice versa for the else statement.
                    data['visited'].update({station: stn_data})

                    # If the user provides a date, add on the date the station was visited to the station dict
                    date: str | None = assign_date(station)

                    if date:
                        data['visited'][station].update({'date_visited': date})

                    # Now that we've copied over the station dict into visited, we can remove it from unvisited with pop(). Vice versa for the else statement.
                    data['unvisited'].pop(station)
                else:
                    data['unvisited'].update({station: stn_data})
                    # Remove the date_visited key from the station dict
                    if data['unvisited'][station].get('date_visited'):
                        data['unvisited'][station].pop('date_visited')

                    data['visited'].pop(station)

                # If the station provided by the user was queued in to_visit, clear to_visit
                if data['to_visit'] == station:
                    data['to_visit'] = ''

                # Write changes to datastore.json so the program remembers them when reopened
                write(data)

                input(
                    '\nOperation completed successfully. Press enter to return to the main menu.'
                )

                break


def reset_stations(data: dict[str, Any]) -> None:
    clear()

    console.print(
        'Warning! you are about to reset [bold underline]ALL VISITED STATIONS![/bold underline] Data that will be lost includes which stations have been visited and on what date you visited them. Type "I know what I\'m doing!" to reset all visited stations, or type anything else to return to the main menu.\n'
    )

    user_input: str = input('> ')

    if user_input == "I know what I'm doing!":
        visited = data['visited']
        # Get all keys (station names) in data['visited'] and turn it into a list so we know which stations we need to reset
        station_names: list[str] = list(visited.keys())

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
def main() -> None:
    data: dict[str, Any] = {}

    # Displays an error if datastore.json is not found in the current working directory rather than crashing outright
    try:
        data = read()
    except FileNotFoundError:
        print(
            'Could not find datastore.json. This file is required for Railway Roulette to run and must be in the same folder as the program.\n\nIf you need a new copy of this file, you can download it here: https://github.com/mudkipscience/rail_roulette/blob/main/datastore.json\n'
        )
        input('Press enter to exit.')

        exit()

    use_enhanced_colours: bool = data['config']['use_enhanced_colours']

    if use_enhanced_colours is False:
        global colours
        colours = colour_store['native']

    while True:
        clear()

        console.print(print_title('Rail Roulette', 'bright_blue'))

        print(
            print_menu(['Get next station', 'Statistics', 'Lookup', 'Options', 'Exit'])
        )

        choice: str = input('> ')

        if choice == '1':
            check_to_visit(data)
        elif choice == '2':
            stats(data)
        elif choice == '3':
            info_view(data)
        elif choice == '4':
            ops_menu(data)
        elif choice == '5':
            exit()
        else:
            print(
                '\nInvalid choice. Please select one of the listed options above by typing the number next to the option.\n'
            )


if __name__ == '__main__':
    main()
