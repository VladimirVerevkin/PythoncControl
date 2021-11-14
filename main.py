# python3 main.py
from flask import Flask, request, Response, current_app
from sensor import Sensor
from cControlDB import DBcControl
from flask_cors import CORS, cross_origin
from flask_apscheduler import APScheduler
import time
import atexit

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# 
def returnJSONSensor(idSensor:int):
    rSensor = Sensor().readData(idSensor) # чтение данных датчка с адресом idSensor
    titleSensor = DBcControl().get_comment_sensors(idSensor) 
    jsonD =  {
        "title": titleSensor,
        "sensor_id": rSensor[0],
        "temper": rSensor[1],
        "setTemper": rSensor[2],
        "controlRele" : rSensor[3],
        "power": rSensor[4],
        "statusRele": rSensor[5],
        "humid": rSensor[6],
        "setHumid": rSensor[7],   
    }
    return jsonD


@app.route('/scannSensors')
@cross_origin()
def scannSensor():
    idSensors = Sensor().scannSensors() #  получить id подключенных датчиков(список) 
    # преобразование списка в словарь
    #idSensors_json = {j:idSensors[j] for j in range(0,len(idSensors),1)}
    return str(idSensors)


@app.route('/readSensor')
@cross_origin()
def readSensor():
    idSensor = int(request.args.get('id'))
    try:
        jsonD = returnJSONSensor(idSensor)
    #     rSensor = Sensor().readData(int(idSensor)) # чтение данных датчка с адресом idSensor
    #     titleSensor = DBcControl().get_comment_sensors(int(idSensor)) 
    #     jsonD =  {
    #         "title": titleSensor,
    #         "sensor_id": rSensor[0],
    #         "temper": rSensor[1],
    #         "setTemper": rSensor[2],
    #         "controlRele" : rSensor[3],
    #         "power": rSensor[4],
    #         "statusRele": rSensor[5],
    #         "humid": rSensor[6],
    #         "setHumid": rSensor[7],   
    #     }
        return jsonD
    except Exception:
        return Response("{'Ошибка':'Датчик не найден'}", status=404, mimetype='application/json')

@app.route('/getSensors')
@cross_origin()
def getSensors():
    idSensors = DBcControl().get_connect_sensors()
    return str(idSensors)
    
@app.route('/writeSensor')
@cross_origin()
def writeSensor():
    #idSensor = 82
    idSensor = request.args.get('id')
    param = request.args.get('param')
    data = request.args.get('data')
    wSensor = Sensor().writeData(int(idSensor),str(param),int(data)) # чтение данных датчка с адресом idSensor
    return str(wSensor)

@app.route('/setidSensor')
@cross_origin()
def setidSensor():
    address = request.args.get('addr')
    sAddrSensor = Sensor().setAddressSensor(int(address))
    return str(sAddrSensor)

@app.route('/updateConnectSensors', methods=['POST'])
@cross_origin()
def updateConnectSensors():
    request_data = request.get_json()
    #address = request.args.get('addr')
    DBcControl().update_connect_sensors(request_data)
    print('updateConnectSensors: '+request_data)
    return "ok"


@app.route('/updatetitle', methods=['POST'])
@cross_origin()
def updateCommentSensor():
    request_data = request.get_json()
    #address = request.args.get('addr')
    DBcControl().update_comment_sensor(request_data)
    print('updateCommentSenso: '+request_data)
    return "ok"


@app.route('/updatesetTemper', methods=['POST'])
@cross_origin()
def updatesetTemperSensor():
    request_data = request.get_json()
    #address = request.args.get('addr')
    DBcControl().update_setTemper_sensor(request_data)
    Sensor().writeData(int(request_data[0]), 'temper', int(request_data[1]))
    print('updatesetTemperSensor: '+request_data)
    return "ok"

@app.route('/updatesetHumid', methods=['POST'])
@cross_origin()
def updatesetHumidSensor():
    request_data = request.get_json()
    #address = request.args.get('addr')
    DBcControl().update_setTemper_sensor(request_data)
    Sensor().writeData(int(request_data[0]), 'humid', int(request_data[1]))
    print('updatesetHumidSensor: '+request_data)
    return "ok"

@app.route('/updatecontrolRele', methods=['POST'])
@cross_origin()
def updatecontrolReleSensor():
    request_data = request.get_json()
    #address = request.args.get('addr')
    DBcControl().update_setTemper_sensor(request_data)
    Sensor().writeData(int(request_data[0]), 'control', int(request_data[1]))
    print('updatecontrolReleSensor: '+request_data)
    return "ok"


#**************************************************************************
#---------------------------- Scheduler -----------------------------------
scheduler = APScheduler()

def scheduledTasck():
    print(" -- scheduledTasck -- ")
    idSensors = DBcControl().get_connect_sensors()  # получить адреса подключенных датчиков
    for idS in idSensors:
        print('scheduledTasck: '+str(idS))
        rSensor = Sensor().readData(int(idS))# считать данные с датчика
        print('scheduledTasck: '+ str(rSensor))
        DBcControl().add_data_history(rSensor[0],rSensor[1],rSensor[2],rSensor[6],rSensor[7],rSensor[3],rSensor[5],rSensor[4])# внести данные в таблицу history
        time.sleep(1) 
    print(' ** endScheduledTasck ** ')


if __name__ == "__main__":
    app.debug=True
    scheduler.add_job(id='Scheduled task', func = scheduledTasck, trigger = 'interval', seconds = 60)
    scheduler.start()
    app.run(host = '0.0.0.0', port=5000, use_reloader=False)
