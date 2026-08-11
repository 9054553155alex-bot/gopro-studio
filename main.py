import flet as ft
import requests

def main(page: ft.Page):
    page.title = "Alex Slow Mo Studio"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20

    # Переменные состояния
    selected_file = ft.Text("Файл не выбран", color="grey", size=14)
    status_text = ft.Text("Подключи GoPro к Wi-Fi", color="yellow", size=15)

    # 1. Управление GoPro
    def check_connection(e):
        try:
            resp = requests.get("http://10.5.5.9/gp/gpControl", timeout=2)
            if resp.status_code == 200:
                status_text.value = "✅ Камера готова!"
                status_text.color = "green"
            else:
                status_text.value = "⚠️ Ошибка подключения"
        except:
            status_text.value = "❌ Нет связи с GoPro"
        page.update()

    def start_record(e):
        try:
            resp = requests.get("http://10.5.5.9/gp/gpControl/command/shutter?p=1", timeout=2)
            if resp.status_code == 200:
                status_text.value = "🔴 ИДЕТ ЗАПИСЬ!"
                status_text.color = "red"
            else:
                status_text.value = "⚠️ Ошибка записи"
        except:
            status_text.value = "❌ Нет связи с GoPro"
        page.update()

    # ИНТЕРФЕЙС ПРИЛОЖЕНИЯ
    page.add(
        ft.Container(height=30),  # Отступ под статус-бар
        ft.Text("Alex Slow Mo Studio", size=26, weight="bold", color="#00d2ff"),
        ft.Divider(height=15, color="transparent"),

        # Блок GoPro
        ft.Container(
            content=ft.Column([
                ft.Text("Управление GoPro", size=18, weight="bold"),
                status_text,
                ft.Row([
                    ft.ElevatedButton("Проверить", on_click=check_connection),
                    ft.ElevatedButton(
                        "Запись", 
                        bgcolor="red", 
                        color="white",
                        on_click=start_record
                    ),
                ], alignment=ft.MainAxisAlignment.START)
            ]),
            padding=15,
            border_radius=10,
            bgcolor="#1e1e24"
        ),

        ft.Divider(height=15, color="transparent"),

        # Блок обработки
        ft.Container(
            content=ft.Column([
                ft.Text("Обработка видео", size=18, weight="bold"),
                ft.TextField(label="Путь к файлу или имя", value="video.mp4"),
                selected_file,
                
                ft.Divider(height=10, color="gray"),
                
                ft.Text("Скорость замедления:", size=14),
                ft.Slider(min=0.1, max=1.0, divisions=9, value=0.5, label="{value}x"),
                
                ft.Divider(height=10, color="gray"),
                
                ft.ElevatedButton("Добавить музыку"),
                
                ft.Divider(height=15, color="transparent"),
                ft.ElevatedButton(
                    "Обработать и сохранить", 
                    bgcolor="#00d2ff", 
                    color="black"
                )
            ]),
            padding=15,
            border_radius=10,
            bgcolor="#1e1e24"
        )
    )

ft.app(target=main)
