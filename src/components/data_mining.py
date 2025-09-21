import flet as ft


def username_field_component():
    return ft.TextField(
        label="Username",
        width=300,
        border_radius=8,
    )


def password_field_component():
    return ft.TextField(
        label="Password",
        password=True,
        can_reveal_password=True,
        width=300,
        border_radius=8,
    )


def objective_field_component():
    return ft.TextField(label="Objective", width=300, border_radius=8)


def results_container_component():
    return ft.Container(
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


def form_container_component(
    username_field, password_field, objective_field, perform_data_mining
):
    return ft.Container(
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
