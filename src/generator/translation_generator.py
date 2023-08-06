import traci


class translation_generator:
    """
    Class responsible for the generation and processing of the necessary
    data structures for the translation layer of DeepSUMO

    This is an internal class and should not be used. Please
    use the translation_controller instead.
    """
    _detector_to_index_buffer: dict[str, int] = None
    _index_to_detector_buffer: dict[int, str] = None

    _order: list[str] = []

    def __init__(self) -> None:
        """
        Initialize generator by creating initial dicts
        """
        self._generate_dicts()

    def _generate_dicts(self) -> None:
        """
        Generate dictionaries and order used for translation
        """
        print("[Translation Generator] - Generating dictionaries...")
        # create variables
        self._order = []
        self._detector_to_index_buffer = dict()
        self._index_to_detector_buffer = dict()

        traffic_light_ids = traci.trafficlight.getIDList()

        curr_index: int = 0
        for detector_id in traci.inductionloop.getIDList():
            # filter out detectors created by traffic light systems
            # as they do not actively collect data
            if not any(t in detector_id for t in traffic_light_ids):
                self._detector_to_index_buffer[detector_id] = curr_index
                self._index_to_detector_buffer[curr_index] = detector_id

                self._order.append(detector_id)
                curr_index += 1

    def get_detector_to_index(self) -> dict[str, int]:
        """Get detector to index dictionary"""
        return self._detector_to_index_buffer

    def get_index_to_detector(self) -> dict[int, str]:
        """Get index to detector dictionary"""
        return self._index_to_detector_buffer

    def get_order_of_detectors(self) -> list[str]:
        """Get processing order of detectors"""
        return self._order
