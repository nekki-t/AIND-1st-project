assignments = []

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    # all values whose length is 2
    twin_target = [box for box in values if len(values[box]) == 2]
    twins = search_twins(values, twin_target)
    naking_for_twins(values, twins)

    return values

def search_twins(values, twin_target):
    twins = []
    for org in twin_target:
        for target in twin_target:
            if org != target and values[org] == values[target]:  # twins!
                not_exist = True
                for twin in twins:
                    if org in twin and target in twin:
                        not_exist = False

                if not_exist:
                    twins.append([org, target])
    return twins

def naking_for_twins(values, twins):
    for twin in twins:
        for unit in g_unitlist:
            if twin[0] in unit and twin[1] in unit:
                for item in unit:
                    if item != twin[0] and item != twin[1]:
                        for s in values[twin[0]]:
                            if len(values[item]) > 1:
                                values[item] = values[item].replace(s, '')


def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s+t for s in A for t in B]

# to make grid from given number string
def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    values = []
    all_digits = '123456789'
    for c in grid:
        if c == '.':
            values.append(all_digits)
        elif c in all_digits:
            values.append(c)
    assert len(values) == 81
    return dict(zip(g_boxes, values))

# to show grid in console
def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in g_boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

# eliminate numbers which can not be in a box
def eliminate(values):
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in g_diagonal_peers[box]: # apply for diagonal rule
            values[peer] = values[peer].replace(digit,'')

    display(values)
    return values

# implementation for only_choice
def only_choice(values):
    for unit in g_unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values[dplaces[0]] = digit
    return values


# reduce options by using eliminate, only_choice and naked twin functions
def reduce_puzzle(values):
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values = eliminate(values)
        values = only_choice(values)
        values = naked_twins(values)
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

# search solution by recursive call
def search(values):
    values = reduce_puzzle(values)
    if values is False:
        return False
    if all(len(values[s]) == 1 for s in g_boxes):
        return values

    n,s = min((len(values[s]), s) for s in g_boxes if len(values[s]) > 1)
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt


# Global variables
rows = 'ABCDEFGHI'
cols = '123456789'
g_boxes = cross(rows, cols)
g_row_units = [cross(r, cols) for r in rows]
g_column_units = [cross(rows, c) for c in cols]
g_square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
g_unitlist = g_row_units + g_column_units + g_square_units
g_units = dict((s, [u for u in g_unitlist if s in u]) for s in g_boxes)
g_peers = dict((s, set(sum(g_units[s],[]))-set([s])) for s in g_boxes)
g_diagonal_des = [rows[i] + cols[i] for i in range(len(rows))]
g_diagonal_asc = [rows[i] + cols[len(rows) - i - 1] for i in range(len(rows))]
g_unitlist.append(g_diagonal_des)
g_unitlist.append(g_diagonal_asc)

g_diagonal_peers = g_peers.copy()

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    #prepare peers which include diagonal ones to be passed to elimination function
    for key in g_diagonal_des:
        for dbox in g_diagonal_des:
            if dbox != key and not dbox in g_peers[key]:
                g_diagonal_peers[key].add(dbox)

    for key in g_diagonal_asc:
        for dbox in g_diagonal_asc:
            if dbox != key and not dbox in g_peers[key]:
                g_diagonal_peers[key].add(dbox)

    values = grid_values(grid)
    return search(values)

if __name__ == '__main__':
    # diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    diag_sudoku_grid = '9.1....8.8.5.7..4.2.4....6...7......5..............83.3..6......9................'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
