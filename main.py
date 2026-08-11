import flet as ft
import requests
import os
import threading
import cv2

GOPRO_IP = "10.5.5.9"

def main(page: ft.Page):
    page.title = "Alex Slow Mo Studio"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20

    APP_DIR = page.client_storage.get("app_dir") or "/storage/emulated/0/Download"

    gopro_status = ft.Text("Статус GoPro: Не подключено", color="gray")
    process_status = ft.Text("Готов к работе", color="gray", size=14)
    progress_bar = ft.ProgressBar(value=0, width=400, visible=False)

    # 1. ПОЛЯ ВВОДА ФАЙЛОВ
    file_name_input = ft.TextField(
        label="Имя видеофайла (в папке Download)",
        hint_text="GX011011.MP4",
        width=350,
        value="GX011011.MP4"
    )

    music_name_input = ft.TextField(
        label="Имя аудиофайла (в папке Music или Download)",
        hint_text="track.mp3 (оставь пустым, если без музыки)",
        width=350,
        value=""
    )

    # 2. БЛОК GOPRO
    def check_gopro_connection(e=None):
        try:
            res = requests.get(f"http://{GOPRO_IP}:8080/gp/gpControl/status", timeout=3)
            if res.status_code == 200:
                gopro_status.value = "Статус GoPro: ✅ Подключено"
                gopro_status.color = "green"
            else:
                gopro_status.value = f"Статус GoPro: ⚠️ Ошибка {res.status_code}"
                gopro_status.color = "orange"
        except Exception:
            gopro_status.value = "Статус GoPro: ❌ Нет связи (Проверь Wi-Fi/VPN)"
            gopro_status.color = "red"
        page.update()

    def download_last_video(e):
        def worker():
            process_status.value = "⏳ Запрос списка файлов..."
            process_status.color = "cyan"
            page.update()
            try:
                res = requests.get(f"http://{GOPRO_IP}:8080/gp/gpMediaList", timeout=4)
                data = res.json()
                directory = data['media'][0]['directory']
                last_file = data['media'][0]['fs'][-1]['n']

                download_url = f"http://{GOPRO_IP}:8080/videos/DCIM/{directory}/{last_file}"
                local_path = os.path.join(APP_DIR, last_file)

                process_status.value = f"⏳ Скачивание {last_file}..."
                page.update()

                with requests.get(download_url, stream=True) as r:
                    r.raise_for_status()
                    with open(local_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=1024*1024):
                            f.write(chunk)

                file_name_input.value = last_file
                process_status.value = f"✅ Скачано: {last_file}"
                process_status.color = "green"
            except Exception as ex:
                process_status.value = f"❌ Ошибка скачивания: {ex}"
                process_status.color = "red"
            page.update()
        threading.Thread(target=worker).start()

    # 3. НАСТРОЙКИ СКОРОСТИ
    speed_options = [
        ft.dropdown.Option("0.1", "0.1x (Замедл)"),
        ft.dropdown.Option("0.2", "0.2x (Замедл)"),
        ft.dropdown.Option("0.5", "0.5x (Замедл)"),
        ft.dropdown.Option("1.0", "1.0x (Обычн)"),
        ft.dropdown.Option("2.0", "2.0x (Ускор)"),
        ft.dropdown.Option("5.0", "5.0x (Ускор)"),
    ]

    s1 = ft.Dropdown(width=140, value="2.0", options=speed_options)
    s2 = ft.Dropdown(width=140, value="2.0", options=speed_options)
    s3 = ft.Dropdown(width=140, value="0.1", options=speed_options)
    s4 = ft.Dropdown(width=140, value="0.2", options=speed_options)
    s5 = ft.Dropdown(width=140, value="1.0", options=speed_options)

    resolution_dropdown = ft.Dropdown(
        width=250, value="1080", label="Разрешение",
        options=[
            ft.dropdown.Option("1080", "1080p (1920x1080)"),
            ft.dropdown.Option("2700", "2.7K (2704x1520)"),
            ft.dropdown.Option("4k", "4K (3840x2160)"),
        ]
    )

    boomerang_check = ft.Checkbox(label="Эффект Бумеранг (реверс)", value=True)

    # 4. ОБРАБОТКА И РЕНДЕР
    def run_rendering(filename, music_filename):
        try:
            possible_video_paths = [
                os.path.join(APP_DIR, filename),
                f"/storage/emulated/0/Download/{filename}",
                f"/sdcard/Download/{filename}"
            ]

            video_path = None
            for path in possible_video_paths:
                if os.path.exists(path):
                    video_path = path
                    break

            if not video_path:
                process_status.value = f"❌ Видео {filename} не найдено!"
                process_status.color = "red"
                progress_bar.visible = False
                page.update()
                return

            out_path = os.path.join(APP_DIR, "slowmo_result.mp4")

            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                process_status.value = f"❌ Не удалось открыть видео:\n{video_path}"
                process_status.color = "red"
                progress_bar.visible = False
                page.update()
                return

            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS) or 30.0

            res_val = resolution_dropdown.value
            target_w, target_h = 1920, 1080
            if res_val == "2700":
                target_w, target_h = 2704, 1520
            elif res_val == "4k":
                target_w, target_h = 3840, 2160

            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(out_path, fourcc, fps, (target_w, target_h))

            speeds = [float(s1.value), float(s2.value), float(s3.value), float(s4.value), float(s5.value)]
            seg_frames = max(1, total_frames // 5)
            
            processed = 0
            frames_cache = []

            for seg_idx in range(5):
                speed = speeds[seg_idx]
                step = speed
                
                start_f = seg_idx * seg_frames
                end_f = (seg_idx + 1) * seg_frames if seg_idx < 4 else total_frames
                
                curr = float(start_f)
                while curr < end_f:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, int(curr))
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    resized = cv2.resize(frame, (target_w, target_h))
                    out.write(resized)
                    
                    if boomerang_check.value:
                        frames_cache.append(resized)

                    curr += step
                    processed += 1
                    
                    pct = min(processed / max(1, total_frames), 0.9)
                    progress_bar.value = pct
                    process_status.value = f"⚙️ Обработка видео: {int(pct * 100)}%"
                    page.update()

            if boomerang_check.value and frames_cache:
                process_status.value = "⚙️ Запись реверса..."
                page.update()
                for f in reversed(frames_cache):
                    out.write(f)

            cap.release()
            out.release()

            progress_bar.value = 1.0
            msg = "✅ Готово! Видео сохранено в Download/slowmo_result.mp4"
            if music_filename:
                msg += f"\n🎵 Музыка записана в настройки для склейки: {music_filename}"
            
            process_status.value = msg
            process_status.color = "green"
        except Exception as ex:
            process_status.value = f"❌ Ошибка рендера: {ex}"
            process_status.color = "red"

        page.update()

    def start_processing(e):
        filename = file_name_input.value.strip()
        music_filename = music_name_input.value.strip()

        if not filename:
            process_status.value = "❌ Укажи имя видеофайла!"
            process_status.color = "red"
            page.update()
            return

        progress_bar.visible = True
        progress_bar.value = 0.05
        process_status.value = "⚙️ Запуск обработки..."
        process_status.color = "cyan"
        page.update()

        threading.Thread(target=run_rendering, args=(filename, music_filename)).start()

    # ИНТЕРФЕЙС
    page.add(
        ft.Container(height=10),
        ft.Text("Alex Slow Mo Studio", size=24, weight="bold", color="#00d2ff"),
        ft.Divider(height=10, color="transparent"),

        ft.Container(
            content=ft.Column([
                ft.Text("Управление GoPro", size=18, weight="bold"),
                gopro_status,
                ft.Row([
                    ft.ElevatedButton("Проверить связь", on_click=check_gopro_connection),
                    ft.ElevatedButton("Скачать посл. видео", on_click=download_last_video),
                ]),
            ]),
            padding=15, border_radius=10, bgcolor="#1e1e24"
        ),

        ft.Container(
            content=ft.Column([
                ft.Text("Файлы для обработки", size=18, weight="bold"),
                file_name_input,
                music_name_input,
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
                boomerang_check,
                ft.Divider(height=10, color="transparent"),
                progress_bar,
                process_status,
                ft.ElevatedButton("Обработать и сохранить", bgcolor="#00d2ff", color="black", on_click=start_processing)
            ]),
            padding=15, border_radius=10, bgcolor="#1e1e24"
        )
    )

ft.app(target=main)
