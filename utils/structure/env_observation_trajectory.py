import numpy as np
import copy
from .env_observations import EnvObservations

class EnvObservationTrajectory:
    def __init__(self, obs_shapes, obs_types, num_agents, num_td_steps):
        assert len(obs_shapes) == len(obs_types), "The length of obs_shapes and obs_types must be the same."
        self.obs_shapes = obs_shapes
        self.obs_types = obs_types
        self.num_agents = num_agents
        self.num_td_steps = num_td_steps
        self.data = self._create_empty_data()

    def _create_empty_data(self):
        observations = {}
        for obs_type, shape in zip(self.obs_types, self.obs_shapes):
            observations[obs_type] = np.zeros((self.num_agents, self.num_td_steps, *shape), dtype=np.float32)
        return observations

    def copy(self):
        new_instance = self.__class__(self.obs_shapes, self.obs_types, self.num_agents, self.num_td_steps)
        for obs_type in self.obs_types:
            new_instance.data[obs_type] = copy.copy(self.data[obs_type])
        return new_instance

    def __getitem__(self, key):
        if isinstance(key, tuple):
            agent_indices, td_idx = key
        else:
            agent_indices = key
            td_idx = slice(None)

        if isinstance(agent_indices, int):
            agent_indices = [agent_indices]

        if isinstance(agent_indices, list):
            new_num_agents = len(agent_indices)
        else:
            new_num_agents = self.num_agents
            agent_indices = slice(None)

        new_observation = EnvObservationTrajectory(self.obs_shapes, self.obs_types, num_agents=new_num_agents, num_td_steps=self.num_td_steps)
        for obs_type in self.obs_types:
            new_observation.data[obs_type] = self.data[obs_type][agent_indices, td_idx]

        return new_observation

    def __setitem__(self, agent_indices, values):
        for obs_type in self.obs_types:
            self.data[obs_type][agent_indices] = values[obs_type]
    
    def reset(self):
        self.data = self._create_empty_data()
                
    def shift(self):
        self.data = {key: np.roll(value, shift=-1, axis=1) for key, value in self.data.items()}  # Shift along the second dimension to the left
        for key in self.data:
            self.data[key][:, -1] = 0  # Set the last time dimension to 0

    def to_vector(self):
        """
        Convert the observations to a vector format.
        Only takes into account obs_types that are vectors after the num_agents dimension.
        Resulting shape will be (num_agents, concatenated_data)
        This method selects the data from the first time step for each agent.
        """
        vectors = []
        for obs_type, shape in zip(self.obs_types, self.obs_shapes):
            # Checking if the shape after num_agents is 1D
            if len(shape) == 1:
                data = self.data[obs_type][:, :]  # Select the first time step for all agents
                vectors.append(data)
        
        concatenated_data = np.concatenate(vectors, axis=-1)  # Concatenate along the data dimension
        return concatenated_data