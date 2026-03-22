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


interval = 5  # Intervalo en segundos para verificar el estado del bot
#ip_antigua = "http://209.105.239.193:80"
ip = "http://38.247.140.62:80"
token = None

def register_user(username, password):
    url = f"{ip}/register"
    data = {"username": username, "password": password}
    response = requests.post(url, json=data, timeout=30)
    if response.status_code == 201:
        # Verifica si la respuesta tiene un 'status' igual a 'success'
        response_data = response.json()
        if response_data.get("status") == "success":
            print("Registro exitoso:", response_data["username"])
            return True, response_data["username"]  # Retorna éxito y username
    else:
        # Si hay un error, se imprime el mensaje de error desde el backend
        print("Error en el registro:", response.json().get("message"))
    return False, ""  # Retorna False si no fue exitoso

def load_session():
    try:
        with open('session_data.json', 'r') as file:
            session_data = json.load(file)
        return session_data.get('token'), session_data.get('username')
    except FileNotFoundError:
        print("ARCHIVO NO ENCONTRADO")
        return None, None

def check_session():
    """Verifica si el usuario ya está logueado usando una llamada al backend con JWT."""
    token, username = load_session()
    if not token:
        print("No hay token disponible.")
        return None
    
    print(f"Token encontrado: {token}")
    
    headers = {"Authorization": token}
    try:
        response = requests.get(f'{ip}/check_session', headers=headers, timeout=30)  
        print(f"Response Status Code: {response.status_code}")  # Imprime el código de estado de la respuesta
        
        if response.status_code == 200:
            session_data = response.json()
            username = session_data.get("username")
            print(f'USERNAMEEEE: {username}')
            return username
        
        elif response.status_code == 401:
            # Token inválido o expirado
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
    """Elimina la sesión de JWT mediante una llamada al backend."""
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

# Funciones para manejar el bot en el VPS
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

        # Fondo de la pantalla
        with self.canvas.before:
            self.bg_color = Color(0.9, 0.95, 1, 1)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_background, pos=self.update_background)

        # Título estilizado
        self.label = Label(
            text="[b]Iniciar Sesión[/b]",
            font_size=28,
            markup=True,
            color=(0, 0.2, 0.5, 1),
        )
        self.layout.add_widget(self.label)

        # Campo de usuario estilizado
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

        # Campo de contraseña estilizado
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

        # Botón de inicio de sesión
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

        # Botón de registrarse
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

        # Verificar si la respuesta es exitosa
        if response.status_code == 200:
            # Obtener el token desde la respuesta JSON
            response_data = response.json()  # Parsear la respuesta JSON
            token = response_data.get("token")  # Obtener el token

            if token:
                print(f'TOKEEEEEEEN: {token}')
                token = token
                # Aquí podrías hacer algo más con el token, como guardarlo para futuras peticiones
                save_session(token, username)
                self.manager.current = "verify_credentials"  # Cambiar la pantalla
                
            else:
                print("No se recibió el token")
                error_message = "No se recibió el token."
                self.label.text = f"[color=#FF0000]Error: {error_message}[/color]"
        else:
            # Si el login no es exitoso, mostrar el mensaje de error
            error_message = response.json().get("message", "Error desconocido")
            self.label.text = f"[color=#FF0000]Error: {error_message}[/color]"

    


class SignupScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(
            orientation='vertical',
            padding=[20, 50, 20, 20],  # Espaciado: izquierda, arriba, derecha, abajo
            spacing=15,
        )

        # Agregar un fondo de color al layout
        with self.layout.canvas.before:
            self.bg_color = Color(rgba=(0.9, 0.95, 1, 1))  # Color claro
            self.bg_rect = Rectangle(size=self.layout.size, pos=self.layout.pos)

        # Actualizar el fondo cuando cambien el tamaño o la posición
        self.layout.bind(size=self.update_background, pos=self.update_background)

        # Título estilizado
        self.label = Label(
            text="[b]Registrarse[/b]",
            font_size=28,
            markup=True,  # Activar etiquetas BBCode
            color=(0, 0.2, 0.5, 1),  # Azul oscuro
        )
        self.layout.add_widget(self.label)

        # Input para el usuario
        self.username_input = TextInput(
            hint_text="Correo electronico",
            size_hint=(1, None),
            height=Window.height * 0.10,  # 10% de la altura de la pantalla
            background_color=(1, 1, 1, 1),  # Blanco puro
            foreground_color=(0, 0, 0, 1),  # Negro
            padding=[10, 10],
        )
        self.layout.add_widget(self.username_input)

        # Input para la contraseña
        self.password_input = TextInput(
            hint_text="Contraseña",
            password=True,
            size_hint=(1, None),
            height=Window.height * 0.10,  # 10% de la altura de la pantalla
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1),
            padding=[10, 10],
        )
        self.layout.add_widget(self.password_input)

        # Botón de registro
        self.signup_button = Button(
            text="Registrarse",
            size_hint=(1, None),
            height=Window.height * 0.15,  # 10% de la altura de la pantalla
            background_normal="",
            background_color=(0.2, 0.6, 0.9, 1),  # Azul claro
            color=(1, 1, 1, 1),  # Texto blanco
            font_size=18,
            bold=True,
        )
        self.signup_button.bind(on_press=self.register_user)
        self.layout.add_widget(self.signup_button)

        # Botón de volver
        self.back_button = Button(
            text="Volver",
            size_hint=(1, None),
            height=Window.height * 0.15,  # 10% de la altura de la pantalla
            background_normal="",
            background_color=(0.9, 0.2, 0.2, 1),  # Rojo claro
            color=(1, 1, 1, 1),  # Texto blanco
            font_size=18,
            bold=True,
        )
        self.back_button.bind(on_press=self.go_to_login)
        self.layout.add_widget(self.back_button)

        # Agregar layout principal a la pantalla
        self.add_widget(self.layout)

    def update_background(self, instance, value):
        self.bg_rect.size = self.layout.size
        self.bg_rect.pos = self.layout.pos

    def go_to_login(self, instance):
        self.manager.current = "login"

    def register_user(self, instance):
        username = self.username_input.text
        password = self.password_input.text
        success, username = register_user(username, password)  # Captura el resultado y el username

        if success:
            # Si el registro es exitoso, guarda el username en el ScreenManager
            self.manager.get_screen("update_account_details").set_username(username)  # Llama a un método para asignar el username
            self.manager.current = "update_account_details"  # Redirigir a la pantalla de detalles de la cuenta
        else:
            self.label.text = "[color=#FF0000][b]El usuario ya existe. Inténtelo con nombre.[/b][/color]"



class AccountDetailsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.username = None  # Inicialización de la variable

        # Fondo personalizado
        with self.canvas.before:
            Color(0.94, 0.96, 0.98, 1)  # Azul claro
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        # Contenedor principal
        main_layout = BoxLayout(orientation='vertical')

        # Subcontenedor con alineación y estilo
        layout = BoxLayout(
            orientation='vertical',
            padding=[40, 80, 40, 40],  # Márgenes alrededor
            spacing=20,
            size_hint=(1, None),
            height=600,  # Altura total del contenido
        )
        layout.bind(minimum_height=layout.setter('height'))  # Ajusta la altura según el contenido

        # Título estilizado
        title = Label(
            text="[b]Detalles de la Cuenta[/b]",
            font_size=28,
            markup=True,  # Activar etiquetas BBCode
            color=(0, 0.2, 0.5, 1),  # Azul oscuro
        )
        layout.add_widget(title)

        # Campos de entrada estilizados
        layout.add_widget(self._create_label("ID de Cuenta:"))
        self.account_id_input = self._create_text_input()
        layout.add_widget(self.account_id_input)

        layout.add_widget(self._create_label("Contraseña de la Cuenta:"))
        self.account_password_input = self._create_text_input(password=True)
        layout.add_widget(self.account_password_input)

        layout.add_widget(self._create_label("Servidor:"))
        self.server_input = self._create_text_input()
        layout.add_widget(self.server_input)

        # Botón estilizado para guardar
        save_button = Button(
            text="Guardar",
            size_hint=(1, None),
            height=Window.height * 0.15,  # 10% de la altura de la pantalla
            background_normal="",
            background_color=(0.2, 0.6, 0.8, 1),  # Azul brillante
            color=(1, 1, 1, 1),  # Texto blanco
            font_size=20,
            bold=True,
        )
        save_button.bind(on_press=self.update_account_details)
        layout.add_widget(save_button)

        # Contenedor con ScrollView para manejar pantallas pequeñas
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(layout)
        main_layout.add_widget(scroll_view)

        self.add_widget(main_layout)

    def _create_label(self, text):
        """Crea un label estilizado."""
        return Label(
            text=text,
            font_size=18,
            size_hint_y=None,
            height=30,  # Altura fija
            color=(0, 0, 0, 1),  # Negro
        )

    def _create_text_input(self, password=False):
        """Crea un campo de entrada estilizado."""
        return TextInput(
            multiline=False,
            password=password,
            size_hint_y=None,
            height=Window.height * 0.10,  # 10% de la altura de la pantalla
            background_color=(1, 1, 1, 1),  # Fondo blanco
            foreground_color=(0, 0, 0, 1),  # Texto negro
            cursor_color=(0.2, 0.6, 0.8, 1),  # Cursor azul
            padding=[10, 10],
        )

    def set_username(self, username):
        self.username = username
        print(f"Username recibido en AccountDetailsScreen: {self.username}")

    def update_account_details(self, instance):
        """Actualiza los detalles de la cuenta en el servidor."""
        username = self.username
        account_id = self.account_id_input.text
        account_password = self.account_password_input.text
        server = self.server_input.text

        if not username or not account_id or not account_password or not server:
            print("Faltan datos")
            return

        # Llamada al servidor para actualizar detalles
        url = f"{ip}/update_account"
        data = {
            "Correo electronico": username,
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
        """Actualiza el fondo dinámicamente."""
        self.rect.pos = self.pos
        self.rect.size = self.size



class VerifyCredentialsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Fondo personalizado
        with self.canvas.before:
            Color(0.9, 0.95, 1, 1)  # Fondo color claro
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)

        # Layout principal (ScrollView para manejar pantallas más pequeñas)
        scroll_view = ScrollView()
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=20, size_hint_y=None)
        main_layout.bind(minimum_height=main_layout.setter('height'))
        scroll_view.add_widget(main_layout)

        # Título estilizado
        title_label = Label(
            text="[b]Verifica tus credenciales[/b]",
            font_size=28,
            markup=True,  # Activar etiquetas BBCode
            color=(0, 0.2, 0.5, 1),  # Azul oscuro
        )
        title_label.bind(size=self._update_text)
        main_layout.add_widget(title_label)

        # Campo de entrada para el nombre de usuario
        self.username_input = TextInput(
            hint_text="Ingresa tu usuario",
            size_hint=(1, None),
            height=Window.height * 0.10,  # 10% de la altura de la pantalla
            multiline=False,
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1),
            cursor_color=(0, 0.5, 1, 1),
            padding=[10, 10],
        )
        main_layout.add_widget(self.username_input)

        # Campo de entrada para la contraseña
        self.password_input = TextInput(
            hint_text="Ingresa contraseña de la cuenta de trading",
            password=True,
            size_hint=(1, None),
            height=Window.height * 0.10,  # 10% de la altura de la pantalla
            multiline=False,
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1),
            cursor_color=(0, 0.5, 1, 1),
            padding=[10, 10],
        )
        main_layout.add_widget(self.password_input)

        # Botón de envío
        submit_button = Button(
            text="Verificar",
            size_hint=(1, None),
            height=Window.height * 0.15,  # 10% de la altura de la pantalla
            background_normal="",
            background_color=(0, 0.5, 1, 1),
            color=(1, 1, 1, 1),
            font_size=18,
            bold=True,
        )
        submit_button.bind(on_press=self.submit_credentials)
        main_layout.add_widget(submit_button)

        # Campo de respuesta
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

        # Añadimos el ScrollView al Screen
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
                self.manager.current = "main"  # Cambiar a la pantalla principal
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

        # Fondo de pantalla
        with self.canvas.before:
            Color(0.8, 0.9, 1, 1)  # Fondo azul claro
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        # Layout principal
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        self.layout.add_widget(Widget(size_hint_y=0.6))  # Espaciador para empujar los elementos hacia abajo

        # Botón de iniciar el bot
        self.start_button = Button(
            text='Iniciar Bot',
            size_hint=(1, None),
            height=Window.height * 0.15,  # 10% de la altura de la pantalla
            background_color=(0, 0.7, 0.2, 1),
            font_size=16
        )
        self.start_button.bind(on_press=self.start_bot)
        self.layout.add_widget(self.start_button)

        # Botón de detener el bot
        self.stop_button = Button(
            text='Detener Bot',
            size_hint=(1, None),
            height=Window.height * 0.15,  # 10% de la altura de la pantalla
            background_color=(0.8, 0, 0, 1),
            font_size=16
        )
        self.stop_button.bind(on_press=self.stop_bot)
        self.layout.add_widget(self.stop_button)

        # Etiqueta de estado
        self.status_label = Label(
            text='Estado: Desconocido',
            size_hint=(1, None),
            height=Window.height * 0.10,  # 10% de la altura de la pantalla
            font_size=16,
            color=(0, 0, 0, 1)
        )
        self.layout.add_widget(self.status_label)

        # Cuadro de texto para mensajes del backend
        self.backend_messages = TextInput(
            hint_text='Mensajes del backend aparecerán aquí...',
            size_hint=(1, 0.3),
            height=Window.height * 0.35,  # 10% de la altura de la pantalla
            readonly=True,
            background_color=(0.95, 0.95, 0.95, 1),  # Color de fondo claro
            font_size=14,
            foreground_color=(0, 0, 0, 1),  # Texto negro
            text_validate_unfocus=False  # No quitar foco al escribir
        )
        self.layout.add_widget(self.backend_messages)

        # Botón para cerrar sesión
        self.logout_button = Button(
            text="Cerrar Sesión",
            size_hint=(1, None),
            height=Window.height * 0.15,  # 10% de la altura de la pantalla
            background_color=(0.3, 0.3, 0.8, 1),
            font_size=16
        )
        self.logout_button.bind(on_press=self.logout)
        self.layout.add_widget(self.logout_button)

        # Botón de suscripción
        self.subscribe_button = Button(
            text="Suscribirse",
            size_hint=(1, None),
            height=Window.height * 0.15,
            background_normal="",
            background_color=(1, 0.6, 0, 1),  # Naranja
            color=(1, 1, 1, 1),  # Texto en blanco
            font_size=18,
            bold=True
        )
        self.subscribe_button.bind(on_press=self.open_subscription_page)
        self.layout.add_widget(self.subscribe_button)

        # Añadimos el layout a la pantalla
        self.add_widget(self.layout)

        # Inicialización de update_event
        self.update_event = None  # Inicializar la variable

    def logout(self, instance):
        """Enviar solicitud para cerrar sesión."""
        try:
            response = requests.post(f'{ip}/logout', timeout=10)
            if response.status_code == 200:
                print("Sesión cerrada correctamente.")
                clear_session()
                # Redirigir al usuario a la pantalla de inicio de sesión
                self.manager.current = "login"
            else:
                self.update_backend_message("Error al cerrar sesión: " + response.text)
        except requests.exceptions.RequestException as e:
            self.update_backend_message(f"Error de conexión al cerrar sesión: {e}")

    def start_bot(self, instance):
        if start_bot_vps():
            self.status_label.text = 'Estado: En ejecución'
            self.update_backend_message("Bot iniciado correctamente.")

            # Iniciar actualización de operaciones si no está programado ya
            if not self.update_event:
                self.update_event = Clock.schedule_interval(self.display_operations, 5)
        else:
            self.status_label.text = 'Error al iniciar el bot en el VPS'
            self.update_backend_message("Error al iniciar el bot.")

    def stop_bot(self, instance):
        if stop_bot_vps():
            self.status_label.text = 'Estado: Detenido'
            self.update_backend_message("Bot detenido correctamente.")

            # Detener la actualización de operaciones
            if self.update_event:
                Clock.unschedule(self.update_event)
                self.update_event = None
        else:
            self.status_label.text = 'Error al detener el bot en el VPS'
            self.update_backend_message("Error al detener el bot.")

    def update_backend_message(self, message):
        """Actualiza el cuadro de texto de los mensajes del backend"""
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
        """Agregar un mensaje al cuadro de texto"""
        self.backend_messages.text = message  # Añadir el nuevo mensaje al final

    def get_operations_from_api(self):
        """Obtener los mensajes de operaciones como texto plano"""
        try:
            response = requests.get(f'{ip}/get_operations', timeout=30)
            if response.status_code == 200:
                print(f'MENSAJES: {response.text}')
                return response.text  # Obtener el texto plano directamente
            else:
                return "Hubo un problema con la solicitud."
        except requests.exceptions.RequestException as e:
            return f"Hubo un problema: {e}"

    def display_operations(self, dt):
        """Muestra los mensajes en el cuadro de texto de la interfaz"""
        messages = self.get_operations_from_api()
        self.add_message(messages)  # Agregar los mensajes al cuadro de texto

    def open_subscription_page(self, instance):
        import webbrowser
        try:
            session_file = "session_data.json"
            # Leer el archivo JSON
            with open(session_file, "r") as file:
                session_data = json.load(file)

            # Extraer el username del archivo
            username = session_data.get("username")
            if not username:
                print("No se encontró 'username' en session_data.json.")
            else:
                # URL del endpoint
                url = f'{ip}/get_logged_in_user'

                # Preparar los datos para enviar
                data = {"username": username}

                # Realizar la solicitud POST
                response = requests.post(url, json=data, timeout=30)

                # Procesar la respuesta
                if response.status_code == 200:
                    response_data = response.json()
                    if response_data["status"] == "success":
                        # Obtener la URL del Payment Link
                        payment_link_url = response_data["payment_link_url"]
                        print(f"Abriendo Payment Link: {payment_link_url}")
                        # Abrir el Payment Link en el navegador
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

        # Verificamos si hay una sesión guardada
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

# Ejecutar la aplicación Kivy
if __name__ == "__main__":
    RealtimeBotApp().run()
