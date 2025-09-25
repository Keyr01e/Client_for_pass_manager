import tkinter
from tkinter import ttk, messagebox
import requests
from requests import session


API_URL = 'http://127.0.0.1:8000'

class APILogin:
    def __init__(self, base_url):
        self.base = base_url.rstrip('/')
        self.session = requests.Session()
        self.token = None


    def login(self, username, password):
        """
                Вход
        """
        url = f'{self.base}/auth/token'

        payload = {
            'grant_type': 'password',
            'username': username,
            'password': password,
            'scope': '',
            'client_id': 'string',
            'client_secret': 'string'
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.post(url, data=payload, headers=headers)
        self.token = response.cookies.get('access_token')
        return response.status_code, response.json()


    def get_cookie(self):
        cookie = {
            'access_token': self.token
        }
        return cookie

    def register(self, username, password):
        """
                Регистрация
        """
        url = f'{self.base}/auth/register'

        data = {
            "username": username,
            "password": password
        }

        response = requests.post(url, json=data)
        print(response.status_code)
        return response.json()

    def create_password_entry(self, service_name: str, service_username_or_email, service_password):
        """
                Создание пароля
        """
        if not self.token:
            return

        url = f'{self.base}/passwords'

        data = {
            'service_name': service_name,
            'username_or_email': service_username_or_email,
            'password': service_password

        }

        print(self.token)
        response = requests.post(url, json=data, cookies=self.get_cookie())
        print(response.text)
        return response.json()

    def get_decoded_password(self, entry_id):
        """
                Расшифровка пароля по id
        """
        if not self.token:
            return
        url = f'{self.base}/passwords/{entry_id}/decrypt'


        response = requests.get(url, cookies=self.get_cookie())
        return response.json()

    def get_passwords(self):
        """
                        Получить все пароли(берётся пул от 0 до 100)
        """

        if not self.token:
            return
        url = f'{self.base}/passwords'

        response = requests.get(url, cookies=self.get_cookie())
        return response.status_code, response.json()



root = APILogin(API_URL)

# print(root.login('string', 'string'))
print(root.login('string', 'string'))
print(root.create_password_entry('asdla;skjfa', 'Nikita', 'aasdfasfsafasdasd'))
# print(root.get_decoded_password(3))
print(root.get_passwords())