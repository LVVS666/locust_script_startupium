import json
import ssl
import time
from locust import User, task, between
from locust.exception import RescheduleTask
from websocket import create_connection, WebSocketConnectionClosedException


class AuthUser(User):
    wait_time = between(5, 6)  # Время ожидания между выполнением задач от 5 до 6 секунд
    data = {
        "id": "4dfe08d0-3c88-4867-a425-210da92527f7",
        "jsonrpc": "2.0",
        "params": [
            {
                "phone": "79996661155",
                "udid": "1a4a9fa8f577915c4d2c31cb20983895",
                "app_version": "23.0",
                "platform": "iOS",
                "os_version": "10.15.7"
            }
        ]
    }

    def on_start(self):
        # Инициализация WebSocket-соединения
        sslopt = {"cert_reqs": ssl.CERT_NONE}
        self.ws = create_connection("wss://dev3partners.berizaryad.ru/ws", sslopt=sslopt)

    def on_stop(self):
        # Закрытие соединения
        self.ws.close()

    @task(2)
    def login(self):
        # Сериализация JSON-объекта в строку
        data_login = self.data.copy()  # Копируем data, чтобы избежать изменения оригинала
        data_login["method"] = "v1_webappLogin"
        data_login["params"][0]['confirmation_type'] = "sms"
        message_login = json.dumps(data_login)

        # Запись времени начала отправки сообщения
        start_time = time.time()

        try:
            # Отправка сообщения
            self.ws.send(message_login)

            # Получение ответа
            response_login = self.ws.recv()

            # Запись успешного ответа
            total_time = int((time.time() - start_time) * 1000)  # Время в миллисекундах
            self.environment.events.request.fire(
                request_type="WebSocket",
                name="login",
                response_time=total_time,
                response_length=len(response_login),
                response="Success",
                exception=None,
            )

            print(f"Received message: {response_login}")

            # Обработка второго сообщения для подтверждения
            data_sms = self.data.copy()  # Копируем data, чтобы избежать изменения оригинала
            data_sms["method"] = "v1_webappConfirm"
            data_sms["params"][0]['code'] = "0001"
            message_sms = json.dumps(data_sms)

            # Запись времени начала отправки сообщения
            start_time = time.time()

            # Отправка сообщения
            self.ws.send(message_sms)

            # Получение ответа
            response_sms = self.ws.recv()

            # Запись успешного ответа
            total_time = int((time.time() - start_time) * 1000)  # Время в миллисекундах
            self.environment.events.request.fire(
                request_type="WebSocket",
                name="confirm",
                response_time=total_time,
                response_length=len(response_sms),
                response="Success",
                exception=None,
            )

            print(f"Received message: {response_sms}")

        except WebSocketConnectionClosedException as e:
            # Запись ошибки, если WebSocket соединение было закрыто
            total_time = int((time.time() - start_time) * 1000)  # Время в миллисекундах
            self.environment.events.request.fire(
                request_type="WebSocket",
                name="login",
                response_time=total_time,
                response_length=0,
                response="Failure",
                exception=e,
            )
            raise RescheduleTask()  # Перезапланировать задачу для выполнения позже

        except Exception as e:
            # Запись других ошибок
            total_time = int((time.time() - start_time) * 1000)  # Время в миллисекундах
            self.environment.events.request.fire(
                request_type="WebSocket",
                name="login",
                response_time=total_time,
                response_length=0,
                response="Failure",
                exception=e,
            )
            raise RescheduleTask()  # Перезапланировать задачу для выполнения позже

# запуск из директории с файлом locustfile.py
# locust -f locustfile.py
