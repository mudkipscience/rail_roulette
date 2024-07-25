from _core import read, write

data = read()
unvisited = data['unvisited']

for station in unvisited:
    print(f'Updated {station}')

    unvisited[station].update({'location': ''})

write(data)
