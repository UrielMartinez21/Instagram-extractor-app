import flet as ft
import json
from pathlib import Path
import logging
import os
from instagrapi import Client
from datetime import datetime
import time


# =====================| DIRECTORIES |=====================
logs_dir = Path(f"{Path.cwd()}/src/logs")
logs_dir.mkdir(exist_ok=True)

sessions_dir = Path(f"{Path.cwd()}/src/sessions")
sessions_dir.mkdir(exist_ok=True)

data_dir = Path(f"{Path.cwd()}/src/instagram_data")
data_dir.mkdir(exist_ok=True)

# =====================| Setup logging|=====================
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(logs_dir / 'instagram_extractor.log', encoding='utf-8') # To save in file
    ]
)
logger = logging.getLogger(__name__)


# =====================| Instagram extractor |======================
class SimpleInstagramExtractor:
    def __init__(self):
        self.client = Client()
        self.logged_in = False
        self.session_file = sessions_dir / "session.json"

    def login(self, username, password) -> bool:
        try:
            # Try to load existing session
            if os.path.exists(self.session_file):
                try:
                    logger.info("Intentando cargar sesión existente...")
                    self.client.load_settings(self.session_file)
                    logger.info("Sesión cargada desde archivo")
                    self.logged_in = True
                    return True
                except Exception as e:
                    logger.warning(f"No se pudo cargar la sesión: {e}")
                    # If loading fails, remove the corrupted session file
                    try:
                        os.remove(self.session_file)
                    except Exception:
                        pass

            # Loggin again
            logger.info(f"Iniciando sesión para usuario: {username}")
            self.client.login(username, password)

            # Save session
            self.client.dump_settings(self.session_file)
            logger.info("Sesión iniciada y guardada")
            self.logged_in = True
            return True

        except Exception as e:
            logger.error(f"Error de login: {e}")
            return False

    def verify_account_access(self, username) -> dict:
        try:
            logger.info(f"Verificando acceso para @{username}...")
            user_info = self.client.user_info_by_username(username)

            access_info = {
                'can_access': True,
                'is_private': user_info.is_private,
                'follower_count': user_info.follower_count,
                'following_count': user_info.following_count,
                'full_name': user_info.full_name or username
            }

            if user_info.is_private:
                logger.warning(f"@{username} es una cuenta privada")
            else:
                logger.info(f"@{username} es una cuenta pública")

            logger.info(f"La cuenta tiene {user_info.follower_count} seguidores y sigue a {user_info.following_count}")
            return access_info

        except Exception as e:
            logger.error(f"No se puede acceder a @{username}: {e}")
            return {'can_access': False, 'error': str(e)}

    def get_followers_list(self, username) -> list:
        try:
            user_info = self.client.user_info_by_username(username)
            user_id = user_info.pk

            logger.info(f"Obteniendo seguidores de @{username} - Total esperado: {user_info.follower_count}")

            # Get all followers
            followers_dict = self.client.user_followers(user_id)

            # Extract only usernames
            followers_list = []
            for follower_info in followers_dict.values():
                followers_list.append(follower_info.username)

            logger.info(f"{len(followers_list)} seguidores obtenidos")
            return followers_list

        except Exception as e:
            logger.error(f"Error obteniendo seguidores de @{username}: {e}")
            return []

    def get_following_list(self, username) -> list:
        try:
            user_info = self.client.user_info_by_username(username)
            user_id = user_info.pk

            logger.info(f"Obteniendo seguidos de @{username} - Total esperado: {user_info.following_count}")

            # Get all following
            following_dict = self.client.user_following(user_id)

            # Extract only usernames
            following_list = []
            for following_info in following_dict.values():
                following_list.append(following_info.username)

            logger.info(f"{len(following_list)} seguidos obtenidos")
            return following_list

        except Exception as e:
            logger.error(f"Error obteniendo seguidos de @{username}: {e}")
            return []

    def extract_account(self, target_username) -> dict:
        if not self.logged_in:
            logger.error("Debes iniciar sesión primero")
            return None

        logger.info(f"Iniciando extracción de datos de @{target_username}")

        # Check account access
        access_info = self.verify_account_access(target_username)
        if not access_info['can_access']:
            logger.error(f"No se puede acceder a la cuenta @{target_username}")
            return None

        # Get followers
        logger.info("=" * 50)
        logger.info("PASO 1: EXTRAYENDO SEGUIDORES")
        logger.info("=" * 50)
        followers = self.get_followers_list(target_username)

        # Delay to avoid rate limits
        logger.info("⏳ Pausa de 5 segundos entre requests...")
        time.sleep(5)

        # Get following
        logger.info("=" * 50)
        logger.info("PASO 2: EXTRAYENDO SEGUIDOS")
        logger.info("=" * 50)
        following = self.get_following_list(target_username)

        # Create data structure
        timestamp = datetime.now()
        account_data = {
            "account": target_username,
            "followers": followers,
            "following": following,
            "extraction_date": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "account_info": access_info,
            "stats": {
                "total_followers": len(followers),
                "total_following": len(following),
                "expected_followers": access_info.get('follower_count', 0),
                "expected_following": access_info.get('following_count', 0)
            }
        }

        # Generate filename
        timestamp_str = timestamp.strftime('%Y%m%d%H%M')
        filename = f"{target_username}_data_{timestamp_str}.json"
        filepath = data_dir / filename

        # Guardar archivo JSON
        logger.info("=" * 50)
        logger.info("PASO 3: GUARDANDO ARCHIVO")
        logger.info("=" * 50)

        try:
            logger.info(f"Guardando datos en: {filepath}")

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(account_data, f, indent=2, ensure_ascii=False)

            # Check file creation
            if filepath.exists():
                file_size = filepath.stat().st_size
                logger.info("Archivo creado exitosamente!")
                logger.info(f"Ubicación: {filepath.absolute()}")
                logger.info(f"Tamaño: {file_size} bytes")
            else:
                logger.error("El archivo no se pudo crear")
                return None

        except Exception as e:
            logger.error(f"Error guardando archivo: {e}")
            return None

        # Mostrar resumen final
        logger.info("=" * 50)
        logger.info("EXTRACCIÓN COMPLETADA")
        logger.info("=" * 50)
        logger.info(f"Cuenta: @{target_username}")
        logger.info(f"Seguidores extraídos: {len(followers)} / {access_info.get('follower_count', 'N/A')} esperados")
        logger.info(f"Seguidos extraídos: {len(following)} / {access_info.get('following_count', 'N/A')} esperados")
        logger.info(f"Archivo: {filename}")
        logger.info(f"Fecha: {account_data['extraction_date']}")

        return {
            'success': True,
            'data': account_data,
            'filepath': str(filepath),
            'filename': filename
        }


