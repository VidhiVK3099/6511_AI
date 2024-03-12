import os
import re
import numpy as np
import time

noOfColors = 4
tile_dimension = 4

class Tile_types:
    def __init__(self, tile):
        self.type = tile[0]
        self.count = tile[1]

    def FUll_Block(self, landscape, startX, startY):
        #Puts full shaped tile to the landscape and returns the copy of updated version
        copy_up = landscape.bushes.copy()
        for i in range(startX, startX + tile_dimension):
            for j in range(startY, startY + tile_dimension):
                copy_up[i][j] = 0
        return copy_up

    def Outer_Boundry(self, landscape, startX, startY):
        #Puts outer shaped tile to the landscape and returns the copy of updated version
        copy_up = landscape.bushes.copy()
        for i in range(startX, startX + tile_dimension):
            for j in range(startY, startY + tile_dimension):
                if (i == startX) or (i == startX + tile_dimension - 1) or (j == startY) or (
                        j == startY + tile_dimension - 1):
                    copy_up[i][j] = 0
        return copy_up

    def EL_Shaped(self, landscape, startX, startY):
        #Puts el shaped tile to the landscape and returns the copy of updated version
        copy_up = landscape.bushes.copy()
        for i in range(startX, startX + tile_dimension):
            for j in range(startY, startY + tile_dimension):
                if (i == startX) or (j == startY):
                    copy_up[i][j] = 0
        return copy_up

    def __str__(self) -> str:
        return f'Tile: {self.type}. Count: {self.count}.'


class Tile_input_fun:

    def __init__(self, file_path):
        with open(file_path, "r") as f:
            lines = f.readlines()

        self.lines = list(map(lambda x: re.sub('[\n]$', '', x), lines))
        self.land_idx, self.tile_idx, self.target_idx, self.land_size = self.get_input_index()
        self.COLORS = noOfColors
        self.land_arr = self.get_landscape()
        self.tiles = self.get_tiles()
        self.targets = self.get_targets()

    def get_input_index(self):
        #Reads the given txt and extracts the indexes of landscape, tiles, and targets from it. Landscape size is also got using this function.
        land_idx, tile_idx, target_idx = 0, 0, 0

        tiles_found = False

        for i, x in enumerate(self.lines):
            if x.startswith('# Landscape'):
                land_idx = i + 1

            elif x.startswith('# Tiles:') and not tiles_found:
                tile_idx = i + 1
                tiles_found = True

            elif x.startswith('# Targets:'):
                target_idx = i + 1

        land_size = len(self.lines[land_idx]) // 2

        return land_idx, tile_idx, target_idx, land_size

    def get_landscape(self):
        #Reads the list of strings to generate a matrix of integers representing landscape.
        land_int = [[0] * self.land_size for _ in range(self.land_size)]
        land_strs = self.lines[self.land_idx:self.land_idx + self.land_size]

        for i in range(self.land_size):
            count = 0
            for j in range(0, 2 * self.land_size, 2):
                if land_strs[i][j] != ' ':
                    land_int[i][count] = int(land_strs[i][j])
                count += 1

        return land_int

    def get_tiles(self):

        #Reads tiles into lists of landscape instance. Tiles are stored there as tile objects.
        tile_objs = []
        tile_strs = self.lines[self.tile_idx]
        tile_strs = re.sub('[{}]', '', tile_strs)
        tile_strs = list(map(lambda t: t.strip(), tile_strs.split(',')))

        for t in tile_strs:
            k, v = t.split('=')
            tile_objs.append(Tile_types((k, int(v))))

        return tile_objs

    def get_targets(self):
        #Reads targets as a dictionary of colors
        tar = self.lines[self.target_idx:self.target_idx + self.COLORS]
        t_dict = {}
        for t in tar:
            k, v = t.split(':')
            t_dict[k] = int(v)

        return t_dict


