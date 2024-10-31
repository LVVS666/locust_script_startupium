import json
import logging
import os
import random
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
    wait_time = between(5, 6)  # Время ожидания между выполнением задач
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
            # # 1. Логин
            # self.login()
            # # 2. Подписка
            # self.subscribe()
            # # 3. Создание карт
            # self.create_cards()

        finally:
            # Закрыть соединение после выполнения всех задач
            if self.ws:
                logging.info("Closing WebSocket connection...")
                self.ws.close()
                self.ws = None  # Обнуление переменной после закрытия
            else:
                logging.info("WebSocket connection is already closed.")

        self.is_task_completed = True  # Установить флаг после выполнения задач

    # def login(self):
    #     data_login = self.data_login.copy()  # Копируем data, чтобы избежать изменения оригинала
    #     phone = f"7999{randint(100,999)}{randint(1000,9999)}"
    #     data_login["params"][0]["phone"] = phone
    #     message_login = json.dumps(data_login)
    #     start_time = time.time()  # Запись времени начала отправки сообщения
    #     try:
    #         self.ws.send(message_login)  # Отправка сообщения
    #         response_login = self.ws.recv()  # Получение ответа
    #         self.success_request(start_time=start_time, response=response_login, name='login')
    #         response_data = json.loads(response_login)
    #         self.access_token = response_data['result']['access_token']
    #         logging.info("Авторизация успешна")
    #     except WebSocketConnectionClosedException as e:
    #         self.exception_request(start_time=start_time, name='login', e=e)
    #     except Exception as e:
    #         logging.info(f"Ошибка авторизации")
    #         self.exception_request(start_time=start_time, name='login', e=e)
    #
    # def subscribe(self):
    #     data_subscribe = self.data_other.copy()  # Копируем data, чтобы избежать изменения оригинала
    #     data_subscribe["method"] = "v1_subscribe"
    #     data_subscribe["params"] = ["webappSubscription", self.access_token]
    #     message_subscribe = json.dumps(data_subscribe)
    #     start_time = time.time()
    #     try:
    #         self.ws.send(message_subscribe)  # Отправка сообщения
    #         response_subscribe = self.ws.recv()  # Получение ответа
    #         self.success_request(start_time=start_time, response=response_subscribe, name='subscribe')
    #         logging.info("Подписка успешна")
    #     except WebSocketConnectionClosedException as e:
    #         self.exception_request(start_time=start_time, name='subscribe', e=e)
    #     except Exception as e:
    #         logging.info("Ошибка подписки")
    #         self.exception_request(start_time=start_time, name='subscribe', e=e)
    #
    # def create_cards(self):
    #     zone_cards = ["RUS_SBER", "RUS_SBER"]
    #     data_cards = self.data_other.copy()  # Копируем data, чтобы избежать изменения оригинала
    #     data_cards["method"] = "v1_webappCardsCreate"
    #     data_cards["params"] = [{"jwt_token": self.access_token, "zone": random.choice(zone_cards)}]
    #     message_cards = json.dumps(data_cards)
    #     start_time = time.time()
    #     try:
    #         self.ws.send(message_cards)  # Отправка сообщения
    #         response_cards = self.ws.recv()  # Получение ответа
    #         self.success_request(start_time=start_time, response=response_cards, name='create_cards')
    #         logging.info("Карта создана")
    #         logging.info("Ожидаем второй ответ из сокета...")
    #         while True:
    #             try:
    #                 second_response = self.ws.recv()
    #                 logging.info("Received second response: %s", second_response)
    #                 logging.info("Ссылка на привязку карты получена")
    #                 break  # Прерываем цикл, когда получили ответ
    #             except WebSocketConnectionClosedException:
    #                 logging.error("WebSocket connection closed while waiting for second response.")
    #                 break  # Прерываем цикл, если соединение закрыто
    #     except WebSocketConnectionClosedException as e:
    #         self.exception_request(start_time=start_time, name='create_cards', e=e)
    #     except Exception as e:
    #         logging.info("Ошибка привязки карты")
    #         self.exception_request(start_time=start_time, name='create_cards', e=e)


    # @task(2)
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

    # @task(2)
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

    # @task(2)
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



    # def short_link(self):
    #     data_short_link = self.data_other.copy()  # Копируем data, чтобы избежать изменения оригинала
    #     data_short_link["method"] = "v1_webappShortLink"
    #     short_link = os.getenv('dev3_short_link')[:83] + str(random.randint(0, 9)) + os.getenv('dev3_short_link')[85:]
    #     data_short_link["params"] = [
    #         {
    #             "short_link": short_link
    #         }]
    #     message_short_link = json.dumps(data_short_link)
    #     start_time = time.time()
    #     try:
    #         self.ws.send(message_short_link)  # Отправка сообщения
    #         response_short_link = self.ws.recv()  # Получение ответа
    #         self.success_request(start_time=start_time, response=response_short_link, name='short_link')
    #     except WebSocketConnectionClosedException as e:
    #         self.exception_request(start_time=start_time, name='short_link', e=e)
    #     except Exception as e:
    #         self.exception_request(start_time=start_time, name='short_link', e=e)





# запуск из директории с файлом partner_gateway.py
# locust -f partner_gateway.py
#locust -f test_script.py -u 1000 -r 100 --headless запуск в хендрежиме