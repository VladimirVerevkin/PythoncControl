# pyhton 3
from serialPort import Sport

class Sensor:
    
    # ****************************************************
    # **************** декодирование данных **************
    # ****************************************************
    
    # декодирование данных темперетуры
    def decoding_temper(self, tem1, tem0, type_sensor):
        if type_sensor == "HDC1080":
            temp = tem1*256+tem0
            temp *= 165
            temp /= 65536
            temp -= 40            
        return temp

    # декодирование установленной температуры
    def decoding_set_temper(self, tem):
        """ Формат установленной температуры: младший байт - бробная часть 1=0.5град, 0=0град.
            Остальная часть(чтаршие биты) - целая часть значения установленной температуры.
            Пример: 1) 0b00010010 ~ 9.0град.     2) 0b00010011 ~ 9.5град.
        """
        f = 0
        if tem & 0x01:
            f=0.5
        return ((tem>>1)+f)

    # декодирование источник(параметр) управления реле 
    def decoding_control_rele(self,con):
        """ Если значение con = 0x0A - управление реле осуществляется по температуре
            если значение con = 0x14 - управление реле осуществяется по влажности
        """
        if con == 0x0A:
            return "temper"
        else:
            return "humid"
    
    # декодирование состояния реле
    def decoding_status_rele(self, status):
        """ Если значение status = 0x3F - реле выключено(нагрузка отключена)
            если значение status = 0x1F - реле включено (нагрузка включена)
        """
        if status == 0x1F:
            return "relay ON"
        else:
            return "relay OFF"


    # декодирование данных влажности
    def decoding_humid(self, hum1, hum0, type_sensor):
        """ Декодирование данных влажности, возвращиется значение относительной влажности (%)
        """
        if type_sensor == "HDC1080":
            hum = (hum1*256+hum0)*100
            hum /=65536
        return hum
    
    # проверка контрольной суммы
    def crc(self, data: list):
        """ проверка контрольной суммы 
        """
        a = list(data)
        a.pop()
        in_CRC = data[len(a)-1]
        a.pop()
        CRC = 0
        for i in a:
            CRC += i
            temp_CRC = CRC>>2
            CRC ^=temp_CRC
        CRC = CRC & 0xFF
        if CRC == in_CRC:
            return True
        else:
            return False
    # декодирование данных полученных от датчика
    def decoding_data_sensor(self,id_sensor, data: list):
        """ Декодирование
        """ 
        idSensor=temper=set_temper=control_rele=power=status_rele=humid=set_humid=0
        if data == []:
            idSensor = id_sensor
        elif self.crc(data): # проверка контрольной суммы
            idSensor = data[0]
            temper = self.decoding_temper(data[1], data[2], "HDC1080")
            temper = float('{:.2f}'.format(temper))
            set_temper = self.decoding_set_temper(data[3])
            control_rele = self.decoding_control_rele(data[4])
            power = data[5] # ????
            status_rele = self.decoding_status_rele(data[6])
            humid = self.decoding_humid(data[7],data[8],"HDC1080")
            humid = float('{:.2f}'.format(humid))
            set_humid = data[9]
        
        return(idSensor, temper, set_temper, control_rele, power, status_rele, humid, set_humid)

    # ***********************************************************

    def readData(self, idSensor):
        """ чтение данных сенсора по idSensor
            возвращает список декодированных данных    
        """
        sData = Sport().read_data_sensor(idSensor)
        return Sensor().decoding_data_sensor(idSensor, sData)
    
    def scannSensors(self):
        """ сканирование 
            возвращает список адресов подключенных датчиков    
        """
        return Sport().scannSensors()

    def writeData(self, idSensor:int, typeParam='', data=0):
        """ передача данных в датчик с адресом idSensor, 
            typeParam - тип передоваемого параметра: температура, влажности...,
            data - значение
        """
        print(" -- writeData --")
        a=0
        if typeParam == "temper":
            a = Sport().set_set_temper(idSensor,data) 
        elif typeParam == "humid":
            a = Sport().set_set_humid(idSensor,data)
        elif typeParam == "control":
            a = Sport().set_control_rele(idSensor,data)
        return 1 if a == 0x38 else 0  

    def setAddressSensor(self, idSensor):
        """ Установка адреса датчика 
            Если адрес присвоен успешно возврашается 1, иначе 0    
        """
        a = Sport().assign_adress_sensor(idSensor)
        return 1 if a == 0x38 else 0

if __name__ == "__main__":
    #print(Sensor().readData(82))
    #print(Sensor().scannSensors())
    #i = [0,1,2,3,4,5]
    #idSensor = [25,12,1,13,50,0]
    #d = {j:idSensor[j] for j in range(0,len(idSensor),1)}
    #print(d)
    #print(Sensor().setAddressSensor(84))
    Sensor().writeData(85,'control',0x14)
