import json
import logging
import os
import ssl
import time
from random import randint
from locust import User, task, between
from locust.exception import RescheduleTask
from websocket import create_connection, WebSocketConnectionClosedException
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.DEBUG)


class SocketTest(User):
    wait_time = between(3, 5)  # Время ожидания между выполнением задач от и до
    data_other = {
        "id": "1",
        "jsonrpc": "2.0",
        "params": []
    }

    def __init__(self, environment):
        super().__init__(environment)
        self.access_token = None
        self.ws = None
        self.lock = False  # Переменная для блокировки одновременных запросов

    def connect_socket(self):
        url_socket = os.getenv('url_socket')
        sslopt = {"cert_reqs": ssl.CERT_NONE}
        try:
            self.ws = create_connection(url=url_socket, sslopt=sslopt)
            logging.info(f"Connected to {url_socket}")
        except Exception as e:
            logging.error(f"Failed to connect: {e}")
            raise RescheduleTask()

    def on_start(self):
        # Устанавливаем соединение при старте
        self.connect_socket()

    def on_stop(self):
        if self.ws:
            self.ws.close()
            logging.info("WebSocket connection closed")

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
        # Пробуем переподключиться
        logging.error(f"Error in task {name}: {e}, reconnecting...")
        self.connect_socket()
        raise RescheduleTask()

    def send_message(self, data, name):
        message = json.dumps(data)
        start_time = time.time()

        # Ожидание освобождения ресурса
        while self.lock:
            time.sleep(0.1)

        self.lock = True  # Блокируем ресурс

        try:
            self.ws.send(message)  # Отправка сообщения
            response = self.ws.recv()  # Получение ответа
            self.success_request(start_time=start_time, response=response, name=name)
        except (WebSocketConnectionClosedException, Exception) as e:
            self.exception_request(start_time=start_time, name=name, e=e)
        finally:
            self.lock = False  # Разблокируем ресурс

    @task(1)
    def locus_nearest_locations(self):
        data = self.data_other.copy()
        data["method"] = "v1_getNearestLocation"
        data["params"] = [{"latitude": randint(55, 58) + 0.8631039, "longitude": randint(37, 39) + 0.6721449}]
        self.send_message(data, 'nearest_locations')

    @task(2)
    def locus_get_nearest_cluster(self):
        data = self.data_other.copy()
        data["method"] = "v1_getNearestCluster"
        data["params"] = [{"latitude": randint(55, 58) + 0.8631039, "longitude": randint(37, 39) + 0.6721449}]
        self.send_message(data, 'get_nearest_cluster')

    @task(3)
    def locus_get_cluster(self):
        data = self.data_other.copy()
        data["method"] = "v1_getClusters"
        data["params"] = [
            {"north_west": {"latitude": randint(55, 59) + 0.88584975247564,
                            "longitude": randint(37, 39) + 0.49739196728512},
             "south_east": {"latitude": randint(55, 59) + 0.62758487182953,
                            "longitude": randint(37, 39) + 0.7548840327148},
             "zoom": randint(10, 17)}
        ]
        self.send_message(data, 'get_cluster')

    @task(1)
    def filter_locus_nearest_locations(self):
        data = self.data_other.copy()
        data["method"] = "v1_getNearestLocation"
        data["params"] = [{
            "latitude": randint(55, 58) + 0.8631039,
            "longitude": randint(37, 39) + 0.6721449,
            "filters": {
                "machine_type": ["LDX", "nas_outdoor", "nas_rus", "NAS", "WIN", "WIN_GEN2"],
                "status": "ok",
                "empty_cells": 1
            }
        }]
        self.send_message(data, 'filter_nearest_locations')

    @task(2)
    def filter_locus_get_nearest_cluster(self):
        data = self.data_other.copy()
        data["method"] = "v1_getNearestCluster"
        data["params"] = [{"latitude": randint(55, 58) + 0.8631039, "longitude": randint(37, 39) + 0.6721449,
                           "filters": {
                               "machine_type": ["LDX", "nas_outdoor", "nas_rus", "NAS", "WIN", "WIN_GEN2"],
                               "status": "ok"
                           }}]
        self.send_message(data, 'filter_locus_get_nearest_cluster')

    @task(3)
    def filter_locus_get_cluster(self):
        data = self.data_other.copy()
        data["method"] = "v1_getClusters"
        data["params"] = [
            {"north_west": {"latitude": randint(55, 59) + 0.88584975247564,
                            "longitude": randint(37, 39) + 0.49739196728512},
             "south_east": {"latitude": randint(55, 59) + 0.62758487182953,
                            "longitude": randint(37, 39) + 0.7548840327148},
             "zoom": randint(10, 17),
             "filters": {
                 "machine_type": ["LDX", "nas_outdoor", "nas_rus", "NAS", "WIN", "WIN_GEN2"],
                 "status": "ok"
             }}
        ]
        self.send_message(data, 'filter_locus_get_cluster')

    @task(1)
    def filter_empty_locus_nearest_locations(self):
        data = self.data_other.copy()
        data["method"] = "v1_getNearestLocation"
        data["params"] = [{
            "latitude": randint(55, 58) + 0.8631039,
            "longitude": randint(37, 39) + 0.6721449,
            "filters": {}
        }]
        self.send_message(data, 'filter_empty_locus_nearest_locations')

    @task(2)
    def filter_empty_locus_get_nearest_cluster(self):
        data = self.data_other.copy()
        data["method"] = "v1_getNearestCluster"
        data["params"] = [{"latitude": randint(55, 58) + 0.8631039, "longitude": randint(37, 39) + 0.6721449,
                           "filters": {}}]
        self.send_message(data, 'filter_empty_locus_get_nearest_cluster')

    @task(3)
    def filter_empty_locus_get_cluster(self):
        data = self.data_other.copy()
        data["method"] = "v1_getClusters"
        data["params"] = [
            {"north_west": {"latitude": randint(55, 59) + 0.88584975247564,
                            "longitude": randint(37, 39) + 0.49739196728512},
             "south_east": {"latitude": randint(55, 59) + 0.62758487182953,
                            "longitude": randint(37, 39) + 0.7548840327148},
             "zoom": randint(10, 17),
             "filters": {}}
        ]
        self.send_message(data, 'filter_empty_locus_get_cluster')
