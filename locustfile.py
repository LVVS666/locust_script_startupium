import json

from locust import task, HttpUser, between
from random import choice
from haralyzer import HarParser


def load_har_file(file_path):
    '''Функция для парсинга .har файла'''
    with open(file_path, 'r', encoding='utf-8') as f:
        har_data = json.load(f)
        print(har_data)
    return HarParser(har_data)


class UserStartupium(HttpUser):
    '''Основной класс пользователя'''
    wait_time = between(5, 6)
    har_parser = load_har_file('session_startupium.har')


    @task(1)
    def all_projects(self):
        '''Показать все проекты'''
        self.client.get('/projects')

    @task(2)
    def project(self):
        '''Показать один рандомный проект'''
        self.client.get(f'/project/{choice([111, 1245, 123, 23124])}')

    @task(3)
    def all_users(self):
        '''Показать всех пользователей'''
        self.client.get('/users')

    @task(4)
    def users(self):
        '''Показать рандомный профиль'''
        self.client.get(f'/profile/{choice([109, 107, 106, 105])}')

    # @task
    # def run_requests_from_har(self):
    #     # Проход по всем записям в HAR файле
    #     for entry in self.har_parser.har_data['log']['entries']:
    #         request = entry['request']
    #         method = request['method']
    #         url = request['url']
    #         headers = {header['name']: header['value'] for header in request['headers']}
    #         params = {param['name']: param['value'] for param in request['queryString']}
    #         post_data = request.get('postData', {}).get('text', '')
    #
    #         # Выполняем запросы на основе данных из HAR файла
    #         if method == 'GET':
    #             self.client.get(url, headers=headers, params=params)
    #         elif method == 'POST':
    #             self.client.post(url, headers=headers, params=params, data=post_data)
    #         elif method == 'PUT':
    #             self.client.put(url, headers=headers, params=params, data=post_data)
    #         elif method == 'DELETE':
    #             self.client.delete(url, headers=headers, params=params)
