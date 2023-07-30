import sumolib
import parser.detector as detect1
from utils.mathstuff import get_length_from_shape


class inductive_loop_base:
    """
    Base class for induction loop classes used for XML-Parsing
    """
    id = None
    lane = None
    position_lane = None
    frequency = None
    speed = None
    vehicles = None
    start_timestep = None
    stop_timestep = None
    file = None
    position_absolute = None
    type = None

    creation_attributes_added = False

    def __init__(self) -> None:
        """Initialize an induction loop base object"""
        pass

    def add_xml_attributes(self, id, lane, pos, freq, file, type):
        """
        Add attributes required to create detector with the premise of adding
        it to the additional.xml file

        A detector with only these values present can NOT be used by further
        logic (e.g. detector_loader)
        """
        self.id = id
        self.lane = lane
        self.position_lane = pos
        self.frequency = freq
        self.file = file
        self.type = type

        self.creation_attributes_added = True

    def get_speed(self):
        """ Get speed attribute of induction loop
        :return: speed attribute
        """
        return self.speed

    def get_lane_position(self):
        """ Get lane position attribute of induction loop
        :return: lane position attribute
        """
        return self.position_lane

    def get_timestep(self):
        """ Get timestep attribute of induction loop
        :return: timestep attribute
        """
        return self.start_timestep

    def get_lane(self):
        """ Get lane attribute of induction loop
        :return: lane attribute
        """
        return self.lane

    def get_type(self):
        """ Get type attribute of induction loop
        :return: type attribute
        """
        return self.type

    def get_id(self):
        """ Get id attribute of induction loop
        :return: id attribute
        """
        return self.id

    def to_xml(self) -> str:
        """ Create XML-Definition/Representation of induction loop
        :return: XML line as string
        """
        if not self.creation_attributes_added:
            print("Not all necessary Attributes for XML-Export added!")
            return ""
        else:
            return '<e1Detector id="%s" lane="%s" pos="%s" freq="%s" file="%s"/>' % (
                self.id, self.lane, self.position_lane, self.frequency, self.file)


class e1_inductive_loop(inductive_loop_base):
    """
    Class representing a simple e1 induction loop
    """
    def __init__(self) -> None:
        """ Initialize e1 induction loop"""
        super().__init__()


class detector_xml_generator:
    """
    
    """
    net: sumolib.net.Net
    edges: list[sumolib.net.edge.Edge]
    detectList: list[detect1.inductive_loop_base] = []
    curr_id = 0

    valid_road_types = ["highway.motorway", "highway.trunk",
                        "highway.primary", "highway.secondary", "highway.tertiary",
                        "highway.residential", "highway.motorway_link", "highway.primary_link",
                        "highway.secondary_link", "highway.tertiary_link", "highway.living_street"]

    def __init__(self, net: sumolib.net.Net) -> None:
        self.edges = net.getEdges()

    def generate_list(self) -> list[detect1.inductive_loop_base]:
        for edge in self.edges:
            if any(t in edge.getType() for t in self.valid_road_types):
                lanes = edge.getLanes()
                step_size: int = 50
                for lane in lanes:
                    lane_length = get_length_from_shape(lane.getShape())
                    num_steps = int(lane_length) // step_size
                    num_detectors = 0
                    tmpList: list[detect1.inductive_loop_base] = []

                    for curr_step in range(0, num_steps):
                        curr_detector_pos: float = curr_step * step_size
                        curr_detector = detect1.e1_inductive_loop()
                        curr_detector.add_xml_attributes(id=self.curr_id,
                                                         lane=lane.getID(),
                                                         pos=curr_detector_pos,
                                                         freq=300,
                                                         file="detectors.xml",
                                                         type="e1")
                        tmpList.append(curr_detector)

                    lengt = 0
                    if lane.getLength() >= lane_length:
                        lengt = lane_length
                    else:
                        lengt = lane.getLength()

                    curr_detector = detect1.e1_inductive_loop()
                    curr_detector.add_xml_attributes(id=self.curr_id,
                                                     lane=lane.getID(),
                                                     pos=lengt,
                                                     freq=300,
                                                     file="detectors.xml",
                                                     type="e1")
                    self.detectList.append(curr_detector)
                    self.curr_id += 1
                    curr_detector = detect1.e1_inductive_loop()
                    curr_detector.add_xml_attributes(id=self.curr_id,
                                                     lane=lane.getID(),
                                                     pos=0,
                                                     freq=300,
                                                     file="detectors.xml",
                                                     type="e1")
                    self.detectList.append(curr_detector)
                    self.curr_id += 1
                print("edge:", edge.getID(), "lanes:", len(edge.getLanes()), "length:", edge.getLength(), "detectors:",
                      num_detectors)

        return self.detectList

    def generate_xml(self, path: str):
        self.generate_list()

        file = open(path, "w")
        file.write("<additional>\n")

        for detector in self.detectList:
            file.write("\t" + detector.to_xml() + "\n")

        file.write("</additional>")
        file.close()
