import json
import logging

import ssl
import time
import certifi

from random import randint
from locust import User, task, between
from locust.exception import RescheduleTask
from websocket import create_connection, WebSocketConnectionClosedException
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.DEBUG)

class SocketTest(User):
    wait_time = between(2, 3)
    data_login = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "v1_webappPartnerLogin",
        "params": [
            {
                "phone": f"7999666{randint(10, 99)}{randint(10, 99)}",  # Генерация случайного номера телефона
                "acquisition_source": "VK"
            }
        ]
    }
    data_other = {
        "id": "1",
        "jsonrpc": "2.0",
        "params": []
    }

    def __init__(self, environment):
        super().__init__(environment)
        self.access_token = None
        self.is_task_completed = False
        self.ws = None  # Переменная для WebSocket соединения

    def on_start(self):
        # Метод на старте, можно использовать для инициализации, если нужно
        pass

    def on_stop(self):
        pass


    def success_request(self, start_time, response, name):
        total_time = int((time.time() - start_time) * 1000)  # Время в миллисекундах
        self.environment.events.request.fire(
            request_type="WebSocket",
            name=name,
            response_time=total_time,
            response_length=len(response),
            response="Success",
            exception=None,
        )

    def exception_request(self, start_time, name, e):
        total_time = int((time.time() - start_time) * 1000)  # Время в миллисекундах
        self.environment.events.request.fire(
            request_type="WebSocket",
            name=name,
            response_time=total_time,
            response_length=0,
            response="Failure",
            exception=e,
        )
        raise RescheduleTask()  # Перезапланировать задачу для выполнения позже

    @task
    def perform_sequence(self):
        if self.is_task_completed:
            return  # Прекратить выполнение, если задача уже была выполнена

        # Открыть WebSocket соединение
        # url_socket = os.getenv('url_socket')
        self.ws = create_connection(
            url="wss://devpartners.berizaryad.ru/ws",
            sslopt={
                "ca_certs": certifi.where(),
                "cert_reqs": ssl.CERT_REQUIRED
            }
        )

        try:
            # Тесты для локуса
            self.locus_nearest_loctions()
            time.sleep(1)
            self.locus_get_nearest_cluster()
            self.locus_get_cluster()
            time.sleep(1)
            self.filter_locus_nearest_loctions()
            self.filter_locus_get_nearest_cluster()
            self.filter_locus_get_cluster()
            time.sleep(1)
            self.filter_empty_locus_nearest_loctions()
            self.filter_empty_locus_get_nearest_cluster()
            self.filter_empty_locus_get_cluster()


        finally:
            # Закрыть соединение после выполнения всех задач
            if self.ws:
                logging.info("Closing WebSocket connection...")
                self.ws.close()
                self.ws = None  # Обнуление переменной после закрытия
            else:
                logging.info("WebSocket connection is already closed.")

        self.is_task_completed = True  # Установить флаг после выполнения задач

    def locus_nearest_loctions(self):
        data_cluster = self.data_other.copy()  # Копируем data, чтобы избежать изменения оригинала
        data_cluster["method"] = "v1_getNearestLocation"
        data_cluster["params"] = [{"latitude": randint(55, 58) + 0.8631039, "longitude": randint(37, 39)+ 0.6721449}]
        message_cluster = json.dumps(data_cluster)
        start_time = time.time()
        try:
            self.ws.send(message_cluster)  # Отправка сообщения
            response_cluster = self.ws.recv()  # Получение ответа
            self.success_request(start_time=start_time, response=response_cluster, name='nearest_loctions')
        except WebSocketConnectionClosedException as e:
            self.exception_request(start_time=start_time, name='nearest_loctions', e=e)
        except Exception as e:
            self.exception_request(start_time=start_time, name='nearest_loctions', e=e)


    def locus_get_nearest_cluster(self):
        data_cluster = self.data_other.copy()  # Копируем data, чтобы избежать изменения оригинала
        data_cluster["method"] = "v1_getNearestCluster"
        data_cluster["params"] = [{"latitude": randint(55, 58) + 0.8631039, "longitude": randint(37, 39) + 0.6721449}]
        message_cluster = json.dumps(data_cluster)
        start_time = time.time()
        try:
            self.ws.send(message_cluster)  # Отправка сообщения
            response_cluster = self.ws.recv()  # Получение ответа
            self.success_request(start_time=start_time, response=response_cluster, name='get_nearest_cluster')
        except WebSocketConnectionClosedException as e:
            self.exception_request(start_time=start_time, name='get_nearest_cluster', e=e)
        except Exception as e:
            self.exception_request(start_time=start_time, name='get_nearest_cluster', e=e)


    def locus_get_cluster(self):
        data_cluster = self.data_other.copy() # Копируем data, чтобы избежать изменения оригинала
        data_cluster["method"] = "v1_getClusters"
        data_cluster["params"] = [
            {"north_west":
                 {"latitude": randint(55, 59) + 0.88584975247564, "longitude": randint(37, 39) + 0.49739196728512},
             "south_east":
                 {"latitude": randint(55, 59) + 0.62758487182953, "longitude": randint(37, 39) + 0.7548840327148},
             "zoom": randint(10, 17)}
        ]
        message_cluster = json.dumps(data_cluster)
        start_time = time.time()
        try:
            self.ws.send(message_cluster)  # Отправка сообщения
            response_cluster = self.ws.recv()  # Получение ответа
            self.success_request(start_time=start_time, response=response_cluster, name='get_cluster')
        except WebSocketConnectionClosedException as e:
            self.exception_request(start_time=start_time, name='get_cluster', e=e)
        except Exception as e:
            self.exception_request(start_time=start_time, name='get_cluster', e=e)



    def filter_locus_nearest_loctions(self):
            data_cluster = self.data_other.copy()  # Копируем data, чтобы избежать изменения оригинала
            data_cluster["method"] = "v1_getNearestLocation"
            data_cluster["params"] = [{
                "latitude": randint(55, 58) + 0.8631039,
                "longitude": randint(37, 39)+ 0.6721449,
                "filters":{
                    "machine_type": ["LDX","nas_outdoor", "nas_rus", "NAS", "WIN", "WIN_GEN2"],
                    "status":"ok",
                    "empty_cells":1}}]
            message_cluster = json.dumps(data_cluster)
            start_time = time.time()
            try:
                self.ws.send(message_cluster)  # Отправка сообщения
                response_cluster = self.ws.recv()  # Получение ответа
                self.success_request(start_time=start_time, response=response_cluster, name='filter_locus_nearest_loctions')
            except WebSocketConnectionClosedException as e:
                self.exception_request(start_time=start_time, name='filter_locus_nearest_loctions', e=e)
            except Exception as e:
                self.exception_request(start_time=start_time, name='filter_locus_nearest_loctions', e=e)


    def filter_locus_get_nearest_cluster(self):
            data_cluster = self.data_other.copy()  # Копируем data, чтобы избежать изменения оригинала
            data_cluster["method"] = "v1_getNearestCluster"
            data_cluster["params"] = [{"latitude": randint(55, 58) + 0.8631039, "longitude": randint(37, 39) + 0.6721449,  "filters":{
                                                    "machine_type": ["LDX","nas_outdoor", "nas_rus", "NAS", "WIN", "WIN_GEN2"],
                                                    "status":"ok"
                }}]
            message_cluster = json.dumps(data_cluster)
            start_time = time.time()
            try:
                self.ws.send(message_cluster)  # Отправка сообщения
                response_cluster = self.ws.recv()  # Получение ответа
                self.success_request(start_time=start_time, response=response_cluster, name='filter_locus_get_nearest_cluster')
            except WebSocketConnectionClosedException as e:
                self.exception_request(start_time=start_time, name='filter_locus_get_nearest_cluster', e=e)
            except Exception as e:
                self.exception_request(start_time=start_time, name='filter_locus_get_nearest_cluster', e=e)


    def filter_locus_get_cluster(self):
            data_cluster = self.data_other.copy() # Копируем data, чтобы избежать изменения оригинала
            data_cluster["method"] = "v1_getClusters"
            data_cluster["params"] = [
                {"north_west":
                     {"latitude": randint(55, 59) + 0.88584975247564, "longitude": randint(37, 39) + 0.49739196728512},
                 "south_east":
                     {"latitude": randint(55, 59) + 0.62758487182953, "longitude": randint(37, 39) + 0.7548840327148},
                 "zoom": randint(10, 17), "filters":{
                                                    "machine_type": ["LDX","nas_outdoor", "nas_rus", "NAS", "WIN", "WIN_GEN2"],
                                                    "status":"ok"
                }}
            ]
            message_cluster = json.dumps(data_cluster)
            start_time = time.time()
            try:
                self.ws.send(message_cluster)  # Отправка сообщения
                response_cluster = self.ws.recv()  # Получение ответа
                self.success_request(start_time=start_time, response=response_cluster, name='filter_locus_get_cluster')
            except WebSocketConnectionClosedException as e:
                self.exception_request(start_time=start_time, name='filter_locus_get_cluster', e=e)
            except Exception as e:
                self.exception_request(start_time=start_time, name='filter_locus_get_cluster', e=e)


    def filter_empty_locus_nearest_loctions(self):
            data_cluster = self.data_other.copy()  # Копируем data, чтобы избежать изменения оригинала
            data_cluster["method"] = "v1_getNearestLocation"
            data_cluster["params"] = [{
                "latitude": randint(55, 58) + 0.8631039,
                "longitude": randint(37, 39)+ 0.6721449,
                "filters":{}}]
            message_cluster = json.dumps(data_cluster)
            start_time = time.time()
            try:
                self.ws.send(message_cluster)  # Отправка сообщения
                response_cluster = self.ws.recv()  # Получение ответа
                self.success_request(start_time=start_time, response=response_cluster, name='filter_empty_locus_nearest_loctions')
            except WebSocketConnectionClosedException as e:
                self.exception_request(start_time=start_time, name='filter_empty_locus_nearest_loctions', e=e)
            except Exception as e:
                self.exception_request(start_time=start_time, name='filter_empty_locus_nearest_loctions', e=e)


    def filter_empty_locus_get_nearest_cluster(self):
            data_cluster = self.data_other.copy()  # Копируем data, чтобы избежать изменения оригинала
            data_cluster["method"] = "v1_getNearestCluster"
            data_cluster["params"] = [{"latitude": randint(55, 58) + 0.8631039, "longitude": randint(37, 39) + 0.6721449,  "filters":{}}]
            message_cluster = json.dumps(data_cluster)
            start_time = time.time()
            try:
                self.ws.send(message_cluster)  # Отправка сообщения
                response_cluster = self.ws.recv()  # Получение ответа
                self.success_request(start_time=start_time, response=response_cluster, name='filter_empty_locus_get_nearest_cluster')
            except WebSocketConnectionClosedException as e:
                self.exception_request(start_time=start_time, name='filter_empty_locus_get_nearest_cluster', e=e)
            except Exception as e:
                self.exception_request(start_time=start_time, name='filter_empty_locus_get_nearest_cluster', e=e)


    def filter_empty_locus_get_cluster(self):
            data_cluster = self.data_other.copy() # Копируем data, чтобы избежать изменения оригинала
            data_cluster["method"] = "v1_getClusters"
            data_cluster["params"] = [
                {"north_west":
                     {"latitude": randint(55, 59) + 0.88584975247564, "longitude": randint(37, 39) + 0.49739196728512},
                 "south_east":
                     {"latitude": randint(55, 59) + 0.62758487182953, "longitude": randint(37, 39) + 0.7548840327148},
                 "zoom": randint(10, 17), "filters":{
                }}
            ]
            message_cluster = json.dumps(data_cluster)
            start_time = time.time()
            try:
                self.ws.send(message_cluster)  # Отправка сообщения
                response_cluster = self.ws.recv()  # Получение ответа
                self.success_request(start_time=start_time, response=response_cluster, name='filter_empty_locus_get_cluster')
            except WebSocketConnectionClosedException as e:
                self.exception_request(start_time=start_time, name='filter_empty_locus_get_cluster', e=e)
            except Exception as e:
                self.exception_request(start_time=start_time, name='filter_empty_locus_get_cluster', e=e)


# запуск из директории с файлом partner_gateway.py
# locust -f partner_gateway.py
#locust -f test_script.py -u 1000 -r 100 --headless запуск в хендрежиме
