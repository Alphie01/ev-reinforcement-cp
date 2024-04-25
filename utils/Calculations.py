import json
import math


class Calculations:
    def __init__(self):
        pass

    def araba_verilerini_al(self, araba_id):
        # Araba verilerini içeren JSON dosyasını oku
        with open('data/cars.json', 'r') as file:
            araba_verileri = json.load(file)

        # İlgili araba verilerini bul
        for araba in araba_verileri:
            if araba["id"] == araba_id:
                return araba

        # Eğer araba ID bulunamazsa None döndür
        return None

    def sarj_suresi_hesapla(self, araba_verileri, sarj_yuzdesi, istasyon_kw):
        if araba_verileri is not None:
            # Alternatif şarj cihazlarının listesi
            charger_list = araba_verileri["dc_charger"]["charging_curve"]

            charging_curve = None
            for curve in charger_list:
                if curve["percentage"] >= sarj_yuzdesi:
                    charging_curve = curve
                    break

            istasyon_max_power = istasyon_kw
            araba_max_power = araba_verileri["dc_charger"]["max_power"]

            sarj_suresi = (araba_verileri["usable_battery_size"] * (sarj_yuzdesi / 100) - araba_verileri["usable_battery_size"] * (charging_curve["percentage"] / 100)) / istasyon_max_power * 60

            return sarj_suresi
        return 0.0

    def doluluk_duzelt(self, doluluk):
        return int(doluluk.split("/")[0])

    def mesafe_hesapla(self, kullanici_lat, kullanici_lon, istasyon_lat, istasyon_lon):
        R = 6371.0

        lat1 = math.radians(kullanici_lat)
        lon1 = math.radians(kullanici_lon)
        lat2 = math.radians(float(istasyon_lat))
        lon2 = math.radians(float(istasyon_lon))

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        mesafe = R * c
        return mesafe

    def skor_hesapla(self, istasyon):
        return (float(istasyon["station_current_kw"]) / 350) + (1 - (float(istasyon["station_price"]) / 8.9)) + (self.doluluk_duzelt(istasyon["station_doluluk"]) / 10)