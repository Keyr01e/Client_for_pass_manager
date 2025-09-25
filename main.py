import customtkinter as ctk
from tkinter import messagebox
import requests

API_URL = 'http://127.0.0.1:8000'  # Убедитесь, что ваш API запущен на этом адресе


class APILogic:
    def __init__(self, base_url):
        self.base = base_url.rstrip('/')
        self.session = requests.Session()
        self.cookie = None

    def _handle_request_error(self, e, operation_name):
        if isinstance(e, requests.exceptions.ConnectionError):
            messagebox.showerror("Ошибка", "Не удалось подключиться к серверу.")
        else:
            messagebox.showerror("Ошибка", f"Произошла ошибка при {operation_name}: {e}")
        return None

    def register(self, username, password):
        url = f'{self.base}/auth/register'
        data = {"username": username, "password": password}
        try:
            response = requests.post(url, json=data)
            return response.json()
        except requests.exceptions.RequestException as e:
            return self._handle_request_error(e, "регистрации")

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
        except requests.exceptions.RequestException as e:
            return self._handle_request_error(e, "входе"), None

    def logout(self):
        if not self.cookie:
            return None, None
        url = f'{self.base}/auth/logout'
        try:
            response = requests.post(url, cookies=self.cookie)
            self.cookie = None
            return response.json(), response.status_code
        except requests.exceptions.RequestException as e:
            return self._handle_request_error(e, "выходе"), None

    def me(self):
        if not self.cookie:
            return None
        url = f'{self.base}/auth/me'
        try:
            response = requests.get(url, cookies=self.cookie)
            return response.json()
        except requests.exceptions.RequestException as e:
            return self._handle_request_error(e, "получении данных пользователя")

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
        except requests.exceptions.RequestException as e:
            return self._handle_request_error(e, "создании записи")

    def get_decoded_password(self, entry_id):
        if not self.cookie:
            messagebox.showwarning("Предупреждение", "Вы не авторизованы.")
            return None
        url = f'{self.base}/passwords/{entry_id}/decrypt'
        try:
            response = requests.get(url, cookies=self.cookie)
            return response.json()
        except requests.exceptions.RequestException as e:
            return self._handle_request_error(e, "расшифровке пароля")

    def get_passwords(self):
        if not self.cookie:
            messagebox.showwarning("Предупреждение", "Вы не авторизованы.")
            return None, None
        url = f'{self.base}/passwords'
        try:
            response = requests.get(url, cookies=self.cookie)
            return response.status_code, response.json()
        except requests.exceptions.RequestException as e:
            return self._handle_request_error(e, "получении паролей"), None

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
        except requests.exceptions.RequestException as e:
            return self._handle_request_error(e, "обновлении записи")

    def delete_password_entry(self, entry_id):
        if not self.cookie:
            messagebox.showwarning("Предупреждение", "Вы не авторизованы.")
            return None, None
        url = f'{self.base}/passwords/{entry_id}'
        try:
            response = requests.delete(url, cookies=self.cookie)
            return response.status_code, response.text
        except requests.exceptions.RequestException as e:
            return self._handle_request_error(e, "удалении записи"), None


