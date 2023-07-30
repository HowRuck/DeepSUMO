from simulation.modules.sim_module import simulation_module
from manager.data_manager import data_manager


class print_model(simulation_module):
    """
    Module that prints stuff.
    """
    original_id = ""
    step_size = 604800 / 100
    curr_percentage_step = 1

    past_times: list[float] = []
    last_time: float = 0

    def __init__(self, road_id: str, interval: int) -> None:
        """
        Initialize module.
        :param road_id: desired road id
        :param interval: update interval value
        """
        super().__init__(interval)
        self.original_id = road_id

    def process_sim_update(self, manager: data_manager):
        """ Process module update
        :param manager: data manager of DeepSUMO
        """
        int_id = manager.translation.get_index(self.original_id)
        features = manager.numpy.get_speed_node_features()
        sequence = []
        for i in range(manager.get_current_processing_step()):
            sequence.append(features[i][int_id] * 3.6)