from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from pyModbusTCP.client import ModbusClient
from simple_pid import PID
#import mysql.connector


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:qyxZog-totsaj-qidco0@localhost:3306/temperature_data'
db = SQLAlchemy(app)


host = "192.168.10.200"
c = ModbusClient(host=host, auto_open=True, auto_close=True)
temperature_reg = 6
heating_reg = 4

#Ergänzung des Modbus Clients
desired_temperature = 27.0
kp = 1.0
ki = 2.0
kd = 0.1
pid = PID(kp, ki, kd, setpoint=desired_temperature)
pid.output_limits = (0, 100)


class Temperature(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    value = db.Column(db.Float, nullable=False)


@app.route('/temperature', methods=['POST'])
def save_temperature():
    temperature = request.json['temperature']
    new_temperature = Temperature(value=temperature)
    db.session.add(new_temperature)
    db.session.commit()
    return 'Temperature saved successfully.'

@app.route('/temperature-data', methods=['GET'])
def get_temperature_data():
    temperatures = Temperature.query.all()
    temperature_values = [temperature.value for temperature in temperatures]
    return jsonify({'temperatures': temperature_values})
    

@app.route('/pid', methods=['GET', 'POST'])
def pid_control():
    if request.method == 'GET':
        #Gib die aktuellen PID-Parameter zurück
        return jsonify({'kp': pid.Kp, 'ki': pid.Ki, 'kd': pid.Kd})
    elif request.method == 'POST':
        #Aktualisiere die PID-Parameter mit den übergebenen Werten
        data = request.json
        kp = data['kp']
        ki = data['ki']
        kd = data['kd']
        pid.tunings = (kp, ki, kd)
        return 'PID parameters updated successfully.'
    
@app.route('/start-heating', methods=['POST'])
def start_heating():
    #Hier startet der Heizvorgang
    c.write_single_register(heating_reg, value=0, step=1)
    return 'Heating started successfully.'

def schreibewert(value, reg):
    value *= 327.67
    c.write_single_register(reg, int(value))

@app.route('/delete-temperature-data', methods=['POST'])
def delete_temperature_data():
    #Löschen der Temperaturdaten aus der Datenbank
    Temperature.query.delete()
    db.session.commit()
    return 'Temperature data deleted successfully.'

def PIDRegelung():
    while True:
        #Lesen der aktuellen Temperatur
        temperature = c.read_holding_registers(temperature_reg, 1)
        #temperature = temperature[0] / 10.0
        temperature = round(float(temperature[0]) / 10, 1)
        print(f'temp: {temperature}')

        #Berechnung des Heizwertes mittels dem PID-Controller
        heating_value = pid(temperature)
        print(f'PID output: {heating_value}')
        
        #heating_reg = st.number_input("Heating Register:", value=0, step=1)

        schreibewert(heating_value, heating_reg)

        #Der Code für die Kommunikation mit dem Modbus-Server und für das Schreiben des Heizwerts
        save_temperature(temperature)

        #Zeitschleife
        #time.sleep(2)

def main():
    PIDRegelung()

if __name__ == '__main__':
    main()

