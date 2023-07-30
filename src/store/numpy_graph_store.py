import numpy as np
import networkx as nx
from controllers.translation_controller import translation_controller


class numpy_graph_store:
    """
    Class that stores all collected detector data in NumPy arrays.
    This is an internal class and should not be used. Please use the numpy_controller instead.
    """
    _node_features_speed: np.array = None
    _node_features_occupancy: np.array = None
    _node_features_vehicles: np.array = None

    _edge_index: np.array = None

    _curr_graph: int = 0
    _total_graphs: int = 0
    _number_of_nodes: int = 0
    _number_of_edges: int = 0

    def __init__(self, total_graphs: int, graph: nx.DiGraph, translation: translation_controller) -> None:
        """
        Initialize store by creating all necessary arrays filled with zeroes
        """
        self._total_graphs = total_graphs
        self._number_of_nodes = graph.number_of_nodes()
        self._number_of_edges = graph.number_of_edges()

        # generate node feature arrays of size (num_graphs, num_nodes}) each
        self._node_features_speed = np.zeros((
            self._total_graphs,
            self._number_of_nodes
        ), dtype=np.float32)

        self._node_features_occupancy = np.zeros((
            self._total_graphs,
            self._number_of_nodes
        ), dtype=np.float32)

        self._node_features_vehicles = np.zeros((
            self._total_graphs,
            self._number_of_nodes
        ), dtype=np.float32)

        print("[Numpy Graph Store] - Created node features:", self._node_features_speed.shape)
        self._generate_edge_index(graph, translation)
        print("[Numpy Graph Store] - Successfully initialized!")

    def _generate_edge_index(self, graph: nx.DiGraph, translation: translation_controller):
        """
        Generate edge index array using edges from before created graph
        """

        # create variable
        self._edge_index = np.zeros((
            2,
            self._number_of_edges
        ), dtype=int)

        # iterate over edges and add to array
        cnt = 0
        for edge in graph.edges():
            # convert SUMO ids into indices
            self._edge_index[0][cnt] = translation.get_index(edge[0])
            self._edge_index[1][cnt] = translation.get_index(edge[1])
            cnt += 1
        print("[Numpy Graph Store] - Created edge index:", self._edge_index.shape)

    def add_new_node_features(self, new_features: list):
        """
        Add new node features to the store.
        The new features are represented by a list of NumPy arrays of size (num_nodes, 3)
        with each index representing one feature in the order:

        speed, occupancy, vehicles
        """
        curr_node_cnt = 0
        for feature in new_features:
            self._node_features_speed[self._curr_graph][curr_node_cnt] = feature[0]
            self._node_features_occupancy[self._curr_graph][curr_node_cnt] = feature[1]
            self._node_features_vehicles[self._curr_graph][curr_node_cnt] = feature[2]
            curr_node_cnt += 1

        self._curr_graph += 1

    def apply_moving_average(self):
        """
        Applies a moving average to the currently stored speed data
        """

        # create buffer features
        tmp_node_features_speed = np.zeros((
            self._total_graphs,
            self._number_of_nodes
        ), dtype=np.float32)

        for curr_graph in range(self._total_graphs):
            # check if moving average of size 4 can be applied for current timestep
            if 4 <= curr_graph <= (self._total_graphs - 4):
                for curr_detector in range(self._number_of_nodes):
                    # collect and average relevant values
                    average_values = self._node_features_speed \
                        [(curr_graph - 4):(curr_graph + 4), curr_detector]
                    tmp_node_features_speed[curr_graph][curr_detector] = np.mean(average_values)

        self._node_features_speed = tmp_node_features_speed

    def get_speed_features(self) -> np.array:
        """ Get speed node features up to the current timestep"""
        return self._node_features_speed[:self._curr_graph]

    def get_occupancy_features(self):
        """ Get occupancy node features up to the current timestep"""
        return self._node_features_occupancy[:self._curr_graph]

    def get_vehicle_number_features(self):
        """ Get vehicle number node features up to the current timestep"""
        return self._node_features_vehicles[:self._curr_graph]

    def get_edge_index(self) -> np.array:
        """ Get edge index"""
        return self._edge_index
