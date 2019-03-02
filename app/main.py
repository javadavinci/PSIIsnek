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

    color = "#00FF00"

    return start_response(color)


@bottle.post('/move')
def move():
    data = bottle.request.json
    snakes = data['board']['snakes']
    food = data['board']['food']
    height = data['board']['height']
    width = data['board']['width']
    grid = [[0 for x in range(width)] for y in range(height)]
    snake = data['board']['snakes']

    """
    TODO: Using the data from the endpoint request object, your
            snake AI must choose a direction to move in.
    """
    #print(snakes)
    #print(json.dumps(data))

    directions = ['up', 'down', 'left', 'right']
    #direction = random.choice(directions)
    health = data["you"]['health']
    if  health < 70:
        return move_response('left')
    else:    
        for s in snakes:
        you = False
        if s['id'] == data['you']:
            snake = s
            you = True
        for idx, val in enumerate(s['coords']):
            x, y = val
            if grid[x][y] != 0:
                continue # Stops snake bodies from overwriting heads at the beginning
            # If this is the forst coordinate, it's the head
            if idx == 0:
                grid[x][y] = 11 if you else 21
            else:
                grid[x][y] = 10 if you else 20
    for coords in food:
        x, y = coords
        grid[x][y] = 2
        
    head = snake['coords'][0]
        
    # Simple macros for each direction
    c_north = [snake['coords'][0][0], snake['coords'][0][1] - 1]
    c_south = [snake['coords'][0][0], snake['coords'][0][1] + 1]
    c_east = [snake['coords'][0][0] + 1, snake['coords'][0][1]]
    c_west = [snake['coords'][0][0] - 1, snake['coords'][0][1]]

        #Check if a given coordiante is safe
        def coords_safe(coords):
            x, y = coords
            if x < 0 or x > width-1: return False # Check if coordinate is inside horizontal bounds
            if y < 0 or y > height-1: return False # Check if coordinate is inside vertical bounds
            if grid[x][y] not in [0,2]: return False # Check if coordinate matches a snake body
            return True
        
        def find_neighbours(coords):
            x, y = coords
            neighbors = []
            
            if coords_safe([x-1, y]): neighbors.append((x-1, y))
            if coords_safe([x, y-1]): neighbors.append((x, y-1))
            if coords_safe([x+1, y]): neighbors.append((x+1, y))
            if coords_safe([x, y+1]): neighbors.append((x, y+1))
            
            return neighbors
        
        finder = astar.pathfinder(neighbors=find_neighbours)
        path = finder( (head[0], head[1]), (food[0][0], food[0][1]) )[1]
        
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
            if next_coord[1] < head[1]:
                direction = "up"
            elif next_coord[1] > head[1]:
                direction = "down"
            elif next_coord[0] > head[0]:
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
