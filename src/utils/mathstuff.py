import math
import numpy as np


def get_length_from_shape(shape: list[tuple]) -> float:
    """
    Calculates the length of the shape (of e.g. a lane)
    :param shape: Shape of the line, represented by as a
                series of coordinates as tuples
    :return: the length of the shape
    """
    # initialize the first pair of coordinates as None
    x0 = None
    y0 = None
    total_length = 0

    # iterate of all coordinated included in the shape
    for x1, y1 in shape:
        # skip first coordinate, as two coordinates are
        # needed for length calculation of vector
        if x0 is not None and y0 is not None:
            # calculate length of partial vector like in eq. 1
            dX = x1 - x0
            dY = y1 - y0

            edge_length = math.sqrt(math.pow(dX, 2) + math.pow(dY, 2))
            # add length to total length
            total_length += edge_length
        # move to next vector
        x0 = x1
        y0 = y1

    return total_length


def get_position_from_shape(shape: list[tuple], distance: int) -> tuple[float, float]:
    """
    Calculates the position of a detector as coordinates using the positional
    attribute of the detector and the shape of its corresponding lane

    This calculation is done according to eq. 2

    :param shape: shape of the lane on which the detector is placed
    :param distance: position attribute of the detector
    :return: position of detector as coordinates represented by a tuple
    """

    # initialize the first pair of coordinates as None
    x0: float = None
    y0: float = None
    total_length = 0

    # calculate position of each new loop based on is "position" and lane shape
    cnt = 0
    # iterate of all coordinated included in the shape
    for x1, y1 in shape:
        # skip first coordinate, as two coordinates are
        # needed for length calculation of the first vector
        if x0 is not None and y0 is not None:
            # calculate the direction vector between both points
            dX = x1 - x0
            dY = y1 - y0

            # calculate length of direction vector and add it to total length
            edge_length = math.sqrt(math.pow(dX, 2) + math.pow(dY, 2))
            total_length += edge_length
            # check if the detector has been reached
            if total_length >= distance:
                # calculate position of detector
                # (refer to eq. 2 for mir information)
                remaining_distance = edge_length - (total_length - distance)
                t = remaining_distance / edge_length

                target_x = (1 - t) * x0 + t * x1
                target_y = (1 - t) * y0 + t * y1

                # exit loop if position is found
                break
            cnt += 1
        # move to next vector
        x0 = x1
        y0 = y1

    return target_x, target_y


def get_distance_between(p1: tuple, p2: tuple):
    """
    Calculates the distance between two points (eq. 1)
    :param p1: source point
    :param p2: target point
    :return: the distance between p1 and p2
    """
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]

    return abs(math.sqrt(math.pow(dx, 2) + math.pow(dy, 2)))
