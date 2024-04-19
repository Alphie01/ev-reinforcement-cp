import torch
import torch.nn.functional as F
import random
import numpy as np

from models.dqn.dqn import DQN


class DQNAgent:
    def __init__(self, state_size, action_size, replay_memory):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.state_size = state_size
        self.action_size = action_size
        self.memory = replay_memory
        self.gamma = 0.99  # discount rate
        self.epsilon = 1.0  # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.model = DQN(state_size, action_size).to(self.device)
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=self.learning_rate)
        self.target_model = DQN(state_size, action_size).to(self.device)
        self.update_target_model()

    def update_target_model(self):
        """Update the target model to match the current model."""
        self.target_model.load_state_dict(self.model.state_dict())

    def remember(self, state, action, next_state, reward, done):
        """Store experience in replay memory."""
        self.memory.push(state, action, next_state, reward, done)

    def act(self, state):
        """Return actions for given state as per current policy."""
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        state = torch.FloatTensor(state).unsqueeze(0)
        act_values = self.model(state)
        return np.argmax(act_values.cpu().data.numpy())

    def replay(self, batch_size):
        """Train the model using randomly sampled mini-batches from the replay memory."""
        if len(self.memory) < batch_size:
            return
        minibatch = self.memory.sample(batch_size)
        for state, action, next_state, reward, done in minibatch:
            # Convert to PyTorch tensors
            state = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            next_state = torch.FloatTensor(next_state).unsqueeze(0).to(self.device)

            # Compute the target Q-value
            target = reward
            if not done:
                target += self.gamma * torch.max(self.target_model(next_state).detach()).item()

            # Get the current Q-value predictions for all actions from the policy model
            current_q_values = self.model(state)
            # Only change the Q-value for the taken action to the target; keep others as is
            new_q_values = current_q_values.clone()
            new_q_values[0][action] = target

            # Zero the parameter gradients
            self.optimizer.zero_grad()
            # Calculate loss
            loss = F.mse_loss(current_q_values, new_q_values)
            # Backpropagation
            loss.backward()
            # Optimize
            self.optimizer.step()

        # Epsilon decay
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def train(self, batch_size):
        """External method to initiate training on a mini-batch."""
        self.replay(batch_size)
