import flet as ft
import requests
import threading
import time
import os

GOPRO_IP = "10.5.5.9"

def main(page: ft.Page):
    page.title = "SlowMo Control 1.5.50 (GoPro Edition)"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 1000
    page.window_height = 800
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    selected_video = [None]
    selected_music = [None]

    status_text = ft.Text("Ожидание действий...", color="gray", size=13)
    progress_bar = ft.ProgressBar(value=0, visible=False)

    # 1. ТАЙМЕР ЗАПИСИ
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

    # Кнопка Play (без капризного alignment)
    play_btn = ft.Container(
        content=ft.Text("▶", color="white", size=22, weight="bold"),
        bgcolor="black",
        border_radius=10,
        width=50,
        height=50,
        on_click=start_timed_recording
    )

    # ДИАЛОГИ ВЫБОРА ФАЙЛОВ
    def on_video_picked(e):
        if e.files:
            selected_video[0] = e.files[0].path
            btn_choose_video.text = f"✅ {e.files[0].name}"
            status_text.value = f"Загружено видео: {e.files[0].name}"
            page.update()

    def on_music_picked(e):
        if e.files:
            selected_music[0] = e.files[0].path
            btn_choose_music.text = f"🎵 {e.files[0].name}"
            status_text.value = f"Загружен трек: {e.files[0].name}"
            page.update()

    video_picker = ft.FilePicker()
    video_picker.on_result = on_video_picked

    music_picker = ft.FilePicker()
    music_picker.on_result = on_music_picked

    # КРАСНЫЕ КНОПКИ
    btn_choose_video = ft.ElevatedButton(
        "Выбрать видео", 
        bgcolor="red", 
        color="white", 
        on_click=lambda _: video_picker.pick_files(file_type=ft.FilePickerFileType.VIDEO)
    )
    
    btn_choose_music = ft.ElevatedButton(
        "Выбрать музыку", 
        bgcolor="red", 
        color="white", 
        on_click=lambda _: music_picker.pick_files(file_type=ft.FilePickerFileType.AUDIO)
    )

    btn_convert = ft.ElevatedButton(
        "🎬 Конвертировать", 
        bgcolor="red", 
        color="white"
    )

    # КОМПАКТНЫЕ 5 ОТРЕЗКОВ
    def create_compact_dropdown():
        return ft.Container(
            content=ft.Dropdown(
                width=75,
                height=38,
                value="1.0x",
                options=[ft.dropdown.Option(x) for x in ["0.1x", "0.2x", "0.5x", "1.0x", "2.0x"]],
                color="black",
                text_size=12
            ),
            bgcolor="white",
            border_radius=8,
            padding=2
        )

    s1 = create_compact_dropdown()
    s2 = create_compact_dropdown()
    s3 = create_compact_dropdown()
    s4 = create_compact_dropdown()
    s5 = create_compact_dropdown()

    # КАЧЕСТВО И РАЗРЕШЕНИЕ
    res_dropdown = ft.Dropdown(
        width=180, value="1920x1080",
        options=[
            ft.dropdown.Option("1920x1080", "1920x1080"),
            ft.dropdown.Option("2704x1520", "2.7K (2704x1520)"),
            ft.dropdown.Option("3840x2160", "4K (3840x2160)"),
        ]
    )

    fps_dropdown = ft.Dropdown(
        width=180, value="60",
        options=[
            ft.dropdown.Option("30", "30 FPS"),
            ft.dropdown.Option("60", "60 FPS"),
            ft.dropdown.Option("120", "120 FPS"),
        ]
    )

    switch_parts = ft.Switch(value=True, label="Разбивать по частям")
    switch_wifi = ft.Switch(value=False, label="Включить Wi-Fi")

    def connect_gopro(e):
        try:
            res = requests.get(f"http://{GOPRO_IP}:8080/gp/gpControl/status", timeout=3)
            if res.status_code == 200:
                status_text.value = "✅ GoPro успешно подключена!"
                status_text.color = "green"
            else:
                status_text.value = f"⚠️ Ошибка ответа GoPro: {res.status_code}"
                status_text.color = "orange"
        except Exception:
            status_text.value = "❌ Ошибка: GoPro не найдена по Wi-Fi"
            status_text.color = "red"
        page.update()

    # ЛЕВАЯ КОЛОНКА
    left_column = ft.Column([
        ft.Row([
            play_btn,
            ft.Column([
                ft.Text("Время записи камеры (сек)", size=12, color="gray"),
                slider_time
            ])
        ]),
        ft.Container(height=180, bgcolor="black", border_radius=8),
        ft.Text("Музыка", size=12, color="gray"),
        ft.Slider(min=0, max=100, value=50, active_color="red"),
        btn_choose_music,
        ft.Divider(height=15),
        switch_parts,
        ft.Row([s1, s2, s3, s4, s5], spacing=5),
        ft.Divider(height=10),
        btn_choose_video,
        btn_convert,
    ], expand=6)

    # ПРАВАЯ КОЛОНКА
    right_column = ft.Column([
        ft.Text("Настройка камеры", weight="bold"),
        ft.Divider(height=10),
        ft.Text("Подключение GoPro", weight="bold", size=13),
        switch_wifi,
        ft.ElevatedButton("Подключить GoPro", on_click=connect_gopro),
        ft.Divider(height=15),
        ft.Text("Подключение телефона", weight="bold", size=13),
        ft.OutlinedButton("Подключить Phone"),
        ft.Divider(height=15),
        ft.Container(
            content=ft.Column([
                ft.Text("Качество", weight="bold", size=13),
                ft.Text("Разрешение:", size=12),
                res_dropdown,
                ft.Text("FPS:", size=12),
                fps_dropdown,
            ]),
            padding=10,
            border_radius=8
        )
    ], expand=4)

    page.add(
        ft.Row([left_column, ft.VerticalDivider(width=20), right_column], vertical_alignment=ft.CrossAxisAlignment.START),
        ft.Divider(),
        progress_bar,
        status_text
    )

ft.app(target=main)
