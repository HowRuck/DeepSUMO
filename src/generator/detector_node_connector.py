import utils.mathstuff as ma
import numpy as np
import libsumo
import sumolib
import controllers.translation_controller as tr


class detector_connector_strategy:
    """
    Base class for all connector strategies. Each strategy has to inherit this class.
    """
    threshold = 0

    def __init__(self, threshold: int) -> None:
        """
        Initialize base connector

        :param threshold: threshold for cost value, all edges with a cost
        below the threshold will not be present in the binary adjacency matrix
        """
        self.threshold = threshold

    def get_cost(self, detector_a_id: str, detector_b_id: str,
                 net: sumolib.net.Net) -> float:
        """
        Get cost between two detectors

        :param detector_a_id: source detector
        :param detector_b_id: target detector
        :param net: sumolib net object
        :return: cost between both detectors as float
        """
        return -1


class dijkstra_connector_strategy(detector_connector_strategy):
    """
    Class that implements the connection strategy of connecting
    two nodes via their shortest path
    """
    def get_cost(self, detector_a_id: str, detector_b_id: str,
                 net: sumolib.net.Net) -> float:
        """
        Get cost between to detectors by their minimum
        travel time calculated using Dijkstra

        :param detector_a_id: source detector
        :param detector_b_id: target detector
        :param net: sumolib net object
        :return: cost between both detectors as float
        """
        edge_a = net.getLane(libsumo.inductionloop
                             .getLaneID(detector_a_id)).getEdge()
        edge_b = net.getLane(libsumo.inductionloop
                             .getLaneID(detector_b_id)).getEdge()

        # get dijkstra result between both edges
        _, dijkstra_cost = net.getFastestPath(edge_a, edge_b)
        # adjust result according to eq. 3
        dijkstra_cost_adjusted = dijkstra_cost - \
            libsumo.inductionloop.getPosition(detector_a_id) / edge_a.getSpeed() - \
                 (edge_b.getLength() -
                   libsumo.inductionloop.getPosition(detector_b_id)) / edge_b.getSpeed()

        return dijkstra_cost_adjusted


class distance_connector_strategy(detector_connector_strategy):
    """
    Class that implements the connection strategy of connecting
    two nodes using their geographical distance
    """
    def get_cost(self, detector_a_id: str, detector_b_id: str, net: sumolib.net.Net) -> float:
        """
        Get cost between to detectors by their geographical distance

        :param detector_a_id: source detector
        :param detector_b_id: target detector
        :param net: sumolib net object
        :return: cost between both detectors as float
        """
        lane_a = net.getLane(libsumo.inductionloop.getLaneID(detector_a_id))
        lane_b = net.getLane(libsumo.inductionloop.getLaneID(detector_b_id))

        # get individual positions of the detector using eq. 2 and eq. 1
        pos_a = ma.get_position_from_shape(lane_a.getShape(),
                                           libsumo.inductionloop.getPosition(detector_a_id))
        pos_b = ma.get_position_from_shape(lane_b.getShape(),
                                           libsumo.inductionloop.getPosition(detector_b_id))

        # return distance between both positions calculated using eq. 1
        return ma.get_distance_between(pos_a, pos_b)


class node_connector:
    """
    Class that implements the connection of all nodes into a graph.

    It also stores all created graph data in various data structures.
    """
    _strat: detector_connector_strategy = None
    self_loops: bool = False

    _num_edges = 0

    _adj_matrix_cost = None
    _adj_matrix_binary = None

    _edge_list_sumo_ids = None
    _edge_list_index_ids = None

    def __init__(self, strat: detector_connector_strategy, net: sumolib.net.Net,
                 translation: tr.translation_controller) -> None:
        """
        Initialize graphs and fill all data structures with correct data.

        :param strat: desired strategy to use when connecting the nodes
        :param net: sumolib net object
        :param translation: translation controller
        """
        self._strat = strat
        self._construct_adj_matrices(net, translation)
        self._construct_edge_list(translation)

    def set_strat(self, strat: detector_connector_strategy):
        """
        Sets strat of detector graph

        :param strat: new strategy
        :return:
        """
        self._strat = strat

    def update(self, net: sumolib.net.Net, translation: tr.translation_controller):
        """
        Recreates the detector graph including all datastructures

        :param net: sumolib net object
        :param translation: translation controller
        """
        self._construct_adj_matrices(net, translation)
        self._construct_edge_list(translation)

    def _construct_adj_matrices(self, net: sumolib.net.Net,
                                translation: tr.translation_controller):
        """
        Constructs the adjacency matrices

        :param net: sumolib net object
        :param translation: translation controller
        """

        # create/reset variables
        self._adj_matrix_cost = np.zeros((len(translation.get_order()),
                                          len(translation.get_order())))
        self._adj_matrix_binary = np.zeros((len(translation.get_order()),
                                            len(translation.get_order())))

        index_a = 0
        for curr_detector_a in translation.get_order():
            index_b = 0
            for curr_detector_b in translation.get_order():
                # get cost between both detectors
                cost = self._strat.get_cost(curr_detector_a, curr_detector_b, net)
                # add cost to cost adjacency matrix
                self._adj_matrix_cost[
                    translation.get_index(curr_detector_a),
                    translation.get_index(curr_detector_b)] = cost
                # if cost ist bigger than the threshold add it to the binary adjacency matrix
                if cost <= self._strat.threshold:
                    self._adj_matrix_binary[
                        translation.get_index(curr_detector_a),
                        translation.get_index(curr_detector_b)] = 1
                    self._num_edges += 1
                    # remove one if self loops is not enabled
                    if not self.self_loops and curr_detector_a == curr_detector_b:
                        self._adj_matrix_binary[
                            translation.get_index(curr_detector_a),
                            translation.get_index(curr_detector_b)] = 0
                        self._num_edges -= 1

                index_b += 1
            index_a += 1

    def _construct_edge_list(self, translation: tr.translation_controller):
        """
        Construct the edge list of the graph

        :param translation: translation controller
        """
        self._edge_list_sumo_ids = np.zeros(shape=(self._num_edges, 2), dtype=object)
        self._edge_list_index_ids = np.zeros(shape=(self._num_edges, 2), dtype=np.float32)

        cnt = 0
        for a in range(len(self._adj_matrix_binary)):
            for b in range(len(self._adj_matrix_binary)):
                # add all present edges to the edge lists
                if self._adj_matrix_binary[a, b] != 0:
                    self._edge_list_sumo_ids[cnt][0] = translation.get_detector_id(a)
                    self._edge_list_sumo_ids[cnt][1] = translation.get_detector_id(b)

                    self._edge_list_index_ids[cnt][0] = a
                    self._edge_list_index_ids[cnt][1] = b
                    cnt += 1
