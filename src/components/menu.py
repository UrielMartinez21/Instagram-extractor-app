import flet as ft

def main_menu_component(show_data_mine_section, show_load_file_section, show_analyze_data_section):
    return ft.Column(
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
