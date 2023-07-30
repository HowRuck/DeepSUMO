import libsumo
import networkx as nx
from controllers.translation_controller import translation_controller
from store.numpy_graph_store import numpy_graph_store


class numpy_graph_controller:
    """
    Class that provides and regulated access to the numpy_graph_store object.
    This is the primary interface for retrieving data from DeepSUMO's store
    """
    _numpy_store = None
    _processing_order: list[str] = []
    _reference_speeds: dict[str, float]

    def __init__(self, total_graphs: int, graph: nx.DiGraph,
                 translation: translation_controller, ref_speeds) -> None:
        """
        Initialize controller and create numpy store object
        """
        self._numpy_store = numpy_graph_store(total_graphs, graph, translation)
        self._reference_speeds = ref_speeds
        self._processing_order = translation.get_order()
        print("[Numpy Graph Controller] - Initialized!")

    def process_next_interval(self):
        """
        Collect data from SUMO using TraCi and add them to the store.
        This is an internal method and should NOT be used by the user.
        """
        feature_list = []
        cnt = 0
        # iterate over all detectors
        for detector_id in self._processing_order:
            tmp = []
            # collect speed from SUMO
            speed = libsumo.inductionloop.getLastIntervalMeanSpeed(detector_id)
            # if no speed was recorded (= no car passed the detector)
            # use the speed limit
            if speed == -1.0:
                speed = self._reference_speeds[detector_id]
                tmp.append(speed)
            else:
                vehicle_mean_speed = libsumo.inductionloop\
                    .getLastIntervalMeanSpeed(detector_id)
                ref_speed = self._reference_speeds[detector_id]
                # adjust occupancy value according to eq. 4
                vehicle_occupancy = libsumo.inductionloop\
                    .getLastIntervalOccupancy(detector_id) / \
                    libsumo.inductionloop.getLastIntervalVehicleNumber(detector_id)
                if vehicle_occupancy >= 1.0:
                    vehicle_occupancy = 1.0
                # calculate final speed according to eq. 5
                final_speed = vehicle_occupancy * vehicle_mean_speed + \
                              (1.0 - vehicle_occupancy) * ref_speed

                tmp.append(final_speed)

            # collect and append other node features
            tmp.append(libsumo.inductionloop.getLastIntervalOccupancy(detector_id))
            tmp.append(libsumo.inductionloop.getLastIntervalVehicleNumber(detector_id))

            feature_list.append(tmp)
            cnt += 1

        # add new features to the store
        self._numpy_store.add_new_node_features(feature_list)

    def apply_moving_average(self):
        """ Apply moving average to currently stored data"""
        self._numpy_store.apply_moving_average()

    def get_edge_index(self):
        """ Get edge index"""
        return self._numpy_store.get_edge_index()

    def get_speed_node_features(self):
        """ Get speed node features up to the current timestep"""
        return self._numpy_store.get_speed_features()

    def get_occupancy_features(self):
        """ Get occupancy node features up to the current timestep"""
        return self._numpy_store.get_occupancy_features()

    def get_vehicle_number_features(self):
        """ Get speed vehicle number features up to the current timestep"""
        return self._numpy_store.get_vehicle_number_features()
