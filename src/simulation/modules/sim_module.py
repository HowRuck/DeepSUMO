from manager.data_manager import data_manager


class simulation_module:
    """
    Base class for all simulation modules.

    This class has to be inherited by all other modules!
    """
    _trigger_step = 0

    def __init__(self, step: int) -> None:
        """
        Initialize the strategy.
        :param step: desired trigger step/frequency
        """
        self._trigger_step = step
        pass

    def get_trigger_step(self) -> int:
        """ Get trigger step of module
        :return: trigger step
        """
        return self._trigger_step

    def process_sim_update(self, manager: data_manager):
        """ Process update of the module. This function is called by the framework to execute the module.
        This method HAS to be inherited by other modules.
        :param manager: data manager object from DeepSUMO
        """
        pass
