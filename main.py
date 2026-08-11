import flet as ft
import requests
import threading
import time
import os

GOPRO_IP = "10.5.5.9"

def main(page: ft.Page):
    page.title = "SlowMo Control 1.5.50 (GoPro Edition)"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 15
    page.scroll = ft.ScrollMode.AUTO

    selected_video = [None]
    selected_music = [None]

    status_text = ft.Text("Готов к работе", color="gray", size=13)
    progress_bar = ft.ProgressBar(value=0, visible=False)

    # 1. ТАЙМЕР ЗАПИСИ
    slider_time = ft.Slider(min=3, max=15, divisions=12, label="{value} сек", value=5, width=180)

    def start_timed_recording(e):
        duration = int(slider_time.value)
        status_text.value = f"🔴 Запись... ({duration} сек)"
        status_text.color = "red"
        page.update()
        def task():
            try:
                requests.get(f"http://{GOPRO_IP}:8080/gp/gpControl/command/shutter?p=1", timeout=3)
                time.sleep(duration)
                requests.get(f"http://{GOPRO_IP}:8080/gp/gpControl/command/shutter?p=0", timeout=3)
                status_text.value = "✅ Запись завершена!"
                status_text.color = "green"
            except Exception as ex:
                status_text.value = f"❌ Ошибка GoPro: {ex}"
                status_text.color = "red"
            page.update()
        threading.Thread(target=task).start()

    play_btn = ft.Container(
        content=ft.Text("▶", color="white", size=22, weight="bold"),
        bgcolor="black",
        border_radius=10,
        width=50,
        height=50,
        on_click=start_timed_recording
    )

    # 2. ДИАЛОГИ ВЫБОРА ФАЙЛОВ ANDROID
    def on_video_picked(e):
        if e.files and len(e.files) > 0:
            selected_video[0] = e.files[0].path
            btn_choose_video.text = f"✅ {e.files[0].name}"
            status_text.value = f"Загружено: {e.files[0].name}"
            status_text.color = "green"
            page.update()

    def on_music_picked(e):
        if e.files and len(e.files) > 0:
            selected_music[0] = e.files[0].path
            btn_choose_music.text = f"🎵 {e.files[0].name}"
            status_text.value = f"Загружен трек: {e.files[0].name}"
            status_text.color = "green"
            page.update()

    video_picker = ft.FilePicker()
    video_picker.on_result = on_video_picked

    music_picker = ft.FilePicker()
    music_picker.on_result = on_music_picked

    page.overlay.extend([video_picker, music_picker])

    # 3. КНОПКИ
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

    # 4. 5 ОТРЕЗКОВ СКОРОСТЕЙ (от 0.1x до 5.0x)
    speed_options = [
        ft.dropdown.Option("0.1", "0.1x"),
        ft.dropdown.Option("0.2", "0.2x"),
        ft.dropdown.Option("0.5", "0.5x"),
        ft.dropdown.Option("1.0", "1.0x"),
        ft.dropdown.Option("2.0", "2.0x"),
        ft.dropdown.Option("3.0", "3.0x"),
        ft.dropdown.Option("4.0", "4.0x"),
        ft.dropdown.Option("5.0", "5.0x"),
    ]

    def create_compact_dropdown():
        return ft.Dropdown(
            width=70,
            height=40,
            value="1.0",
            options=speed_options,
            color="black",
            text_size=11
        )

    s1, s2, s3, s4, s5 = [create_compact_dropdown() for _ in range(5)]

    # 5. КАЧЕСТВО И FPS
    res_dropdown = ft.Dropdown(
        width=160, value="1920x1080",
        options=[
            ft.dropdown.Option("1920x1080", "1920x1080"),
            ft.dropdown.Option("2704x1520", "2.7K"),
            ft.dropdown.Option("3840x2160", "4K"),
        ]
    )

    fps_dropdown = ft.Dropdown(
        width=160, value="60",
        options=[
            ft.dropdown.Option("30", "30 FPS"),
            ft.dropdown.Option("60", "60 FPS"),
            ft.dropdown.Option("120", "120 FPS"),
        ]
    )

    switch_parts = ft.Switch(value=True, label="Разбивать по частям")
    switch_boomerang = ft.Switch(value=False, label="🔁 Эффект Бумеранг")
    switch_wifi = ft.Switch(value=False, label="Включить Wi-Fi")

    def connect_gopro(e):
        try:
            res = requests.get(f"http://{GOPRO_IP}:8080/gp/gpControl/status", timeout=3)
            if res.status_code == 200:
                status_text.value = "✅ GoPro успешно подключена!"
                status_text.color = "green"
            else:
                status_text.value = f"⚠️ Ошибка ответа: {res.status_code}"
                status_text.color = "orange"
        except Exception:
            status_text.value = "❌ GoPro не найдена по Wi-Fi"
            status_text.color = "red"
        page.update()

    # 6. СБОРКА ИНТЕРФЕЙСА
    left_column = ft.Column([
        ft.Row([
            play_btn,
            ft.Column([
                ft.Text("Время записи камеры (сек)", size=12, color="gray"),
                slider_time
            ])
        ]),
        ft.Container(height=160, bgcolor="black", border_radius=8),
        ft.Text("Музыка", size=12, color="gray"),
        ft.Slider(min=0, max=100, value=50, active_color="red"),
        btn_choose_music,
        ft.Divider(height=10),
        switch_parts,
        switch_boomerang,
        ft.Row([s1, s2, s3, s4, s5], spacing=3),
        ft.Divider(height=10),
        btn_choose_video,
        btn_convert,
    ], expand=6)

    right_column = ft.Column([
        ft.Text("Настройка камеры", weight="bold"),
        ft.Divider(height=10),
        ft.Text("Подключение GoPro", weight="bold", size=13),
        switch_wifi,
        ft.ElevatedButton("Подключить GoPro", on_click=connect_gopro),
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
        ft.Row([left_column, ft.VerticalDivider(width=10), right_column], vertical_alignment=ft.CrossAxisAlignment.START),
        ft.Divider(),
        progress_bar,
        status_text
    )

ft.app(target=main)
