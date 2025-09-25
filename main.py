import tkinter as tk
from tkinter import messagebox, simpledialog
import requests

API_URL = 'http://127.0.0.1:8000'


class APILogic:
    def __init__(self, base_url):
        self.base = base_url.rstrip('/')
        self.session = requests.Session()
        self.cookie = None

    def register(self, username, password):
        url = f'{self.base}/auth/register'
        data = {"username": username, "password": password}
        try:
            response = requests.post(url, json=data)
            return response.json()
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Ошибка", "Не удалось подключиться к серверу.")
            return None  # Возвращаем None при ошибке
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при регистрации: {e}")
            return None

    def login(self, username, password):
        url = f'{self.base}/auth/token'
        payload = {
            'grant_type': 'password',
            'username': username,
            'password': password,
            'scope': '',
            'client_id': 'string',
            'client_secret': 'string'
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        try:
            response = requests.post(url, data=payload, headers=headers)
            self.cookie = response.cookies
            return response.status_code, response.json()
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Ошибка", "Не удалось подключиться к серверу.")
            return None, None  # Возвращаем None, None при ошибке
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при входе: {e}")
            return None, None

    def logout(self):
        if not self.cookie:
            return None, None  # Убедимся, что возвращаем два значения, если нет куки
        url = f'{self.base}/auth/logout'
        try:
            response = requests.post(url, cookies=self.cookie)
            self.cookie = None
            return response.json(), response.status_code
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Ошибка", "Не удалось подключиться к серверу.")
            return None, None  # Возвращаем None, None при ошибке
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при выходе: {e}")
            return None, None

    def me(self):
        if not self.cookie:
            return None
        url = f'{self.base}/auth/me'
        try:
            response = requests.get(url, cookies=self.cookie)
            return response.json()
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Ошибка", "Не удалось подключиться к серверу.")
            return None
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при получении данных пользователя: {e}")
            return None

    def create_password_entry(self, service_name: str, service_username_or_email, service_password):
        if not self.cookie:
            messagebox.showwarning("Предупреждение", "Вы не авторизованы.")
            return None
        url = f'{self.base}/passwords'
        data = {
            'service_name': service_name,
            'username_or_email': service_username_or_email,
            'password': service_password
        }
        try:
            response = requests.post(url, json=data, cookies=self.cookie)
            return response.json()
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Ошибка", "Не удалось подключиться к серверу.")
            return None
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при создании записи: {e}")
            return None

    def get_decoded_password(self, entry_id):
        if not self.cookie:
            messagebox.showwarning("Предупреждение", "Вы не авторизованы.")
            return None
        url = f'{self.base}/passwords/{entry_id}/decrypt'
        try:
            response = requests.get(url, cookies=self.cookie)
            return response.json()
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Ошибка", "Не удалось подключиться к серверу.")
            return None
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при расшифровке пароля: {e}")
            return None

    def get_passwords(self):
        if not self.cookie:
            messagebox.showwarning("Предупреждение", "Вы не авторизованы.")
            return None, None
        url = f'{self.base}/passwords'
        try:
            response = requests.get(url, cookies=self.cookie)
            return response.status_code, response.json()
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Ошибка", "Не удалось подключиться к серверу.")
            return None, None
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при получении паролей: {e}")
            return None, None

    def update_password_entry(self, entry_id, service_name, service_username_or_email, service_password):
        if not self.cookie:
            messagebox.showwarning("Предупреждение", "Вы не авторизованы.")
            return None
        url = f'{self.base}/passwords/{entry_id}'
        data = {
            "service_name": service_name,
            "username_or_email": service_username_or_email,
            "password": service_password
        }
        try:
            response = requests.put(url, json=data, cookies=self.cookie)
            return response.json()
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Ошибка", "Не удалось подключиться к серверу.")
            return None
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при обновлении записи: {e}")
            return None

    def delete_password_entry(self, entry_id):
        if not self.cookie:
            messagebox.showwarning("Предупреждение", "Вы не авторизованы.")
            return None, None
        url = f'{self.base}/passwords/{entry_id}'
        try:
            response = requests.delete(url, cookies=self.cookie)
            return response.status_code, response.text
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Ошибка", "Не удалось подключиться к серверу.")
            return None, None
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при удалении записи: {e}")
            return None, None


class PasswordManagerApp:
    def __init__(self, master):
        self.master = master
        master.title("Менеджер паролей")
        master.geometry("400x600")

        self.api = APILogic(API_URL)

        self.create_login_widgets()

    def create_login_widgets(self):
        self.clear_frame()

        self.username_label = tk.Label(self.master, text="Имя пользователя:")
        self.username_label.pack(pady=5)
        self.username_entry = tk.Entry(self.master)
        self.username_entry.pack(pady=5)

        self.password_label = tk.Label(self.master, text="Пароль:")
        self.password_label.pack(pady=5)
        self.password_entry = tk.Entry(self.master, show="*")
        self.password_entry.pack(pady=5)

        self.login_button = tk.Button(self.master, text="Войти", command=self.login)
        self.login_button.pack(pady=10)

        self.register_button = tk.Button(self.master, text="Зарегистрироваться", command=self.register)
        self.register_button.pack(pady=5)

    def create_main_app_widgets(self):
        self.clear_frame()

        self.master.geometry("600x600")

        self.current_user_label = tk.Label(self.master, text="Текущий пользователь: Загрузка...")
        self.current_user_label.pack(pady=5)
        self.update_current_user_info()

        self.create_password_frame = tk.LabelFrame(self.master, text="Создать запись")
        self.create_password_frame.pack(pady=10, padx=10, fill="x")

        tk.Label(self.create_password_frame, text="Сервис:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.service_entry = tk.Entry(self.create_password_frame)
        self.service_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        tk.Label(self.create_password_frame, text="Логин/Email:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.service_username_entry = tk.Entry(self.create_password_frame)
        self.service_username_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        tk.Label(self.create_password_frame, text="Пароль:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.service_password_entry = tk.Entry(self.create_password_frame, show="*")
        self.service_password_entry.grid(row=2, column=1, padx=5, pady=2, sticky="ew")

        create_button = tk.Button(self.create_password_frame, text="Создать пароль", command=self.create_password_entry)
        create_button.grid(row=3, columnspan=2, pady=5)

        self.passwords_frame = tk.LabelFrame(self.master, text="Сохраненные пароли")
        self.passwords_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.passwords_listbox = tk.Listbox(self.passwords_frame)
        self.passwords_listbox.pack(side="left", fill="both", expand=True)
        self.passwords_listbox.bind("<Double-Button-1>", self.show_password_details)

        self.scrollbar = tk.Scrollbar(self.passwords_frame, orient="vertical", command=self.passwords_listbox.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.passwords_listbox.config(yscrollcommand=self.scrollbar.set)

        self.refresh_button = tk.Button(self.master, text="Обновить список", command=self.load_passwords)
        self.refresh_button.pack(pady=5)

        self.logout_button = tk.Button(self.master, text="Выйти", command=self.logout)
        self.logout_button.pack(pady=10)

        self.load_passwords()

    def clear_frame(self):
        for widget in self.master.winfo_children():
            widget.destroy()

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showwarning("Предупреждение", "Пожалуйста, введите имя пользователя и пароль.")
            return

        response = self.api.register(username, password)
        if response and "id" in response:
            messagebox.showinfo("Успех", "Регистрация прошла успешно!")
            self.create_login_widgets()  # Возвращаемся к окну входа
        elif response:  # Если ответ не None, но нет "id"
            messagebox.showerror("Ошибка регистрации", response.get("detail", "Неизвестная ошибка"))

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showwarning("Предупреждение", "Пожалуйста, введите имя пользователя и пароль.")
            return

        status_code, response_data = self.api.login(username, password)
        if status_code == 200:
            messagebox.showinfo("Успех", "Вход выполнен успешно!")
            self.create_main_app_widgets()
        elif response_data:  # Если response_data не None, но статус не 200
            messagebox.showerror("Ошибка входа", response_data.get("detail", "Неизвестная ошибка"))

    def logout(self):
        response_data, status_code = self.api.logout()
        # Проверяем, что status_code не None перед сравнением
        if status_code == 200:
            messagebox.showinfo("Выход", "Вы успешно вышли из системы.")
            self.create_login_widgets()
        elif response_data:  # Если response_data не None, но статус не 200
            messagebox.showerror("Ошибка выхода", response_data.get("detail", "Неизвестная ошибка"))

    def update_current_user_info(self):
        user_info = self.api.me()
        if user_info and "username" in user_info:
            self.current_user_label.config(text=f"Текущий пользователь: {user_info['username']}")
        else:
            self.current_user_label.config(text="Текущий пользователь: Неизвестно")

    def create_password_entry(self):
        service = self.service_entry.get()
        username_or_email = self.service_username_entry.get()
        password = self.service_password_entry.get()

        if not service or not username_or_email or not password:
            messagebox.showwarning("Предупреждение", "Пожалуйста, заполните все поля для создания записи.")
            return

        response = self.api.create_password_entry(service, username_or_email, password)
        if response and "id" in response:
            messagebox.showinfo("Успех", "Запись о пароле успешно создана!")
            self.service_entry.delete(0, tk.END)
            self.service_username_entry.delete(0, tk.END)
            self.service_password_entry.delete(0, tk.END)
            self.load_passwords()
        elif response:
            messagebox.showerror("Ошибка создания записи", response.get("detail", "Неизвестная ошибка"))

    def load_passwords(self):
        self.passwords_listbox.delete(0, tk.END)
        status_code, passwords_data = self.api.get_passwords()
        if status_code == 200 and isinstance(passwords_data, list):
            for entry in passwords_data:
                self.passwords_listbox.insert(tk.END,
                                              f"ID: {entry['id']} | Сервис: {entry['service_name']} | Логин: {entry['username_or_email']}")
            self.all_passwords_data = passwords_data  # Сохраняем все данные для дальнейшего использования
        elif passwords_data:
            messagebox.showerror("Ошибка загрузки паролей", passwords_data.get("detail", "Неизвестная ошибка"))

    def show_password_details(self, event):
        selected_index = self.passwords_listbox.curselection()
        if not selected_index:
            return

        entry_text = self.passwords_listbox.get(selected_index[0])
        # Убедитесь, что строка содержит "ID: " перед извлечением
        if "ID: " in entry_text:
            entry_id_str = entry_text.split(" | ")[0].replace("ID: ", "")
            entry_id = int(entry_id_str)
        else:
            messagebox.showerror("Ошибка", "Не удалось извлечь ID записи.")
            return

        details_window = tk.Toplevel(self.master)
        details_window.title(f"Детали пароля (ID: {entry_id})")
        details_window.geometry("350x250")

        # Найти полную запись по ID
        selected_entry = next((entry for entry in self.all_passwords_data if entry['id'] == entry_id), None)

        if selected_entry:
            tk.Label(details_window, text=f"Сервис: {selected_entry['service_name']}").pack(pady=2)
            tk.Label(details_window, text=f"Логин/Email: {selected_entry['username_or_email']}").pack(pady=2)

            # Поле для отображения пароля
            password_display = tk.StringVar()
            password_entry_widget = tk.Entry(details_window, textvariable=password_display, show="*")
            password_entry_widget.pack(pady=5)

            # Кнопка для расшифровки
            def decrypt_and_show():
                decoded_pass = self.api.get_decoded_password(entry_id)
                if decoded_pass and "password" in decoded_pass:
                    password_display.set(decoded_pass["password"])
                    password_entry_widget.config(show="")  # Показать пароль
                elif decoded_pass:
                    messagebox.showerror("Ошибка расшифровки", decoded_pass.get("detail", "Неизвестная ошибка"))

            decrypt_button = tk.Button(details_window, text="Показать пароль", command=decrypt_and_show)
            decrypt_button.pack(pady=5)

            # Кнопки для обновления и удаления
            tk.Button(details_window, text="Обновить",
                      command=lambda: self.open_update_window(entry_id, selected_entry)).pack(pady=5)
            tk.Button(details_window, text="Удалить",
                      command=lambda: self.delete_password_entry(entry_id, details_window)).pack(pady=5)
        else:
            tk.Label(details_window, text="Детали не найдены.").pack(pady=20)

    def open_update_window(self, entry_id, current_data):
        update_window = tk.Toplevel(self.master)
        update_window.title(f"Обновить запись (ID: {entry_id})")
        update_window.geometry("300x200")

        tk.Label(update_window, text="Сервис:").pack(pady=2)
        service_var = tk.StringVar(value=current_data['service_name'])
        service_entry = tk.Entry(update_window, textvariable=service_var)
        service_entry.pack(pady=2)

        tk.Label(update_window, text="Логин/Email:").pack(pady=2)
        username_var = tk.StringVar(value=current_data['username_or_email'])
        username_entry = tk.Entry(update_window, textvariable=username_var)
        username_entry.pack(pady=2)

        tk.Label(update_window, text="Новый пароль:").pack(pady=2)
        password_var = tk.StringVar()
        password_entry = tk.Entry(update_window, textvariable=password_var, show="*")
        password_entry.pack(pady=2)

        def perform_update():
            new_service = service_var.get()
            new_username = username_var.get()
            new_password = password_var.get()

            if not new_service or not new_username or not new_password:
                messagebox.showwarning("Предупреждение", "Пожалуйста, заполните все поля для обновления.")
                return

            response = self.api.update_password_entry(entry_id, new_service, new_username, new_password)
            if response and "id" in response:
                messagebox.showinfo("Успех", "Запись успешно обновлена!")
                update_window.destroy()
                self.load_passwords()
            elif response:
                messagebox.showerror("Ошибка обновления", response.get("detail", "Неизвестная ошибка"))

        # Исправлена опечатка здесь: paddy -> pady
        tk.Button(update_window, text="Сохранить изменения", command=perform_update).pack(pady=10)

    def delete_password_entry(self, entry_id, parent_window):
        if messagebox.askyesno("Подтверждение удаления", f"Вы уверены, что хотите удалить запись с ID: {entry_id}?"):
            status_code, response_text = self.api.delete_password_entry(entry_id)
            # Проверяем, что status_code не None перед сравнением
            if status_code == 204:
                messagebox.showinfo("Успех", "Запись успешно удалена.")
                if parent_window:  # Закрываем окно деталей, если оно передано
                    parent_window.destroy()
                self.load_passwords()
            elif response_text:  # Если response_text не None, но статус не 204
                messagebox.showerror("Ошибка удаления", f"Не удалось удалить запись: {response_text}")


if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordManagerApp(root)
    root.mainloop()