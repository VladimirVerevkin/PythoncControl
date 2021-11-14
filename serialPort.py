# python3 sportSerial.py

import serial
import RPi.GPIO as GPIO
import time

class Sport:
    
    #namePort = '/dev/serial0'
    #speedPort = 115200   
      
    def __init__(self):
        """Constructor"""
        self.ser = serial.Serial('/dev/serial0', 9600, timeout = 1)
        ''' настройки порта '''
        #self.ser = serial.Serial("/dev/serial0")
        self.ser.baudrate = 9600
        self.ser.timeout = 1
        GPIO.setmode(GPIO.BCM) #
        GPIO.setup(2, GPIO.OUT, initial=GPIO.LOW)
        print(' -- init serialPort -- ')

    # перевод Rpi в режим передачи или приема данных
    def set_bus_rw(self,route):
        """ Перевод в режим передачи данных Rpi - вывод gpio2 = 1 (route = 'tx')
            Перевод в режим приема данных Rpi - вывод gpio2 = 0
        """
        time.sleep(0.01)
        if route == "tx":
            # перевод ШД в режим write
            GPIO.output(2, GPIO.HIGH)
        else:
            # перевод ШД в режим read
            GPIO.output(2, GPIO.LOW)
        # пауза(для перехода)
        time.sleep(0.05)
    
    # чтение данных  - до 20 байт 
    def readPort(self):
        """ Чтение данных с последовательно порта 20 байт или по таймеру - timeout """
        return(self.ser.read(20))

    # присвоить датчику адрес
    def assign_adress_sensor(self,idSensor):
        """ присвоить адрес датчику адрес=idSensor
        """
        s = 0
        for i in 0xCC, 0xAA, 0xAA, 0xAA, idSensor:
            self.set_bus_rw("tx")
            self.ser.write(bytes([i]))
        self.set_bus_rw("rx")
        s = self.readPort()  
        return s[len(s)-1]
    
    # установить значение температуры
    def set_set_temper(self, idSensor, temper):
        s = 0
        if temper - int(temper) == 0:
            temper = int(temper) << 1
        else:
            temper = (int(temper) << 1) + 1

        for i in 0xCC, 0xAA, idSensor, 0x0F, 0x03, temper:
            self.set_bus_rw("tx")
            self.ser.write(bytes([i]))
        self.set_bus_rw("rx")
        s = self.readPort()  
        return s[len(s)-1]
    
    # установить значение влажности
    def set_set_humid(self, idSensor, humid):
        for i in 0xCC, 0xAA, idSensor, 0x0F, 0x06, humid:
            self.set_bus_rw("tx")
            self.ser.write(bytes([i]))
        self.set_bus_rw("rx")
        s = self.readPort()  
        return s[len(s)-1]
    
    # установить параметр управления реле нагрузки (от температуры или от влажности или выключено)
    def set_control_rele(self, idSensor, con):
        for i in 0xCC, 0xAA, idSensor, 0x0F, 0x09, con:
            self.set_bus_rw("tx")
            self.ser.write(bytes([i]))
        self.set_bus_rw("rx")
        s = self.readPort()  
        return s[len(s)-1]
    
    # чтение данны с датчика
    def read_data_sensor(self,idSensor):
        """ Чтение данных с датчика с адресом idSensor.
            Результат возвращается ввиде списка, данные в формате датчика.
        """
        for i in 0xCC, 0xAA, idSensor, 0xF0:
            self.set_bus_rw("tx")
            self.ser.write(bytes([i]))
        self.set_bus_rw("rx")
        s = list(self.readPort())  
        s.pop(0)
        return s 

    # сканирование датчиков
    def scannSensors(self):
        """ Сканирование шины для определения подключенных датчиков.
            Сканирование осуществляется перебором адресов от 0 до 255.
            Результат сканирования возвращается в виде списка адресов 
            подключенных датчиков.
        """
        idSensor = []
        for id_sensor in range(80,90,1):
            for j in 0xCC, 0xAA, id_sensor, 0xF0:
                self.set_bus_rw("tx")
                self.ser.write(bytes([j]))
            self.set_bus_rw("rx")
            s = self.readPort()
            if int(s[len(s)-1]) == 0x38: # если (последний)первый байт 0х38
                idSensor.append(id_sensor)  # внесение idSensor-а в список
        self.ser.close()
        return(idSensor)

   
if __name__ == "__main__":
    print('******** Запущен файл serialPort.py ***********')
    q = Sport()
    print(q.read_data_sensor(90))
    GPIO.cleanup()


