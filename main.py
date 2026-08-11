import flet as ft
import requests
import threading
import time
import os

GOPRO_IP = "10.5.5.9"
DOWNLOAD_DIR = "/storage/emulated/0/Download"

def main(page: ft.Page):
    page.title = "SlowMo Control 2.0"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    selected_video = [None]
    selected_music = [None]

    status_text = ft.Text("Готов к работе", color="white", size=13)
    progress_bar = ft.ProgressBar(value=0, visible=False)

    # 1. ТАЙМЕР И КНОПКА PLAY (через текст для 100% стабильности в APK)
    slider_time = ft.Slider(min=3, max=15, divisions=12, label="{value} сек", value=5, width=200)

    def start_timed_recording(e):
        duration = int(slider_time.value)
        status_text.value = f"🔴 Запись... ({duration} сек)"
        page.update()
        def task():
            try:
                requests.get(f"http://{GOPRO_IP}:8080/gp/gpControl/command/shutter?p=1", timeout=3)
                time.sleep(duration)
                requests.get(f"http://{GOPRO_IP}:8080/gp/gpControl/command/shutter?p=0", timeout=3)
                status_text.value = "✅ Запись завершена"
            except Exception as ex:
                status_text.value = f"❌ Ошибка записи: {ex}"
            page.update()
        threading.Thread(target=task).start()

    play_btn = ft.Container(
        content=ft.Text("▶", color="white", size=22, weight="bold"),
        bgcolor="black",
        border_radius=10,
        width=50,
        height=50,
        alignment=ft.alignment.center,
        on_click=start_timed_recording
    )

    # ВЫБОР ФАЙЛОВ (Текстовые поля для надежности на Android)
    video_input = ft.TextField(label="Видео из Download", value="GX011011.MP4", width=250)
    music_input = ft.TextField(label="Музыка (опционально)", value="", width=250)

    # 4. КОМПАКТНЫЕ 5 ОТРЕЗКОВ
    def create_compact_dropdown():
        return ft.Container(
            content=ft.Dropdown(
                width=65,
                height=38,
                value="1.0x",
                options=[ft.dropdown.Option(x) for x in ["0.1x", "0.2x", "0.5x", "1.0x", "2.0x"]],
                border_color="transparent",
                color="black",
                text_size=11
            ),
            bgcolor="white",
            border=ft.border.all(1, "black"),
            border_radius=8,
            padding=ft.padding.only(left=2, right=2)
        )

    s1, s2, s3, s4, s5 = [create_compact_dropdown() for _ in range(5)]

    # 5. КАЧЕСТВО
    res_dropdown = ft.Dropdown(
        width=180, value="1920x1080",
        options=[
            ft.dropdown.Option("1920x1080", "1920x1080"),
            ft.dropdown.Option("2704x1520", "2.7K (2704x1520)"),
            ft.dropdown.Option("3840x2160", "4K (3840x2160)"),
        ],
        border_color="black"
    )

    fps_dropdown = ft.Dropdown(
        width=180, value="60",
        options=[
            ft.dropdown.Option("30", "30 FPS"),
            ft.dropdown.Option("60", "60 FPS"),
            ft.dropdown.Option("120", "120 FPS"),
        ],
        border_color="black"
    )

    switch_parts = ft.Switch(value=True, label="Разбивать по частям")
    switch_wifi = ft.Switch(value=False, label="Включить Wi-Fi")

    def connect_gopro(e):
        try:
            res = requests.get(f"http://{GOPRO_IP}:8080/gp/gpControl/status", timeout=3)
            if res.status_code == 200:
                status_text.value = "✅ GoPro подключена!"
                status_text.color = "green"
            else:
                status_text.value = f"⚠️ Ошибка ответа: {res.status_code}"
                status_text.color = "orange"
        except Exception:
            status_text.value = "❌ Нет связи с GoPro"
            status_text.color = "red"
        page.update()

    # 6 & 7. КРАСНЫЕ КНОПКИ
    btn_convert = ft.ElevatedButton("🎬 Конвертировать", bgcolor="red", color="white", width=250)

    # ИНТЕРФЕЙС
    left_column = ft.Column([
        ft.Row([
            play_btn,
            ft.Column([
                ft.Text("Время записи (сек)", size=12, color="gray"),
                slider_time
            ])
        ]),
        ft.Container(height=140, bgcolor="black", border_radius=8, content=ft.Text("ПЛЕЕР", text_align=ft.TextAlign.CENTER)),
        ft.Text("Музыка", size=12, color="gray"),
        music_input,
        ft.Divider(height=10),
        switch_parts,
        ft.Row([s1, s2, s3, s4, s5], spacing=4),
        ft.Divider(height=10),
        video_input,
        btn_convert,
    ], expand=6)

    right_column = ft.Column([
        ft.Text("Настройка камеры", weight="bold"),
        ft.Divider(height=5),
        ft.Text("GoPro Wi-Fi", weight="bold", size=12),
        switch_wifi,
        ft.ElevatedButton("Подключить GoPro", on_click=connect_gopro),
        ft.Divider(height=10),
        ft.Text("Качество", weight="bold", size=12),
        res_dropdown,
        fps_dropdown,
    ], expand=4)

    page.add(
        ft.Row([left_column, ft.VerticalDivider(width=10), right_column], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.START),
        ft.Divider(),
        progress_bar,
        status_text
    )

ft.app(target=main)
