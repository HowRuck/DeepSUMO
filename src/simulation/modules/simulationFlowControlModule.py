from simulation.modules.sim_module import simulation_module
from manager.data_manager import data_manager
import random
from datetime import datetime, timedelta
import libsumo


class simulationFlowControlModule(simulation_module):
    """
    Class representing a module that has the ability to adjust the simulations traffic density
    by modifying the "scale" value of the simulation according to preset rules.
    """

    _curr_week_day: int = 0  # Monday = 0, Tuesday = 1 [...] Sunday = 6
    _curr_hour: int = 0  # 0 - 23
    _last_sim_step: int = 0
    _default_flow: float = 0.8
    _last_hour = 294719457

    _start: datetime = datetime(2023, 3, 20, 0)

    # rules for traffic scale values
    # (from [week_day, hour], to [week_day, hour]) => [min flow, max flow]
    flow_laws: dict[tuple[tuple[int, int], tuple[int, int]], tuple[float, float]] = {
        # Monday
        ((0, 6), (0, 9)): (2.5, 3.0),
        ((0, 9), (0, 16)): (1.8, 2.0),
        ((0, 16), (0, 18)): (2.5, 3.0),
        ((0, 18), (0, 21)): (1.1, 1.4),
        ((0, 1), (1, 6)): (0.1, 0.2),
        # Tuesday
        ((1, 6), (1, 9)): (2.5, 3.0),
        ((1, 9), (1, 16)): (1.4, 1.8),
        ((1, 16), (1, 18)): (2.5, 3.0),
        ((1, 18), (1, 21)): (1.1, 1.4),
        ((1, 21), (2, 6)): (0.1, 0.2),
        # Wednesday
        ((2, 6), (2, 9)): (2.5, 3.0),
        ((2, 9), (2, 16)): (1.4, 1.8),
        ((2, 16), (2, 18)): (2.5, 3.0),
        ((2, 18), (2, 21)): (1.1, 1.4),
        ((2, 21), (3, 6)): (0.1, 0.2),
        # Thursday
        ((3, 6), (3, 9)): (2.5, 3.0),
        ((3, 9), (3, 16)): (1.4, 1.8),
        ((3, 16), (3, 18)): (2.5, 3.0),
        ((3, 18), (3, 21)): (1.1, 1.4),
        ((3, 21), (4, 6)): (0.1, 0.2),
        # Friday
        ((4, 6), (4, 9)): (2.5, 3.0),
        ((4, 9), (4, 16)): (1.4, 1.8),
        ((4, 16), (4, 18)): (2.5, 3.0),
        ((4, 18), (4, 21)): (1.1, 1.4),
        ((4, 21), (5, 10)): (0.1, 0.2),
        # Saturday
        ((5, 10), (5, 13)): (0.7, 0.9),
        ((5, 13), (5, 16)): (1.1, 1.4),
        ((5, 16), (5, 20)): (0.7, 0.9),
        ((5, 20), (5, 22)): (0.4, 0.5),
        ((5, 22), (5, 23)): (0.6, 0.7),
        ((5, 23), (6, 12)): (0.1, 0.3),
        # Sunday
        ((6, 12), (6, 18)): (0.4, 0.7),
        ((6, 18), (6, 22)): (0.5, 0.8),
        ((6, 22), (0, 6)): (0.1, 0.2)
    }

    start_month = 0
    start_year = 2000
    start_minute = 0

    def __init__(self, trigger: int) -> None:
        """ Initialize the module.
        :param trigger: trigger step/frequency
        """
        super().__init__(trigger)
        print(self._start.weekday())

    def process_sim_update(self, manager: data_manager):
        """ Process update of module by adjusting the scale of the simulation based on
        the "current" time and weekday
        :param manager: data manager of DeppSUMO
        """
        sec = int(libsumo.simulation.getTime())
        curr = self._start + timedelta(seconds=sec)

        def in_between(interval: tuple[tuple[int, int], tuple[int, int]], curr: tuple[int, int]):
            """ check if a tuple of <weekday, hour> is chronologically in between two other tuples
            e.g. (1, 12) is in between (1, 10) and (3, 10) but not in between (0, 12) and (1, 10)
            :param interval: tuple consisting of <start interval, stop interval>
            :param curr: target interval
            :return: true or false
            """
            total_hours_start = interval[0][0] * 24 + interval[0][1]
            total_hours_end = interval[1][0] * 24 + interval[1][1]
            total_hours_target = curr[0] * 24 + curr[1]

            if total_hours_end < total_hours_start:
                total_hours_end += 7 * 24
                if total_hours_target < total_hours_start:
                    total_hours_target += 7 * 24

            if total_hours_start <= total_hours_target <= total_hours_end:
                return True
            else:
                return False

        target = (curr.weekday(), curr.hour)
        # initialize variable to store flow interval with default value of 1.0
        new_flow: tuple[float, float] = (1.0, 1.0)

        # check all intervals and set scale value according to matching interval
        for curr_interval in self.flow_laws.keys():
            if in_between(curr_interval, target):
                random_min, random_max = self.flow_laws[curr_interval]
                new_flow = self.flow_laws[curr_interval]
                new_scale = random.uniform(random_min, random_max)
                libsumo.simulation.setScale(new_scale)
                break

        # print visualisation output
        if curr.hour != self._curr_hour:
            print("-----DONG, DONG, DONG-----")
            print("Passed one hour!")
            print("Day:", curr.weekday(), "Hour:", curr.hour)
            print("Flow between", new_flow[0], "and", new_flow[1])
            self._curr_hour = curr.hour
