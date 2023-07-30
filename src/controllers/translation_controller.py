import generator.translation_generator as tr_gen


class translation_controller:
    """
    Class that regulates access to the translation generator object
    and provides translation services
    """
    _translation_gen: tr_gen.translation_generator = None

    def __init__(self) -> None:
        """
        Initialize translation controller and generate dictionaries
        """
        self._translation_gen = tr_gen.translation_generator()
        print("[Translation Controller] - Successfully initialized!")

    def get_detector_id(self, index: int) -> str:
        """Get SUMO-Id of detector at index"""
        return self._translation_gen.get_index_to_detector()[index]

    def get_index(self, detector_id: str) -> int:
        """Get index of SUMO detector"""
        return self._translation_gen.get_detector_to_index()[detector_id]

    def get_order(self) -> list[str]:
        """
        Get processing order, when iterating over all detectors
        using this order/list is recommended as it represents the internal
        order of detectors and excludes detectors created by traffic light systems
        """
        return self._translation_gen.get_order_of_detectors()
