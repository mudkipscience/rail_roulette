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

print(os.listdir())


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


# Main program
def main(data):
    clear()
    print('\n-+ Random-Metro-Station-Choosinator 3000 +-\n')
    print('1) Get next station')
    print('2) View statistics')
    print('3) Exit\n')

    choice = input('> ')

    if choice == '1':
        get_station(data)
    elif choice == '2':
        pass
    elif choice == '3':
        exit()
    else:
        print(
            '\nInvalid choice. Please select one of the listed options above by typing the number next to the option.\n'
        )

    main(data)


def get_station(data):
    stations = list(data['unvisited'].keys())
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
        station = random.choice(stations)
        station_info = data['unvisited'][station]

        print(
            f'Looks like you\'re heading to... {station}, located on the {station_info['line']} line! {station} is {station_info['distance']}km from the CBD. Journeys to {station} on average take {time_conversion[station_info['time']]} minutes.\n'
        )
        print('1) Reroll')
        print('2) Accept\n')

        while True:
            choice = input('> ')
            if choice == '1':
                get_station(data)
                break
            elif choice == '2':
                to_visit = data['unvisited'].pop(station)
                data['to_visit'].update({station: to_visit})
                write(data)
                break
            else:
                print(
                    '\nInvalid choice. Please select one of the listed options above by typing the number next to the option.\n'
                )
        
        break

main(read())

"""
Time:
0 = under 10 min
1 = 11-20 min
2 = 21-30 min
3 = 31-40 min
4 = 41-50 min
5 = 51-60 min
6 = 61-70 min
7 = 71-80 min
8 = 81-90 min
9 = 91-100 min
10 = 101-110 min

stored = data['stored']
visited = data['visited']
unvisited = data['unvisited']
name = 'Aircraft'
info = unvisited.pop(name)
visited.update({name: info})
print(json.dumps(data, indent = 4))
#dict(sorted(data['unvisited_stations'].items()))
"""
