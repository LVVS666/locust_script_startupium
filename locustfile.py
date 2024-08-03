import json

from locust import User, task, between
from websocket import create_connection
import ssl

class Login(User):
    wait_time = between(5, 6)  # Время ожидания между выполнением задачам от 5 до 6 секунд

    def on_start(self):
        # Инициализация WebSocket-соединения
        sslopt = {"cert_reqs": ssl.CERT_NONE}
        self.ws = create_connection("wss://dev3partners.berizaryad.ru/ws", sslopt=sslopt)

    def on_stop(self):
        # Закрытие соединения
        self.ws.close()

    @task(2) # чем больше число в декораторе task, тем задача будет чаще выполнятся в сравнение с другими
    def login(self):
        data = {
            "id": "4dfe08d0-3c88-4867-a425-210da92527f7",
            "jsonrpc": "2.0",
            "method": "v1_webappLogin",
            "params": [
                {
                    "phone": "79996661155",
                    "confirmation_type": "sms",
                    "udid": "1a4a9fa8f577915c4d2c31cb20983895",
                    "app_version": "23.0",
                    "platform": "iOS",
                    "os_version": "10.15.7"
                }
            ]
        }
        # Сериализация JSON-объекта в строку
        message = json.dumps(data)
        # Отправка сообщения
        self.ws.send(message)
        # Получение ответа
        response = self.ws.recv()
        print(f"Received message: {response}")

    @task(2)
    def send_sms(self):
        data = {
            "id": "4dfe08d0-3c88-4867-a425-210da92527f7",
            "jsonrpc": "2.0",
            "method": "v1_webappLogin",
            "params": [
                {
                    "phone": "79996661155",
                    "code" : "0001",
                    "udid": "1a4a9fa8f577915c4d2c31cb20983895",
                    "app_version": "23.0",
                    "platform": "iOS",
                    "os_version": "10.15.7"
                }
            ]
        }
        message = json.dumps(data)
        self.ws.send(message)
        response = self.ws.recv()
        print(f"Received message: {response}")



# запуск из директории с файлом locustfile.py
# locust -f locustfile.py