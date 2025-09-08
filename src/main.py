import flet as ft
from pathlib import Path

from config.settings import setup_logger
from core.instagram_comparator import InstagramComparator
from core.instagram_extractor import SimpleInstagramExtractor
from utils.helpers import get_json_files_for_account, load_json_file ,format_json_data, format_comparison_data


# =====================| DIRECTORIES |=====================
logs_dir = Path(f"{Path.cwd()}/src/logs")
logs_dir.mkdir(exist_ok=True)

sessions_dir = Path(f"{Path.cwd()}/src/sessions")
sessions_dir.mkdir(exist_ok=True)

data_dir = Path(f"{Path.cwd()}/src/instagram_data")
data_dir.mkdir(exist_ok=True)

logger = setup_logger(logs_dir)

# =====================| Flet App |======================
def main(page: ft.Page):
    # =====================| Page Configuration |======================
    page.title = "Instagram Data Analyzer"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 20

    def on_account_name_change(e):
        """Se ejecuta cuando cambia el texto del campo de cuenta"""
        account_name = account_name_field.value.strip()
        
        if not account_name:
            # Limpiar el multiselect si no hay texto
            file_selector.options = []
            file_selector.update()
            return
        
        # Buscar archivos relacionados
        json_files = get_json_files_for_account(account_name, data_dir, logger)
        
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

    def show_analyze_data_section(e):
        page.clean()

        back_button = ft.ElevatedButton(
            "← Volver al Menú",
            on_click=show_main_menu_section,
            bgcolor=ft.Colors.GREY_500,
            color=ft.Colors.WHITE,
        )

        # Layout de analyze data
        analyze_layout = ft.Column(
            [
                back_button,
                ft.Container(height=15),
                ft.Row(
                    [analyze_form_container, ft.Container(width=40), analyze_results_container],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ]
        )

        page.add(analyze_layout)
        page.update()

    def on_analyze_account_name_change(e):
        """Se ejecuta cuando cambia el texto del campo de cuenta para análisis"""
        account_name = analyze_account_name_field.value.strip()
        
        if not account_name:
            # Limpiar los multiselects si no hay texto
            analyze_file1_selector.options = []
            analyze_file2_selector.options = []
            analyze_file1_selector.value = None
            analyze_file2_selector.value = None
            analyze_files_found_text.value = "Ingresa un nombre de cuenta para buscar archivos"
            analyze_files_found_text.color = ft.Colors.GREY_600
            
            # Actualizar todos los componentes al mismo tiempo
            analyze_file1_selector.update()
            analyze_file2_selector.update()
            analyze_files_found_text.update()
            return
        
        # Buscar archivos relacionados usando la clase comparator
        comparator = InstagramComparator(data_dir, logger)
        json_files_paths = comparator.find_account_files(account_name)
        
        # Convertir a formato similar al de load file
        json_files = []
        for file_path in json_files_paths:
            filename = Path(file_path).name
            try:
                # Extraer timestamp del nombre del archivo
                timestamp_part = filename.replace(f"{account_name}_data_", "").replace(".json", "")
                if len(timestamp_part) == 12:  # YYYYMMDDHHMM
                    year = timestamp_part[:4]
                    month = timestamp_part[4:6]
                    day = timestamp_part[6:8]
                    hour = timestamp_part[8:10]
                    minute = timestamp_part[10:12]
                    formatted_date = f"{day}/{month}/{year} {hour}:{minute}"
                    display_name = f"{formatted_date} - {filename}"
                else:
                    display_name = filename
            except Exception:
                display_name = filename
                
            json_files.append({
                'path': file_path,
                'display_name': display_name,
                'timestamp': timestamp_part if 'timestamp_part' in locals() else ""
            })
        
        # Ordenar por timestamp (más reciente primero)
        json_files.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Actualizar las opciones de ambos multiselects
        if json_files:
            options = [
                ft.dropdown.Option(
                    key=file_info['path'],
                    text=file_info['display_name']
                ) for file_info in json_files
            ]
            
            # analyze_file1_selector.options = options.copy()
            # analyze_file2_selector.options = options.copy()
            analyze_file1_selector.options = [
                ft.dropdown.Option(key=opt.key, text=opt.text) for opt in options
            ]
            analyze_file2_selector.options = [
                ft.dropdown.Option(key=opt.key, text=opt.text) for opt in options
            ]
            analyze_files_found_text.value = f"✅ {len(json_files)} archivo(s) encontrado(s)"
            analyze_files_found_text.color = ft.Colors.GREEN_700
        else:
            analyze_file1_selector.options = []
            analyze_file2_selector.options = []
            analyze_files_found_text.value = f"❌ No se encontraron archivos para '{account_name}'"
            analyze_files_found_text.color = ft.Colors.RED_700
        
        # Limpiar selecciones previas
        analyze_file1_selector.value = None
        analyze_file2_selector.value = None
        
        # Actualizar todos los componentes al final, en el orden correcto
        analyze_files_found_text.update()
        analyze_file1_selector.update()
        analyze_file2_selector.update()

    def create_comparison_lists(comparison):
        """Crea las listas para mostrar en las pestañas de comparación"""
        changes = comparison['changes']
        relationships = comparison['current_relationships']
        
        # Nuevos seguidores
        new_followers_text = "\n".join([f"• @{username}" for username in changes['new_followers']]) if changes['new_followers'] else "No hay nuevos seguidores"
        
        # Seguidores perdidos
        lost_followers_text = "\n".join([f"• @{username}" for username in changes['lost_followers']]) if changes['lost_followers'] else "No se perdieron seguidores"
        
        # Nuevos seguidos
        new_following_text = "\n".join([f"• @{username}" for username in changes['new_following']]) if changes['new_following'] else "No hay nuevos seguidos"
        
        # Dejó de seguir
        unfollowed_text = "\n".join([f"• @{username}" for username in changes['unfollowed']]) if changes['unfollowed'] else "No dejó de seguir a nadie"
        
        # Seguimiento mutuo
        mutual_follows_text = "\n".join([f"• @{username}" for username in relationships['mutual_follows']]) if relationships['mutual_follows'] else "No hay seguimiento mutuo"
        
        # Sigue pero no lo siguen
        follows_not_followed_text = "\n".join([f"• @{username}" for username in relationships['follows_but_not_followed']]) if relationships['follows_but_not_followed'] else "Todos los que sigue lo siguen de vuelta"
        
        return {
            'new_followers': new_followers_text,
            'lost_followers': lost_followers_text,
            'new_following': new_following_text,
            'unfollowed': unfollowed_text,
            'mutual_follows': mutual_follows_text,
            'follows_not_followed': follows_not_followed_text
        }

    def perform_comparison(e):
        """Realiza la comparación entre los dos archivos seleccionados"""
        account_name = analyze_account_name_field.value.strip()
        file1_key = analyze_file1_selector.value
        file2_key = analyze_file2_selector.value
        
        # Validaciones
        if not account_name:
            analyze_results_container.content.controls[0].value = "❌ Por favor, ingresa el nombre de la cuenta."
            analyze_results_container.update()
            return
        
        if not file1_key or not file2_key:
            analyze_results_container.content.controls[0].value = "❌ Por favor, selecciona ambos archivos para comparar."
            analyze_results_container.update()
            return
        
        # Extraer las rutas reales de los archivos desde los keys
        file1 = file1_key.replace("file1_", "") if file1_key.startswith("file1_") else file1_key
        file2 = file2_key.replace("file2_", "") if file2_key.startswith("file2_") else file2_key
        
        if file1 == file2:
            analyze_results_container.content.controls[0].value = "❌ Por favor, selecciona dos archivos diferentes."
            analyze_results_container.update()
            return
        
        try:
            # Mostrar mensaje de procesamiento
            analyze_results_container.content.controls[0].value = "⏳ Analizando datos..."
            analyze_results_container.update()
            
            # Realizar comparación
            comparator = InstagramComparator(data_dir, logger)
            comparison_result = comparator.compare_data(file1, file2)
            
            if not comparison_result:
                analyze_results_container.content.controls[0].value = "❌ Error al comparar los archivos. Verifica que sean de la misma cuenta."
                analyze_results_container.update()
                return
            
            # Formatear datos
            formatted_info = format_comparison_data(comparison_result)
            comparison_lists = create_comparison_lists(comparison_result)
            
            # Crear contenedores para las pestañas
            def create_tab_container(content, bg_color, border_color):
                return ft.Container(
                    content=ft.Text(
                        content,
                        size=11,
                        color=ft.Colors.BLACK87,
                        selectable=True
                    ),
                    padding=ft.padding.all(15),
                    bgcolor=bg_color,
                    border_radius=8,
                    border=ft.border.all(1, border_color),
                    height=300,
                )
            
            # Crear las pestañas con los diferentes análisis
            tabs_container = ft.Tabs(
                selected_index=0,
                animation_duration=300,
                tabs=[
                    ft.Tab(
                        text=f"➕ Nuevos Seguidores ({len(comparison_result['changes']['new_followers'])})",
                        content=create_tab_container(comparison_lists['new_followers'], ft.Colors.GREEN_50, ft.Colors.GREEN_200)
                    ),
                    ft.Tab(
                        text=f"➖ Seguidores Perdidos ({len(comparison_result['changes']['lost_followers'])})",
                        content=create_tab_container(comparison_lists['lost_followers'], ft.Colors.RED_50, ft.Colors.RED_200)
                    ),
                    ft.Tab(
                        text=f"➕ Nuevos Seguidos ({len(comparison_result['changes']['new_following'])})",
                        content=create_tab_container(comparison_lists['new_following'], ft.Colors.BLUE_50, ft.Colors.BLUE_200)
                    ),
                    ft.Tab(
                        text=f"➖ Dejó de Seguir ({len(comparison_result['changes']['unfollowed'])})",
                        content=create_tab_container(comparison_lists['unfollowed'], ft.Colors.ORANGE_50, ft.Colors.ORANGE_200)
                    ),
                    ft.Tab(
                        text=f"💫 Mutuos ({len(comparison_result['current_relationships']['mutual_follows'])})",
                        content=create_tab_container(comparison_lists['mutual_follows'], ft.Colors.PURPLE_50, ft.Colors.PURPLE_200)
                    ),
                    ft.Tab(
                        text=f"🔄 Sin Reciprocidad ({len(comparison_result['current_relationships']['follows_but_not_followed'])})",
                        content=create_tab_container(comparison_lists['follows_not_followed'], ft.Colors.YELLOW_50, ft.Colors.YELLOW_200)
                    )
                ],
                height=350
            )
            
            # Actualizar contenedor de resultados
            analyze_results_container.content = ft.Column([
                # Información de comparación
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
                
                # Pestañas con análisis detallado
                tabs_container
                
            ], 
            scroll=ft.ScrollMode.AUTO,
            spacing=10
            )
            
        except Exception as e:
            error_message = f"❌ Error durante el análisis: {str(e)}"
            analyze_results_container.content.controls[0].value = error_message
            analyze_results_container.content.controls[0].color = ft.Colors.RED_700
            logger.error(f"Error en comparación: {e}")
        
        analyze_results_container.update()

    def show_main_menu_section(e):
        page.clean()
        page.add(main_menu)
        page.update()

    # =====================| Instagram functions |======================
    

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
        extractor = SimpleInstagramExtractor(sessions_dir, data_dir, logger)

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
    # =====================| Analyze Data Form Components |======================
    # Campo para el nombre de la cuenta
    analyze_account_name_field = ft.TextField(
        label="Nombre de la cuenta (sin @)",
        hint_text="Ejemplo: mar_tz_ml",
        width=300,
        border_radius=8,
        on_change=on_analyze_account_name_change,
    )

    # Texto para mostrar cuántos archivos se encontraron
    analyze_files_found_text = ft.Text(
        "Ingresa un nombre de cuenta para buscar archivos",
        size=12,
        color=ft.Colors.GREY_600
    )

    # Selector del primer archivo
    analyze_file1_selector = ft.Dropdown(
        label="Primer archivo (más antiguo)",
        width=300,
        options=[],
        border_radius=8,
    )

    # Selector del segundo archivo
    analyze_file2_selector = ft.Dropdown(
        label="Segundo archivo (más reciente)",
        width=300,
        options=[],
        border_radius=8,
    )

    # Contenedor de resultados para analyze data
    analyze_results_container = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "Selecciona dos archivos para comparar los datos",
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

    # Formulario de analyze data
    analyze_form_container = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "📊 Comparar Datos",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.PURPLE_800,
                ),
                ft.Container(height=20),
                analyze_account_name_field,
                ft.Container(height=10),
                analyze_files_found_text,
                ft.Container(height=15),
                analyze_file1_selector,
                ft.Container(height=15),
                analyze_file2_selector,
                ft.Container(height=20),
                ft.ElevatedButton(
                    "Comparar Archivos",
                    on_click=perform_comparison,
                    width=300,
                    height=45,
                    bgcolor=ft.Colors.PURPLE_600,
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
                        on_click=show_analyze_data_section,
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
