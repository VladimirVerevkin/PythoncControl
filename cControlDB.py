# PostgreSQL
import psycopg2

class DBcControl:
 
    def __init__(self):
        """ Constructor """
        self.connection = psycopg2.connect(
            user = "pi",
            password = "1234",
            host = "127.0.0.1",
            port = "5432",
            database = "ccontrol"
            )
        print("Database opened successfully")
    
    
    def read_all_table(self, name_table):
        """ Чтение всей таблицы с именем name_table """
        print(" --- read_table - " + name_table + " ---")
        cursor = self.connection.cursor()
        mySQLQuery = """SELECT * FROM """ + name_table + """;"""
        cursor.execute(mySQLQuery)
        result = cursor.fetchall()
        cursor.close
        self.connection.close()
        return result

    # ****** ****************** методы для работы с таблицой sensors ******************************************

    # заполнить таблицу sensors значениями по умолчанию
    def fill_in_table_sensors(self, con='not_conn', set_Temp=0, set_Humid=100, set_Rele='off', set_comment=''):
        print(" --- fill_in_table_sensors --- ")
        cursor = self.connection.cursor()
        mySQLQuery = ("""TRUNCATE sensors;""") # Опустошение таблицы sensors
        cursor.execute(mySQLQuery)
        for idSensor in range(0,256,1):
            mySQLQuery = ("""INSERT INTO sensors VALUES ("""+str(idSensor)+""", '"""+str(con)+"""', """
                                                             +str(set_Temp)+""", """+str(set_Humid)+""", '"""
                                                             +str(set_Rele)+"""', '"""+str(set_comment)+"""');""" )
            cursor.execute(mySQLQuery)
        self.connection.commit()
        cursor.close
        self.connection.close()
                       
    # обновить значение(строку) в таблице sensors    
    def update_tab_sensors(self, idSensor, con='not_conn', set_Temp=0, set_Humid=100, set_Rele='off', set_comment=''):
        """ Обновление строки в таблице sensors,
            Строка выбирается из столбца idsensor со значением idSensor
        """
        print(" --- update_tab_sensors --- ")
        cursor = self.connection.cursor()
        mySQLQuery = ("""UPDATE sensors SET connect='"""+str(con)+"""', settemp="""+str(set_Temp)+""", sethumid="""
                                                        +str(set_Humid)+""", rele='"""+str(set_Rele)+"""', comment='"""
                                                        +str(set_comment)+"""' WHERE idsensor="""+str(idSensor)+""";""") 
        cursor.execute(mySQLQuery)
        self.connection.commit()
        cursor.close
        self.connection.close()
    
    # получить строку из таблицы sebsors по idSensor - по номеру(адресу) датчика
    def get_data_sensor(self, idSensor):
        """ Получить строку из таблицы sensors в виде списка
        """
        print(" --- get_data_sensors --- ")
        cursor = self.connection.cursor()
        mySQLQuery = ("""SELECT * FROM sensors WHERE idsensor='"""+str(idSensor)+"""';""")
        cursor.execute(mySQLQuery)
        result = cursor.fetchall()
        cursor.close
        self.connection.close()
        return result
    
    # получить список подключенных датчиков
    def get_connect_sensors(self):
        """ Получение списка подключенных датчиков и их настройки из таблицы sensors
        """
        print(" --- get_connect_sensors --- ")
        cursor = self.connection.cursor()
        mySQLQuery = ("""SELECT idsensor FROM sensors WHERE connect='conn' ORDER BY idsensor ASC;""")
        cursor.execute(mySQLQuery)
        #result = cursor.fetchone()
        result = []
        while True:
            tmp = cursor.fetchone()
            if tmp:
                result.append(tmp[0])
            else:
                break    
        cursor.close
        self.connection.close()
        return result
    
    # чтение comment по idSensor - комментарий к датчику
    def get_comment_sensors(self,idSensor):
        """ Возвращается значение поля comment датчика с адресом idSensor  
        """
        print(" --- get_comment_sensors --- ") 
        cursor = self.connection.cursor()
        mySQLQuery = ("""SELECT comment FROM sensors WHERE idsensor='"""+str(idSensor)+"""';""")
        cursor.execute(mySQLQuery)
        result = cursor.fetchone()
        cursor.close
        self.connection.close()
        return result[0]
    
    # обновить список подключенных датчиков(обновить значения в столбце connect)
    def update_connect_sensors(self, sensors):
        """ Обновление в таблице sensors столбца connect
            В столбце connect все значения устанавливаются в not_conn,
            после чего устаналвиаются conn где idsensor == sensors
        """
        print(" --- update_connect_sensors --- ")
        cursor = self.connection.cursor()
        mySQLQuery = ("""UPDATE sensors SET connect='not_conn' WHERE connect='conn';""") 
        cursor.execute(mySQLQuery)
        self.connection.commit()
        mySQLQuery = ("""UPDATE sensors SET connect='conn' WHERE""")
        for i in range(0,len(sensors),1):
            if i==0:
                mySQLQuery += " idsensor='"+str(sensors[i])+"'"
            else:
                mySQLQuery += " OR idsensor='"+str(sensors[i])+"'"
        mySQLQuery += ";"
        cursor.execute(mySQLQuery)
        self.connection.commit()
        cursor.close
        self.connection.close()

    # обновить значение установленной температуры датчика(обновить значения в столбце settemp)
    def update_setTemper_sensor(self, data):
        """ Обновление в таблице sensors значение settemp для сенсора c idSensor
        """
        idSensor = data[0]
        setTemper = str(data[1])
        print(" --- update_setTemper_sensor --- ")
        cursor = self.connection.cursor()
        mySQLQuery = ("""UPDATE sensors SET settemp='"""+str(setTemper)+"""' WHERE idsensor='"""+str(idSensor)+"""';""")
        print(mySQLQuery)
        cursor.execute(mySQLQuery)
        self.connection.commit()
        cursor.close
        self.connection.close()


    # обновление comment по idSensor - комментарий к датчику
    def update_comment_sensor(self, data):
        """ Обновление в таблице sensors поля comment датчика с idSensor
        """
        print(" --- update_comment_sensors --- ") 
        idSensor = data[0]
        comment = str(data[1])
        print(str(idSensor))
        print(comment)
        cursor = self.connection.cursor()
        mySQLQuery = ("""UPDATE sensors SET comment='"""+comment+"""' WHERE idsensor='"""+str(idSensor)+"""';""")
        cursor.execute(mySQLQuery)
        self.connection.commit()
        cursor.close
        self.connection.close()


