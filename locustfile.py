from locust import task, HttpUser
from random import choice


class UserStartupium(HttpUser):

    @task(1)
    def all_projects(self):
        self.client.get('/projects')

    @task(3)
    def project(self):
        self.client.get(f'/project/{choice([111, 1245, 123, 23124])}')

    @task(1)
    def all_users(self):
        self.client.get('/users')

    @task(1)
    def users(self):
        self.client.get(f'/profile/{choice([109, 107, 106, 105])}')


