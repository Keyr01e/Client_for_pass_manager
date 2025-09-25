# import tkinter
# from tkinter import ttk, messagebox
import requests

API_URL = 'http://127.0.0.1:8000'

class APILogic:
    def __init__(self, base_url):
        self.base = base_url.rstrip('/')
        self.session = requests.Session()
        self.cookie = {
            'access_token': None
        }
        
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
        # self.token = response.cookies.get('access_token')
        self.cookie = response.cookies 
        return response.status_code, response.json()

    def logout(self):
        if not self.cookie:
            return
        url = f'{self.base}/auth/logout'
        response = requests.post(url, cookies=self.cookie)
        self.cookie = None
        return response.json(), response.status_code


    def me(self):
        """
                        Получить данные о пользователе
        """
        url = f'{self.base}/auth/me'
        response = requests.get(url, cookies=self.cookie)
        return response.json()



    def create_password_entry(self, service_name: str, service_username_or_email, service_password):
        """
                Создание пароля
        """
        if not self.cookie:
            return

        url = f'{self.base}/passwords'

        data = {
            'service_name': service_name,
            'username_or_email': service_username_or_email,
            'password': service_password

        }

        print(self.cookie)
        response = requests.post(url, json=data, cookies=self.cookie)
        print(response.text)
        return response.json()

    def get_decoded_password(self, entry_id):
        """
                Расшифровка пароля по id
        """
        if not self.cookie:
            return
        url = f'{self.base}/passwords/{entry_id}/decrypt'


        response = requests.get(url, cookies=self.cookie)
        return response.json()

    def get_passwords(self):
        """
                        Получить все пароли(берётся пул от 0 до 100)
        """

        if not self.cookie:
            return
        url = f'{self.base}/passwords'

        response = requests.get(url, cookies=self.cookie)
        return response.status_code, response.json()

    def update_password_entry(self, entry_id, service_name, service_username_or_email, service_password):
        """
                        Обновить данные о сохраненном в бд пароле
        """
        url = f'{self.base}/passwords/{entry_id}'

        data = {
              "service_name": service_name,
              "username_or_email": service_username_or_email,
              "password": service_password
                }

        response = requests.put(url, json=data, cookies=self.cookie)
        return response.json()

    def delete_password_entry(self, entry_id):
        if not self.cookie:
            return

        url = f'{self.base}/passwords/{entry_id}'

        response = requests.delete(url, cookies=self.cookie)
        return response.status_code, response.text

root = APILogic(API_URL)

# print(root.login('string', 'string'))
print(root.login('string', 'string'))
print(root.create_password_entry('asdla;skjfa', 'Nikita', 'aasdfasfsafasdasd'))
# print(root.get_decoded_password(3))
# print(root.get_passwords())
# print(root.me())
# print(root.update_password_entry(1, 'Pass manager', 'Username_for_passmanager', '121314'))
# print(root.delete_password_entry(4))
# print(root.logout())
