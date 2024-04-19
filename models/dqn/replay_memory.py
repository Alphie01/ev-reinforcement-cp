import random
from collections import namedtuple, deque

Experience = namedtuple('Experience', ('state', 'action', 'next_state', 'reward', 'done'))


class ReplayMemory:
    def __init__(self, capacity):
        self.capacity = capacity
        self.memory = deque([], maxlen=capacity)

    def push(self, *args):
        """Save an experience."""
        self.memory.append(Experience(*args))

    def sample(self, batch_size):
        """Sample a batch of experiences randomly from memory."""
        return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)
