from controllers.numpy_graph_controller import numpy_graph_controller
from controllers.translation_controller import translation_controller
from controllers.detector_graph_controller import detector_graph_controller
from generator.detector_node_connector import node_connector, detector_connector_strategy
import sumolib


class data_manager:
    _settings: dict = None

    _curr_processing_step = 0

    net: sumolib.net.Net = None
    detector_graph: detector_graph_controller = None
    translation: translation_controller = None
    numpy: numpy_graph_controller = None

    def __init__(self, settings: dict, strat: detector_connector_strategy) -> None:
        """
        Initialize data manager and all underlying components such as
        the detector graph, translation and numpy graph
        :param settings: settings object of DeepSUMO
        :param strat: desired strategy for connecting the detectors
        """
        self._settings = settings
        # create a net object from net.xml file
        self.net = sumolib.net.readNet(settings["sumo_net_path"])

        # initialize other components
        self.translation = translation_controller()
        self.detector_graph = \
            detector_graph_controller(strat, self.net, settings, self.translation)
        self.numpy = numpy_graph_controller(self._settings["total_graphs"],
                                            self.detector_graph.get_detector_graph(),
                                            self.translation,
                                            self.detector_graph.gen_ref_speeds())

    def add_connector_start(self, strat: detector_connector_strategy):
        """
        Change the connector strategy
        :param strat: desired strategy
        """
        self.detector_graph.set_strat(strat)

    def get_current_processing_step(self):
        """
        Get the current processing step
        :return: current processing step
        """
        return self._curr_processing_step

    def add_processing_step(self):
        """ Add one two the current processing step

        This method is internal and should not be called by the user.
        """
        self._curr_processing_step += 1
