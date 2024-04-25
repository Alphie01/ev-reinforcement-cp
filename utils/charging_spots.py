
import json
from utils.Calculations import Calculations



calculation = Calculations()

class ChargingSpots():
    
    def __init__(self, json_file):
        self.data = None
        self.data = json_file
    
    def charging_spots(self, lat, longitude, maxCount = 5):
            # JSON dosyasından verileri al


        en_iyi_5_sarj_istasyonlari = []
        for istasyon in self.data:
            doluluk = calculation.doluluk_duzelt(istasyon["station_doluluk"])
            if doluluk == 10:
                continue

            istasyon_latitude = istasyon["station_latitude"]
            istasyon_longitude = istasyon["station_longitude"]

            mesafe = calculation.mesafe_hesapla(lat, longitude, istasyon_latitude, istasyon_longitude)

            skor = calculation.skor_hesapla(istasyon)

            if len(en_iyi_5_sarj_istasyonlari) < maxCount:
                en_iyi_5_sarj_istasyonlari.append({'istasyon': istasyon, 'mesafe':  mesafe, 'skor':  skor})
                en_iyi_5_sarj_istasyonlari.sort(key=lambda x: x['mesafe'])
            else:
                en_iyi_5_sarj_istasyonlari.sort(key=lambda x: x['mesafe'])
                if mesafe < en_iyi_5_sarj_istasyonlari[4]['mesafe']:
                    en_iyi_5_sarj_istasyonlari.pop()
                    en_iyi_5_sarj_istasyonlari.append({'istasyon': istasyon, 'mesafe':  mesafe, 'skor':  skor})
        return en_iyi_5_sarj_istasyonlari
