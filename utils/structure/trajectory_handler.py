import numpy as np

class BatchTrajectory:
    def __init__(self, state, action, reward, next_state, done):
        self.state = state
        self.action = action
        self.reward = reward
        self.next_state = next_state
        self.done = done

    def __iter__(self):
        yield self.state
        yield self.action
        yield self.reward
        yield self.next_state
        yield self.done
        
class MultiEnvTrajectories:
    def __init__(self, env_ids=None, agent_ids=None, states=None, actions=None, rewards=None, next_states=None, dones_terminated=None, dones_truncated=None, td_errors=None):
        self.env_ids = env_ids 
        self.agent_ids = agent_ids 
        self.states = states 
        self.actions = actions 
        self.rewards = rewards 
        self.next_states = next_states 
        self.dones_terminated = dones_terminated 
        self.dones_truncated = dones_truncated 
        self.td_errors = td_errors 

    def _add_attribute(self, attr_name, values):
        attr = getattr(self, attr_name)
        # If values is not None and is non-empty, extend the attribute
        if values is not None and len(values) > 0:
            # Convert values to numpy array if it's a list
            if isinstance(values, list):
                values = np.array(values)
            # If the attribute is None, set it to values
            if attr is None or len(attr) == 0:
                setattr(self, attr_name, values)
            else:
                # Convert the attribute to numpy array if it's a list
                if isinstance(attr, list):
                    attr = np.array(attr)
                # concatenate existing attribute and new values
                setattr(self, attr_name, np.concatenate((attr, values), axis=0))

    def add(self, env_ids, agent_ids, states, actions, rewards, next_states, dones_terminated, dones_truncated, td_errors=None):
        self._add_attribute('env_ids', env_ids)
        self._add_attribute('agent_ids', agent_ids)
        self._add_attribute('states', states)
        self._add_attribute('actions', actions)
        self._add_attribute('rewards', rewards)
        self._add_attribute('next_states', next_states)
        self._add_attribute('dones_terminated', dones_terminated)
        self._add_attribute('dones_truncated', dones_truncated)
        self._add_attribute('td_errors', td_errors)

    