class Landscape_funs:
    def __init__(self, tile_input):
        self.bushes = tile_input.land_arr
        self.tiles = tile_input.tiles
        self.targets = tile_input.targets
        self.land_size = tile_input.land_size
        self.current = self.count_colors(self.bushes)
        self.states = [self.bushes]
        self.solution_map = {}

    def put_tile(self, tile, startXi, startXj):
        #Puts the given tile to the given coordinate and returns the copy of the landscape

        if tile.type == 'OUTER_BOUNDARY':
            return tile.Outer_Boundry(self, startXi, startXj)
        elif tile.type == 'EL_SHAPE':
            return tile.EL_Shaped(self, startXi, startXj)
        elif tile.type == 'FULL_BLOCK':
            return tile.FUll_Block(self, startXi, startXj)

    def get_variable_lands(self):
        #Function to get the small sublandscapes size of 4x4
        new_l = []
        divider = self.land_size // tile_dimension
        arr = np.array(self.bushes)
        ver_split = np.array_split(arr, divider, axis=0)

        for a in ver_split:
            hor_split = np.array_split(a, divider, axis=1)
            hor_split = list(map(lambda x: x.tolist(), hor_split))
            new_l += hor_split

        return new_l

    def get_variables(self):
        #Gets the coordinates of 4x4 divided sublandscapes.
        divider = self.land_size // tile_dimension
        startXi, startXj = 0, 0
        variables = [(startXi, startXj)]
        for i in range(divider ** 2):
            variables.append((startXi, startXj))
            startXi, startXj = self.get_next_location(startXi, startXj)

        return variables

    def count_colors(self, landscape=None):
        #Counts the color of given landscpae. If no landscape is given counts the colors of current attribute of the class instance

        color_dict = {'1': 0, '2': 0, '3': 0, '4': 0}

        if landscape is None:
            landscape = self.bushes

        for i in range(self.land_size):
            for j in range(self.land_size):
                if landscape[i][j] != 0:
                    color_dict[str(landscape[i][j])] += 1

        return color_dict

    def check_distance(self, colors):
        #Checks color distance between given colors and target
        diff_dict = {'1': 0, '2': 0, '3': 0, '4': 0}

        for key, val in self.targets.items():
            diff_dict[key] = colors[key] - val

        return diff_dict

    def has_reached_target(self):
        #Checks whether the current state of the landscape instance has reached the target.
        if all(self.current[key] == self.targets[key] for key, val in self.current.items()):
            return True
        else:
            return False

    def create_copy(self):
        #Creates copy of the given list of lists.
        cp = [[0] * self.land_size for _ in range(self.land_size)]

        for i in range(self.land_size):
            for j in range(self.land_size):
                cp[i][j] = self.bushes[i][j]

        return cp

    def can_put_tile(self, tile, startXi, startXj):
        #Considering the color constraints, checks whether given tile can be put on the given coordinates.

        possible = self.put_tile(tile, startXi, startXj)
        colors = self.count_colors(possible)

        for key, _ in colors.items():
            if colors[key] < self.targets[key]:
                return False

        return True

    def get_next_location(self, startXi, startXj):
        #Considering the land size, calculates the next location to put the tile by incrementing the previous coordinates with tile size

        if startXi + tile_dimension < self.land_size:
            startXi += tile_dimension
        else:
            startXi = 0

            if startXj + tile_dimension < self.land_size:
                startXj += tile_dimension
        return startXi, startXj

    def print_output(self):
        #Prints the solution map as the output
        res = '# Tiles:\n'
        for i, (key, val) in enumerate(self.solution_map.items()):
            res += f'{i} {tile_dimension} {val}\n'
        return res

    def __str__(self) -> str:
        #Str function to print the landscape instance in readable format
        formatting = "\n***************************************\n"
        for i in range(self.land_size):
            for j in range(self.land_size):
                if self.bushes[i][j] > 0:
                    formatting += str(self.bushes[i][j]) + " "
                else:
                    formatting += ' ' + " "
            formatting += "\n"

        return formatting


def backtracking(landscape, startXi, startXj):
    #Recursive backtracking algorithm to solve the problem.

    if landscape.has_reached_target():
        return True

    for tile in landscape.tiles:
        if tile.count == 0:
            continue

        copied = landscape.create_copy()

        if landscape.can_put_tile(tile, startXi, startXj):
            tile.count -= 1
            landscape.bushes = landscape.put_tile(tile, startXi, startXj)
            landscape.current = landscape.count_colors(landscape.bushes)
            landscape.solution_map[f'X{startXi}Y{startXj}'] = tile.type

            prevXj, prevXi = startXj, startXi
            startXi, startXj = landscape.get_next_location(startXi, startXj)

            if backtracking(landscape, startXi, startXj):
                return True

            startXi, startXj = prevXi, prevXj
            landscape.bushes = copied
            landscape.current = landscape.count_colors(landscape.bushes)
            tile.count += 1

    return False


def tile_count(tile1, tile2):
    #Checks whether there is enough tile to use for the current operation
    if tile1.count - 1 < 0 or tile2.count - 1 < 0:
        return False
    else:
        return True


def bush_count(landscape, subland1, subland2, tile1, tile2):
    #Checks whether the tiles can be put to the landscape at the same time vithout violating the final color limitation
    variables = landscape.get_variables()
    return landscape.can_put_tile(tile1, variables[subland1]) and landscape.can_put_tile(tile2, variables[subland2])


# List of constraints
constraints = [tile_count, bush_count]
# Total count of tiles (land_size/ tile_dimension ^2)
# Total final count of colors (example: {‘1’: 21, ‘2’: 25, ‘3’: 22, ‘4’:22}

def revise(landscape, subland1, subland2):
    #Make variable `subland1` arc consistent with variable `subland2`. Sublandscape is a 4x4 sized divisions of the landscape
    variables = landscape.get_variables()
    domains = [landscape.tiles for _ in variables]
    revised = False

    # Get x and y domains
    Xi_domain = domains[subland1]
    Xj_domain = domains[subland2]

    for Xi_tile in Xi_domain:
        satisfies = False
        for Xj_tile in Xj_domain:
            for constraint in constraints:
                if constraint(Xi_tile, Xj_tile):
                    satisfies = True
                else:
                    satisfies = False

        if not satisfies:
            Xi_domain.remove(Xi_tile)
            revised = True

    return revised


def AC3_algorithm(arcs):
    #Update `domains` such that each variable is arc consistent.S
    # Add all the arcs to a queue.
    queue = arcs[:]

    while queue:
        # Take the first arc off the queue (dequeue)
        (Xi, Xj) = queue.pop(0)

        # Make Xi arc consistent with Xj
        revised = revise(Xi, Xj)

        if revised:
            # Add all arcs of the form (Xk, Xi) to the queue (enqueue)
            neighbors = [neighbor for neighbor in arcs if neighbor[1] == Xi]
            queue = queue + neighbors


def main():
    input_name = 'tilesproblem_1327003789161000.txt'
    file = os.path.join('inputs', input_name)
    tile_input = Tile_input_fun(file)
    landscape = Landscape_funs(tile_input)

    print("Input Landscape:")
    print(landscape)
    print("Target Colors:")
    print(landscape.targets)

    start_time = time.time()
    backtracking(landscape, 0, 0)
    print("Solved Landscape:")
    print(landscape)
    print("Colors after solving:")
    print(landscape.count_colors(landscape.bushes))
    print("Output:")
    print(landscape.print_output())
    print("Execution Time: %.6f seconds" % (time.time() - start_time))


if __name__ == "__main__":
    main()
