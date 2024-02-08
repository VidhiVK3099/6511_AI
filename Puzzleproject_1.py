import heapq

# Define the goal state for the puzzle
def goal_state(n):
    return tuple(range(n*n))

# Define the possible moves for the blank space
def known_directions(n, position):
    total_moves = []
    row, col = position // n, position % n
    if row > 0:
        total_moves.append(-n)  # Move up
    if row < n - 1:
        total_moves.append(n)   # Move down
    if col > 0:
        total_moves.append(-1)  # Move left
    if col < n - 1:
        total_moves.append(1)   # Move right
    return total_moves

# Defined the heuristic function (Manhattan distance)
def Manhattan_diatance(n, state):
    hn = 0
    for val in range(n*n):
        if state[val] != 0:
            goal_row, goal_col = state[val] // n, state[val] % n
            current_row, current_col = val // n, val % n
            hn += abs(goal_row - current_row) + abs(goal_col - current_col)
    return hn

# Define the A* search algorithm
def aStar_Search(n, initial_state):
    open_set = [(Manhattan_diatance(n, initial_state), 0, initial_state.index(0), initial_state)]
    heapq.heapify(open_set)
    visited = set()

    while open_set:
        _, gn, _, state = heapq.heappop(open_set)
        if state == goal_state(n):
            return gn

        if state not in visited:
            visited.add(state)
            blank_index = state.index(0)
            for move in known_directions(n, blank_index):
                new_state = list(state)
                new_blank_index = blank_index + move
                new_state[blank_index], new_state[new_blank_index] = new_state[new_blank_index], new_state[blank_index]
                new_state = tuple(new_state)
                if new_state not in visited:
                    heapq.heappush(open_set, (gn + 1 + Manhattan_diatance(n, new_state), gn + 1, new_blank_index, new_state))
    return -1

# Main function prints f(n) = g(n)+ h(n) along with the start state and goal state.
def main():
    # Read the puzzle configuration from the file (file_name.txt)
    file_name = input("Enter the filename containing the start state of the puzzle:")
    try:
        with open(file_name, 'r') as file:
            lines = file.readlines()

    # Process the puzzle configuration
        n = len(lines)
        initial_state = tuple(int(num) for line in lines for num in line.split())

    # Check if the puzzle configurations are within the constraints
        if n < 3 or n > 25:
            print("Invalid puzzle size. Size should be between 3 and 25.")
            return
        if len(initial_state) != n*n or sorted(initial_state) != list(range(n*n)):
            print("Invalid puzzle configuration.")
            return

    # prints the start state
        print("Start State:")
        for i_num in range(0, len(initial_state), n):
            print('\t'.join(map(str, initial_state[i_num:i_num+n])))

    # Solves the puzzle using A* search algorithm
        moves = aStar_Search(n, initial_state)

    # prints total number of moves and Final state
        if moves == -1:
            print("No solution found.")
        else:
            print("Number of moves required to solve the puzzle: f(n)= g(n)+h(n)= ", moves)
        print("goal state:")
        goal = goal_state(n)
        for f_num in range(0, n*n, n):
            print('\t'.join(map(str, goal[f_num:f_num+n])))
    except FileNotFoundError:
        print("file not found.")

if __name__ == "__main__":
    main()
