# MT5 - Interfaz Cliente (Kivy)

Aplicación de escritorio hecha con **Kivy** que permite:

- Registro e inicio de sesión de usuario
- Verificación de credenciales de cuenta de trading
- Inicio y detención de bot remoto
- Consulta de estado y operaciones del bot
- Apertura de enlace de suscripción

El script principal de esta interfaz es `main.py`.

## Requisitos

Este proyecto usa las siguientes dependencias externas:

- Kivy==2.3.0
- requests==2.32.5

Estas versiones están guardadas en `requirements.txt`.

## Instalación

Desde la carpeta del proyecto:

```bash
pip install -r requirements.txt
```

## Ejecución

```bash
python main.py
```

## Flujo general de la app

1. Pantalla de login o registro.
2. Si se registra un usuario nuevo, se piden detalles de cuenta (ID, contraseña y servidor).
3. Verificación de credenciales de trading.
4. Acceso a pantalla principal para iniciar/detener bot, ver estado y mensajes.

## Archivo de sesión

La aplicación guarda sesión en:

- `session_data.json`

Incluye token y username.

## Endpoints backend usados

La app consume un backend HTTP configurado en el script con la variable `ip`, por ejemplo:

- /register
- /login
- /check_session
- /logout
- /update_account
- /initialize-mt5
- /start_bot
- /stop_bot
- /check_bot_status
- /get_operations
- /get_logged_in_user

