import flet as ft
import requests
import threading
import time

GOPRO_IP = "10.5.5.9"

def main(page: ft.Page):
    page.title = "Alex Slow Mo Studio"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#121216"
    page.padding = 16
    page.scroll = ft.ScrollMode.AUTO

    # Запрос разрешений на доступ к медиафайлам при запуске приложения
    def request_permissions():
        try:
            page.permissions.request([
                "android.permission.READ_EXTERNAL_STORAGE",
                "android.permission.WRITE_EXTERNAL_STORAGE",
                "android.permission.READ_MEDIA_VIDEO",
                "android.permission.READ_MEDIA_AUDIO",
                "android.permission.MANAGE_EXTERNAL_STORAGE"
            ])
        except Exception:
            pass

    page.on_load = lambda _: request_permissions()

    # Цветовая палитра
    CARD_BG = "#1e1e24"
    INPUT_BG = "#18181c"
    CYAN_ACCENT = "#28c7fa"
    GREEN_ACCENT = "#4caf50"
    BORDER_COLOR = "#33333d"

    status_text = ft.Text("Готов к работе", color="#a0a0a0", size=13)
    progress_bar = ft.ProgressBar(value=0, visible=False, color=CYAN_ACCENT)

    # 1. УПРАВЛЕНИЕ GOPRO
    gopro_status_text = ft.Text("Подключи GoPro к Wi-Fi", color="#ffd54f", size=13)

    def check_gopro(e):
        def task():
            try:
                res = requests.get(f"http://{GOPRO_IP}:8080/gp/gpControl/status", timeout=3)
                if res.status_code == 200:
                    gopro_status_text.value = "✅ Подключено!"
                    gopro_status_text.color = GREEN_ACCENT
                else:
                    gopro_status_text.value = f"⚠️ Ошибка: {res.status_code}"
                    gopro_status_text.color = "orange"
            except Exception:
                gopro_status_text.value = "❌ Не найдена по Wi-Fi"
                gopro_status_text.color = "red"
            page.update()
        threading.Thread(target=task).start()

    def start_recording(e):
        def task():
            try:
                requests.get(f"http://{GOPRO_IP}:8080/gp/gpControl/command/shutter?p=1", timeout=3)
                gopro_status_text.value = "🔴 Запись началась..."
                gopro_status_text.color = "red"
            except Exception as ex:
                gopro_status_text.value = f"❌ Ошибка записи: {ex}"
                gopro_status_text.color = "red"
            page.update()
        threading.Thread(target=task).start()

    card_gopro = ft.Container(
        content=ft.Column([
            ft.Text("Управление GoPro", weight="bold", size=16),
            gopro_status_text,
            ft.Row([
                ft.OutlinedButton("Проверить", on_click=check_gopro, style=ft.ButtonStyle(color="white")),
                ft.ElevatedButton("НАЧАТЬ ЗАПИСЬ", bgcolor=GREEN_ACCENT, color="white", on_click=start_recording),
            ], spacing=10),
            ft.TextButton("📥 Скачать последнее видео", style=ft.ButtonStyle(color="#90caf9")),
        ]),
        bgcolor=CARD_BG,
        padding=16,
        border_radius=12,
    )

    # 2. ФАЙЛЫ ДЛЯ ОБРАБОТКИ
    video_dd = ft.Dropdown(
        label="Выбери видео из Download",
        bgcolor=INPUT_BG,
        border_color=BORDER_COLOR,
        border_radius=8,
        options=[ft.dropdown.Option("video1.mp4", "video1.mp4")]
    )

    music_dd = ft.Dropdown(
        label="Выбери трек из Music",
        value="no_music",
        bgcolor=INPUT_BG,
        border_color=BORDER_COLOR,
        border_radius=8,
        options=[ft.dropdown.Option("no_music", "Без музыки")]
    )

    card_files = ft.Container(
        content=ft.Column([
            ft.Text("Файлы для обработки", weight="bold", size=16),
            ft.Container(height=8),  # Отступ под заголовком
            video_dd,
            ft.Container(height=16),  # Увеличенный отступ между полями
            music_dd,
        ], spacing=0),
        bgcolor=CARD_BG,
        padding=16,
        border_radius=12,
    )

    # 3. НАСТРОЙКА СКОРОСТИ 5 ОТРЕЗКОВ
    speed_options = [
        ft.dropdown.Option("0.1", "0.1x (Замедл.)"),
        ft.dropdown.Option("0.2", "0.2x (Замедл.)"),
        ft.dropdown.Option("0.5", "0.5x (Замедл.)"),
        ft.dropdown.Option("1.0", "1.0x (Обычн.)"),
        ft.dropdown.Option("2.0", "2.0x (Ускор.)"),
    ]

    def make_speed_dropdown(default_val):
        return ft.Dropdown(
            value=default_val,
            options=speed_options,
            bgcolor=INPUT_BG,
            border_color=BORDER_COLOR,
            border_radius=8,
            content_padding=8,
            expand=True
        )

    s1 = make_speed_dropdown("0.2")
    s2 = make_speed_dropdown("1.0")
    s3 = make_speed_dropdown("0.1")
    s4 = make_speed_dropdown("2.0")
    s5 = make_speed_dropdown("0.5")

    res_dropdown = ft.Dropdown(
        label="Разрешение",
        value="1080p",
        bgcolor=INPUT_BG,
        border_color=BORDER_COLOR,
        border_radius=8,
        options=[
            ft.dropdown.Option("1080p", "1080p (1920x1080)"),
            ft.dropdown.Option("2.7k", "2.7K (2704x1520)"),
            ft.dropdown.Option("4k", "4K (3840x2160)"),
        ]
    )

    cb_boomerang = ft.Checkbox(label="Эффект Бумеранг (реверс)", value=False)

    btn_process = ft.ElevatedButton(
        "Обработать и сохранить",
        bgcolor=CYAN_ACCENT,
        color="black",
        weight="bold",
        height=45,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20))
    )

    card_settings = ft.Container(
        content=ft.Column([
            ft.Text("Настройка скорости 5 отрезков", weight="bold", size=16),
            ft.Row([ft.Text("1:", color="gray"), s1, ft.Text("2:", color="gray"), s2], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([ft.Text("3:", color="gray"), s3, ft.Text("4:", color="gray"), s4], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([ft.Text("5:", color="gray"), s5, ft.Container(expand=True)], alignment=ft.MainAxisAlignment.CENTER),
            ft.Divider(color=BORDER_COLOR, height=20),
            res_dropdown,
            cb_boomerang,
            ft.Container(height=10),
            status_text,
            btn_process,
        ], spacing=10),
        bgcolor=CARD_BG,
        padding=16,
        border_radius=12,
    )

    # Заголовок приложения
    header = ft.Text("Alex Slow Mo Studio", size=22, weight="bold", color=CYAN_ACCENT)

    page.add(
        header,
        card_gopro,
        card_files,
        card_settings,
        progress_bar
    )

ft.app(target=main)
