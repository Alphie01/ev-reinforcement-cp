from flask import Flask, request, jsonify
import json

from main import ReinforcementAIModel
from utils.Calculations import Calculations
from utils.charging_spots import ChargingSpots

app = Flask(__name__)

calculation = Calculations()
chargingSpots = ChargingSpots()
model = ReinforcementAIModel()

@app.route('/get_directions', methods=['POST'])
def get_directions():

    kullanici_latitude = float(request.form['lat'])
    kullanici_longitude = float(request.form['long'])
    maxCount = 5
    if 'max_station' in request.form:
        maxCount = int(request.form['max_station'])

    en_iyi_5_sarj_istasyonlari = chargingSpots.charging_spots(lat=kullanici_latitude, longitude=kullanici_longitude, maxCount=maxCount)
    return jsonify({'id': 0, 'returns': en_iyi_5_sarj_istasyonlari})

@app.route('/get_best_direction', methods=['POST'])
def get_best_directions():  # Farklı bir isim kullanıldı
    kullanici_latitude = float(request.form['lat'])
    kullanici_longitude = float(request.form['long'])

    en_iyi_5_sarj_istasyonlari = chargingSpots.charging_spots(lat=kullanici_latitude, longitude=kullanici_longitude)

    print(en_iyi_5_sarj_istasyonlari)
    """ station = model.selectBestSpot(stations=) """

    return jsonify({'id': 0, 'returns': []})


if __name__ == '__main__':

    all_episodes_completed = model.initAI()
    
    if all_episodes_completed:
        app.run(debug=True, port=3000)