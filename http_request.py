import hashlib
import json
import random
import secrets
from flask import Flask, request, jsonify

from main import ReinforcementAIModel
from utils.Calculations import Calculations
from utils.charging_spots import ChargingSpots
import mysql.connector

app = Flask(__name__)

calculation = Calculations()

model = ReinforcementAIModel()


""" DATABASE CONNECTİON """
db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="ev_admin_user",
        database="deneme"
)
cursor = db.cursor(dictionary=True)



@app.route('/directions', methods=['POST'])
def get_directions():
    if 'search' in request.form:
        sql = "SELECT * FROM station WHERE station_displayName LIKE %s LIMIT 8"
        cursor.execute(sql, ('%' + request.form['search'] + '%',))  # Parametreleri (tuple) verme
        result = cursor.fetchall()
        return jsonify({'id': 0, 'returns': result})
    
    sql = "SELECT * FROM station"
    cursor.execute(sql, (request.form))
    stations = cursor.fetchall()
    chargingSpots = ChargingSpots(json_file=stations)
    
    if 'get_direction' in request.form:
        kullanici_latitude = float(request.form['lat'])
        kullanici_longitude = float(request.form['long'])
        maxCount = 5
        if 'max_station' in request.form:
            maxCount = int(request.form['max_station'])

        en_iyi_5_sarj_istasyonlari = chargingSpots.charging_spots(lat=kullanici_latitude, longitude=kullanici_longitude, maxCount=maxCount)
        return jsonify({'id': 0, 'returns': en_iyi_5_sarj_istasyonlari})
    if 'get_best_direction' in request.form:
        kullanici_latitude = float(request.form['lat'])
        kullanici_longitude = float(request.form['long'])
        best_station = []
        en_iyi_5_sarj_istasyonlari = chargingSpots.charging_spots(lat=kullanici_latitude, longitude=kullanici_longitude)

        #TODO ai kısmının entegresi response olarak best_station ==

        return jsonify({'id': 0, 'returns': best_station})

@app.route('/comments', methods=['POST'])
def station_comments():
    if 'station_comments' in request.form and 'station_id' in request.form:
        try:
            sql = "SELECT * FROM station_review WHERE station_review_stationId=%s"
            cursor.execute(sql, (request.form['station_id'],))  # Parametreleri (tuple) verme
            result = cursor.fetchall()
            return jsonify({'id': 0, 'returns': result})
        except:
            return jsonify({'id':-1})
    
    if 'create_new_comment' in request.form and 'station_review_stationId' in request.form:
        try:
            cursor.execute("SELECT * FROM station_review WHERE station_review_stationId = %s and station_review_authorId=%s", (request.form['station_review_stationId'],request.form['user_id'],))
            user_exists = cursor.fetchone()
            if user_exists:
                return jsonify({'error': 'Daha Önceden Yorum Yapılmış.', 'return' : user_exists})
            
            kullanicikaydet_query = """INSERT INTO station_review 
                                        (station_review_stationId, station_review_rating, station_review_authorName, station_review_text, station_review_authorId)
                                        VALUES (%s, %s, %s, %s, %s)"""

            kullanicikaydet_data = (request.form['station_review_stationId'],request.form['station_review_rating'],request.form['station_review_authorName'],request.form['station_review_text'],request.form['user_id'],)

            cursor.execute(kullanicikaydet_query, kullanicikaydet_data)
            db.commit()
            return json.dumps({'id': '0'}), 200
        except:
            jsonify({'id' : -1})
    if 'update_comment' in request.form and 'station_review_id' in request.form and 'user_id' in request.form:
        try:
            sql = """UPDATE station_review SET 
                        station_review_stationId=%s, station_review_rating=%s, station_review_authorName=%s, station_review_text=%s
                        WHERE station_review_authorId=%s AND station_review_id=%s"""
            cursor.execute(sql, (request.form['station_review_stationId'],request.form['station_review_rating'],request.form['station_review_authorName'],request.form['station_review_text'],request.form['user_id'],request.form['station_review_id'],))
            db.commit()
            
            if cursor.rowcount > 0:
                return jsonify({'id': 0})
        except:
            return jsonify({'id': -1, 'message': 'Güncelleme başarısız oldu.'})
    
    if 'delete_comment' in request.form and 'station_review_id' in request.form and 'user_id' in request.form:
        try:
            sql = "DELETE FROM station_review WHERE station_review_id=%s AND station_review_authorId=%s"
            cursor.execute(sql,(request.form['station_review_id'],request.form['user_id'],))
            db.commit()
            return jsonify({'id': 0})
        except:
            return jsonify({'id': -1, 'message': 'Silme başarısız oldu.'})

