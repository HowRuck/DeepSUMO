from simulation.modules.sim_module import simulation_module
from manager.data_manager import data_manager
from matplotlib import pyplot as plt
import traci


class road_visualization_module(simulation_module):
    """
    Module that continuously prints information about a specific road/detector.
    """
    original_id = ""

    def __init__(self, road_id: str, trigger_step: int) -> None:
        """ Initialize module.
        :param road_id: ID of desired road (SUMO-ID)
        :param trigger_step: trigger step
        """
        super().__init__(trigger_step)
        self.original_id = road_id

    def process_sim_update(self, manager: data_manager):
        """ Process update of module.
        :param manager: data manager of DeepSUMO
        """
        self.plot(manager)
        return

    def plot(self, data_manager: data_manager):
        """ Plot speed data of detector.
        :param data_manager:
        :return:
        """
        graphs = int(data_manager._settings["total_graphs"])

        translation_controller = data_manager.translation
        lane_id = traci.inductionloop.getLaneID(self.original_id)
        edge = data_manager.net.getLane(lane_id).getEdge()

        print("Plotting (probably only a section of)", edge.getName())
        print("net.xml ID:", self.original_id)
        print("torch ID:", translation_controller.get_index(self.original_id))

        features_speed = data_manager.numpy.get_speed_node_features()
        features_vehicles = data_manager.numpy.get_vehicle_number_features()
        features_occupancy = data_manager.numpy.get_occupancy_features()

        sequence_speed = []
        sequence_vehicles = []
        sequence_occupancy = []
        for i in range(data_manager.get_current_processing_step()):
            sequence_speed.append(features_speed[i][translation_controller.get_index(self.original_id)] * 3.6)
            sequence_vehicles.append(features_vehicles[i][translation_controller.get_index(self.original_id)])
            sequence_occupancy.append(features_occupancy[i][translation_controller.get_index(self.original_id)])
        size, _ = features_speed.shape

        print("Plotting ")
        x = range(0, size)
        plt.plot(x, sequence_speed)
        plt.xlabel("step")
        plt.ylabel("speed")
        plt.title(str(edge.getName()) + " [" + str(self.original_id) + "]")
        plt.show()