# =====================| Flet App |======================
def main(page: ft.Page):
    # =====================| Page Configuration |======================
    page.title = "Instagram Data Analyzer"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 20

    # =====================| Helpers |======================
    def get_json_files_for_account(account_name):
        """Busca todos los archivos JSON relacionados con una cuenta específica"""
        if not account_name.strip():
            return []
        
        try:
            json_files = []
            # Buscar archivos que contengan el nombre de la cuenta
            for file_path in data_dir.glob("*.json"):
                filename = file_path.name
                # Verificar si el archivo corresponde a la cuenta buscada
                if filename.startswith(f"{account_name}_data_"):
                    # Extraer información del archivo
                    try:
                        # Formato esperado: account_data_YYYYMMDDHHMM.json
                        timestamp_part = filename.replace(f"{account_name}_data_", "").replace(".json", "")
                        # Formatear la fecha para mostrar
                        if len(timestamp_part) == 12:  # YYYYMMDDHHMM
                            year = timestamp_part[:4]
                            month = timestamp_part[4:6]
                            day = timestamp_part[6:8]
                            hour = timestamp_part[8:10]
                            minute = timestamp_part[10:12]
                            formatted_date = f"{day}/{month}/{year} {hour}:{minute}"
                            
                            json_files.append({
                                'filename': filename,
                                'path': str(file_path),
                                'display_name': f"{formatted_date} - {filename}",
                                'timestamp': timestamp_part
                            })
                    except Exception as e:
                        # Si no se puede parsear la fecha, agregar el archivo de todas formas
                        json_files.append({
                            'filename': filename,
                            'path': str(file_path),
                            'display_name': filename,
                            'timestamp': ""
                        })
            
            # Ordenar por timestamp (más reciente primero)
            json_files.sort(key=lambda x: x['timestamp'], reverse=True)
            return json_files
            
        except Exception as e:
            logger.error(f"Error buscando archivos para {account_name}: {e}")
            return []


    def load_json_file(file_path):
        """Carga y valida un archivo JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Validar que tenga la estructura esperada
            required_keys = ['account', 'followers', 'following', 'extraction_date']
            for key in required_keys:
                if key not in data:
                    raise ValueError(f"El archivo no tiene la estructura esperada. Falta la clave: {key}")

            return data

        except json.JSONDecodeError:
            raise ValueError("El archivo no es un JSON válido")
        except Exception as e:
            raise ValueError(f"Error cargando el archivo: {str(e)}")

    def on_account_name_change(e):
        """Se ejecuta cuando cambia el texto del campo de cuenta"""
        account_name = account_name_field.value.strip()
        
        if not account_name:
            # Limpiar el multiselect si no hay texto
            file_selector.options = []
            file_selector.update()
            return
        
        # Buscar archivos relacionados
        json_files = get_json_files_for_account(account_name)
        
        # Actualizar las opciones del multiselect
        if json_files:
            file_selector.options = [
                ft.dropdown.Option(
                    key=file_info['path'],
                    text=file_info['display_name']
                ) for file_info in json_files
            ]
            files_found_text.value = f"✅ {len(json_files)} archivo(s) encontrado(s)"
            files_found_text.color = ft.Colors.GREEN_700
        else:
            file_selector.options = []
            files_found_text.value = f"❌ No se encontraron archivos para '{account_name}'"
            files_found_text.color = ft.Colors.RED_700
        
        # Limpiar selección previa
        file_selector.value = None
        file_selector.update()
        files_found_text.update()

    def load_and_display_file(e):
        """Carga el archivo seleccionado y muestra los datos"""
        account_name = account_name_field.value.strip()
        selected_file = file_selector.value
        
        if not account_name:
            load_results_container.content.controls[0].value = "❌ Por favor, ingresa el nombre de la cuenta."
            load_results_container.update()
            return
        
        if not selected_file:
            load_results_container.content.controls[0].value = "❌ Por favor, selecciona un archivo."
            load_results_container.update()
            return
        
        try:
            # Mostrar mensaje de carga
            load_results_container.content.controls[0].value = "⏳ Cargando archivo..."
            load_results_container.update()
            
            # Cargar el archivo JSON
            data = load_json_file(selected_file)
            
            # Usar las mismas funciones que en data mining para mostrar los datos
            formatted_info = format_json_data(data)
            followers_text, following_text = create_expandable_lists(data)
            
            # Crear contenedores para las pestañas
            followers_container = ft.Container(
                content=ft.Text(
                    followers_text,
                    size=11,
                    color=ft.Colors.BLACK87,
                    selectable=True
                ),
                padding=ft.padding.all(15),
                bgcolor=ft.Colors.GREEN_50,
                border_radius=8,
                border=ft.border.all(1, ft.Colors.GREEN_200),
                height=300,
            )

            following_container = ft.Container(
                content=ft.Text(
                    following_text,
                    size=11,
                    color=ft.Colors.BLACK87,
                    selectable=True
                ),
                padding=ft.padding.all(15),
                bgcolor=ft.Colors.ORANGE_50,
                border_radius=8,
                border=ft.border.all(1, ft.Colors.ORANGE_200),
                height=300,
            )

            # Crear las pestañas
            tabs_container = ft.Tabs(
                selected_index=0,
                animation_duration=300,
                tabs=[
                    ft.Tab(
                        text=f"👥 Seguidores ({len(data.get('followers', []))})",
                        content=followers_container
                    ),
                    ft.Tab(
                        text=f"➡️ Siguiendo ({len(data.get('following', []))})",
                        content=following_container
                    )
                ],
                height=350
            )

            # Actualizar el contenedor de resultados
            load_results_container.content = ft.Column([
                # Información del archivo cargado
                ft.Container(
                    content=ft.Text(
                        f"📁 Archivo cargado: {Path(selected_file).name}",
                        size=14,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.PURPLE_800
                    ),
                    padding=ft.padding.all(10),
                    border_radius=8,
                    bgcolor=ft.Colors.PURPLE_50,
                    border=ft.border.all(1, ft.Colors.PURPLE_200),
                    margin=ft.margin.only(bottom=10)
                ),
                
                # Información principal
                ft.Container(
                    content=ft.Text(
                        formatted_info,
                        size=12,
                        color=ft.Colors.BLACK87,
                        font_family="monospace"
                    ),
                    padding=ft.padding.all(15),
                    border_radius=8,
                    bgcolor=ft.Colors.BLUE_50,
                    border=ft.border.all(1, ft.Colors.BLUE_200),
                    margin=ft.margin.only(bottom=15)
                ),
                
                # Pestañas
                tabs_container
                
            ], 
            scroll=ft.ScrollMode.AUTO,
            spacing=10
            )
            
        except Exception as e:
            error_message = f"❌ Error cargando el archivo: {str(e)}"
            load_results_container.content.controls[0].value = error_message
            load_results_container.content.controls[0].color = ft.Colors.RED_700
        
        load_results_container.update()


    # =====================| Navigation Functions |======================
    def show_data_mine_section(e):
        page.clean()

        back_button = ft.ElevatedButton(
            "← Volver al Menú",
            on_click=show_main_menu_section,
            bgcolor=ft.Colors.GREY_500,
            color=ft.Colors.WHITE,
        )

        # -> Layout de data mining
        data_mine_layout = ft.Column(
            [
                back_button,
                ft.Container(height=15),
                ft.Row(
                    [form_container, ft.Container(width=40), results_container],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ]
        )

        page.add(data_mine_layout)
        page.update()

    def show_load_file_section(e):
        page.clean()

        back_button = ft.ElevatedButton(
            "← Volver al Menú",
            on_click=show_main_menu_section,
            bgcolor=ft.Colors.GREY_500,
            color=ft.Colors.WHITE,
        )

        # -> Layout de load file
        load_file_layout = ft.Column(
            [
                back_button,
                ft.Container(height=15),
                ft.Row(
                    [load_form_container, ft.Container(width=40), load_results_container],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ]
        )

        page.add(load_file_layout)
        page.update()

    def show_main_menu_section(e):
        page.clean()
        page.add(main_menu)
        page.update()

    # =====================| Instagram functions |======================
    def format_json_data(data):
        account_info = data.get('account_info', {})
        stats = data.get('stats', {})
        
        # Crear el texto formateado
        formatted_text = f"""
            📊 INFORMACIÓN DE LA CUENTA
            ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

            👤 Cuenta: @{data.get('account', 'N/A')}
            📝 Nombre: {account_info.get('full_name', 'N/A')}
            🔒 Privada: {'Sí' if account_info.get('is_private', False) else 'No'}
            📅 Extracción: {data.get('extraction_date', 'N/A')}

            📈 ESTADÍSTICAS
            ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

            👥 Seguidores: {stats.get('total_followers', 0)} / {stats.get('expected_followers', 0)} esperados
            ➡️ Siguiendo: {stats.get('total_following', 0)} / {stats.get('expected_following', 0)} esperados

            📋 LISTAS EXTRAÍDAS
            ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

            📂 Seguidores ({len(data.get('followers', []))})
            📂 Siguiendo ({len(data.get('following', []))})
        """

        return formatted_text

    def create_expandable_lists(data):
        followers = data.get('followers', [])
        following = data.get('following', [])
        
        # Mostrar todos los seguidores (no solo preview)
        if followers:
            followers_text = "\n".join([f"• @{username}" for username in followers])
        else:
            followers_text = "No hay seguidores disponibles"
        
        # Mostrar todos los siguiendo (no solo preview)  
        if following:
            following_text = "\n".join([f"• @{username}" for username in following])
        else:
            following_text = "No hay usuarios seguidos disponibles"
        
        return followers_text, following_text

    def perform_data_mining(e):
        username = username_field.value.strip()
        password = password_field.value.strip()
        objective = objective_field.value.strip()

        if not username or not password or not objective:
            results_container.content.controls[0].value = "Por favor, completa todos los campos."
            results_container.update()
            return

        # -> Clear previous results
        results_container.content.controls[0].value = "Procesando..."
        results_container.update()

        # -> Initialize Instagram extractor
        extractor = SimpleInstagramExtractor()

        # -> Login
        if not extractor.login(username, password):
            results_container.content.controls[0].value = "Error al iniciar sesión. Verifica tus credenciales."
            results_container.update()
            return

        # -> Extract data
        extraction_result = extractor.extract_account(objective)
        if extraction_result and extraction_result.get('success'):
            data = extraction_result.get('data', {})

            # Formatear los datos
            formatted_info = format_json_data(data)
            followers_text, following_text = create_expandable_lists(data)

            followers_container = ft.Container(
                content=ft.Text(
                    followers_text,
                    size=11,
                    color=ft.Colors.BLACK87,
                    selectable=True
                ),
                padding=ft.padding.all(15),
                bgcolor=ft.Colors.GREEN_50,
                border_radius=8,
                border=ft.border.all(1, ft.Colors.GREEN_200),
                height=300,  # Altura fija
                # Removemos el scroll del contenedor individual
            )

            following_container = ft.Container(
                content=ft.Text(
                    following_text,
                    size=11,
                    color=ft.Colors.BLACK87,
                    selectable=True
                ),
                padding=ft.padding.all(15),
                bgcolor=ft.Colors.ORANGE_50,
                border_radius=8,
                border=ft.border.all(1, ft.Colors.ORANGE_200),
                height=300,  # Altura fija
                # Removemos el scroll del contenedor individual
            )

            # Crear las pestañas de manera más simple
            tabs_container = ft.Tabs(
                selected_index=0,
                animation_duration=300,
                tabs=[
                    ft.Tab(
                        text=f"👥 Seguidores ({len(data.get('followers', []))})",
                        content=followers_container
                    ),
                    ft.Tab(
                        text=f"➡️ Siguiendo ({len(data.get('following', []))})",
                        content=following_container
                    )
                ],
                height=350  # Altura total del tabs
            )

            # Actualizar el contenedor de resultados
            results_container.content = ft.Column([
                # Información principal
                ft.Container(
                    content=ft.Text(
                        formatted_info,
                        size=12,
                        color=ft.Colors.BLACK87,
                        font_family="monospace"
                    ),
                    padding=ft.padding.all(15),
                    border_radius=8,
                    bgcolor=ft.Colors.BLUE_50,
                    border=ft.border.all(1, ft.Colors.BLUE_200),
                    margin=ft.margin.only(bottom=15)
                ),
                
                # Pestañas
                tabs_container
                
            ], 
            scroll=ft.ScrollMode.AUTO,  # Solo un scroll en el contenedor principal
            spacing=10
            )
        else:
            results_container.content.controls[0].value = "Error extrayendo datos."
        
        results_container.update()

    # =====================| Fields to data mining section |======================
    # Input fields
    username_field = ft.TextField(
        label="Username",
        width=300,
        border_radius=8,
    )
    password_field = ft.TextField(
        label="Password",
        password=True,
        can_reveal_password=True,
        width=300,
        border_radius=8,
    )
    objective_field = ft.TextField(label="Objective", width=300, border_radius=8)

    # Area to show results
    results_container = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "Resultados aparecerán aquí",
                    size=16,
                    color=ft.Colors.GREY_600,
                    text_align=ft.TextAlign.CENTER,
                )
            ]
        ),
        width=500,
        height=500,
        padding=20,
        border_radius=8,
        bgcolor=ft.Colors.GREY_50,
    )

    # Form to data mining
    form_container = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "🔍 Data Mining",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_800,
                ),
                ft.Container(height=20),
                username_field,
                ft.Container(height=15),
                password_field,
                ft.Container(height=15),
                objective_field,
                ft.Container(height=20),
                ft.ElevatedButton(
                    "Enviar",
                    on_click=perform_data_mining,
                    width=300,
                    height=45,
                    bgcolor=ft.Colors.BLUE_600,
                    color=ft.Colors.WHITE,
                ),
            ],
        ),
        width=350,
        padding=20,
        border_radius=8,
        bgcolor=ft.Colors.WHITE,
    )

    # =====================| Load File Form Components |======================
    # Campo para el nombre de la cuenta
    account_name_field = ft.TextField(
        label="Nombre de la cuenta (sin @)",
        hint_text="Ejemplo: mar_tz_ml",
        width=300,
        border_radius=8,
        on_change=on_account_name_change,  # Se ejecuta cada vez que cambia el texto
    )

    # Texto para mostrar cuántos archivos se encontraron
    files_found_text = ft.Text(
        "Ingresa un nombre de cuenta para buscar archivos",
        size=12,
        color=ft.Colors.GREY_600
    )

    # Selector de archivos
    file_selector = ft.Dropdown(
        label="Seleccionar archivo",
        width=300,
        options=[],  # Se llena dinámicamente
        border_radius=8,
    )

    # Contenedor de resultados para load file
    load_results_container = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "Selecciona un archivo para ver los datos",
                    size=16,
                    color=ft.Colors.GREY_600,
                    text_align=ft.TextAlign.CENTER,
                )
            ]
        ),
        width=500,
        height=500,
        padding=20,
        border_radius=8,
        bgcolor=ft.Colors.GREY_50,
    )

    # Formulario de load file
    load_form_container = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "📁 Cargar Archivo",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.GREEN_800,
                ),
                ft.Container(height=20),
                account_name_field,
                ft.Container(height=10),
                files_found_text,
                ft.Container(height=15),
                file_selector,
                ft.Container(height=20),
                ft.ElevatedButton(
                    "Cargar y Mostrar",
                    on_click=load_and_display_file,
                    width=300,
                    height=45,
                    bgcolor=ft.Colors.GREEN_600,
                    color=ft.Colors.WHITE,
                ),
            ],
        ),
        width=350,
        padding=20,
        border_radius=8,
        bgcolor=ft.Colors.WHITE,
    )

    # =====================| Main Menu Layout |======================
    main_menu = ft.Column(
        [
            ft.Text(
                "Instagram Data Analyzer",
                size=32,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.Container(height=30),
            ft.Column(
                [
                    ft.ElevatedButton(
                        "Data Mine",
                        on_click=show_data_mine_section,
                        width=200,
                        height=50,
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.BLUE_500,
                    ),
                    ft.Container(height=15),
                    ft.ElevatedButton(
                        "Load File",
                        on_click=show_load_file_section,
                        width=200,
                        height=50,
                        bgcolor=ft.Colors.GREEN_500,
                        color=ft.Colors.WHITE,
                    ),
                    ft.Container(height=15),
                    ft.ElevatedButton(
                        "Analyze Data",
                        # on_click=lambda e: print("[+]Analyze Data clicked"),
                        width=200,
                        height=50,
                        bgcolor=ft.Colors.PURPLE_500,
                        color=ft.Colors.WHITE,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # Show main menu initially
    page.add(main_menu)


if __name__ == "__main__":
    ft.app(main)
