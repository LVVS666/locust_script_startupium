import json

from locust import User, task, between
from websocket import create_connection
import ssl


class AuthUser(User):
    wait_time = between(5, 6)  # Время ожидания между выполнением задачам от 5 до 6 секунд
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

    @task(2) # чем больше число в декораторе task, тем задача будет чаще выполнятся в сравнение с другими
    def login(self):
        # Сериализация JSON-объекта в строку
        data_login = self.data
        data_login["method"] = "v1_webappLogin"
        data_login["params"][0]['confirmation_type'] = "sms"
        message_login = json.dumps(data_login)
        # Отправка сообщения
        self.ws.send(message_login)
        # Получение ответа
        response_login = self.ws.recv()
        print(f"Received message: {response_login}")
        data_sms = self.data
        data_login["method"] = "v1_webappConfirm"
        data_sms["params"][0]['code'] = "0001"
        message_sms = json.dumps(data_sms)
        self.ws.send(message_sms)
        response_sms = self.ws.recv()
        print(f"Received message: {response_sms}")

# запуск из директории с файлом locustfile.py
# locust -f locustfile.py

