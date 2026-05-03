import os
import json
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
import requests
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget 
from kivy.clock import Clock


interval = 5
#ip_antigua = "http://209.105.239.193:80"
ip = "http://38.247.140.62:80"
token = None

def register_user(username, password):
    url = f"{ip}/register"
    data = {"username": username, "password": password}
    response = requests.post(url, json=data, timeout=30)
    if response.status_code == 201:
        response_data = response.json()
        if response_data.get("status") == "success":
            print("Registro exitoso:", response_data["username"])
            return True, response_data["username"] 
    else:
        print("Error en el registro:", response.json().get("message"))
    return False, ""  

def load_session():
    try:
        with open('session_data.json', 'r') as file:
            session_data = json.load(file)
        return session_data.get('token'), session_data.get('username')
    except FileNotFoundError:
        print("ARCHIVO NO ENCONTRADO")
        return None, None

def check_session():
    token, username = load_session()
    if not token:
        print("No hay token disponible.")
        return None
    
    print(f"Token encontrado: {token}")
    
    headers = {"Authorization": token}
    try:
        response = requests.get(f'{ip}/check_session', headers=headers, timeout=30)  
        print(f"Response Status Code: {response.status_code}")  
        
        if response.status_code == 200:
            session_data = response.json()
            username = session_data.get("username")
            print(f'USERNAMEEEE: {username}')
            return username
        
        elif response.status_code == 401:
            error_message = response.json().get("message", "Error desconocido")
            print(f"Error: {error_message}")
            return None
        
        else:
            print(f"Error en la respuesta: {response.status_code}")
            return None
    
    except Exception as e:
        print(f"Error al hacer la solicitud: {str(e)}")
        return None

def clear_session():
    archivo = "session_data.json"
    if os.path.exists(archivo):
        os.remove(archivo)
        print(f"Archivo {archivo} eliminado con éxito.")
    else:
        print(f"El archivo {archivo} no existe.")
    """if token:
        headers = {"Authorization": token}
        response = requests.post(f'{ip}/logout', headers=headers, timeout=30) 
        if response.status_code == 200:
            print("Sesión eliminada correctamente")
            token = None"""

def save_session(token, username):
    session_data = {
        "token": token,
        "username": username
    }
    with open('session_data.json', 'w') as file:
        json.dump(session_data, file)

def start_bot_vps():
    try:
        response = requests.post(f'{ip}/start_bot', timeout=30)
        return response.status_code == 200
    except Exception as e:
        print(f"Excepción al iniciar el bot en el VPS: {e}")
        return False

def stop_bot_vps():
    try:
        response = requests.post(f'{ip}/stop_bot', timeout=30)
        return response.status_code == 200
    except Exception as e:
        print(f"Excepción al detener el bot en el VPS: {e}")
        return False

