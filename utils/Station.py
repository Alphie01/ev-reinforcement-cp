import pandas as pd
import json

class Stations:
    def __init__(self, json_file):
        self.stations = None
        self.stations = self.load_stations_from_json(json_file)

    def load_stations_from_json(self, json_file):
        with open(json_file, 'r') as file:
            data = json.load(file)
        
        istasyonlar = []
        for istasyon in data:
            occupied_spots = int(istasyon['doluluk'].split('/')[0])
            max_spots = int(istasyon['doluluk'].split('/')[1])
            all_time_kw = float(istasyon['all_time_kw'])
            current_kw = float(istasyon['current_kw'])
            price = int(istasyon['price'])
            place = int(istasyon['place'])
            istasyon_dict = {
                "occupied_spots": occupied_spots,
                "max_spots": max_spots,
                "all_time_kw": all_time_kw,
                "current_kw": current_kw,
                "price" : price,
                "place" : place
                
            }
            istasyonlar.append(istasyon_dict)
        
        return istasyonlar