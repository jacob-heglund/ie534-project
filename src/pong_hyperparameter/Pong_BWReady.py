''' CHANGE ENVIRONMENT HERE'''
''' ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ '''
env_id = "PongNoFrameskip-v0"
''' ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ '''
import math, random

import gym
import numpy as np

import torch
import torch.nn as nn
import torch.optim as optim
import torch.autograd as autograd
from torch.autograd import Variable
import torch.nn.functional as F
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# torch.manual_seed(1356)

# Device configuration
# device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# torch.cuda.manual_seed(1356)
# torch.backends.cudnn.deterministic = True

# out_dir = '/u/training/tra442/scratch/'
out_dir = 'outdir/'

from wrappers import make_atari, wrap_deepmind, wrap_pytorch
env    = make_atari(env_id)
env    = wrap_deepmind(env)
env    = wrap_pytorch(env)

import math, random

import gym
import numpy as np

import torch
import torch.nn as nn
import torch.optim as optim
import torch.autograd as autograd
from torch.autograd import Variable
import torch.nn.functional as F
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

import matplotlib.pyplot as plt

USE_CUDA = torch.cuda.is_available()
Variable = lambda *args, **kwargs: autograd.Variable(*args, **kwargs).cuda() if USE_CUDA else autograd.Variable(*args, **kwargs)

from collections import deque

class ReplayBuffer(object):
    def __init__(self, capacity):
        self.buffer = deque(maxlen=capacity)

    def push(self, state, action, reward, next_state, done):
        state      = np.expand_dims(state, 0)
        next_state = np.expand_dims(next_state, 0)

        self.buffer.append((state, action, reward, next_state, done))

    def sample(self, batch_size):
        state, action, reward, next_state, done = zip(*random.sample(self.buffer, batch_size))
        return np.concatenate(state), action, reward, np.concatenate(next_state), done

    def __len__(self):
        return len(self.buffer)


def update_target(current_model, target_model):
    target_model.load_state_dict(current_model.state_dict())

estimated_next_q_state_values=[]
estimated_next_q_value=[]

def compute_td_loss(batch_size):
    state, action, reward, next_state, done = replay_buffer.sample(batch_size)

    state      = Variable(torch.FloatTensor(np.float32(state)))
    next_state = Variable(torch.FloatTensor(np.float32(next_state)))
    action     = Variable(torch.LongTensor(action))
    reward     = Variable(torch.FloatTensor(reward))
    done       = Variable(torch.FloatTensor(done))

    q_values      = current_model(state)
    next_q_values = current_model(next_state)
    next_q_state_values = target_model(next_state)

    estimated_next_q_state_values.append(next_q_state_values)


    q_value       = q_values.gather(1, action.unsqueeze(1)).squeeze(1)
    next_q_value = next_q_state_values.gather(1, torch.max(next_q_values, 1)[1].unsqueeze(1)).squeeze(1)

    estimated_next_q_value.append(next_q_value)

    expected_q_value = reward + gamma * next_q_value * (1 - done)

    loss = (q_value - Variable(expected_q_value.data)).pow(2).mean()

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    return loss

# def plot(frame_idx, rewards, losses):
# #     clear_output(True)
#     plt.figure(figsize=(20,5))
#     plt.subplot(131)
#     plt.title('frame %s. reward: %s' % (frame_idx, np.mean(rewards[-10:])))
#     plt.plot(rewards)
#     plt.savefig(out_dir + 'rew_plt/rewards{}.png'.format(frame_idx))

#     plt.subplot(132)
#     plt.title('loss')
#     plt.plot(losses)
#     plt.savefig(out_dir + 'los_plt/losses{}.png'.format(frame_idx))
#     plt.show()

