
import torch

def masked_tensor_mean(tensor, mask, dim=0, keepdim=False):
    # Ensure mask is a boolean tensor
    mask_bool = mask.bool()
    # Multiply the tensor by the mask, zeroing out the elements of the tensor where mask is False
    masked_tensor = tensor * mask_bool
    # Sum the masked tensor across the batch dimension (dim=0)
    sum_per_sequence = torch.sum(masked_tensor, dim=dim, keepdim=keepdim)
    # Count the number of True entries in the mask per sequence for normalization
    count_per_sequence = torch.sum(mask_bool, dim=dim, keepdim=keepdim)
    # Handle potential division by zero in case some sequences are fully masked
    # If count_per_sequence is 0, replace it with 1 to prevent division by zero
    count_per_sequence = torch.clamp(count_per_sequence, min=1)
    # Calculate the mean by dividing the sum by the number of unmasked entries
    mean_per_sequence = sum_per_sequence / count_per_sequence
    return mean_per_sequence

def calculate_advantage(estimated_value, expected_value):
    with torch.no_grad():
        advantage = (expected_value - estimated_value)
    return advantage

def calculate_value_loss(estimated_value, expected_value, mask=None):
    loss = (estimated_value - expected_value).square()
    if mask is not None:
        loss = masked_tensor_mean(loss, mask)
    else:
        loss = loss.mean(dim = 0)
    return loss

def create_padding_mask_before_dones(dones: torch.Tensor) -> torch.Tensor:
    """
    Creates a padding mask for a trajectory by sampling from the end of the sequence. The mask is set to 0 
    (masked) for elements occurring before the 'done' signal when viewed from the end of the trajectory. 
    This includes padding elements that are positioned on the left side of the first 'done' signal in the 
    reversed sequence. The elements from the 'done' signal to the end of the trajectory (rightmost end) 
    are unmasked (set to 1).

    This function is useful for trajectories where sampling starts from the end and padding occurs before 
    the 'done' signal in the reversed order.

    Args:
    - dones (torch.Tensor): The tensor representing the 'done' signals in the trajectory.

    Returns:
    - mask (torch.Tensor): The resultant padding mask tensor. In this mask, elements occurring before the 
      'done' signal in the reversed sequence are masked (set to 0), while the elements from the 'done' 
      signal to the end of the trajectory are unmasked (set to 1).
    """
    mask = torch.ones_like(dones)

    if mask.size(1) > 1:
        # Reverse 'dones' along the specified axis (axis=1)
        reversed_dones = torch.flip(dones, dims=[1])

        # Perform cumulative sum on the reversed tensor
        cumulative_dones_reversed = torch.cumsum(reversed_dones[:,1:], dim=1)

        # Reverse the result back to get the cumulative sum in the original order
        cumulative_dones = torch.flip(cumulative_dones_reversed, dims=[1])
        
        mask[:, :-1, :] = 1 - cumulative_dones
    
    return mask

def calculate_lambda_returns(rewards, values, future_values, dones, discount_factor, td_lambda):
    """
    Calculate lambda returns for each time step in the trajectory.

    Args:
    - rewards (torch.Tensor): Tensor of rewards.
    - values (torch.Tensor): Tensor of estimated state values.
    - future_returns (torch.Tensor): Tensor of future returns estimated, for example, by a target network.
    - mask (torch.Tensor): Mask to indicate valid parts of the trajectory.
    - discount_factor (float): Discount factor (gamma).
    - td_lambda (float): Lambda parameter for weighting n-step returns.

    Returns:
    - torch.Tensor: Lambda returns for each time step.
    """
    batch_size, seq_len, _ = rewards.shape
    lambda_returns = torch.zeros_like(rewards)
    future_returns = torch.zeros_like(future_values)
    future_returns[:,-1:] = future_values[:,-1:]
    mask = 1 - dones
    
    for t in reversed(range(seq_len)):
        # Calculate the TD error
        td_error = rewards[:, t, :] + mask[:, t, :] * (discount_factor * future_returns[:, t, :] - values[:, t, :]) 

        # Update the future return
        future_returns[:, t, :] =  mask[:, t, :] * values[:, t, :] + td_error * td_lambda

        # Apply the mask and store the lambda return
        lambda_returns[:, t, :] = future_returns[:, t, :] 

    return lambda_returns

def calculate_accumulative_rewards(rewards, discount_factor, mask):
    batch_size, seq_len, _ = rewards.shape
    # Initialize a tensor for accumulative rewards with zeros
    accumulative_rewards = torch.zeros_like(rewards)

    # Loop backwards through the sequence
    for t in reversed(range(seq_len)):
        if t == seq_len - 1:
            # If it's the last step, the accumulative reward is just the immediate reward
            accumulative_rewards[:, t, :] = rewards[:, t, :]* mask[:, t, :]
        else:
            # Accumulate reward at step t with the discounted reward at t+1, but only where the mask is true
            accumulative_rewards[:, t, :] = (rewards[:, t, :] + discount_factor * accumulative_rewards[:, t+1, :])* mask[:, t, :]

    return accumulative_rewards

def compute_discounted_future_value(discount_factor, max_seq_len):
    # Create a range tensor [0, 1, 2, ..., max_seq_len-1]
    discount_exponents = max_seq_len - torch.arange(max_seq_len).unsqueeze(0)

    # Compute the discount factors by raising to the power of the exponents
    discount_factors = discount_factor ** discount_exponents

    # Return the discount factors with an additional dimension to match the expected shape
    return discount_factors.unsqueeze(-1)

def compute_gae(values, rewards, dones, gamma, tau=0.95):
    """
    Compute Generalized Advantage Estimation (GAE).
    
    Args:
    - values (torch.Tensor): Estimated values with shape [batch_size, num_td_steps+1, 1].
    - rewards (torch.Tensor): Observed rewards with shape [batch_size, num_td_steps, 1].
    - dones (torch.Tensor): done flags (1 if terminal state, else 1) with shape [batch_size, num_td_steps, 1].
    - gamma (float): Discount factor.
    - tau (float): GAE parameter for bias-variance trade-off.

    Returns:
    - advantages (torch.Tensor): Computed advantages with shape [batch_size, num_td_steps, 1].
    """
    # Copy the inputs to avoid modifying original tensors
    # Prepare tensor for advantages
    advantages = torch.zeros_like(rewards)
    gae = 0  # Initialize GAE

    # Iterate through timesteps in reverse to calculate GAE
    for t in reversed(range(rewards.size(1))):
        # Calculate temporal difference error
        delta = rewards[:, t] + gamma * values[:, t + 1] * (1 - dones[:, t]) - values[:, t]
        # Update GAE
        gae = delta + gamma * tau * gae * (1 - dones[:, t])
        # Store computed advantage
        advantages[:, t] = gae

    return advantages