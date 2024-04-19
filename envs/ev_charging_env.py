import numpy as np
import gym
from gym import spaces


class EVChargingEnv(gym.Env):
    """
    Environment for choosing the best charging station in a single-step scenario.
    """

    def __init__(self, max_stations=5):
        super(EVChargingEnv, self).__init__()
        self.max_stations = max_stations
        self.action_space = spaces.Discrete(self.max_stations + 1)  # Choose one of the stations or none

        # Feature definitions
        self.ev_features = np.array([[5.5, 100],  # EV's battery level (%)
                                     [4.5, 35]])  # Average consumption (kWh/100km)
        self.num_ev_features = self.ev_features.shape[0]

        self.max_distance = 50  # Maximum distance to a station (km)
        self.max_charging_rate = 350  # Maximum charging rate available at a station (kW)
        self.max_price = 10  # Maximum price per kWh ($)

        # Define station features' min max bounds
        station_feature_bounds = np.array([[1, self.max_distance],  # Distance to the station (0-50 km)
                                           [1, 10],  # Max Charging Spots (1-10)
                                           [0, 10],  # Occupied Charging Spots (0 to Max Charging Spots)
                                           [0, self.max_charging_rate],  # Current charging rate available (kW)
                                           [2, self.max_price],  # Price per kWh ($)
                                           [0, 5]])  # Rating of the charging station (0-5)
        self.num_station_features = station_feature_bounds.shape[0]

        # Repeat station feature bounds for max_stations and concatenate with EV features
        self.all_stations_features = np.repeat(station_feature_bounds[np.newaxis, :, :], max_stations, axis=0)
        total_bounds = np.concatenate((self.ev_features, self.all_stations_features.reshape(-1, 2)), axis=0)

        self.observation_space = spaces.Box(low=total_bounds[:, 0], high=total_bounds[:, 1], dtype=np.float32)

        self.state = None

    def reset(self):
        # Initialize state with zeros for padding
        self.state = np.zeros(self.observation_space.shape[0])

        
        # EV'nin batarya seviyesini ve ortalama tüketimini rastgele değerlerle belirle
        self.state[0] = np.random.uniform(5.5, 100)  # Batarya seviyesi yüzde olarak (10% ile 100% arası)
        self.state[1] = np.random.uniform(4.5, 35)  # Ortalama tüketim (15 ile 25 kWh/100km arası)

        # Mevcut istasyonların dinamik bir sayısını varsayalım (en fazla max_stations)
        # Bu, haritada 5 istasyondan az istasyon olduğunda için, veya 5 olarak ayarlayabiliriz
        num_available_stations = np.random.randint(1, self.max_stations + 1)

        # İstasyonların özelliklerini gerçekçi değerlerle doldur
        for i in range(num_available_stations):
            start_idx = self.num_ev_features + (i * self.num_station_features)
            
            # Her bir istasyon için gerçekçi özellik değerlerini oluştur
            distance = np.random.uniform(1, self.max_distance)  # İstasyona uzaklık (km cinsinden)
            max_spots = np.random.randint(1, 11)  # Maksimum Şarj Yerleri
            occupied_spots = np.random.randint(0, max_spots + 1)  # Dolu Şarj Yerleri, maksimum şarj yerlerine eşit veya küçük olacak şekilde
            all_time_kw = np.random.uniform(22, self.max_charging_rate)  # Dolu olmayan zamanlarda maksimum şarj hızı
            charging_rate = (max_spots - occupied_spots) / 10 * all_time_kw  # Mevcut şarj hızı kW cinsinden
            price = np.random.uniform(2, self.max_price)  # kWh başına fiyat
            rating = np.random.uniform(0, 5)  # Şarj istasyonunun derecesi

            self.state[start_idx:start_idx + self.num_station_features] = [distance, max_spots, occupied_spots,
                                                                        charging_rate, price, rating]
        return self.state


    def step(self, action):
        """
        Take an action and return the new state, reward, done, and info.
        In this single-step scenario, done is always True after one step.
        """

        reward = self._calculate_reward(action)
        done = True  # Single-step scenario
        info = {}  # Additional data can be returned here
        return self.state, reward, done, info

    def _calculate_reward(self, action):
        """
        Calculate the reward for choosing a specific station, considering occupancy.
        """
        if action == self.max_stations:  # Action to not choose any station
            return -10  # Arbitrary penalty for not choosing a station

        # Extract station features from state
        station_idx = self.num_ev_features + action * self.num_station_features  # Calculate index in state array
        station_features = self.state[station_idx:station_idx + self.num_station_features]

        distance, max_spots, occupied_spots, charging_rate, price, rating = station_features

        # Check if chosen station is a padded (non-existent) station
        if max_spots == 0:
            return -10  # Penalty for choosing a non-existent station

        # Constants for weighting
        alpha = 5.0  # Adjusted weight for charging rate importance
        beta = 2.0  # Adjusted weight for distance importance
        gamma = 3.0  # Adjusted weight for price sensitivity
        delta = 1.0  # Weight for rating

        # Normalize features
        normalized_charging_rate = charging_rate / self.max_charging_rate
        normalized_distance = distance / self.max_distance
        normalized_price = price / self.max_price

        # Compute reward with adjustments for scale
        reward = (alpha * normalized_charging_rate) - (beta * normalized_distance ** 2) - (gamma * normalized_price) + (
                delta * rating)

        return reward

    def render(self, mode='console'):
        if mode != 'console':
            raise NotImplementedError('Only console mode is supported.')
        print(f'State: {self.state}, Action space: {self.action_space}')
    
    #TODO : checkleme kısmının entegrasyonu
    def select_best_station(self, stations):
        best_station = None
        best_reward = float('-inf')  # Başlangıçta en iyi ödülü negatif sonsuz olarak ayarlayın
        for station in stations:
            # Her istasyon için ödülü hesaplayın
            reward = self._calculate_reward(station)
            # Eğer bu istasyonun ödülü, şu ana kadar görülen en iyi ödül ise
            if reward > best_reward:
                best_reward = reward
                best_station = station
        return best_station