class CnnDQN(nn.Module):
    def __init__(self, input_shape, num_actions):
        super(CnnDQN, self).__init__()

        self.input_shape = input_shape
        self.num_actions = num_actions

        self.features = nn.Sequential(
            nn.Conv2d(input_shape[0], 32, kernel_size=8, stride=4),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=4, stride=2),
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3, stride=1),
            nn.ReLU()
        )

        self.fc = nn.Sequential(
            nn.Linear(self.feature_size(), 512),
            nn.ReLU(),
            nn.Linear(512, self.num_actions)
        )

    def forward(self, x):
        x = self.features(x)
        x = x.view(x.size(0), -1)
        x = self.fc(x)
        return x

    def feature_size(self):
        return self.features(autograd.Variable(torch.zeros(1, *self.input_shape))).view(1, -1).size(1)

    def act(self, state, epsilon):
        if random.random() > epsilon:
            state   = Variable(torch.FloatTensor(np.float32(state)).unsqueeze(0), volatile=True)
            q_value = self.forward(state)
            action  = q_value.max(1)[1].data[0]
        else:
            action = random.randrange(env.action_space.n)
        return action

current_model = CnnDQN(env.observation_space.shape, env.action_space.n)
# current_model = torch.load('target_PongNoFrameskip-v0_19100000.model')
# current_model.load_state_dict(torch.load('target_PongNoFrameskip-v0_19100000.ckpt'))
target_model  = CnnDQN(env.observation_space.shape, env.action_space.n)
# target_model = torch.load('target_PongNoFrameskip-v0_19100000.model')
# target_model.load_state_dict(torch.load('target_PongNoFrameskip-v0_19100000.ckpt'))

# current_model = torch.load('outdir/cur_mod/current200000.model')
# target_model = torch.load('outdir/tar_mod/target200000.model')

if USE_CUDA:
    current_model = current_model.cuda()
    target_model  = target_model.cuda()

optimizer = optim.Adam(current_model.parameters(), lr=0.00001)

replay_initial = 10000
replay_buffer = ReplayBuffer(1000000)

update_target(current_model, target_model)

epsilon_start = 1.0
epsilon_final = 0.01
epsilon_decay = 1000000

epsilon_by_frame = lambda frame_idx: epsilon_final + (epsilon_start - epsilon_final) * math.exp(-1. * frame_idx / epsilon_decay)

num_frames = 1000000
batch_size = 32
gamma      = 0.99

losses = []
all_rewards = []
episode_reward = 0

state = env.reset()
# env.render()
for frame_idx in range(1, num_frames + 1):
    epsilon = epsilon_by_frame(frame_idx)
    action = current_model.act(state, epsilon)

    next_state, reward, done, _ = env.step(action)
    replay_buffer.push(state, action, reward, next_state, done)
#     env.render()

    state = next_state
    episode_reward += reward

    if (frame_idx%100000==0):
        # SAVING LOSS AND REWARD
        np.save(out_dir + 'losses_ddqn_seed0.npy',np.array(losses))
        np.save(out_dir + 'rewards_ddqn_seed0.npy',np.array(all_rewards))

#         SAVING CHECKPOINTS
        torch.save(current_model.state_dict(),out_dir + 'cur_ckp_ddqn/current{}_seed0_DDQN.ckpt'.format(frame_idx))
        torch.save(target_model.state_dict(),out_dir + 'tar_ckp_ddqn/target{}_seed0_DDQN.ckpt'.format(frame_idx))

#         SAVING MODELS
        torch.save(current_model,out_dir + 'cur_mod_ddqn/current{}_seed0_DDQN.model'.format(frame_idx))
        torch.save(target_model,out_dir + 'tar_mod_ddqn/target{}_seed0_DDQN.model'.format(frame_idx))

#         SAVING ESTIMATED Q VALUES
        np.save(out_dir + 'next_q_state_values_ddqn_seed0.npy',np.array(estimated_next_q_state_values))
        np.save(out_dir + 'next_q_value_ddqn_seed0.npy',np.array(estimated_next_q_value))

    if done:
        state = env.reset()
        all_rewards.append(episode_reward)
        episode_reward = 0

    if frame_idx % 10000==0:
        print('Frame: ',frame_idx)

    if (len(replay_buffer) > replay_initial) and (frame_idx%4==0):
        loss = compute_td_loss(batch_size)
        losses.append(loss.item())

#     if frame_idx % 100000 == 0:
#         plot(frame_idx, all_rewards, losses)

    if frame_idx % 10000 == 0:
        update_target(current_model, target_model)
