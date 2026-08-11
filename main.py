import flet as ft
import requests
import os

def main(page: ft.Page):
    page.title = "Alex Slow Mo Studio"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20

    is_recording = False
    status_text = ft.Text("Подключи GoPro к Wi-Fi", color="yellow", size=15)
    process_status = ft.Text("Готов к работе", color="gray", size=14)

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
        process_status.color = "yellow"
        page.update()
        try:
            media_resp = requests.get("http://10.5.5.9:8080/gp/gpMediaList", timeout=4)
            if media_resp.status_code == 200:
                data = media_resp.json()
                last_folder = data['media'][-1]
                folder_name = last_folder['directory']
                last_file = last_folder['fs'][-1]['n']
                file_url = f"http://10.5.5.9:8080/videos/DCIM/{folder_name}/{last_file}"
                process_status.value = f"📥 Скачиваем {last_file}..."
                page.update()
                video_data = requests.get(file_url, timeout=15)
                with open("input_video.mp4", "wb") as f:
                    f.write(video_data.content)
                process_status.value = f"✅ Сохранено: input_video.mp4"
                process_status.color = "green"
                selected_video_label.value = "Выбрано: input_video.mp4"
                selected_video_label.color = "cyan"
            else:
                process_status.value = "⚠️ Не удалось получить список файлов"
                process_status.color = "orange"
        except Exception:
            process_status.value = "❌ Ошибка скачивания с GoPro"
            process_status.color = "red"
        page.update()

    rec_btn = ft.ElevatedButton("НАЧАТЬ ЗАПИСЬ", bgcolor="green", color="white", on_click=toggle_record)

    # 2. Поиск и выбор Видео / Музыки
    selected_video_label = ft.Text("Видео не выбрано", color="gray")
    selected_music_label = ft.Text("Музыка не выбрана", color="gray")

    def filter_video_list(e):
        query = video_search_input.value.lower()
        video_list_view.controls.clear()
        # Демо-список файлов + реальный поиск локальных файлов .mp4
        all_files = ["input_video.mp4", "gopro_clip_001.mp4", "gopro_clip_002.mp4", "slowmo_test.mp4"]
        for f in all_files:
            if query in f.lower():
                video_list_view.controls.append(
                    ft.ListTile(
                        title=ft.Text(f),
                        on_click=lambda ev, file_name=f: select_video(file_name)
                    )
                )
        page.update()

    def select_video(name):
        selected_video_label.value = f"📹 Выбрано видео: {name}"
        selected_video_label.color = "cyan"
        page.update()

    def filter_music_list(e):
        query = music_search_input.value.lower()
        music_list_view.controls.clear()
        all_tracks = ["track_01_action.mp3", "drive_rock.mp3", "chill_background.mp3", "slowmo_beat.mp3"]
        for m in all_tracks:
            if query in m.lower():
                music_list_view.controls.append(
                    ft.ListTile(
                        title=ft.Text(m),
                        on_click=lambda ev, track_name=m: select_music(track_name)
                    )
                )
        page.update()

    def select_music(name):
        selected_music_label.value = f"🎵 Выбрана музыка: {name}"
        selected_music_label.color = "cyan"
        page.update()

    video_search_input = ft.TextField(label="🔍 Поиск видео...", on_change=filter_video_list)
    video_list_view = ft.ListView(height=100, spacing=5)

    music_search_input = ft.TextField(label="🔍 Поиск музыки...", on_change=filter_music_list)
    music_list_view = ft.ListView(height=100, spacing=5)

    # Инициализация списков при старте
    filter_video_list(None)
    filter_music_list(None)

    # 3. Настройка 5 отрезков (выпадающие меню от 0.1x до 7x)
    speed_options = [
        ft.dropdown.Option("0.1x (Замедление)"),
        ft.dropdown.Option("0.2x (Замедление)"),
        ft.dropdown.Option("0.5x (Замедление)"),
        ft.dropdown.Option("1.0x (Норм)"),
        ft.dropdown.Option("2.0x (Ускорение)"),
        ft.dropdown.Option("3.0x (Ускорение)"),
        ft.dropdown.Option("4.0x (Ускорение)"),
        ft.dropdown.Option("5.0x (Ускорение)"),
        ft.dropdown.Option("6.0x (Ускорение)"),
        ft.dropdown.Option("7.0x (Ускорение)"),
    ]

    segments_container = ft.Column([
        ft.Row([ft.Text("Отрезок 1:"), ft.Dropdown(width=200, value="0.2x (Замедление)", options=speed_options)]),
        ft.Row([ft.Text("Отрезок 2:"), ft.Dropdown(width=200, value="1.0x (Норм)", options=speed_options)]),
        ft.Row([ft.Text("Отрезок 3:"), ft.Dropdown(width=200, value="0.1x (Замедление)", options=speed_options)]),
        ft.Row([ft.Text("Отрезок 4:"), ft.Dropdown(width=200, value="2.0x (Ускорение)", options=speed_options)]),
        ft.Row([ft.Text("Отрезок 5:"), ft.Dropdown(width=200, value="0.5x (Замедление)", options=speed_options)]),
    ])

    def run_processing(e):
        process_status.value = "⚙️ Применение скоростей к 5 отрезкам + сведение..."
        process_status.color = "cyan"
        page.update()

    # СБОРКА ИНТЕРФЕЙСА
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

        # Блок Выбора Видео
        ft.Container(
            content=ft.Column([
                ft.Text("Выбор видео (Поиск)", size=18, weight="bold"),
                selected_video_label,
                video_search_input,
                video_list_view
            ]),
            padding=15, border_radius=10, bgcolor="#1e1e24"
        ),

        ft.Divider(height=10, color="transparent"),

        # Блок Выбора Музыки
        ft.Container(
            content=ft.Column([
                ft.Text("Выбор аудио / музыки", size=18, weight="bold"),
                selected_music_label,
                music_search_input,
                music_list_view
            ]),
            padding=15, border_radius=10, bgcolor="#1e1e24"
        ),

        ft.Divider(height=10, color="transparent"),

        # Блок Настройки 5 Отрезков
        ft.Container(
            content=ft.Column([
                ft.Text("Разбивка на 5 отрезков (Скорость от 0.1x до 7x)", size=18, weight="bold"),
                segments_container,
                ft.Divider(height=10, color="gray"),
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