@app.route('/user', methods=['POST'])
def userRequests():
    if 'fetchUserByMail' in request.form:
        if 'kullanici_mail' in request.form and 'kullanici_password' in request.form:
            kullanici_mail = request.form['kullanici_mail']
            kullanici_password = hashlib.md5(request.form['kullanici_password'].encode()).hexdigest()

            sql = "SELECT * FROM kullanici WHERE kullanici_mail=%s AND kullanici_password=%s"
            cursor.execute(sql, (kullanici_mail, kullanici_password))
            kullanici = cursor.fetchone()

            if kullanici:
                returns = {
                    'id': 0,
                    'kullanici': kullanici
                }
                return jsonify(returns)
            else:
                return jsonify({'id': -1, 'message': 'Kullanıcı bulunamadı.'})
            
        else:
            return jsonify({'id': -1, 'message': 'Eksik parametre.'})
        
    if 'fetchUserByToken' in request.form:
        if 'userToken' in request.form:
            kullanici_secret_token = request.form['userToken']

            sql = "SELECT * FROM kullanici WHERE kullanici_secretToken=%s"
            cursor.execute(sql, (kullanici_secret_token,))
            kullanici = cursor.fetchone()
            if kullanici:
                returns = {
                    'id': 0,
                    'kullanici': kullanici
                }
                return jsonify(returns)
            else:
                return jsonify({'id': -1, 'message': 'Kullanıcı bulunamadı.'})
                
        else:
            return jsonify({'id': -1, 'message': 'Eksik parametre.'})
    
    if 'kullanici_register' in request.form:
        try:
            cursor.execute("SELECT * FROM kullanici WHERE kullanici_mail = %s", (request.form['kullanici_mail'],))
            user_exists = cursor.fetchone()
            if user_exists:
                return json.dumps({'error': 'Bu e-posta adresi zaten kullanımda'}), 400

            random_mail_key = random.randint(1000, 9999)
            kullanici_yetki = 0
            token = secrets.token_hex(16)
            kullanici_passwordone = request.form['kullanici_password']
            password = hashlib.md5(kullanici_passwordone.encode()).hexdigest()

            kullanicikaydet_query = """INSERT INTO kullanici 
                                    (kullanici_adsoyad, kullanici_mail, kullanici_password, kullanici_gsm, kullanici_gender,
                                    kullanici_adres, kullanici_ad, kullanici_mail_key, kullanici_secretToken, kullanici_yetki)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

            kullanicikaydet_data = (request.form['kullanici_adsoyad'], request.form['kullanici_mail'], password,
                                    request.form['kullanici_gsm'], request.form['kullanici_gender'], request.form['kullanici_adres'],
                                    request.form['kullanici_ad'], random_mail_key, token, kullanici_yetki)

            cursor.execute(kullanicikaydet_query, kullanicikaydet_data)
            db.commit()

            # E-posta gönderme ve başarılı yanıt hazırlama
            # sendMail fonksiyonunu kullanarak e-posta gönderme işlemi burada yapılabilir

            return json.dumps({'id': '0'}), 200
        except:
            json.dumps({'id':-1})
        
    if 'user_update' in request.form:
        try:
            kullanici_mail = request.form['kullanici_mail']
            kullanici_ad = request.form['kullanici_ad']
            kullanici_gsm = request.form['kullanici_gsm']
            kullanici_tc = request.form['kullanici_tc']
            kullanici_adsoyad = request.form['kullanici_adsoyad']
            kullanici_adres = request.form['kullanici_adres']
            kullanici_il = request.form['kullanici_il']
            kullanici_ilce = request.form['kullanici_ilce']
            kullanici_birthDate = request.form['kullanici_birthDate']
            kullanici_gender = request.form['kullanici_gender']
            kullanici_secretToken = request.form['kullanici_secretToken']

            if kullanici_birthDate:
                mysql_date = kullanici_birthDate
            else:
                mysql_date = '2024-01-01'

            sql = """UPDATE kullanici SET 
                        kullanici_mail=%s, kullanici_ad=%s, kullanici_gsm=%s, kullanici_adsoyad=%s, 
                        kullanici_adres=%s, kullanici_il=%s, kullanici_ilce=%s, kullanici_tc=%s, 
                        kullanici_birthDate=%s, kullanici_gender=%s
                        WHERE kullanici_secretToken=%s"""
            cursor.execute(sql, (kullanici_mail, kullanici_ad, kullanici_gsm, kullanici_adsoyad, 
                                kullanici_adres, kullanici_il, kullanici_ilce, kullanici_tc, 
                                mysql_date, kullanici_gender, kullanici_secretToken))
            db.commit()
            if cursor.rowcount > 0:
                return jsonify({'id': 0})
        except:
            return jsonify({'id': -1, 'message': 'Güncelleme başarısız oldu.'})

"""     if 'resend_mail_key' in request.form:
        
    if 'check_mail_key' in request.form: """




@app.route('/get_cars', methods=['POST'])
def get_cars():
    
    if 'araba_id' in request.form:
        try:
            cursor.execute("SELECT * FROM arabalar WHERE araba_id = %s", (request.form['araba_id'],))
            cars = cursor.fetchone()
            return jsonify({'id': 0, 'returns': cars})
        except:
            return json.dumps({'id' : 1})
        

    cursor.execute("SELECT * FROM arabalar")
    cars = cursor.fetchall()

    return jsonify({'id': 0, 'returns': cars})



if __name__ == '__main__':

    all_episodes_completed = model.initAI()
    if all_episodes_completed:
        app.run(debug=True, port=9000, host='192.168.0.6')