class PasswordManagerApp:
    def __init__(self, master):
        self.master = master
        master.title("Менеджер паролей")
        master.geometry("400x600")

        # Установка темы CustomTkinter
        ctk.set_appearance_mode("System")  # "System", "Dark", "Light"
        ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"

        self.api = APILogic(API_URL)
        self.all_passwords_data = []  # Для хранения полных данных паролей

        self.create_login_widgets()

    def create_login_widgets(self):
        self.clear_frame()

        self.login_frame = ctk.CTkFrame(self.master)
        self.login_frame.pack(pady=20, padx=60, fill="both", expand=True)

        ctk.CTkLabel(self.login_frame, text="Вход / Регистрация", font=ctk.CTkFont(size=20, weight="bold")).pack(
            pady=(20, 10))

        ctk.CTkLabel(self.login_frame, text="Имя пользователя:").pack(pady=(10, 0))
        self.username_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Введите имя пользователя")
        self.username_entry.pack(pady=(0, 10))

        ctk.CTkLabel(self.login_frame, text="Пароль:").pack(pady=(10, 0))
        self.password_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Введите пароль", show="*")
        self.password_entry.pack(pady=(0, 20))

        self.login_button = ctk.CTkButton(self.login_frame, text="Войти", command=self.login)
        self.login_button.pack(pady=5)

        self.register_button = ctk.CTkButton(self.login_frame, text="Зарегистрироваться", command=self.register)
        self.register_button.pack(pady=5)

    def create_main_app_widgets(self):
        self.clear_frame()
        self.master.geometry("800x700")  # Увеличиваем размер для основного окна

        # Панель для информации о пользователе и кнопок управления
        top_frame = ctk.CTkFrame(self.master)
        top_frame.pack(pady=10, padx=10, fill="x")

        self.current_user_label = ctk.CTkLabel(top_frame, text="Текущий пользователь: Загрузка...",
                                               font=ctk.CTkFont(size=14))
        self.current_user_label.pack(side="left", padx=10, pady=5)
        self.update_current_user_info()

        self.logout_button = ctk.CTkButton(top_frame, text="Выйти", command=self.logout, fg_color="red",
                                           hover_color="#c0392b")
        self.logout_button.pack(side="right", padx=10, pady=5)

        self.refresh_button = ctk.CTkButton(top_frame, text="Обновить список", command=self.load_passwords)
        self.refresh_button.pack(side="right", padx=10, pady=5)

        # Фрейм для создания записи
        self.create_password_frame = ctk.CTkFrame(self.master)
        self.create_password_frame.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(self.create_password_frame, text="Создать новую запись",
                     font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, columnspan=2, pady=10)

        ctk.CTkLabel(self.create_password_frame, text="Сервис:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.service_entry = ctk.CTkEntry(self.create_password_frame, placeholder_text="Название сервиса")
        self.service_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        ctk.CTkLabel(self.create_password_frame, text="Логин/Email:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.service_username_entry = ctk.CTkEntry(self.create_password_frame, placeholder_text="Логин или Email")
        self.service_username_entry.grid(row=2, column=1, padx=5, pady=2, sticky="ew")

        ctk.CTkLabel(self.create_password_frame, text="Пароль:").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        self.service_password_entry = ctk.CTkEntry(self.create_password_frame, placeholder_text="Пароль", show="*")
        self.service_password_entry.grid(row=3, column=1, padx=5, pady=2, sticky="ew")

        self.create_password_frame.grid_columnconfigure(1, weight=1)  # Для растягивания поля ввода

        create_button = ctk.CTkButton(self.create_password_frame, text="Создать пароль",
                                      command=self.create_password_entry)
        create_button.grid(row=4, columnspan=2, pady=10)

        # Фрейм для списка паролей
        self.passwords_frame = ctk.CTkFrame(self.master)
        self.passwords_frame.pack(pady=10, padx=10, fill="both", expand=True)
        ctk.CTkLabel(self.passwords_frame, text="Сохраненные пароли", font=ctk.CTkFont(size=16, weight="bold")).pack(
            pady=(0, 10))

        self.passwords_scroll_frame = ctk.CTkScrollableFrame(self.passwords_frame, height=250)
        self.passwords_scroll_frame.pack(fill="both", expand=True, padx=10, pady=5)

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
            self.create_login_widgets()
        elif response:
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
        elif response_data:
            messagebox.showerror("Ошибка входа", response_data.get("detail", "Неизвестная ошибка"))

    def logout(self):
        response_data, status_code = self.api.logout()
        if status_code == 200:
            messagebox.showinfo("Выход", "Вы успешно вышли из системы.")
            self.create_login_widgets()
        elif response_data:
            messagebox.showerror("Ошибка выхода", response_data.get("detail", "Неизвестная ошибка"))

    def update_current_user_info(self):
        user_info = self.api.me()
        if user_info and "username" in user_info:
            self.current_user_label.configure(text=f"Текущий пользователь: {user_info['username']}")
        else:
            self.current_user_label.configure(text="Текущий пользователь: Неизвестно")

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
            self.service_entry.delete(0, ctk.END)
            self.service_username_entry.delete(0, ctk.END)
            self.service_password_entry.delete(0, ctk.END)
            self.load_passwords()
        elif response:
            messagebox.showerror("Ошибка создания записи", response.get("detail", "Неизвестная ошибка"))

    def load_passwords(self):
        # Очищаем содержимое ScrollableFrame
        for widget in self.passwords_scroll_frame.winfo_children():
            widget.destroy()

        status_code, passwords_data = self.api.get_passwords()
        if status_code == 200 and isinstance(passwords_data, list):
            self.all_passwords_data = passwords_data  # Сохраняем все данные
            if not passwords_data:
                ctk.CTkLabel(self.passwords_scroll_frame, text="Пока нет сохраненных паролей.", text_color="gray").pack(
                    pady=10)
            for entry in passwords_data:
                entry_frame = ctk.CTkFrame(self.passwords_scroll_frame, corner_radius=10)
                entry_frame.pack(fill="x", pady=5, padx=5)

                ctk.CTkLabel(entry_frame, text=f"Сервис: {entry['service_name']}",
                             font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=10, pady=5)
                ctk.CTkLabel(entry_frame, text=f"Логин: {entry['username_or_email']}").pack(side="left", padx=10,
                                                                                            pady=5)

                # Используем lambda для передачи entry_id в show_password_details
                details_button = ctk.CTkButton(entry_frame, text="Детали",
                                               command=lambda entry_id=entry['id'],
                                                              data=entry: self.show_password_details(entry_id, data))
                details_button.pack(side="right", padx=10, pady=5)
        elif passwords_data:
            messagebox.showerror("Ошибка загрузки паролей", passwords_data.get("detail", "Неизвестная ошибка"))

    def show_password_details(self, entry_id, selected_entry):
        details_window = ctk.CTkToplevel(self.master)
        details_window.title(f"Детали пароля (ID: {entry_id})")
        details_window.geometry("400x350")
        details_window.grab_set()  # Сделать окно модальным

        ctk.CTkLabel(details_window, text=f"Сервис: {selected_entry['service_name']}",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        ctk.CTkLabel(details_window, text=f"Логин/Email: {selected_entry['username_or_email']}",
                     font=ctk.CTkFont(size=14)).pack(pady=5)

        password_display = ctk.StringVar()
        password_entry_widget = ctk.CTkEntry(details_window, textvariable=password_display, show="*", width=250)
        password_entry_widget.pack(pady=10)

        def decrypt_and_show():
            decoded_pass = self.api.get_decoded_password(entry_id)
            if decoded_pass and "password" in decoded_pass:
                password_display.set(decoded_pass["password"])
                password_entry_widget.configure(show="")  # Показать пароль
                decrypt_button.configure(text="Скрыть пароль", command=hide_password)
            elif decoded_pass:
                messagebox.showerror("Ошибка расшифровки", decoded_pass.get("detail", "Неизвестная ошибка"))

        def hide_password():
            password_display.set("")
            password_entry_widget.configure(show="*")
            decrypt_button.configure(text="Показать пароль", command=decrypt_and_show)

        decrypt_button = ctk.CTkButton(details_window, text="Показать пароль", command=decrypt_and_show)
        decrypt_button.pack(pady=5)

        # Кнопки для обновления и удаления
        button_frame = ctk.CTkFrame(details_window, fg_color="transparent")
        button_frame.pack(pady=10)

        ctk.CTkButton(button_frame, text="Обновить",
                      command=lambda: self.open_update_window(entry_id, selected_entry, details_window)).pack(
            side="left", padx=5)
        ctk.CTkButton(button_frame, text="Удалить",
                      command=lambda: self.delete_password_entry_ui(entry_id, details_window), fg_color="red",
                      hover_color="#c0392b").pack(side="left", padx=5)

    def open_update_window(self, entry_id, current_data, parent_window):
        update_window = ctk.CTkToplevel(self.master)
        update_window.title(f"Обновить запись (ID: {entry_id})")
        update_window.geometry("350x300")
        update_window.grab_set()  # Сделать окно модальным

        ctk.CTkLabel(update_window, text="Обновить запись", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        ctk.CTkLabel(update_window, text="Сервис:").pack(pady=(5, 0))
        service_var = ctk.StringVar(value=current_data['service_name'])
        service_entry = ctk.CTkEntry(update_window, textvariable=service_var, width=250)
        service_entry.pack(pady=(0, 5))

        ctk.CTkLabel(update_window, text="Логин/Email:").pack(pady=(5, 0))
        username_var = ctk.StringVar(value=current_data['username_or_email'])
        username_entry = ctk.CTkEntry(update_window, textvariable=username_var, width=250)
        username_entry.pack(pady=(0, 5))

        ctk.CTkLabel(update_window, text="Новый пароль:").pack(pady=(5, 0))
        password_var = ctk.StringVar()
        password_entry = ctk.CTkEntry(update_window, textvariable=password_var, show="*", width=250,
                                      placeholder_text="Оставьте пустым, если не меняете")
        password_entry.pack(pady=(0, 10))

        def perform_update():
            new_service = service_var.get()
            new_username = username_var.get()
            new_password = password_var.get()

            # Если пароль не введен, используем текущий пароль (нужно будет получать его расшифрованным с сервера)
            # В данном примере, если поле пустое, предполагается, что пароль не меняется,
            # но API требует пароль, поэтому для простоты я делаю его обязательным.
            # В реальном приложении можно было бы получить текущий расшифрованный пароль
            # и отправить его, если пользователь не ввел новый.
            if not new_service or not new_username:
                messagebox.showwarning("Предупреждение", "Пожалуйста, заполните поля 'Сервис' и 'Логин/Email'.")
                return

            # Для обновления пароля его обязательно нужно ввести, иначе можно отправить старый
            # (предполагая, что API это обработает или вы сами получите старый расшифрованный)
            if not new_password:
                messagebox.showwarning("Предупреждение",
                                       "Пожалуйста, введите новый пароль или повторите старый для обновления.")
                return

            response = self.api.update_password_entry(entry_id, new_service, new_username, new_password)
            if response and "id" in response:
                messagebox.showinfo("Успех", "Запись успешно обновлена!")
                update_window.destroy()
                parent_window.destroy()  # Закрываем окно деталей
                self.load_passwords()
            elif response:
                messagebox.showerror("Ошибка обновления", response.get("detail", "Неизвестная ошибка"))

        ctk.CTkButton(update_window, text="Сохранить изменения", command=perform_update).pack(pady=10)

    def delete_password_entry_ui(self, entry_id, parent_window):
        if messagebox.askyesno("Подтверждение удаления", f"Вы уверены, что хотите удалить запись с ID: {entry_id}?"):
            status_code, response_text = self.api.delete_password_entry(entry_id)
            if status_code == 204:
                messagebox.showinfo("Успех", "Запись успешно удалена.")
                if parent_window:
                    parent_window.destroy()  # Закрываем окно деталей
                self.load_passwords()
            elif response_text:
                messagebox.showerror("Ошибка удаления", f"Не удалось удалить запись: {response_text}")


if __name__ == "__main__":
    root = ctk.CTk()
    app = PasswordManagerApp(root)
    root.mainloop()