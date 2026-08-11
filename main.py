import flet as ft
import requests
import os
import subprocess
import re
import threading

DOWNLOAD_DIR = "/storage/emulated/0/Download"
MUSIC_DIR = "/storage/emulated/0/Music"

def main(page: ft.Page):
    page.title = "Alex Slow Mo Studio"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20

    is_recording = False
    status_text = ft.Text("Подключи GoPro к Wi-Fi", color="yellow", size=15)
    process_status = ft.Text("Готов к работе", color="gray", size=14)
    progress_bar = ft.ProgressBar(value=0, width=400, visible=False)

    # 1. GOPRO: СТАП/СТОП И СКАЧИВАНИЕ
    def check_connection(e):
        try:
            resp = requests.get("http://10.5.5.9/gp/gpControl", timeout=2)
            status_text.value = "✅ Камера готова!" if resp.status_code == 200 else "⚠️ Ошибка подключения"
            status_text.color = "green" if resp.status_code == 200 else "orange"
        except:
            status_text.value = "❌ Нет связи с GoPro"
            status_text.color = "red"
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
            status_text.color = "red"
        page.update()

    def download_last_video(e):
        process_status.value = "⏳ Запрос списка файлов..."
        process_status.color = "yellow"
        page.update()
        try:
            media_resp = requests.get("http://10.5.5.9:8080/gp/gpMediaList", timeout=4)
            if media_resp.status_code == 200:
                data = media_resp.json()
                media_list = data.get('media', [])
                if not media_list:
                    process_status.value = "⚠️ Карта памяти пуста"
                    page.update()
                    return
                
                last_folder_data = media_list[-1]
                folder_name = last_folder_data.get('directory', last_folder_data.get('d', '100GOPRO'))
                files_list = last_folder_data.get('fs', [])
                if not files_list:
                    process_status.value = "⚠️ Файлы не найдены"
                    page.update()
                    return
                
                last_file = files_list[-1].get('n', files_list[-1].get('name'))
                file_url = f"http://10.5.5.9:8080/videos/DCIM/{folder_name}/{last_file}"
                
                process_status.value = f"📥 Скачивание {last_file}..."
                page.update()
                
                if not os.path.exists(DOWNLOAD_DIR):
                    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

                save_path = os.path.join(DOWNLOAD_DIR, last_file)
                r = requests.get(file_url, timeout=60)
                with open(save_path, 'wb') as f:
                    f.write(r.content)
                    
                process_status.value = f"✅ Скачано в Download/{last_file}"
                process_status.color = "green"
                refresh_file_lists(None)
            else:
                process_status.value = "⚠️ Ошибка HTTP от GoPro"
        except Exception as err:
            process_status.value = f"❌ Ошибка скачивания: {err}"
            process_status.color = "red"
        page.update()

    rec_btn = ft.ElevatedButton("НАЧАТЬ ЗАПИСЬ", bgcolor="green", color="white", on_click=toggle_record)

    # 2. СКАНЕР ПАПОК DOWNLOAD И MUSIC
    video_dropdown = ft.Dropdown(label="Выбери видео из Download", width=340)
    music_dropdown = ft.Dropdown(label="Выбери трек из Music (необязательно)", width=340)

    def refresh_file_lists(e):
        # Сканируем видео
        video_dropdown.options.clear()
        if os.path.exists(DOWNLOAD_DIR):
            v_files = [f for f in os.listdir(DOWNLOAD_DIR) if f.lower().endswith(('.mp4', '.mov', '.mkv'))]
            for vf in v_files:
                video_dropdown.options.append(ft.dropdown.Option(vf))
            if v_files:
                video_dropdown.value = v_files[0]
        
        # Сканируем музыку
        music_dropdown.options.clear()
        music_dropdown.options.append(ft.dropdown.Option("", "Без музыки"))
        if os.path.exists(MUSIC_DIR):
            m_files = [f for f in os.listdir(MUSIC_DIR) if f.lower().endswith(('.mp3', '.wav', '.aac', '.m4a'))]
            for mf in m_files:
                music_dropdown.options.append(ft.dropdown.Option(mf))
        music_dropdown.value = ""
        page.update()

    # 3. НАСТРОЙКИ СКОРОСТИ И РАЗРЕШЕНИЯ
    speed_options = [
        ft.dropdown.Option("0.1", "0.1x (Замедл)"),
        ft.dropdown.Option("0.2", "0.2x (Замедл)"),
        ft.dropdown.Option("0.5", "0.5x (Замедл)"),
        ft.dropdown.Option("1.0", "1.0x (Обычн)"),
        ft.dropdown.Option("2.0", "2.0x (Ускор)"),
        ft.dropdown.Option("5.0", "5.0x (Ускор)"),
        ft.dropdown.Option("7.0", "7.0x (Ускор)"),
    ]

    s1 = ft.Dropdown(width=140, value="0.2", options=speed_options)
    s2 = ft.Dropdown(width=140, value="1.0", options=speed_options)
    s3 = ft.Dropdown(width=140, value="0.1", options=speed_options)
    s4 = ft.Dropdown(width=140, value="2.0", options=speed_options)
    s5 = ft.Dropdown(width=140, value="0.5", options=speed_options)

    resolution_dropdown = ft.Dropdown(
        width=250, value="1080", label="Разрешение",
        options=[
            ft.dropdown.Option("1080", "1080p (1920x1080)"),
            ft.dropdown.Option("2700", "2.7K (2704x1520)"),
            ft.dropdown.Option("4k", "4K (3840x2160)"),
        ]
    )

    # 4. РЕАЛЬНЫЙ РЕНДЕР FFMPEG С ПРОГРЕСС-БАРОМ
    def start_ffmpeg_process(e):
        if not video_dropdown.value:
            process_status.value = "❌ Ошибка: Выбери видео из списка!"
            process_status.color = "red"
            page.update()
            return

        in_video = os.path.join(DOWNLOAD_DIR, video_dropdown.value)
        out_video = os.path.join(DOWNLOAD_DIR, f"slowmo_{video_dropdown.value}")

        progress_bar.visible = True
        progress_bar.value = 0
        process_status.value = "⚙️ Запуск рендера..."
        process_status.color = "cyan"
        page.update()

        def render_thread():
            try:
                res_val = resolution_dropdown.value
                scale = "scale=1920:1080"
                if res_val == "2700":
                    scale = "scale=2704:1520"
                elif res_val == "4k":
                    scale = "scale=3840:2160"

                # Базовая команда FFmpeg
                cmd = [
                    "ffmpeg", "-y", "-i", in_video,
                    "-vf", f"{scale},setpts={1/float(s1.value)}*PTS",
                    "-c:v", "libx264", "-preset", "ultrafast", out_video
                ]

                proc = subprocess.Popen(cmd, stderr=subprocess.PIPE, universal_newlines=True)

                for line in proc.stderr:
                    if "time=" in line:
                        m = re.search(r'time=(\d+):(\d+):(\d+\.\d+)', line)
                        if m:
                            h, mn, s = map(float, m.groups())
                            cur_sec = h * 3600 + mn * 60 + s
                            pct = min(cur_sec / 15.0, 1.0)  # Расчет %
                            progress_bar.value = pct
                            process_status.value = f"⚙️ Обработка: {int(pct * 100)}%"
                            page.update()

                proc.wait()
                progress_bar.value = 1.0
                process_status.value = f"✅ Готово! Сохранено: slowmo_{video_dropdown.value}"
                process_status.color = "green"
            except Exception as ex:
                process_status.value = f"❌ Ошибка рендера: {ex}"
                process_status.color = "red"
            page.update()

        threading.Thread(target=render_thread).start()

    # Первичная загрузка списков
    refresh_file_lists(None)

    # ИНТЕРФЕЙС
    page.add(
        ft.Container(height=30),
        ft.Text("Alex Slow Mo Studio", size=26, weight="bold", color="#00d2ff"),
        ft.Divider(height=10, color="transparent"),

        ft.Container(
            content=ft.Column([
                ft.Text("Управление GoPro", size=18, weight="bold"),
                status_text,
                ft.Row([
                    ft.ElevatedButton("Проверить", on_click=check_connection),
                    rec_btn,
                ]),
                ft.ElevatedButton("📥 Скачать последнее видео", on_click=download_last_video)
            ]),
            padding=15, border_radius=10, bgcolor="#1e1e24"
        ),

        ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Файлы для обработки", size=18, weight="bold"),
                    ft.IconButton(icon=ft.icons.REFRESH, on_click=refresh_file_lists)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                video_dropdown,
                music_dropdown,
            ]),
            padding=15, border_radius=10, bgcolor="#1e1e24"
        ),

        ft.Container(
            content=ft.Column([
                ft.Text("Настройка скорости 5 отрезков", size=18, weight="bold"),
                ft.Row([ft.Text("1:"), s1, ft.Text("2:"), s2]),
                ft.Row([ft.Text("3:"), s3, ft.Text("4:"), s4]),
                ft.Row([ft.Text("5:"), s5]),
                ft.Divider(height=10, color="gray"),
                resolution_dropdown,
                ft.Checkbox(label="Эффект Бумеранг (реверс)", value=False),
                ft.Divider(height=10, color="transparent"),
                progress_bar,
                process_status,
                ft.ElevatedButton("Обработать и сохранить", bgcolor="#00d2ff", color="black", on_click=start_ffmpeg_process)
            ]),
            padding=15, border_radius=10, bgcolor="#1e1e24"
        )
    )

ft.app(target=main)
