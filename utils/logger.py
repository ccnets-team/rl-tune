from datetime import datetime
import os

METRICS_CATEGORY_MAP = {
    'losses': 'Losses',
    'values': 'Values',
    'errors': 'CoopErrors',
    'costs': 'TransitionCosts'
}

def log_data(trainer, logger, train_reward_per_step, test_reward_per_step, train_accumulative_rewards, test_accumulative_rewards, metrics, step, time_cost):
    epsilon = trainer.get_exploration_rate()
    learning_rate = trainer.get_lr()

    # Creating a dictionary to log scalar data efficiently
    scalar_logs = {
        "Episode/TrainRewards": train_accumulative_rewards if train_accumulative_rewards is not None else None,
        "Episode/TestRewards": test_accumulative_rewards if test_accumulative_rewards is not None else None,
        "Step/TrainReward": train_reward_per_step if train_reward_per_step is not None else None,
        "Step/TestReward": test_reward_per_step if test_reward_per_step is not None else None,
        "Step/Time": time_cost,
        "Step/LearningRate": learning_rate,
        "Step/ExplorationRate": epsilon,
    }

    # Log scalar data
    for name, value in scalar_logs.items():
        if value is not None:
            logger.add_scalar(name, value, step)

    if metrics is not None:
        # Loop over each metrics category and log each metric with a specific prefix
        for category_name, category_metrics in metrics.__dict__.items():
            # Map the category_name to the new desired name
            mapped_category_name = METRICS_CATEGORY_MAP.get(category_name, category_name.title())
            
            for metric_name, metric_value in category_metrics.items():
                if metric_value is not None:
                    components = metric_name.split('_')

                    if len(components) > 1:  # if there is more than one word in metric_name
                        new_metric_name = components[-2].title()  # select only the previous of the last word and capitalize it
                    else:  # if there is only one word in metric_name
                        new_metric_name = components[0].title()                         
                        
                    log_name = f"{mapped_category_name}/{new_metric_name}"
                    logger.add_scalar(log_name, metric_value, step)

def get_log_name(log_path):
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_dir = f"{log_path}/{current_time}"
    
    # Check if the directory exists, if it does, append a suffix to make it unique
    suffix = 0
    while os.path.isdir(log_dir):
        suffix += 1
        log_dir = f"{log_path}/{current_time}_{suffix}"
    
    return log_dir
