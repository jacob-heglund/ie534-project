# Double Deep Q-Learning with Atari Environments

## Directory Structure

├── docs                        # Non-code documents

├── figures                     # Images and graphs

├── misc_code_examples          # Any useful examples of RL implementations

├── misc_models

├── src                         # Code for our implementation of the project

└── README.md

Directory tree generated using <http://tree-generator.herokuapp.com/>
> Use short, lowercase names for directories

## Generating Videos (after training)

To get videos, copy the 'checkpoints' folder to the same directory as generate_videos.py,
then run generate_videos.py.  This will create a 'videos' folder.

Note: The current pipeline is to generate checkpoints on BW using training.py,then generate videos on a personal computer using generate_videos.py since BW doesn't have the right version of gym.  This will hopefully change.