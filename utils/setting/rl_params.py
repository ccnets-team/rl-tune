from nn.gpt import GPT

# Start training after this number of steps

class TrainingParameters:
    # Initialize training parameters
    def __init__(self, batch_size=64, replay_ratio=8, train_intervel = 4):
        self.batch_size = batch_size  # Batch size for training
        self.replay_ratio = replay_ratio  # How often past experiences are reused in training (batch size / samples per step)
        self.train_intervel  = train_intervel  # Determines how frequently training updates occur based on the number of explorations before each update
        self.early_training_start_step = "none"  # Training starts when the replay buffer is full. Set to a specific step count to start training earlier.
                
class AlgorithmParameters:
    # Initialize algorithm parameters
    def __init__(self, discount_factor=0.99, td_lambda = 0.9, num_td_steps=16, use_dynamic_td_steps=False, use_gae_advantage=False, curiosity_factor=0.0):
        self.discount_factor = discount_factor  # Discount factor for future rewards
        self.td_lambda = td_lambda # TD lambda parameter for weighting n-step returns.
        self.num_td_steps = num_td_steps  # Number of TD steps for multi-step returns
        # Flag to enable dynamic adjustment of TD steps based on exploration-exploitation balance.
        # When True, the number of TD steps is automatically adjusted during training, potentially 
        # increasing as the exploration rate decreases, to balance exploration and exploitation.
        self.use_dynamic_td_steps = use_dynamic_td_steps  
        self.use_gae_advantage = use_gae_advantage  # Whether to use Generalized Advantage Estimation
        self.curiosity_factor = curiosity_factor  # Influences the agent's desire to explore new experiences and learn through intrinsic rewards
            
class NetworkParameters:
    # Initialize network parameters
    def __init__(self, num_layer=5, hidden_size=256, dropout = 0.0, rev_env_hidden_size_mul = 0.5):
        self.critic_network = GPT  # Critic network architecture (GPT in this case)
        self.actor_network = GPT  # Actor network architecture (GPT in this case)
        self.reverse_env_network = GPT  # Reverse environment network architecture (GPT in this case)
        self.num_layer = num_layer  # Number of layers in the networks
        self.hidden_size = hidden_size  # Demension of model 
        self.dropout = dropout  # Dropout rate
        self.rev_env_hidden_size_mul = rev_env_hidden_size_mul  # Hidden size multiplier for reverse environment network
        
class OptimizationParameters:
    # Initialize optimization parameters
    def __init__(self, beta1=0.9, lr_gamma=0.9998, step_size=4, lr=1e-4, tau=5e-3, clip_grad_range=0.5):
        self.beta1 = beta1  # Beta1 parameter for Adam optimizer
        self.lr_gamma = lr_gamma  # Learning rate decay factor
        self.step_size = step_size  # Step size for learning rate scheduling
        self.lr = lr  # Initial learning rate
        self.tau = tau  # Target network update rate
        self.clip_grad_range = clip_grad_range  
        
class ExplorationParameters:
    # Initialize exploration parameters
    def __init__(self, noise_type='none', initial_exploration=1.0, min_exploration=0.01, decay_percentage=0.8, decay_mode='linear',
                 max_steps=400000):
        self.noise_type = noise_type  # Type of exploration noise ('none' for no noise)
        self.initial_exploration = initial_exploration  # Initial exploration rate
        self.min_exploration = min_exploration  # Minimum exploration rate
        self.decay_percentage = decay_percentage  # Percentage of total steps for exploration decay
        self.decay_mode = decay_mode  # Mode of exploration decay ('linear' for linear decay)
        self.max_steps = max_steps 
        
class MemoryParameters:
    # Initialize memory parameters
    def __init__(self, buffer_type='standard', buffer_size=128000):
        self.buffer_type = buffer_type  # Type of replay buffer ('standard' for standard buffer)
        self.buffer_size = int(buffer_size)  # Size of the replay buffer
        
class NormalizationParameters:
    # Initialize normalization parameters
    def __init__(self, reward_scale = 1, clip_norm_range = 10, window_size = 20, reward_normalizer='hybrid_moving_mean_var', state_normalizer='running_mean_std'):
        self.reward_scale = reward_scale  # Scaling factor for rewards
        self.clip_norm_range = clip_norm_range  
        self.window_size = window_size  
        self.reward_normalizer = reward_normalizer  # reward normalization method (e.g., 'running_mean_std, hybrid_moving_mean_var')
        self.state_normalizer = state_normalizer  # State normalization method (e.g., 'running_mean_std, hybrid_moving_mean_var')

class RLParameters:
    def __init__(self,
                 training: TrainingParameters = None,
                 algorithm: AlgorithmParameters = None,
                 network: NetworkParameters = None,
                 optimization: OptimizationParameters = None,
                 exploration: ExplorationParameters = None,
                 memory: MemoryParameters = None,
                 normalization: NormalizationParameters = None):
        
        # Initialize RL parameters
        self.training = TrainingParameters() if training is None else training
        self.algorithm = AlgorithmParameters() if algorithm is None else algorithm
        self.network = NetworkParameters() if network is None else network
        self.optimization = OptimizationParameters() if optimization is None else optimization
        self.exploration = ExplorationParameters() if exploration is None else exploration
        self.memory = MemoryParameters() if memory is None else memory
        self.normalization = NormalizationParameters() if normalization is None else normalization
            
    def __iter__(self):
        yield self.training
        yield self.algorithm 
        yield self.network
        yield self.optimization
        yield self.exploration
        yield self.memory
        yield self.normalization
        
