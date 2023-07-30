from simulation.modules.sim_module import simulation_module
from manager.data_manager import data_manager
import time
import libsumo


class progress_module(simulation_module):
    """
    Module that prints information and metrics about the
    current progress of the simulation.
    """
    original_id = ""
    step_size = 604800 / 100
    curr_percentage_step = 1

    past_times: list[float] = []
    last_time: float = 0

    def __init__(self, interval: int) -> None:
        """ Initialize the module
        :param interval: threshold value, this should be "sim_length // 100"
        """
        super().__init__(interval)

    def process_sim_update(self, manager: data_manager):
        """ Process module update
        :param manager: data manager of DeepSUMO
        """
        # calculate how long it took to simulate the last "interval"
        curr_time = time.time()
        if self.last_time != 0:
            # add time to list
            self.past_times.append(curr_time - self.last_time)

            # calculate average time of simulating one interval
            avg_time = 0
            for i_time in self.past_times:
                avg_time += i_time
            avg_time = avg_time / len(self.past_times)

            # print metrics
            print("-----", self.curr_percentage_step, "% -----")
            print("sim_step:", libsumo.simulation.getTime())
            print("last_sim_time:", round((curr_time - self.last_time), 2), "seconds")
            print("scale:", libsumo.simulation.getScale())
            print("ETA:", round(((avg_time * (100 - self.curr_percentage_step)) / 60), 2), "minutes")
        # update internal variables
        self.curr_percentage_step += 1
        self.last_time = curr_time
