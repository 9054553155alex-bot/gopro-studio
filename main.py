import flet as ft
import requests
import os
import threading
import cv2

def main(page: ft.Page):
    page.title = "Alex Slow Mo Studio"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20

    process_status = ft.Text("Готов к работе", color="gray", size=14)
    progress_bar = ft.ProgressBar(value=0, width=400, visible=False)

    # Пути выбранных файлов
    selected_video_path = None
    selected_music_path = None

    video_label = ft.Text("Видео не выбрано", color="orange")
    music_label = ft.Text("Музыка не выбрана (без музыки)", color="gray")

    # 1. НАТИВНЫЙ ВЫБОР ФАЙЛОВ (FILE PICKER)
    def on_video_selected(e: ft.FilePickerResultEvent):
        nonlocal selected_video_path
        if e.files:
            selected_video_path = e.files[0].path
            video_label.value = f"✅ Видео: {e.files[0].name}"
            video_label.color = "green"
        page.update()

    def on_music_selected(e: ft.FilePickerResultEvent):
        nonlocal selected_music_path
        if e.files:
            selected_music_path = e.files[0].path
            music_label.value = f"🎵 Трек: {e.files[0].name}"
            music_label.color = "green"
        page.update()

    video_picker = ft.FilePicker(on_result=on_video_selected)
    music_picker = ft.FilePicker(on_result=on_music_selected)
    page.overlay.extend([video_picker, music_picker])

    # 2. НАСТРОЙКИ СКОРОСТИ И РАЗРЕШЕНИЯ
    speed_options = [
        ft.dropdown.Option("0.1", "0.1x (Замедл)"),
        ft.dropdown.Option("0.2", "0.2x (Замедл)"),
        ft.dropdown.Option("0.5", "0.5x (Замедл)"),
        ft.dropdown.Option("1.0", "1.0x (Обычн)"),
        ft.dropdown.Option("2.0", "2.0x (Ускор)"),
        ft.dropdown.Option("5.0", "5.0x (Ускор)"),
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

    boomerang_check = ft.Checkbox(label="Эффект Бумеранг (реверс)", value=False)

    # 3. ОБРАБОТКА ВИДЕО ЧЕРЕЗ OPENCV
    def run_rendering():
        try:
            out_dir = "/storage/emulated/0/Download"
            if not os.path.exists(out_dir):
                out_dir = os.path.dirname(selected_video_path)
                
            out_path = os.path.join(out_dir, "slowmo_result.mp4")

            cap = cv2.VideoCapture(selected_video_path)
            if not cap.isOpened():
                process_status.value = "❌ Ошибка: Не удалось открыть файл!"
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
                    process_status.value = f"⚙️ Обработка: {int(pct * 100)}%"
                    page.update()

            if boomerang_check.value and frames_cache:
                process_status.value = "⚙️ Запись реверса..."
                page.update()
                for f in reversed(frames_cache):
                    out.write(f)

            cap.release()
            out.release()

            progress_bar.value = 1.0
            process_status.value = f"✅ Сохранено: {out_path}"
            process_status.color = "green"
        except Exception as ex:
            process_status.value = f"❌ Ошибка рендера: {ex}"
            process_status.color = "red"

        page.update()

    def start_processing(e):
        if not selected_video_path:
            process_status.value = "❌ Сначала выбери видео файл!"
            process_status.color = "red"
            page.update()
            return

        progress_bar.visible = True
        progress_bar.value = 0.05
        process_status.value = "⚙️ Запуск обработки..."
        process_status.color = "cyan"
        page.update()

        threading.Thread(target=run_rendering).start()

    # ИНТЕРФЕЙС
    page.add(
        ft.Container(height=20),
        ft.Text("Alex Slow Mo Studio", size=24, weight="bold", color="#00d2ff"),
        ft.Divider(height=10, color="transparent"),

        ft.Container(
            content=ft.Column([
                ft.Text("Файлы для обработки", size=18, weight="bold"),
                ft.ElevatedButton("📂 Выбрать видео", on_click=lambda _: video_picker.pick_files(file_type=ft.FilePickerFileType.VIDEO)),
                video_label,
                ft.Divider(height=5, color="transparent"),
                ft.ElevatedButton("🎵 Выбрать музыку", on_click=lambda _: music_picker.pick_files(file_type=ft.FilePickerFileType.AUDIO)),
                music_label,
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
