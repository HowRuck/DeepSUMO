import torch
from torch_geometric.data import InMemoryDataset, Data
import manager.data_manager as dat_man
import numpy as np
from utils.math_utils import z_score

class adaptive_speed2vec_dataset(InMemoryDataset):
    data_manager: dat_man.data_manager
    creation_step: int
    
    def __init__(self, data_manager: dat_man.data_manager, creation_step: int ,root='', transform=None, pre_transform=None):
        self.data_manager = data_manager
        self.creation_step = creation_step
        super().__init__(root, transform, pre_transform)
        print(self.processed_paths[0])
        self.data, self.slices, self.n_node, self.mean, self.std_dev = torch.load(self.processed_paths[0])
    
    @property
    def raw_file_names(self):
        return ["test"]
    
    @property
    def processed_file_names(self):
        return ["test_data.pt"]
        
    def process(self):
        settings = self.data_manager._settings
        
        
        edge_index = torch.from_numpy(self.data_manager.numpy.get_edge_index())
        edge_index = edge_index.int()
        print(edge_index.shape)
        print(edge_index.dtype)
        
        raw_features = self.data_manager.numpy.get_speed_node_features()
        # only create the dataset for graphs which have valid measurements (!=0)
        # this is done because if the dataset is created before the simmulation is finished
        # possibly a lot ov values will be 0 because they were initialized with 0 but 
        # their timestep was not processed yet
        mean = np.mean(raw_features)
        std_dev = np.std(raw_features)
        raw_features = z_score(raw_features, np.mean(raw_features), np.std(raw_features))
        W = self.data_manager.detector_graph.get_cost_adj_matrix()
        b = self.data_manager.detector_graph.get_binary_adj_matrix()

        _, n_node = raw_features.shape
        edge_attr = torch.zeros((n_node ** 2, 1))
        num_edges = 0

        sequences = []
        for i in range(n_node):
            for j in range(n_node):
                if b[i, j] != 0:
                    edge_attr[num_edges] = W[i, j]
                    num_edges += 1
        edge_attr = edge_attr.resize_(num_edges, 1)


        for i in range(self.creation_step - 40):
            g = Data()
            g.__num_nodes__ = n_node

            g.edge_attr = edge_attr
            g.edge_index = edge_index

            start = i
            end = start + settings["N_HIST"] + settings["N_PRED"]
            full_window = np.swapaxes(raw_features[start:end, :], 0, 1)
            g.x = torch.FloatTensor(full_window[:, 0:settings["N_HIST"]])
            g.y = torch.FloatTensor(full_window[:, settings["N_HIST"]::])

            sequences += [g]
        
        #for s in sequences:
            #print(s)
        
        data, slices = self.collate(sequences)
        torch.save((data, slices, n_node, mean, std_dev), self.processed_paths[0]) 