
# coding: utf-8

# In[ ]:


''' CHANGE ENVIRONMENT HERE'''
''' ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ '''
env_id = "MsPacmanNoFrameskip-v0"
''' ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ '''
import math, random

import gym
import numpy as np
import adam

import torch
import torch.nn as nn
import torch.optim as optim
import torch.autograd as autograd
from torch.autograd import Variable
import torch.nn.functional as F
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

print('Imported Everything ...')

# In[1]:



out_dir = '/u/training/tra442/scratch/'


# In[2]:


from wrappers import make_atari, wrap_deepmind, wrap_pytorch
env    = make_atari(env_id)
env    = wrap_deepmind(env)
env    = wrap_pytorch(env)

print('ran make_atari, wrap_deepmind, wrap_pytorch')


# In[3]:


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


# In[4]:


import matplotlib.pyplot as plt


# In[6]:


USE_CUDA = torch.cuda.is_available()
Variable = lambda *args, **kwargs: autograd.Variable(*args, **kwargs).cuda() if USE_CUDA else autograd.Variable(*args, **kwargs)


# In[5]:


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


# In[7]:


epsilon_start = 1.0
epsilon_final = 0.01
epsilon_decay = 500

epsilon_by_frame = lambda frame_idx: epsilon_final + (epsilon_start - epsilon_final) * math.exp(-1. * frame_idx / epsilon_decay)


# In[9]:


class DQN(nn.Module):
    def __init__(self, num_inputs, num_actions):
        super(DQN, self).__init__()

        self.layers = nn.Sequential(
            nn.Linear(env.observation_space.shape[0], 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, env.action_space.n)
        )

    def forward(self, x):
        return self.layers(x)

    def act(self, state, epsilon):
        if random.random() > epsilon:
            state   = Variable(torch.FloatTensor(state).unsqueeze(0), volatile=True)
            q_value = self.forward(state)
            action  = q_value.max(1)[1].data.item()
        else:
            action = random.randrange(env.action_space.n)
        return action


# In[10]:


# current_model = DQN(env.observation_space.shape[0], env.action_space.n)
# target_model  = DQN(env.observation_space.shape[0], env.action_space.n)
#
# if USE_CUDA:
#     current_model = current_model.cuda()
#     target_model  = target_model.cuda()
#
# optimizer = optim.Adam(current_model.parameters())
#
# replay_buffer = ReplayBuffer(1000)


# In[11]:


def update_target(current_model, target_model):
    target_model.load_state_dict(current_model.state_dict())


# In[12]:




# In[13]:


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

    q_value       = q_values.gather(1, action.unsqueeze(1)).squeeze(1)
    next_q_value = next_q_state_values.gather(1, torch.max(next_q_values, 1)[1].unsqueeze(1)).squeeze(1)
    expected_q_value = reward + gamma * next_q_value * (1 - done)

    loss = (q_value - Variable(expected_q_value.data)).pow(2).mean()

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    return loss


# In[14]:


def plot(frame_idx, rewards, losses):
    # clear_output(True)
    plt.figure(figsize=(20,5))
    plt.subplot(131)
    plt.title('frame %s. reward: %s' % (frame_idx, np.mean(rewards[-10:])))
    plt.plot(rewards)
    plt.savefig(out_dir + 'rew_plt/rewards_{}_{}.png'.format(env_id,frame_idx))

    plt.subplot(132)
    plt.title('loss')
    plt.plot(losses)
    plt.savefig(out_dir + 'los_plt/losses_{}_{}.png'.format(env_id,frame_idx))
#     plt.show()


# In[15]:


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


# In[16]:


current_model = CnnDQN(env.observation_space.shape, env.action_space.n)
# current_model.load_state_dict(torch.load('current.ckpt'))
target_model  = CnnDQN(env.observation_space.shape, env.action_space.n)
# target_model.load_state_dict(torch.load('target.ckpt'))

if USE_CUDA:
    current_model = current_model.cuda()
    target_model  = target_model.cuda()

# optimizer = optim.Adam(current_model.parameters(), lr=0.00001)
optimizer = adam.Adam(current_model.parameters(), lr=0.00001)

replay_initial = 10000
replay_buffer = ReplayBuffer(100000)

update_target(current_model, target_model)


# In[17]:


epsilon_start = 1.0
epsilon_final = 0.01
epsilon_decay = 30000

epsilon_by_frame = lambda frame_idx: epsilon_final + (epsilon_start - epsilon_final) * math.exp(-1. * frame_idx / epsilon_decay)


# In[ ]:


num_frames = 10000000
batch_size = 32
gamma      = 0.99

losses = []
all_rewards = []
episode_reward = 0

state = env.reset()
print('~~~~~~~~~~~~~Starting Training~~~~~~~~~~~~~')
for frame_idx in range(1, num_frames + 1):
    epsilon = epsilon_by_frame(frame_idx)
    action = current_model.act(state, epsilon)

    next_state, reward, done, _ = env.step(action)
    replay_buffer.push(state, action, reward, next_state, done)

    state = next_state
    episode_reward += reward

    if (frame_idx%100000==0):
        # SAVING LOSS AND REWARD
        np.save(out_dir + 'losses_{}.npy'.format(env_id),np.array(losses))
        np.save(out_dir + 'rewards_{}.npy'.format(env_id),np.array(all_rewards))

#         SAVING CHECKPOINTS
        torch.save(current_model.state_dict(),out_dir + 'cur_ckp/current_{}_{}.ckpt'.format(env_id,frame_idx))
        torch.save(target_model.state_dict(),out_dir + 'tar_ckp/target_{}_{}.ckpt'.format(env_id,frame_idx))

#         SAVING MODELS
        torch.save(current_model,out_dir + 'cur_mod/current_{}_{}.model'.format(env_id,frame_idx))
        torch.save(target_model,out_dir + 'tar_mod/target_{}_{}.model'.format(env_id,frame_idx))

    if done:
        state = env.reset()
        all_rewards.append(episode_reward)
        episode_reward = 0

    if len(replay_buffer) > replay_initial:
        loss = compute_td_loss(batch_size)
        losses.append(loss.item())

    # if frame_idx % 100000 == 0:
    #     plot(frame_idx, all_rewards, losses)

    if frame_idx % 10000 == 0:
        update_target(current_model, target_model)
        print('Target updated, we are at {} frames'.format(frame_idx))
