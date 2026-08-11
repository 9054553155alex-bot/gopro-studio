
import flet as ft
import requests

def main(page: ft.Page):
    page.title = "Alex Slow Mo Studio"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO
    page.padding = ft.padding.only(top=50, left=20, right=20, bottom=30)

    # Переменные состояния
    selected_file = ft.Text("Файл не выбран", color="grey", size=14)
    status_text = ft.Text("Подключи GoPro к Wi-Fi", color="yellow", size=15)

    # 1. Логика GoPro
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

    # 2. Выбор файлов
    def pick_video_result(e: ft.FilePickerResultEvent):
        if e.files:
            selected_file.value = f"📹 Видео: {e.files[0].name}"
            selected_file.color = "white"
            page.update()

    file_picker = ft.FilePicker(on_result=pick_video_result)
    page.overlay.append(file_picker)

    # ИНТЕРФЕЙС
    page.add(
        ft.Text("Alex Slow Mo Studio", size=26, weight="bold", color="#00d2ff"),
        ft.Divider(height=15, color="transparent"),

        # Блок управления GoPro
        ft.Container(
            content=ft.Column([
                ft.Text("Управление GoPro", size=18, weight="bold"),
                status_text,
                ft.Row([
                    ft.ElevatedButton("Проверить", on_click=check_connection),
                    ft.ElevatedButton(
                        "Запись", 
                        icon=ft.icons.FIBER_MANUAL_RECORD, 
                        icon_color="white", 
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

        # Блок обработки видео
        ft.Container(
            content=ft.Column([
                ft.Text("Обработка видео", size=18, weight="bold"),
                ft.ElevatedButton(
                    "Выбрать видео", 
                    icon=ft.icons.VIDEO_LIBRARY,
                    on_click=lambda _: file_picker.pick_files(allow_multiple=False, allowed_extensions=["mp4", "mov"])
                ),
                selected_file,
                
                ft.Divider(height=10, color="gray"),
                
                ft.Text("Скорость замедления:", size=14),
                ft.Slider(min=0.1, max=1.0, divisions=9, value=0.5, label="{value}x"),
                
                ft.Divider(height=10, color="gray"),
                
                ft.ElevatedButton("Добавить музыку", icon=ft.icons.MUSIC_NOTE),
                
                ft.Divider(height=15, color="transparent"),
                ft.ElevatedButton(
                    "Обработать и сохранить", 
                    icon=ft.icons.AUTO_FIX_HIGH,
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
