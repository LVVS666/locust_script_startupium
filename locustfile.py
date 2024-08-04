import json
import ssl
import time
from random import randint

from locust import User, task, between
from locust.exception import RescheduleTask
from websocket import create_connection, WebSocketConnectionClosedException


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
    data_cluster = {
        "id": "1",
        "jsonrpc": "2.0",
        "params": []}

    def on_start(self):
        # Инициализация WebSocket-соединения
        sslopt = {"cert_reqs": ssl.CERT_NONE}
        self.ws = create_connection("wss://dev3partners.berizaryad.ru/ws", sslopt=sslopt)

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

    @task(1)
    def login(self):
        # Сериализация JSON-объекта в строку
        data_login = self.data_login.copy()  # Копируем data, чтобы избежать изменения оригинала
        data_login["method"] = "v1_webappLogin"
        data_login["params"][0]['confirmation_type'] = "sms"
        phone = f"7999666{randint(10,99)}{randint(10,99)}"
        data_login["params"][0]["phone"] = phone
        message_login = json.dumps(data_login)
        start_time = time.time()  # Запись времени начала отправки сообщения
        try:
            self.ws.send(message_login)  # Отправка сообщения
            response_login = self.ws.recv()  # Получение ответа
            self.success_request(start_time=start_time, response=response_login, name='login')

            # Обработка второго сообщения для подтверждения
            data_sms = self.data_login.copy()  # Копируем data, чтобы избежать изменения оригинала
            data_sms["method"] = "v1_webappConfirm"
            data_sms["params"][0]['code'] = "0001"
            data_sms["params"][0]["phone"] = phone
            message_sms = json.dumps(data_sms)
            start_time = time.time()
            self.ws.send(message_sms)
            response_sms = self.ws.recv()
            self.success_request(start_time=start_time, response=response_sms, name='confirm')

        except WebSocketConnectionClosedException as e:
            self.exception_request(start_time=start_time, name='login', e=e)

        except Exception as e:
            self.exception_request(start_time=start_time, name='login', e=e)

    @task(3)
    def locus_nearest_loction(self):
        data_cluster = self.data_cluster.copy()  # Копируем data, чтобы избежать изменения оригинала
        data_cluster["method"] = "v1_getNearestLocation"
        data_cluster["params"] = [{"latitude": randint(55, 58) + 0.8631039, "longitude": randint(37, 39)+ 0.6721449}]
        message_cluster = json.dumps(data_cluster)
        start_time = time.time()
        try:
            self.ws.send(message_cluster)  # Отправка сообщения
            response_cluster = self.ws.recv()  # Получение ответа
            self.success_request(start_time=start_time, response=response_cluster, name='nearest_loction')
        except WebSocketConnectionClosedException as e:
            self.exception_request(start_time=start_time, name='nearest_loction', e=e)
        except Exception as e:
            self.exception_request(start_time=start_time, name='nearest_loction', e=e)

    @task(3)
    def locus_get_nearest_cluster(self):
        data_cluster = self.data_cluster.copy()  # Копируем data, чтобы избежать изменения оригинала
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


# запуск из директории с файлом locustfile.py
# locust -f locustfile.py
