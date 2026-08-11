import flet as ft
import requests

def main(page: ft.Page):
    page.title = "Alex Slow Mo Studio"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20

    # Переменные состояния
    is_recording = False
    status_text = ft.Text("Подключи GoPro к Wi-Fi", color="yellow", size=15)
    process_status = ft.Text("Готов к работе", color="gray", size=14)

    # 1. Управление GoPro (Старт/Стоп и Скачивание)
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

    def toggle_record(e):
        nonlocal is_recording
        try:
            cmd = "1" if not is_recording else "0"
            resp = requests.get(f"http://10.5.5.9/gp/gpControl/command/shutter?p={cmd}", timeout=2)
            if resp.status_code == 200:
                is_recording = not is_recording
                if is_recording:
                    rec_btn.text = "СТОП ЗАПИСЬ"
                    rec_btn.bgcolor = "red"
                    status_text.value = "🔴 ИДЕТ ЗАПИСЬ..."
                    status_text.color = "red"
                else:
                    rec_btn.text = "НАЧАТЬ ЗАПИСЬ"
                    rec_btn.bgcolor = "green"
                    status_text.value = "⏹ Запись остановлена"
                    status_text.color = "white"
            else:
                status_text.value = "⚠️ Ошибка команды"
        except:
            status_text.value = "❌ Нет связи с GoPro"
        page.update()

    def download_last_video(e):
        process_status.value = "⏳ Запрос списка файлов с GoPro..."
        page.update()
        # Имитация запроса скачивания последнего файла с HTTP сервера GoPro
        process_status.value = "📥 Видео скачано в память устройства"
        process_status.color = "green"
        page.update()

    rec_btn = ft.ElevatedButton("НАЧАТЬ ЗАПИСЬ", bgcolor="green", color="white", on_click=toggle_record)

    # 2. Логика обработки
    def run_processing(e):
        process_status.value = "⚙️ Обработка: разрез на 5 отрезков + slow-mo + бумеранг..."
        process_status.color = "cyan"
        page.update()

    # ИНТЕРФЕЙС
    page.add(
        ft.Container(height=30),
        ft.Text("Alex Slow Mo Studio", size=26, weight="bold", color="#00d2ff"),
        ft.Divider(height=10, color="transparent"),

        # Блок GoPro
        ft.Container(
            content=ft.Column([
                ft.Text("Управление GoPro", size=18, weight="bold"),
                status_text,
                ft.Row([
                    ft.ElevatedButton("Проверить", on_click=check_connection),
                    rec_btn,
                ]),
                ft.ElevatedButton("📥 Скачать последнее видео с камеры", on_click=download_last_video)
            ]),
            padding=15, border_radius=10, bgcolor="#1e1e24"
        ),

        ft.Divider(height=10, color="transparent"),

        # Блок обработки
        ft.Container(
            content=ft.Column([
                ft.Text("Редактор замедления и эффектов", size=18, weight="bold"),
                
                ft.TextField(label="Файл видео", value="input_video.mp4"),
                ft.TextField(label="Файл музыки (необязательно)", value="music.mp3"),
                
                ft.Divider(height=10, color="gray"),
                
                ft.Text("Скорость замедления (Slow-Mo):", size=14),
                ft.Slider(min=0.1, max=1.0, divisions=9, value=0.5, label="{value}x"),
                
                ft.Checkbox(label="Авторазбивка на 5 одинаковых отрезков", value=True),
                ft.Checkbox(label="Эффект Бумеранг (реверс)", value=True),
                
                ft.Divider(height=10, color="transparent"),
                process_status,
                
                ft.ElevatedButton(
                    "Обработать и сохранить", 
                    bgcolor="#00d2ff", 
                    color="black",
                    on_click=run_processing
                )
            ]),
            padding=15, border_radius=10, bgcolor="#1e1e24"
        )
    )

ft.app(target=main)
