import flet as ft


def account_name_field_component(on_account_name_change):
    return ft.TextField(
        label="Nombre de la cuenta (sin @)",
        hint_text="Ejemplo: mar_tz_ml",
        width=300,
        border_radius=8,
        on_change=on_account_name_change,  # Se ejecuta cada vez que cambia el texto
    )


def files_found_text_component():
    return ft.Text(
        "Ingresa un nombre de cuenta para buscar archivos",
        size=12,
        color=ft.Colors.GREY_600
    )


def file_selector_component():
    return ft.Dropdown(
        label="Seleccionar archivo",
        width=300,
        options=[],  # Se llena dinámicamente
        border_radius=8,
    )


def load_results_container_component():
    return ft.Container(
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


def load_form_container_component(
    account_name_field,
    files_found_text,
    file_selector,
    load_and_display_file,
):
    return ft.Container(
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