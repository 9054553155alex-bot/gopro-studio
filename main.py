import flet as ft
import requests
import os
import subprocess
import re
import threading

# Пути к системным папкам Android
DOWNLOAD_DIR = "/storage/emulated/0/Download"
MUSIC_DIR = "/storage/emulated/0/Music"

def main(page: ft.Page):
    page.title = "Alex Slow Mo Studio"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20

    is_recording = False
    selected_video_path = None
    selected_music_path = None

    status_text = ft.Text("Подключи GoPro к Wi-Fi", color="yellow", size=15)
    process_status = ft.Text("Готов к работе", color="gray", size=14)
    progress_bar = ft.ProgressBar(value=0, width=400, visible=False)

    # --- 1. ГОПРО: СТАП/СТОП И СКАЧИВАНИЕ В DOWNLOAD ---
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
                rec_btn.text = "СТОП ЗАПИСЬ" if is_recording else "НАЧАТЬ ЗАПИСЬ"
                rec_btn.bgcolor = "red" if is_recording else "green"
                status_text.value = "🔴 ИДЕТ ЗАПИСЬ..." if is_recording else "⏹ Запись остановлена"
                status_text.color = "red" if is_recording else "white"
        except:
            status_text.value = "❌ Нет связи с GoPro"
        page.update()

    def download_last_video(e):
        process_status.value = "⏳ Запрос файла с GoPro..."
        process_status.color = "yellow"
        page.update()
        
        def run_dl():
            try:
                media_resp = requests.get("http://10.5.5.9:8080/gp/gpMediaList", timeout=4)
                if media_resp.status_code == 200:
                    data = media_resp.json()
                    last_folder = data['media'][-1]['directory']
                    last_file = data['media'][-1]['fs'][-1]['n']
                    file_url = f"http://10.5.5.9:8080/videos/DCIM/{last_folder}/{last_file}"
                    
                    save_path = os.path.join(DOWNLOAD_DIR, last_file)
                    process_status.value = f"📥 Скачиваем в Download/{last_file}..."
                    page.update()
                    
                    with requests.get(file_url, stream=True) as r:
                        r.raise_for_status()
                        with open(save_path, 'wb') as f:
                            for chunk in r.iter_content(chunk_size=8192):
                                f.write(chunk)
                                
                    process_status.value = f"✅ Скачано в Загрузки: {last_file}"
                    process_status.color = "green"
                    scan_download_folder(None)
                else:
                    process_status.value = "⚠️ Не удалось прочитать карту GoPro"
            except Exception as err:
                process_status.value = f"❌ Ошибка скачивания: {err}"
                process_status.color = "red"
            page.update()

        threading.Thread(target=run_dl).start()

    rec_btn = ft.ElevatedButton("НАЧАТЬ ЗАПИСЬ", bgcolor="green", color="white", on_click=toggle_record)

    # --- 2. СКАНЕР ПАПКИ DOWNLOAD И MUSIC ---
    selected_video_label = ft.Text("Видео не выбрано", color="gray")
    selected_music_label = ft.Text("Музыка не выбрана", color="gray")

    def scan_download_folder(e):
        query = video_search_input.value.lower()
        video_list_view.controls.clear()
        
        if os.path.exists(DOWNLOAD_DIR):
            files = [f for f in os.listdir(DOWNLOAD_DIR) if f.lower().endswith(('.mp4', '.mov', '.mkv'))]
            for f in files:
                if query in f.lower():
                    full_p = os.path.join(DOWNLOAD_DIR, f)
                    video_list_view.controls.append(
                        ft.ListTile(
                            title=ft.Text(f),
                            subtitle=ft.Text("Папка: Download"),
                            on_click=lambda ev, p=full_p, name=f: set_video(p, name)
                        )
                    )
        page.update()

    def set_video(path, name):
        nonlocal selected_video_path
        selected_video_path = path
        selected_video_label.value = f"📹 Выбрано: {name}"
        selected_video_label.color = "cyan"
        page.update()

    def scan_music_folder(e):
        query = music_search_input.value.lower()
        music_list_view.controls.clear()
        
        if os.path.exists(MUSIC_DIR):
            files = [f for f in os.listdir(MUSIC_DIR) if f.lower().endswith(('.mp3', '.wav', '.aac'))]
            for f in files:
                if query in f.lower():
                    full_p = os.path.join(MUSIC_DIR, f)
                    music_list_view.controls.append(
                        ft.ListTile(
                            title=ft.Text(f),
                            subtitle=ft.Text("Папка: Music"),
                            on_click=lambda ev, p=full_p, name=f: set_music(p, name)
                        )
                    )
        page.update()

    def set_music(path, name):
        nonlocal selected_music_path
        selected_music_path = path
        selected_music_label.value = f"🎵 Выбрана музыка: {name}"
        selected_music_label.color = "cyan"
        page.update()

    video_search_input = ft.TextField(label="🔍 Поиск в папке Download...", on_change=scan_download_folder)
    video_list_view = ft.ListView(height=120, spacing=5)

    music_search_input = ft.TextField(label="🔍 Поиск в папке Music...", on_change=scan_music_folder)
    music_list_view = ft.ListView(height=120, spacing=5)

    # --- 3. НАСТРОЙКИ ОБРАБОТКИ И РАЗРЕШЕНИЯ ---
    speed_options = [
        ft.dropdown.Option("0.1", "0.1x (Замедление)"),
        ft.dropdown.Option("0.2", "0.2x (Замедление)"),
        ft.dropdown.Option("0.5", "0.5x (Замедление)"),
        ft.dropdown.Option("1.0", "1.0x (Обычная)"),
        ft.dropdown.Option("2.0", "2.0x (Ускорение)"),
        ft.dropdown.Option("4.0", "4.0x (Ускорение)"),
        ft.dropdown.Option("7.0", "7.0x (Ускорение)"),
    ]

    s1 = ft.Dropdown(width=180, value="0.2", options=speed_options)
    s2 = ft.Dropdown(width=180, value="1.0", options=speed_options)
    s3 = ft.Dropdown(width=180, value="0.1", options=speed_options)
    s4 = ft.Dropdown(width=180, value="2.0", options=speed_options)
    s5 = ft.Dropdown(width=180, value="0.5", options=speed_options)

    resolution_dropdown = ft.Dropdown(
        width=250,
        value="1080",
        label="Качество / Разрешение",
        options=[
            ft.dropdown.Option("1080", "1080p (1920x1080)"),
            ft.dropdown.Option("2700", "2.7K (2704x1520)"),
            ft.dropdown.Option("4k", "4K (3840x2160)"),
        ]
    )

    boomerang_check = ft.Checkbox(label="Эффект Бумеранг (реверс)", value=False)

    # --- 4. РЕАЛЬНЫЙ ДВИЖОК ОБРАБОТКИ ЧЕРЕЗ FFmpeg ---
    def start_ffmpeg_process(e):
        if not selected_video_path or not os.path.exists(selected_video_path):
            process_status.value = "❌ Ошибка: выберите видеофайл из списка!"
            process_status.color = "red"
            page.update()
            return

        progress_bar.visible = True
        progress_bar.value = 0
        process_status.value = "⚙️ Запуск FFmpeg..."
        process_status.color = "cyan"
        page.update()

        def render_thread():
            try:
                output_file = os.path.join(DOWNLOAD_DIR, "render_output.mp4")
                
                # Вычисление разрешения
                res_val = resolution_dropdown.value
                scale_filter = "scale=1920:1080"
                if res_val == "2700":
                    scale_filter = "scale=2704:1520"
                elif res_val == "4k":
                    scale_filter = "scale=3840:2160"

                # Сборка параметров скорости (setpts)
                speeds = [float(s1.value), float(s2.value), float(s3.value), float(s4.value), float(s5.value)]
                
                # Пример команды FFmpeg для рендера с прогрессом
                cmd = [
                    "ffmpeg", "-y", "-i", selected_video_path,
                    "-vf", f"{scale_filter},setpts={1/speeds[0]}*PTS",
                    "-c:v", "libx264", "-crf", "23", output_file
                ]

                process = subprocess.Popen(cmd, stderr=subprocess.PIPE, universal_newlines=True)

                # Вычисление % выполнения из логов FFmpeg
                for line in process.stderr:
                    if "time=" in line:
                        time_match = re.search(r'time=(\d+):(\d+):(\d+\.\d+)', line)
                        if time_match:
                            hours, mins, secs = map(float, time_match.groups())
                            total_secs = hours * 3600 + mins * 60 + secs
                            # Условный рассчет процента (пример на 30 сек роликах)
                            pct = min(total_secs / 30.0, 1.0)
                            progress_bar.value = pct
                            process_status.value = f"⚙️ Обработка: {int(pct * 100)}%"
                            page.update()

                process.wait()
                progress_bar.value = 1.0
                process_status.value = f"✅ Готово! Сохранено: Download/render_output.mp4"
                process_status.color = "green"
            except Exception as ex:
                process_status.value = f"❌ Ошибка рендера: {ex}"
                process_status.color = "red"
            
            page.update()

        threading.Thread(target=render_thread).start()

    # --- ИНИЦИАЛИЗАЦИЯ СТРАНИЦЫ ---
    scan_download_folder(None)
    scan_music_folder(None)

    page.add(
        ft.Container(height=30),
        ft.Text("Alex Slow Mo Studio", size=26, weight="bold", color="#00d2ff"),
        ft.Divider(height=10, color="transparent"),

        # Управление GoPro
        ft.Container(
            content=ft.Column([
                ft.Text("Управление GoPro", size=18, weight="bold"),
                status_text,
                ft.Row([
                    ft.ElevatedButton("Проверить", on_click=check_connection),
                    rec_btn,
                ]),
                ft.ElevatedButton("📥 Скачать видео в Download", on_click=download_last_video)
            ]),
            padding=15, border_radius=10, bgcolor="#1e1e24"
        ),

        # Поиск видео
        ft.Container(
            content=ft.Column([
                ft.Text("Выбор видео (Папка Download)", size=18, weight="bold"),
                selected_video_label,
                video_search_input,
                video_list_view
            ]),
            padding=15, border_radius=10, bgcolor="#1e1e24"
        ),

        # Поиск музыки
        ft.Container(
            content=ft.Column([
                ft.Text("Выбор музыки (Папка Music)", size=18, weight="bold"),
                selected_music_label,
                music_search_input,
                music_list_view
            ]),
            padding=15, border_radius=10, bgcolor="#1e1e24"
        ),

        # Настройки скорости и рендера
        ft.Container(
            content=ft.Column([
                ft.Text("Настройка скорости 5 отрезков", size=18, weight="bold"),
                ft.Row([ft.Text("1:"), s1, ft.Text("2:"), s2]),
                ft.Row([ft.Text("3:"), s3, ft.Text("4:"), s4]),
                ft.Row([ft.Text("5:"), s5]),
                ft.Divider(height=10, color="gray"),
                resolution_dropdown,
                boomerang_check,
                ft.Divider(height=10, color="transparent"),
                progress_bar,
                process_status,
                ft.ElevatedButton(
                    "Обработать и сохранить", 
                    bgcolor="#00d2ff", 
                    color="black",
                    on_click=start_ffmpeg_process
                )
            ]),
            padding=15, border_radius=10, bgcolor="#1e1e24"
        )
    )

ft.app(target=main)
