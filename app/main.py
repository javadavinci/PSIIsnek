import json
import os
import random
import bottle
from pypaths import astar

from api import ping_response, start_response, move_response, end_response

@bottle.route('/')
def index():
    return '''
    Battlesnake documentation can be found at
       <a href="https://docs.battlesnake.io">https://docs.battlesnake.io</a>.
    '''

@bottle.route('/static/<path:path>')
def static(path):
    """
    Given a path, return the static file located relative
    to the static folder.

    This can be used to return the snake head URL in an API response.
    """
    return bottle.static_file(path, root='static/')

@bottle.post('/ping')
def ping():
    """
    A keep-alive endpoint used to prevent cloud application platforms,
    such as Heroku, from sleeping the application instance.
    """
    return ping_response()

@bottle.post('/start')
def start():
    data = bottle.request.json

    """
    TODO: If you intend to have a stateful snake AI,
            initialize your snake state here using the
            request's data if necessary.
    """
    print(json.dumps(data))

    color = "#49301f"

    return start_response(color)


@bottle.post('/move')
def move():
    data = bottle.request.json
    snakes = data['board']['snakes']
    food = data['board']['food']
    height = data['board']['height']
    width = data['board']['width']
    health = data["you"]['health']
    grid = [[0 for x in range(width)] for y in range(height)]
    snake = []
    nearestfood = {'dist': -1, 'x': 0, 'y': 0}
    for i in snakes:
        snake.append(i['body'])

    """
    TODO: Using the data from the endpoint request object, your
            snake AI must choose a direction to move in.
    """
    #print(snakes)
    #print(json.dumps(data))

    directions = ['up', 'down', 'left', 'right']
    #direction = random.choice(directions)

    for s in snakes:
        you = False
        if s['id'] == data['you']['id']:
            you = True
        for idx, val in enumerate(s['body']):
            x = val['x']
            y = val['y']
            if grid[x][y] != 0:
                continue  # Stops snake bodies from overwriting heads at the beginning
            # If this is the first coordinate, it's the head
            if idx == 0:
                if you is True:
                    grid[x][y] = 11
                else:
                    grid[x][y] = 21
                    if (len(data['you']['body']) - 1) > (len(s['body']) - + 1):
                        try:
                            grid[x + 1][y] = 21
                        except IndexError:
                            pass
                        try:
                            grid[x][y + 1] = 21
                        except IndexError:
                            pass
                        try:
                            grid[x - 1][y] = 21
                        except IndexError:
                            pass
                        try:
                            grid[x][y - 1] = 21
                        except IndexError:
                            pass
            elif idx == (len(data['you']['body']) - 1):
                if you is True:
                    grid[x][y] = 3
                else:
                    grid[x][y] = 22
            else:
                if you is True:
                    grid[x][y] = 10
                else:
                    grid[x][y] = 20

    head = data['you']['body'][0]

    for coords in food:
        x = coords['x']
        y = coords['y']
        grid[x][y] = 2
        hx = abs(head['x'] - x)
        hy = abs(head['y'] - y)
        xy = hx + hy
        if nearestfood['dist'] > xy or nearestfood['dist'] is -1:
            nearestfood['dist'] = xy
            nearestfood['x'] = x
            nearestfood['y'] = y
            print("closest food: " + str(nearestfood))

    print(data['turn'])



    # Simple macros for each direction
    c_north = [head['x'], head['y'] - 1]
    c_south = [head['x'], head['y'] + 1]
    c_east = [head['x'] + 1, head['y']]
    c_west = [head['x'] - 1, head['y']]

        #Check if a given coordiante is safe
    def coords_safe(coords):
        x, y = coords
        if x < 0 or x > width-1: return False # Check if coordinate is inside horizontal bounds
        if y < 0 or y > height-1: return False # Check if coordinate is inside vertical bounds
        if grid[x][y] not in [0, 2, 3]: return False # Check if coordinate matches a snake body
        return True

    def find_neighbours(coords):
        x, y = coords
        neighbors = []

        if coords_safe([x-1, y]):
            neighbors.append((x-1, y))
        if coords_safe([x, y-1]):
            neighbors.append((x, y-1))
        if coords_safe([x+1, y]):
            neighbors.append((x+1, y))
        if coords_safe([x, y+1]):
            neighbors.append((x, y+1))

        return neighbors

    tail = data['you']['body'][-1]

    if health < 70:
        finder = astar.pathfinder(neighbors=find_neighbours)
        path = finder((head['x'], head['y']), (nearestfood['x'], nearestfood['y']))[1]
    else:
        finder = astar.pathfinder(neighbors=find_neighbours)
        path = finder((head['x'], head['y']), (tail['x'], tail['y']))[1]

    if len(path) < 2:
        finder = astar.pathfinder(neighbors=find_neighbours)
        path = finder((head['x'], head['y']), (tail['x'], tail['y']))[1]

        if len(path) < 2:
            if coords_safe(c_north):
                direction = "up"
            elif coords_safe(c_south):
                direction = "down"
            elif coords_safe(c_east):
                direction = "right"
            else:
                direction = "left"
        else:
            next_coord = path[1]
            if next_coord[1] < head['y']:
                direction = "up"
            elif next_coord[1] > head['y']:
                direction = "down"
            elif next_coord[0] > head['x']:
                direction = "right"
            else:
                direction = "left"
    else:
        next_coord = path[1]
        if next_coord[1] < head['y']:
            direction = "up"
        elif next_coord[1] > head['y']:
            direction = "down"
        elif next_coord[0] > head['x']:
            direction = "right"
        else:
            direction = "left"

    print(direction)
    return move_response(direction)

@bottle.post('/end')
def end():
    data = bottle.request.json

    """
    TODO: If your snake AI was stateful,
        clean up any stateful objects here.
    """
    print(json.dumps(data))

    return end_response()

# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug=os.getenv('DEBUG', True)
    )
