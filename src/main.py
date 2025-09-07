import flet as ft
import json

def main(page: ft.Page):
    page.title = "Instagram Data Analyzer"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 20

    # Variables para los campos del formulario
    username_field = ft.TextField(label="Username", width=300, border_radius=8,)
    password_field = ft.TextField(label="Password", password=True, can_reveal_password=True, width=300, border_radius=8)
    objective_field = ft.TextField(label="Objective", width=300, border_radius=8)

    # Área para mostrar los resultados
    results_container = ft.Container(
        content=ft.Column(
            [ft.Text("Resultados aparecerán aquí", size=16, color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER)]
        ),
        width=500,
        height=500,
        padding=20,
        border=ft.border.all(1, ft.Colors.GREY_300),
        border_radius=8,
        bgcolor=ft.Colors.GREY_50,
    )

    def format_json_data(data):
        """Formatea el JSON para mejor visualización"""
        try:
            if isinstance(data, str):
                data = json.loads(data)
            
            # Crear elementos visuales para mostrar la información
            elements = []
            
            # Información de la cuenta
            if "account_info" in data:
                info = data["account_info"]
                elements.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text("📱 Información de la Cuenta", 
                                        size=18, 
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.BLUE_800),
                                ft.Text(f"Nombre: {info.get('full_name', 'N/A')}", size=14),
                                ft.Text(f"Cuenta privada: {'Sí' if info.get('is_private') else 'No'}", size=14),
                                ft.Text(f"Seguidores: {info.get('follower_count', 0)}", size=14),
                                ft.Text(f"Siguiendo: {info.get('following_count', 0)}", size=14),
                            ]),
                            padding=15
                        ),
                        elevation=2,
                        margin=ft.margin.only(bottom=10)
                    )
                )
            
            # Estadísticas
            if "stats" in data:
                stats = data["stats"]
                elements.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text("📊 Estadísticas", 
                                        size=18, 
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.GREEN_800),
                                ft.Text(f"Total seguidores: {stats.get('total_followers', 0)}", size=14),
                                ft.Text(f"Total siguiendo: {stats.get('total_following', 0)}", size=14),
                                ft.Text(f"Seguidores mutuos: {stats.get('mutual_follows_count', 0)}", size=14),
                                ft.Text(f"Sigues pero no te siguen: {stats.get('follows_but_not_followed_count', 0)}", size=14),
                                ft.Text(f"Te siguen pero no sigues: {stats.get('followed_but_not_following_count', 0)}", size=14),
                            ]),
                            padding=15
                        ),
                        elevation=2,
                        margin=ft.margin.only(bottom=10)
                    )
                )
            
            # Información de comparación (si existe)
            if "comparison_info" in data:
                comp = data["comparison_info"]
                elements.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text("🔄 Comparación", 
                                        size=18, 
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.PURPLE_800),
                                ft.Text(f"Archivo 1: {comp['file1']['date']}", size=12),
                                ft.Text(f"Seguidores: {comp['file1']['followers_count']}", size=12),
                                ft.Text(f"Archivo 2: {comp['file2']['date']}", size=12),
                                ft.Text(f"Seguidores: {comp['file2']['followers_count']}", size=12),
                            ]),
                            padding=15
                        ),
                        elevation=2,
                        margin=ft.margin.only(bottom=10)
                    )
                )
            
            # Cambios (si existen)
            if "changes" in data:
                changes = data["changes"]
                elements.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text("📈 Cambios Recientes", 
                                        size=18, 
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.ORANGE_800),
                                ft.Text(f"Nuevos seguidores: {len(changes.get('new_followers', []))}", size=14, color=ft.Colors.GREEN_600),
                                ft.Text(f"Seguidores perdidos: {len(changes.get('lost_followers', []))}", size=14, color=ft.Colors.RED_600),
                                ft.Text(f"Nuevos siguiendo: {len(changes.get('new_following', []))}", size=14, color=ft.Colors.BLUE_600),
                                ft.Text(f"Dejaste de seguir: {len(changes.get('unfollowed', []))}", size=14, color=ft.Colors.GREY_600),
                            ]),
                            padding=15
                        ),
                        elevation=2,
                        margin=ft.margin.only(bottom=10)
                    )
                )
            
            return ft.Column(
                elements,
                scroll=ft.ScrollMode.AUTO,
                height=580,
            )
            
        except Exception as e:
            return ft.Column([
                ft.Text(f"Error al procesar datos: {str(e)}", 
                       color=ft.Colors.RED_600, 
                       size=14),
                ft.Container(
                    content=ft.Text(str(data), 
                                  size=12, 
                                  color=ft.Colors.GREY_700),
                    padding=10,
                    bgcolor=ft.Colors.GREY_100,
                    border_radius=5,
                )
            ])
    
    def submit_data_mine(e):
        """Función que se ejecuta cuando se envía el formulario"""
        username = username_field.value
        password = password_field.value
        # objective = objective_field.value
        
        if not username or not password:
            # Mostrar error si faltan campos
            results_container.content = ft.Column([
                ft.Icon(ft.icons.ERROR, color=ft.Colors.RED_500, size=50),
                ft.Text("Error: Username y Password son requeridos", 
                       color=ft.Colors.RED_600, 
                       size=16,
                       weight=ft.FontWeight.BOLD)
            ])
            page.update()
            return
        
        # Mostrar indicador de carga
        results_container.content = ft.Column([
            ft.ProgressRing(),
            ft.Text("Procesando datos...", size=16)
        ])
        page.update()
        
        # Aquí llamarías a tu servicio real
        # Por ahora simulo con datos de ejemplo del documento
        sample_data = {
            "account": username,
            "account_info": {
                "can_access": True,
                "is_private": True,
                "follower_count": 94,
                "following_count": 88,
                "full_name": "Usuario Demo"
            },
            "stats": {
                "total_followers": 94,
                "total_following": 88,
                "mutual_follows_count": 83,
                "follows_but_not_followed_count": 5,
                "followed_but_not_following_count": 11
            },
            "extraction_date": "2025-09-06 12:00:00"
        }
        
        # TODO: Reemplazar con tu servicio real
        # result = tu_servicio.data_mine(username, password, objective)
        
        # Actualizar el contenedor con los resultados formateados
        results_container.content = format_json_data(sample_data)
        page.update()
    
    # Formulario de data mining
    form_container = ft.Container(
        content=ft.Column([
            ft.Text("🔍 Data Mining", 
                   size=20, 
                   weight=ft.FontWeight.BOLD,
                   color=ft.Colors.BLUE_800),
            ft.Container(height=20),
            username_field,
            ft.Container(height=15),
            password_field,
            ft.Container(height=15),
            objective_field,
            ft.Container(height=20),
            ft.ElevatedButton(
                "Enviar",
                on_click=submit_data_mine,
                width=300,
                height=45,
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.BLUE_600,
                    color=ft.Colors.WHITE,
                )
            )
        ]),
        width=350,
        padding=20,
        border=ft.border.all(1, ft.Colors.GREY_300),
        border_radius=8,
        bgcolor=ft.Colors.WHITE,
    )
    
    # Estado de la aplicación
    main_menu = ft.Column([
        ft.Text(
            "Instagram Data Analyzer",
            size=32,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER
        ),
        ft.Container(height=30),
        ft.Column([
            ft.ElevatedButton(
                "Data Mine",
                on_click=lambda e: show_data_mine(),
                width=200,
                height=50,
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.BLUE_500,
                    color=ft.Colors.WHITE,
                )
            ),
            ft.Container(height=15),
            ft.ElevatedButton(
                "Load File",
                on_click=lambda e: print("Load File clicked"),
                width=200,
                height=50,
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.GREEN_500,
                    color=ft.Colors.WHITE,
                )
            ),
            ft.Container(height=15),
            ft.ElevatedButton(
                "Analyze Data",
                on_click=lambda e: print("Analyze Data clicked"),
                width=200,
                height=50,
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.PURPLE_500,
                    color=ft.Colors.WHITE,
                )
            ),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    
    def show_data_mine():
        """Mostrar la vista de data mining"""
        page.clean()
        
        # Botón para volver al menú principal
        back_button = ft.ElevatedButton(
            "← Volver al Menú",
            on_click=lambda e: show_main_menu(),
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.GREY_500,
                color=ft.Colors.WHITE,
            )
        )
        
        # Layout de data mining
        data_mine_layout = ft.Column([
            back_button,
            ft.Container(height=20),
            ft.Row([
                form_container,
                ft.Container(width=20),
                results_container
            ], alignment=ft.MainAxisAlignment.CENTER)
        ])
        
        page.add(data_mine_layout)
        page.update()
    
    def show_main_menu():
        """Mostrar el menú principal"""
        page.clean()
        page.add(main_menu)
        page.update()
    
    # Mostrar menú principal inicialmente
    page.add(main_menu)

if __name__ == "__main__":
    ft.app(target=main)