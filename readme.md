# Double Deep Q-Learning with Atari Environments

## Directory Structure

Directory tree generated using <http://tree-generator.herokuapp.com/>

•
├── docs                        # Non-code documents
│   ├── blue_waters
│   │   ├── bw_tutorial         # Instructor's tutorial for running batch jobs
│   │   └── pbs_stuff           # Jacob's way of running batch jobs
│   └── papers                  # Any useful papers or textbooks
├── figures                     # Images and graphs
├── misc_code_examples          # Any useful examples of RL implementations
├── misc_models
├── src                         # Code for our implementation of the project
│   ├── dqn                     # Deep Q-Learning
│   │   ├── videos              # Videos of networks trained for X frames for env_id
│   │   │   └── env_id_n
│   │   │       └── frame_X
│   │   └── checkpoints         # Network checkpoints at frame X for env_id
│   │       └── env_id_n
│   └── ddqn                    # Double Deep Q-Learning
│       ├── videos              # Videos of networks trained for X frames for env_id
│       │   └── env_id_n
│       │       └── frame_X
│       └── checkpoints         # Network checkpoints at frame X for env_id
│           └── env_id_n
└── README.md

> Use short lowercase names at least for the top-level files and folders except
>`README.md`

## Generating Videos (after training)

To get videos, copy the 'checkpoints' folder to the same directory as generate_videos.py,
then run generate_videos.py.  This will create a 'videos' folder.

Note: The current pipeline is to generate checkpoints on BW using training.py,then generate videos on a personal computer using generate_videos.py since BW doesn't have the right version of gym.  This will hopefully change.