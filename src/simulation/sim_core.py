from manager.data_manager import data_manager
from generator.detector_node_connector import detector_connector_strategy
from simulation.modules.sim_module import simulation_module
import traci


class simulation_core:
    """
    Initializes the simulation core object and basically all of DeepSUMO.
    During initialization the simulation is started using the parameters set up in the setting object.
    If more parameters are needed, they can be passed as an array using the "launch_arguments" parameter and are then
    added to the SUMO start command.
    """
    _sumoCmd = ""

    _settings = None
    _data: data_manager = None

    _curr_sim_step = 0
    _curr_processing_step = 0

    _processing_observers = []
    _post_observers = []

    def __init__(self, settings: dict, strategy: detector_connector_strategy,
                 launch_arguments: list[str] = None) -> None:
        # copy settings
        self._settings = settings

        # assemble SUMO start command
        self._sumoCmd = [self._settings["sumo_exec_path"], "-c", self._settings["sumo_config_path"], "--no-warnings",
                         "true"]
        if launch_arguments is not None:
            for arg in launch_arguments:
                self._sumoCmd.append(arg)

        # start SUMO and initialize data manager
        traci.start(self._sumoCmd)
        self._data = data_manager(settings, strategy)

    def start_simulation(self):
        """ Start the main simulation loop of DeepSUMO """
        self._curr_sim_step = 0

        while self._curr_sim_step < int(self._settings["sim_length"]):
            self._go_simulation_step()

        # apply moving average to denoise data
        self._data.numpy.apply_moving_average()

        # process all post observers
        for observer in self._post_observers:
            observer.process_sim_update(self._data)

    def stop_simulation(self):
        """ Stop the simulation and close TraCi connection"""
        traci.close()

    def _go_simulation_step(self):
        """ Perform one simulation step including all aspects
        of DeepSUMO (data collection, modules etc.)
        """

        # go SUMO simulation step
        traci.simulationStep()

        # check if data should be collected, and collect data if needed
        if (self._curr_sim_step % int(self._settings["interval_length"]) == 0 and
                self._curr_sim_step != 0):
            self._data.numpy.process_next_interval()
            self._curr_processing_step += 1
            self._data.add_processing_step()

        # call all modules update functions if configured
        for observer in self._processing_observers:
            if (self._curr_sim_step != 0 and
                    self._curr_sim_step % observer.get_trigger_step() == 0):
                observer.process_sim_update(self._data)

        self._curr_sim_step += 1

    def add_post_observer(self, observer: simulation_module):
        """Add a post observer to run directly after the simulation finishes"""
        self._post_observers.append(observer)

    def add_continuous_observer(self, observer: simulation_module):
        """ Add a continuous observer to run at set intervals while the simulation is running."""
        self._processing_observers.append(observer)

    def add_connector_strat(self, strat: detector_connector_strategy):
        """Change the connector strategy"""
        self._data.add_connector_start(strat)

    def get_data(self) -> data_manager:
        """Get the data object"""
        return self._data
