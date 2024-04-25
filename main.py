from agents.agent import DQNAgent
from envs.ev_charging_env import EVChargingEnv
from models.dqn.replay_memory import ReplayMemory
from utils.Station import Stations
class ReinforcementAIModel():
    TARGET_UPDATE_FREQUENCY = 10  # Her 10 bölümde bir hedef ağını güncelle
    BATCH_SIZE = 64  # Replay belleğinden örnekleme alınacak minibatch boyutu
    N_EPISODES = 20  # Toplam eğitim için bölüm sayısı

    env = EVChargingEnv(max_stations=5)  # Ortamı başlat
    state_size = env.observation_space.shape[0]
    action_size = env.action_space.n

    replay_memory_capacity = 25_000  # Gereksinimlerinize göre ayarlayın
    replay_memory = ReplayMemory(replay_memory_capacity)

    agent = DQNAgent(state_size, action_size, replay_memory)  # DQN ajanını başlat



    def initAI(self):
        for episode in range(self.N_EPISODES):  # type: ignore
            state = self.env.reset()  # type: ignore
            total_reward = 0
            while True:
                action = self.agent.act(state)
                next_state, reward, done, _ = self.env.step(action)
                self.agent.remember(state, action, next_state, reward, done)
                state = next_state
                total_reward += reward
                if done:
                    break
            # Replay belleğinden bir minibatch örnekle ve bir öğrenme adımı gerçekleştir
            self.agent.train(self.BATCH_SIZE)
            # Periyodik olarak hedef ağ ağırlıklarını güncelle
            if episode % self.TARGET_UPDATE_FREQUENCY == 0:
                self.agent.update_target_model()
            # Günlüğe veya her bölüm sonrası mantığa burada yer verebilirsiniz
            print(f"Bölüm {episode}, Bir Adımlık Ödül: {total_reward}")
        return True  # Tüm bölümler tamamlandığında True döndür
    
    def selectBestSpot(self, stations = []):
        returnStations = self.env.select_best_station(stations=stations)
        return returnStations

