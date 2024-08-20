import json
import logging
import os
import random
import ssl
import time


from random import randint
from locust import User, task, between
from locust.exception import RescheduleTask
from websocket import create_connection, WebSocketConnectionClosedException, WebSocketBadStatusException
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.DEBUG)

class SocketTest(User):
    wait_time = between(5, 6)  # Время ожидания между выполнением задач от 5 до 6 секунд
    data_login = {
        "id": "1",
        "jsonrpc": "2.0",
        "params": [
            {
                "udid": "1a4a9fa8f577915c4d2c31cb20983895",
                "app_version": "23.0",
                "platform": "iOS",
                "os_version": "10.15.7"
            }
        ]
    }
    data_other = {
        "id": "1",
        "jsonrpc": "2.0",
        "params": []}


    def on_start(self):
        url_socket = os.getenv('url_socket')
        sslopt = {"cert_reqs": ssl.CERT_NONE}
        self.ws = create_connection(url=url_socket, sslopt=sslopt)


    def on_stop(self):
        # Закрытие соединения
        self.ws.close()

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

    # @task(2)
    # def login(self):
    #     # Сериализация JSON-объекта в строку
    #     data_login = self.data_login.copy()  # Копируем data, чтобы избежать изменения оригинала
    #     data_login["method"] = "v1_webappLogin"
    #     data_login["params"][0]['confirmation_type'] = "sms"
    #     phone = f"7999666{randint(10,99)}{randint(10,99)}"
    #     data_login["params"][0]["phone"] = phone
    #     message_login = json.dumps(data_login)
    #     start_time = time.time()  # Запись времени начала отправки сообщения
    #     try:
    #         self.ws.send(message_login)  # Отправка сообщения
    #         response_login = self.ws.recv()  # Получение ответа
    #         self.success_request(start_time=start_time, response=response_login, name='login')
    #
    #         # Обработка второго сообщения для подтверждения
    #         data_sms = self.data_login.copy()  # Копируем data, чтобы избежать изменения оригинала
    #         data_sms["method"] = "v1_webappConfirm"
    #         data_sms["params"][0]['code'] = "0001"
    #         data_sms["params"][0]["phone"] = phone
    #         message_sms = json.dumps(data_sms)
    #         start_time = time.time()
    #         self.ws.send(message_sms)
    #         response_sms = self.ws.recv()
    #         self.access_token = response_sms['result']['access_token']
    #         self.success_request(start_time=start_time, response=response_sms, name='confirm')
    #
    #     except WebSocketConnectionClosedException as e:
    #         self.exception_request(start_time=start_time, name='login', e=e)
    #
    #     except Exception as e:
    #         self.exception_request(start_time=start_time, name='login', e=e)
    #
    # @task(1)
    # def get_cards(self):
    #     zone_cards = ["YANDEX_DRIVE", "RUS_SBER"]
    #     data_cards = self.data_other.copy()  # Копируем data, чтобы избежать изменения оригинала
    #     data_cards["method"] = "v1_webappCards"
    #     data_cards["params"] = [{"jwt_token": self.access_token, "zone": random.choice(zone_cards)}]
    #     message_cards = json.dumps(data_cards)
    #     start_time = time.time()
    #     try:
    #         self.ws.send(message_cards)  # Отправка сообщения
    #         response_cards = self.ws.recv()  # Получение ответа
    #         self.success_request(start_time=start_time, response=response_cards, name='get_cards')
    #     except WebSocketConnectionClosedException as e:
    #         self.exception_request(start_time=start_time, name='get_cards', e=e)
    #     except Exception as e:
    #         self.exception_request(start_time=start_time, name='get_cards', e=e)
    #
    # @task(1)
    # def get_orders(self):
    #     data_orders = self.data_other.copy()  # Копируем data, чтобы избежать изменения оригинала
    #     data_orders["method"] = "v1_webappOrders"
    #     data_orders["params"] = [{"jwt_token": self.access_token}]
    #     message_orders = json.dumps(data_orders)
    #     start_time = time.time()
    #     try:
    #         self.ws.send(message_orders)  # Отправка сообщения
    #         response_orders = self.ws.recv()  # Получение ответа
    #         self.success_request(start_time=start_time, response=response_orders, name='get_orders')
    #     except WebSocketConnectionClosedException as e:
    #         self.exception_request(start_time=start_time, name='get_orders', e=e)
    #     except Exception as e:
    #         self.exception_request(start_time=start_time, name='get_orders', e=e)
    #
    # @task(3)
    # def vendings(self):
    #     data_vendings = self.data_other.copy()  # Копируем data, чтобы избежать изменения оригинала
    #     data_vendings["method"] = "v1_webappVendings"
    #     data_vendings["params"] = [{"id": randint(100, 500)}]
    #     message_vendings = json.dumps(data_vendings)
    #     start_time = time.time()
    #     try:
    #         self.ws.send(message_vendings)  # Отправка сообщения
    #         response_vendings = self.ws.recv()  # Получение ответа
    #         self.success_request(start_time=start_time, response=response_vendings, name='vendings')
    #     except WebSocketConnectionClosedException as e:
    #         self.exception_request(start_time=start_time, name='vendings', e=e)
    #     except Exception as e:
    #         self.exception_request(start_time=start_time, name='vendings', e=e)
    #
    # @task(3)
    # def vending_id(self):
    #     vendings_id = [int(f'111{randint(0, 9)}'), int(f'1111{randint(0, 9)}')]
    #     data_vending_id = self.data_other.copy()  # Копируем data, чтобы избежать изменения оригинала
    #     data_vending_id["method"] = "v1_webappVendings"
    #     data_vending_id["params"] = [{"id": random.choice(vendings_id)}]
    #     message_vending_id = json.dumps(data_vending_id)
    #     start_time = time.time()
    #     try:
    #         self.ws.send(message_vending_id)  # Отправка сообщения
    #         response_vending_id = self.ws.recv()  # Получение ответа
    #         self.success_request(start_time=start_time, response=response_vending_id, name='vending_id')
    #     except WebSocketConnectionClosedException as e:
    #         self.exception_request(start_time=start_time, name='vending_id', e=e)
    #     except Exception as e:
    #         self.exception_request(start_time=start_time, name='vending_id', e=e)


    @task(1)
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

    @task(2)
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

    @task(3)
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


    @task(1)
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

    @task(2)
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

    @task(3)
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

    @task(1)
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

    @task(2)
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

    @task(3)
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

# запуск из директории с файлом locustfile.py
# locust -f locustfile.py
