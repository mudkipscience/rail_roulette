from _core import (
    clear,
    print_menu,
    assign_date,
    read,
    write,
    fuzzy_search,
    get_colours,
    console,
)
from _core import INT_TO_TIMERANGE, LINE_GROUPS
import _options as ops
from typing import Any
import random


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


def fmt_lines_groups(data: dict[str, Any], station: str) -> list[list[str]]:
    # Takes a list and mutates it to add colour to each line/group, as well as adding commas and ' and ' to make nicer and readable when we join it into a string later on.
    def prettify_list(items: list[str]) -> None:
        colours = get_colours(data)
        # Adds rich styling (colours here) to each group/station. Found using this syntax was easier over using enumerate() as I need the index of the item anyway.
        for i, item in enumerate(items):
            colour: str | None = colours.get(item) or colours.get(LINE_GROUPS[item][0])
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

    station_groups_list: list[str] = []
    station_info: dict[str, Any] = data['unvisited'].get(station) or data[
        'visited'
    ].get(station)
    # Make a copy of the line info because if we mutated it we would end up writing those changes to datastore.json
    station_lines_list: list[str] = station_info['line'].copy()

    # This codeblock checks if all lines in a group serve the station, and if so removes the individual lines and adds the group to reduce clutter.
    # Loop through each group
    for group in LINE_GROUPS:
        group_lines = LINE_GROUPS[group]
        matched_lines: list[str] = []

        # Loop through each line in the group
        for line in group_lines:
            # Check if the station is served by the group line. If yes append to matched_lines
            if line in station_info['line']:
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

    return [station_groups_list, station_lines_list]


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


# Selects a random station from the data['unvisited'] dictionary/object by doing (sparkles) magic (sparkles)
def roll_station(data: dict[str, Any]) -> None:
    # Check whether there are any stations left to visit (the function we call here is just a screen that congratulates the user and gives options to return to main menu or exit)
    if len(data['unvisited']) == 0:
        no_unvisited()
        return

    # Get the name's of all stations by converting the dictionary keys (the names) into a list.
    stations: list[str] = list(data['unvisited'].keys())

    while True:
        clear()

        # Pick a random station name from our list made above
        station: str = random.choice(stations)
        station_info: dict[str, Any] = data['unvisited'][station]
        groups_and_lines: list[list[str]] = fmt_lines_groups(data, station)

        console.print(f"Looks like you're heading to... [bold]{station}!\n")
        console.print(
            f'• [bold]{station}[/bold] is served by the {"".join(groups_and_lines[0])}{"".join(groups_and_lines[1])}.'
        )
        console.print(
            f'• [bold]{station}[/bold] is {station_info["distance"]}km from Southern Cross.'
        )
        console.print(
            f'• Journeys to [bold]{station}[/bold] take {INT_TO_TIMERANGE[station_info["time"]]} minutes on average.\n'
        )
        print(print_menu(['Reroll', 'Accept']))

        while True:
            choice: str = input('> ')
            if choice == '1':
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

        if choice != '1':
            break


# Statistics page. Currently contains info on how many stations have been visited in total and for each group/line.
def stats(data: dict[str, Any]) -> None:
    colours: dict[str, str] = get_colours(data)

    # Returns the count of unvisited and total unique stations in a group in a list [visited, total]
    def count_unique_stns(group: str) -> list[int]:
        # Get lines associated with a group from line_groups dict defined near the top of the file
        group_lines: list[str] = LINE_GROUPS[group]
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
        group_lines: list[str] = LINE_GROUPS[group]
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
    for group in LINE_GROUPS:
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


def lookup_stn(data: dict[str, Any]) -> None:
    while True:
        clear()

        print('To look up information on a station, type in its name below:\n')

        station: str | None = fuzzy_search(data, True)

        clear()

        if station:
            station_info: dict[str, Any] = data['unvisited'].get(station) or data[
                'visited'
            ].get(station)

            groups_and_lines: list[list[str]] = fmt_lines_groups(data, station)

            console.print(f'-+ {station} +-\n')
            console.print(
                f'• [bold]{station}[/bold] is served by the {"".join(groups_and_lines[0])}{"".join(groups_and_lines[1])}.'
            )
            console.print(
                f'• [bold]{station}[/bold] is {station_info["distance"]}km from Southern Cross.'
            )
            console.print(
                f'• Journeys to [bold]{station}[/bold] take {INT_TO_TIMERANGE[station_info["time"]]} minutes on average.'
            )
            if data['visited'].get(station):
                if data['visited'][station].get('date_visited'):
                    console.print(
                        f'• You visited [bold]{station}[/bold] on {data["visited"][station].get("date_visited")}.'
                    )
                else:
                    console.print(f'• You have visited {station} before.')

            # Print blank line
            console.print()

            print(print_menu(['Lookup another station', 'Main menu']))

            while True:
                choice: str = input('> ')

                if choice == '1':
                    break
                elif choice == '2':
                    return
                else:
                    print(
                        '\nInvalid choice. Please select one of the listed options above by typing the number next to the option.\n'
                    )


# Main program
def main() -> None:
    data = read()

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
            lookup_stn(data)
        elif choice == '4':
            ops.menu(data)
        elif choice == '5':
            exit()
        else:
            print(
                '\nInvalid choice. Please select one of the listed options above by typing the number next to the option.\n'
            )


if __name__ == '__main__':
    main()