def check_bot_status_vps():
    try:
        response = requests.get(f'{ip}/check_bot_status', timeout=30)
        if response.status_code == 200:
            return response.json().get("active", False)
    except requests.RequestException as e:
        print(f"Excepción al verificar el estado del bot en el VPS: {e}")
    return False

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(
            orientation='vertical',
            padding=[20, 50, 20, 20],
            spacing=15,
        )

        with self.canvas.before:
            self.bg_color = Color(0.9, 0.95, 1, 1)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_background, pos=self.update_background)

        self.label = Label(
            text="[b]Iniciar Sesión[/b]",
            font_size=28,
            markup=True,
            color=(0, 0.2, 0.5, 1),
        )
        self.layout.add_widget(self.label)

        self.username_input = TextInput(
            hint_text="username",
            size_hint=(1, None),
            height=Window.height * 0.10,
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1),
            cursor_color=(0, 0.5, 1, 1),
            padding=[10, 10]
        )
        self.layout.add_widget(self.username_input)

        self.password_input = TextInput(
            hint_text="Contraseña",
            password=True,
            size_hint=(1, None),
            height=Window.height * 0.10,
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1),
            cursor_color=(0, 0.5, 1, 1),
            padding=[10, 10]
        )
        self.layout.add_widget(self.password_input)

        self.login_button = Button(
            text="Iniciar Sesión",
            size_hint=(1, None),
            height=Window.height * 0.15,
            background_normal="",
            background_color=(0, 0.5, 1, 1),
            color=(1, 1, 1, 1),
            font_size=18,
            bold=True
        )
        self.login_button.bind(on_press=self.verify_credentials)
        self.layout.add_widget(self.login_button)

        self.signup_button = Button(
            text="Registrarse",
            size_hint=(1, None),
            height=Window.height * 0.15,
            background_normal="",
            background_color=(0.2, 0.8, 0.2, 1),
            color=(1, 1, 1, 1),
            font_size=18,
            bold=True
        )
        self.signup_button.bind(on_press=self.go_to_signup)
        self.layout.add_widget(self.signup_button)

        self.add_widget(self.layout)

    def update_background(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

    def go_to_signup(self, instance):
        self.manager.current = "signup"

    def verify_credentials(self, instance):
        global token
        username = self.username_input.text
        password = self.password_input.text

        response = requests.post(f'{ip}/login', json={"username": username, "password": password})

        if response.status_code == 200:
            response_data = response.json()  
            token = response_data.get("token")  

            if token:
                print(f'TOKEEEEEEEN: {token}')
                token = token
                save_session(token, username)
                self.manager.current = "verify_credentials"  
                
            else:
                print("No se recibió el token")
                error_message = "No se recibió el token."
                self.label.text = f"[color=#FF0000]Error: {error_message}[/color]"
        else:
            error_message = response.json().get("message", "Error desconocido")
            self.label.text = f"[color=#FF0000]Error: {error_message}[/color]"

    


class SignupScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(
            orientation='vertical',
            padding=[20, 50, 20, 20], 
            spacing=15,
        )

        with self.layout.canvas.before:
            self.bg_color = Color(rgba=(0.9, 0.95, 1, 1))  
            self.bg_rect = Rectangle(size=self.layout.size, pos=self.layout.pos)

        self.layout.bind(size=self.update_background, pos=self.update_background)

        self.label = Label(
            text="[b]Registrarse[/b]",
            font_size=28,
            markup=True,  
            color=(0, 0.2, 0.5, 1), 
        )
        self.layout.add_widget(self.label)

        self.username_input = TextInput(
            hint_text="username",
            size_hint=(1, None),
            height=Window.height * 0.10,  
            background_color=(1, 1, 1, 1),  
            foreground_color=(0, 0, 0, 1),  
            padding=[10, 10],
        )
        self.layout.add_widget(self.username_input)

        self.password_input = TextInput(
            hint_text="Contraseña",
            password=True,
            size_hint=(1, None),
            height=Window.height * 0.10,  
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1),
            padding=[10, 10],
        )
        self.layout.add_widget(self.password_input)

        self.signup_button = Button(
            text="Registrarse",
            size_hint=(1, None),
            height=Window.height * 0.15,  
            background_normal="",
            background_color=(0.2, 0.6, 0.9, 1),  
            color=(1, 1, 1, 1),  
            font_size=18,
            bold=True,
        )
        self.signup_button.bind(on_press=self.register_user)
        self.layout.add_widget(self.signup_button)

        self.back_button = Button(
            text="Volver",
            size_hint=(1, None),
            height=Window.height * 0.15,  
            background_normal="",
            background_color=(0.9, 0.2, 0.2, 1),  
            color=(1, 1, 1, 1), 
            font_size=18,
            bold=True,
        )
        self.back_button.bind(on_press=self.go_to_login)
        self.layout.add_widget(self.back_button)

        self.add_widget(self.layout)

    def update_background(self, instance, value):
        self.bg_rect.size = self.layout.size
        self.bg_rect.pos = self.layout.pos

    def go_to_login(self, instance):
        self.manager.current = "login"

    def register_user(self, instance):
        username = self.username_input.text
        password = self.password_input.text
        success, username = register_user(username, password) 

        if success:
            self.manager.get_screen("update_account_details").set_username(username)  
            self.manager.current = "update_account_details"  
        else:
            self.label.text = "[color=#FF0000][b]El usuario ya existe. Inténtelo con nombre.[/b][/color]"



class AccountDetailsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.username = None  

        with self.canvas.before:
            Color(0.94, 0.96, 0.98, 1) 
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        main_layout = BoxLayout(orientation='vertical')

        layout = BoxLayout(
            orientation='vertical',
            padding=[40, 80, 40, 40],  
            spacing=20,
            size_hint=(1, None),
            height=600,  
        )
        layout.bind(minimum_height=layout.setter('height'))  

        title = Label(
            text="[b]Detalles de la Cuenta[/b]",
            font_size=28,
            markup=True,  
            color=(0, 0.2, 0.5, 1),  
        )
        layout.add_widget(title)

        layout.add_widget(self._create_label("ID de Cuenta:"))
        self.account_id_input = self._create_text_input()
        layout.add_widget(self.account_id_input)

        layout.add_widget(self._create_label("Contraseña de la Cuenta:"))
        self.account_password_input = self._create_text_input(password=True)
        layout.add_widget(self.account_password_input)

        layout.add_widget(self._create_label("Servidor:"))
        self.server_input = self._create_text_input()
        layout.add_widget(self.server_input)

        save_button = Button(
            text="Guardar",
            size_hint=(1, None),
            height=Window.height * 0.15,  
            background_normal="",
            background_color=(0.2, 0.6, 0.8, 1), 
            color=(1, 1, 1, 1),  
            font_size=20,
            bold=True,
        )
        save_button.bind(on_press=self.update_account_details)
        layout.add_widget(save_button)

        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(layout)
        main_layout.add_widget(scroll_view)

        self.add_widget(main_layout)

    def _create_label(self, text):
        return Label(
            text=text,
            font_size=18,
            size_hint_y=None,
            height=30,  
            color=(0, 0, 0, 1), 
        )

    def _create_text_input(self, password=False):
        return TextInput(
            multiline=False,
            password=password,
            size_hint_y=None,
            height=Window.height * 0.10, 
            background_color=(1, 1, 1, 1),  
            foreground_color=(0, 0, 0, 1),  
            cursor_color=(0.2, 0.6, 0.8, 1), 
            padding=[10, 10],
        )

    def set_username(self, username):
        self.username = username
        print(f"Username recibido en AccountDetailsScreen: {self.username}")

    def update_account_details(self, instance):
        username = self.username
        account_id = self.account_id_input.text
        account_password = self.account_password_input.text
        server = self.server_input.text

        if not username or not account_id or not account_password or not server:
            print("Faltan datos")
            return

        url = f"{ip}/update_account"
        data = {
            "username": username,
            "account_id": account_id,
            "account_password": account_password,
            "server": server,
        }
        try:
            response = requests.put(url, json=data, timeout=30)
            if response.status_code == 200:
                print("Detalles de la cuenta actualizados correctamente")
                self.manager.current = "verify_credentials"
            else:
                print("Error al actualizar detalles:", response.json()["message"])
        except requests.exceptions.RequestException as e:
            print(f"Error en la conexión: {e}")

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size



class VerifyCredentialsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(0.9, 0.95, 1, 1)  
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)

        scroll_view = ScrollView()
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=20, size_hint_y=None)
        main_layout.bind(minimum_height=main_layout.setter('height'))
        scroll_view.add_widget(main_layout)

        title_label = Label(
            text="[b]Verifica tus credenciales[/b]",
            font_size=28,
            markup=True,  
            color=(0, 0.2, 0.5, 1),  
        )
        title_label.bind(size=self._update_text)
        main_layout.add_widget(title_label)

        self.username_input = TextInput(
            hint_text="Ingresa tu usuario",
            size_hint=(1, None),
            height=Window.height * 0.10, 
            multiline=False,
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1),
            cursor_color=(0, 0.5, 1, 1),
            padding=[10, 10],
        )
        main_layout.add_widget(self.username_input)

        self.password_input = TextInput(
            hint_text="Ingresa contraseña de la cuenta de trading",
            password=True,
            size_hint=(1, None),
            height=Window.height * 0.10,  
            multiline=False,
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1),
            cursor_color=(0, 0.5, 1, 1),
            padding=[10, 10],
        )
        main_layout.add_widget(self.password_input)

        submit_button = Button(
            text="Verificar",
            size_hint=(1, None),
            height=Window.height * 0.15, 
            background_normal="",
            background_color=(0, 0.5, 1, 1),
            color=(1, 1, 1, 1),
            font_size=18,
            bold=True,
        )
        submit_button.bind(on_press=self.submit_credentials)
        main_layout.add_widget(submit_button)

        self.response_label = TextInput(
            readonly=True,
            multiline=True,
            hint_text="La respuesta aparecerá aquí",
            size_hint=(1, None),
            height=100,
            background_color=(0.95, 0.95, 0.95, 1),
            foreground_color=(0, 0, 0, 1),
            cursor_color=(0, 0.5, 1, 1),
            padding=[10, 10],
        )
        main_layout.add_widget(self.response_label)

        self.add_widget(scroll_view)

    def submit_credentials(self, instance):
        username = self.username_input.text
        password = self.password_input.text
        try:
            response = requests.post(
                f'{ip}/initialize-mt5',
                timeout=50,
                json={"username": username, "password": password},
            )
            if response.status_code == 200:
                self.response_label.text = response.json().get("message", "Success!")
                self.manager.current = "main"  
            else:
                self.response_label.text = response.json().get("message", "Login failed.")
        except requests.exceptions.RequestException as e:
            self.response_label.text = f"Error: {e}"

    def _update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

    def _update_text(self, instance, value):
        instance.text_size = instance.size


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(0.8, 0.9, 1, 1)  
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        self.layout.add_widget(Widget(size_hint_y=0.6))  

        self.start_button = Button(
            text='Iniciar Bot',
            size_hint=(1, None),
            height=Window.height * 0.15, 
            background_color=(0, 0.7, 0.2, 1),
            font_size=16
        )
        self.start_button.bind(on_press=self.start_bot)
        self.layout.add_widget(self.start_button)

        self.stop_button = Button(
            text='Detener Bot',
            size_hint=(1, None),
            height=Window.height * 0.15,  
            background_color=(0.8, 0, 0, 1),
            font_size=16
        )
        self.stop_button.bind(on_press=self.stop_bot)
        self.layout.add_widget(self.stop_button)

        self.status_label = Label(
            text='Estado: Desconocido',
            size_hint=(1, None),
            height=Window.height * 0.10,  
            font_size=16,
            color=(0, 0, 0, 1)
        )
        self.layout.add_widget(self.status_label)

        self.backend_messages = TextInput(
            hint_text='Mensajes del backend aparecerán aquí...',
            size_hint=(1, 0.3),
            height=Window.height * 0.35,  
            readonly=True,
            background_color=(0.95, 0.95, 0.95, 1), 
            font_size=14,
            foreground_color=(0, 0, 0, 1),  
            text_validate_unfocus=False  
        )
        self.layout.add_widget(self.backend_messages)

        self.logout_button = Button(
            text="Cerrar Sesión",
            size_hint=(1, None),
            height=Window.height * 0.15, 
            background_color=(0.3, 0.3, 0.8, 1),
            font_size=16
        )
        self.logout_button.bind(on_press=self.logout)
        self.layout.add_widget(self.logout_button)

        self.subscribe_button = Button(
            text="Suscribirse",
            size_hint=(1, None),
            height=Window.height * 0.15,
            background_normal="",
            background_color=(1, 0.6, 0, 1), 
            color=(1, 1, 1, 1),  
            font_size=18,
            bold=True
        )
        self.subscribe_button.bind(on_press=self.open_subscription_page)
        self.layout.add_widget(self.subscribe_button)

        self.add_widget(self.layout)

        self.update_event = None  

    def logout(self, instance):
        try:
            response = requests.post(f'{ip}/logout', timeout=10)
            if response.status_code == 200:
                print("Sesión cerrada correctamente.")
                clear_session()
                self.manager.current = "login"
            else:
                self.update_backend_message("Error al cerrar sesión: " + response.text)
        except requests.exceptions.RequestException as e:
            self.update_backend_message(f"Error de conexión al cerrar sesión: {e}")

    def start_bot(self, instance):
        if start_bot_vps():
            self.status_label.text = 'Estado: En ejecución'
            self.update_backend_message("Bot iniciado correctamente.")

            if not self.update_event:
                self.update_event = Clock.schedule_interval(self.display_operations, 5)
        else:
            self.status_label.text = 'Error al iniciar el bot en el VPS'
            self.update_backend_message("Error al iniciar el bot.")

    def stop_bot(self, instance):
        if stop_bot_vps():
            self.status_label.text = 'Estado: Detenido'
            self.update_backend_message("Bot detenido correctamente.")

            if self.update_event:
                Clock.unschedule(self.update_event)
                self.update_event = None
        else:
            self.status_label.text = 'Error al detener el bot en el VPS'
            self.update_backend_message("Error al detener el bot.")

    def update_backend_message(self, message):
        self.backend_messages.text += f"\n{message}"

    def update_status(self, dt):
        if check_bot_status_vps():
            self.status_label.text = 'Estado: En ejecución'
        else:
            self.status_label.text = 'Estado: Detenido'

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size 

    def add_message(self, message):
        self.backend_messages.text = message  

    def get_operations_from_api(self):
        try:
            response = requests.get(f'{ip}/get_operations', timeout=30)
            if response.status_code == 200:
                print(f'MENSAJES: {response.text}')
                return response.text  
            else:
                return "Hubo un problema con la solicitud."
        except requests.exceptions.RequestException as e:
            return f"Hubo un problema: {e}"

    def display_operations(self, dt):
        messages = self.get_operations_from_api()
        self.add_message(messages)  

    def open_subscription_page(self, instance):
        import webbrowser
        try:
            session_file = "session_data.json"
            with open(session_file, "r") as file:
                session_data = json.load(file)

            username = session_data.get("username")
            if not username:
                print("No se encontró 'username' en session_data.json.")
            else:
                url = f'{ip}/get_logged_in_user'

                data = {"username": username}

                response = requests.post(url, json=data, timeout=30)

                if response.status_code == 200:
                    response_data = response.json()
                    if response_data["status"] == "success":
                        payment_link_url = response_data["payment_link_url"]
                        print(f"Abriendo Payment Link: {payment_link_url}")
                        webbrowser.open(payment_link_url)
                else:
                    print("Error en la solicitud:", response.status_code)
        except FileNotFoundError:
            print(f"El archivo {session_file} no existe.")
        except json.JSONDecodeError:
            print(f"Error al decodificar el archivo {session_file}. Asegúrate de que el formato sea válido.")
        except requests.exceptions.RequestException as e:
            print("Error al conectar con el servidor:", e)
        #webbrowser.open("https://buy.stripe.com/test_8wM155dwHafF5IQ5kk")


class RealtimeBotApp(App):
    def build(self):
        Window.size = (Window.width, Window.height)
        sm = ScreenManager()

        if check_session() is not None:
            sm.add_widget(MainScreen(name="main"))
        else:
            sm.add_widget(LoginScreen(name="login"))

        sm.add_widget(SignupScreen(name="signup"))
        sm.add_widget(AccountDetailsScreen(name="update_account_details"))
        sm.add_widget(VerifyCredentialsScreen(name="verify_credentials"))
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(LoginScreen(name="login"))
        return sm

if __name__ == "__main__":
    RealtimeBotApp().run()