# ************************ методы для работы с таблицой history ******************************************
    def add_data_history(self, idSensor, Temper, setTemper, Humid, setHumid, controlRele, statusRele, power):
        print(" --- add_data_history --- ")
        cursor = self.connection.cursor()
        mySQLQuery = ("""INSERT INTO history (idsensor, temper, settemper, humid, sethumid, controlrele, statusrele, power, seltime) VALUES ( """
                        +str(idSensor)+""", """+str(Temper)+""", """+str(setTemper)+""", """
                        +str(Humid)+""", """+str(setHumid)+""", '"""+str(controlRele)+"""', '"""
                        +str(statusRele)+"""', """+str(power)+""", """+"now()"+""");""")   
        print('add_data_history mySQLQuery: '+ mySQLQuery) 
        cursor.execute(mySQLQuery)
        self.connection.commit()
        cursor.close
        self.connection.close()
        

if __name__ == "__main__":
    print(" ***** Запущен файл cControl.py ***** ")
    DB = DBcControl()
    #DB.update_connect_sensors(10)
    #print(DB.get_comment_sensors(85))
    #DB.update_comment_sensors(80,'это для теста')
    DB.update_setTemper_sensor(80,5)
    #DB.fill_in_table_sensors() # значения по умочанию в таб. sensors
    #DB.update_tab_sensors(104, "conn", 4, 85, "off", "Датчик на улице")
    #print(DB.get_data_sensors(5))
    #print(DB.get_connect_sensors())
    #DB.add_data_history(1, 25, 2.5, 65, 87, "temp","off", 75)
    #print(DB.read_all_table("sensors"))
   