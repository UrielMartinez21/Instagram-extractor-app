import flet as ft


def analyze_account_name_field_component(on_analyze_account_name_change):
    return ft.TextField(
        label="Nombre de la cuenta (sin @)",
        hint_text="Ejemplo: mar_tz_ml",
        width=300,
        border_radius=8,
        on_change=on_analyze_account_name_change,
    )


def analyze_files_found_text_component():
    return ft.Text(
        "Ingresa un nombre de cuenta para buscar archivos",
        size=12,
        color=ft.Colors.GREY_600,
    )


def analyze_file1_selector_component():
    return ft.Dropdown(
        label="Primer archivo (más antiguo)",
        width=300,
        options=[],
        border_radius=8,
    )


def analyze_file2_selector_component():
    return ft.Dropdown(
        label="Segundo archivo (más reciente)",
        width=300,
        options=[],
        border_radius=8,
    )


def analyze_results_container_component():
    return ft.Container(
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


def analyze_form_container_component(
    analyze_account_name_field,
    analyze_files_found_text,
    analyze_file1_selector,
    analyze_file2_selector,
    perform_comparison,
):
    return ft.Container(
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
