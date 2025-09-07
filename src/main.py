import flet as ft
import json


def main(page: ft.Page):
    # =====================| Page Configuration |======================
    page.title = "Instagram Data Analyzer"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 20

    # =====================| Navigation Functions |======================
    def show_data_mine_section(e):
        page.clean()

        back_button = ft.ElevatedButton(
            "← Volver al Menú",
            on_click=show_main_menu_section,
            bgcolor=ft.Colors.GREY_500,
            color=ft.Colors.WHITE,
        )

        # Layout de data mining
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

    def show_main_menu_section(e):
        page.clean()
        page.add(main_menu)
        page.update()

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
                        on_click=print("Load File clicked"),
                        width=200,
                        height=50,
                        bgcolor=ft.Colors.GREEN_500,
                        color=ft.Colors.WHITE,
                    ),
                    ft.Container(height=15),
                    ft.ElevatedButton(
                        "Analyze Data",
                        on_click=print("Analyze Data clicked"),
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
