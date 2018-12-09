import numpy as np
import matplotlib.pyplot as plt
import os 


# data_dir = './Pong/ddqn/losses'
# data_dir = './Pong/ddqn/qvalues'
data_dir = './Pong/ddqn/rewards'

for i in range(5):
    if data_dir == './Pong/ddqn/losses':
        fn = 'losses_ddqn_seed' + str(i) + '.npy'
        title = 'Losses'
    
    if data_dir == './Pong/ddqn/qvalues':
        # fn = 'next_q_state_values_ddqn_seed' + str(i) + '.npy'
        fn = 'next_q_value_ddqn_seed' + str(i) + '.npy'
        title = 'Q-Values'
    
    if data_dir == './Pong/ddqn/rewards':
        fn = 'rewards_ddqn_seed' + str(i) + '.npy'
        title = 'Rewards'

    path = os.path.join(data_dir, fn)
    data = np.load(path)

    data_list = np.ndarray.tolist(data)

    plt.plot(data_list[100:], alpha = .5, c = 'b')

# data_dir = './Pong/dqn/losses'
# data_dir = './Pong/dqn/qvalues'
data_dir = './Pong/dqn/rewards'

for i in range(5):
    if data_dir == './Pong/dqn/losses':
        fn = 'losses_dqn_seed' + str(i) + '.npy'
        title = 'Losses'
    
    if data_dir == './Pong/dqn/qvalues':
        # fn = 'next_q_state_values_ddqn_seed' + str(i) + '.npy'
        fn = 'next_q_value_dqn_seed' + str(i) + '.npy'
        title = 'Q-Values'
    
    if data_dir == './Pong/dqn/rewards':
        fn = 'rewards_dqn_seed' + str(i) + '.npy'
        title = 'Rewards'

    path = os.path.join(data_dir, fn)
    data = np.load(path)

    data_list = np.ndarray.tolist(data)

    plt.plot(data_list[100:], alpha = .5, c = 'r')




plt.title(title)
plt.show()
