from generator.detector_node_connector import detector_connector_strategy, node_connector
import networkx as nx
import sumolib
import numpy as np
from controllers.translation_controller import translation_controller
import traci


class detector_graph_controller:
    """
    Class responsible for regulating access to the graph object of the framework.

    This class provides services all around the detector graph created by DeepSUMO
    """
    _connector: node_connector = None
    _detector_graph: nx.DiGraph = None

    _net: sumolib.net.Net = None

    def __init__(self, strat: detector_connector_strategy, net: sumolib.net.Net,
                 settings: dict, translation: translation_controller) -> None:
        """
        Initialize graph controller and create associated graphs
        :param strat: desired strategy to use for connecting nodes
        :param net: sumolib net object
        :param settings: DeepSUMO's settings object
        :param translation: Translation controller for translation services
        """
        print("[Detector Graph Controller] - Generating graph, "
              "this can take a while...")
        self._graph_nodes = translation.get_order()
        self._net = net
        self._detector_graph = nx.DiGraph()
        self._connector = node_connector(strat, net, translation)

        self._setup_nodes(settings)
        self._setup_edges()

        print("[Detector Graph Controller] - Graph complete! Nodes:",
              self._detector_graph.number_of_nodes(),
              "Edges:", self._detector_graph.number_of_edges())

    def gen_ref_speeds(self) -> dict[str, float]:
        """
        Function that generated a dictionaries containing all
        detectors (SUMO ID's) and the speed limit of the street they are on.
        :return: A dictionary structured as <SUMO-ID, speed limit>
        """
        ref_speeds: dict[str, float] = {}
        for node in self._detector_graph:
            lane_id = traci.inductionloop.getLaneID(node)
            ref_speed = self._net.getLane(lane_id).getSpeed()
            ref_speeds[node] = ref_speed

        return ref_speeds

    def get_detector_graph(self) -> nx.DiGraph:
        """ Get the detector graph as a NetworkX DiGraph.

        The ids used in this graph are the SUMO-ID's
        :return: detector graph
        """
        return self._detector_graph

    def get_cost_adj_matrix(self):
        """ Get the adjacency matrix of the graph containing all
        detectors-pairs and their cost values
        :return: the adjacency matrix of size (num_detectors, num_detectors)
        containing the cost values
        """
        return self._connector._adj_matrix_cost

    def get_binary_adj_matrix(self):
        """ Get the binary adjacency matrix of the graph
        with 1 if cost > threshold, otherwise 0
        :return: the binary adjacency matrix
        of size (num_detectors, num_detectors)
        """
        return self._connector._adj_matrix_binary

    def get_edge_list_by_index(self):
        """ Get edge-list of graph containing indices
        :return: edge-list containing indices
        """
        return self._connector._edge_list_index_ids

    def get_edge_list_by_sumo_id(self):
        """ Get edge-list of graph containing SUMO-ID's
        :return: edge-list containing SUMO-ID'S
        """
        return self._connector._edge_list_sumo_ids

    def _setup_nodes(self, settings):
        """ Sets up the nodes of the nx.DiGraph
        :param settings: settings object of DeepSUMO
        """
        for detector_id in self._graph_nodes:
            self._detector_graph.add_node(detector_id)

    def set_strat(self, strat: detector_connector_strategy):
        """ Set strategy of graph. This will not trigger a recalculation of
        the whole graph.

        To recalculate the graph call the update_graph function.
        :param strat: desired strategy
        """
        self._connector.set_strat(strat)
        self._setup_edges()

    def update_graph(self, net: sumolib.net.Net,
                     translation: translation_controller):
        """
        Update the graph.
        :param net: sumolib net object
        :param translation: translation controller
        :return:
        """
        self._connector.update(net, translation)

    def _setup_edges(self):
        """Setup edges of the nx.DiGraph
        """
        self._detector_graph.clear_edges()
        tmp_edges: np.array = self._connector._edge_list_sumo_ids

        for edge in tmp_edges:
            self._detector_graph.add_edge(edge[0], edge[1])
