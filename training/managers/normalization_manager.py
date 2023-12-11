import torch
from preprocessing.normalizer.running_z_standardizer import RunningZStandardizer
from preprocessing.normalizer.running_mean_std import RunningMeanStd
from preprocessing.normalizer.exponential_moving_mean_var import ExponentialMovingMeanVar
from preprocessing.normalizer.hybrid_moving_mean_var import HybridMovingMeanVar

import numpy as np
from utils.structure.trajectories  import BatchTrajectory

TRANSITION_STATE_IDX = 0
TRANSITION_NEXT_STATE_IDX = 3
TRANSITION_REWARD_IDX = 2

class NormalizerBase:
    def __init__(self, vector_size, norm_type_key, normalization_params, device):
        self.normalizer = None
        self.vector_size = vector_size

        norm_type = getattr(normalization_params, norm_type_key)
        if norm_type == "running_z_standardizer":
            self.normalizer = RunningZStandardizer(vector_size, device)
        elif norm_type == "running_mean_std":
            self.normalizer = RunningMeanStd(vector_size, device)
        elif norm_type == "exponential_moving_mean_var":
            self.normalizer = ExponentialMovingMeanVar(vector_size, device)
        elif norm_type == "hybrid_moving_mean_var":
            self.normalizer = HybridMovingMeanVar(vector_size, device)
            
        self.device = device
            
    def _update_normalizer(self, data):
        if self.normalizer is not None:
            data = torch.FloatTensor(data).to(self.device)
            first_seq_data = data.view(-1, *data.shape[2:])
            # Update the normalizer
            self.normalizer.update(first_seq_data)

    def normalize_data(self, data):
        if self.normalizer is not None:
            data = self.normalizer.normalize(data)
        return data
    
class NormalizationUtils:
    def __init__(self, env_config, normalization, device):
        self.state_manager = NormalizerBase(env_config.state_size, 'state_normalizer', normalization, device=device)
        self.reward_manager = NormalizerBase(1, 'reward_normalizer', normalization, device=device)
        self.reward_scale = normalization.reward_scale
        self.reward_shift = normalization.reward_shift
        self.state_indices = [TRANSITION_STATE_IDX, TRANSITION_NEXT_STATE_IDX]
        self.reward_indices = [TRANSITION_REWARD_IDX]

    def normalize_state(self, state):
        return self.state_manager.normalize_data(   state)

    def normalize_reward(self, reward):
        return self.reward_scale*self.reward_manager.normalize_data(reward) + self.reward_shift
    
    def get_state_normalizer(self):
        return self.state_manager.normalizer

    def get_reward_normalizer(self):
        return self.reward_manager.normalizer

    def transform_transition(self, trans: BatchTrajectory):
        trans.state = self.normalize_state(trans.state)
        trans.next_state = self.normalize_state(trans.next_state)
        trans.reward = self.normalize_reward(trans.reward)
        return trans
    
    def update_normalizer(self, samples):
        for index in self.state_indices:
            data = np.stack([sample[index] for sample in samples], axis=0)
            self.state_manager._update_normalizer(data)

        for index in self.reward_indices:
            data = np.stack([sample[index] for sample in samples], axis=0)
            self.reward_manager._update_normalizer(data)

