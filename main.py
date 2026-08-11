import flet as ft
import requests
import os

def main(page: ft.Page):
    page.title = "Alex Slow Mo Studio"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20

    is_recording = False
    download_dir = "/storage/emulated/0/Download"

    status_text = ft.Text("Подключи GoPro к Wi-Fi", color="yellow", size=15)
    process_status = ft.Text("Готов к работе", color="gray", size=14)

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
                
                if not os.path.exists(download_dir):
                    os.makedirs(download_dir, exist_ok=True)

                save_path = os.path.join(download_dir, last_file)
                r = requests.get(file_url, timeout=60)
                with open(save_path, 'wb') as f:
                    f.write(r.content)
                    
                video_input.value = last_file
                process_status.value = f"✅ Скачано в Download/{last_file}"
                process_status.color = "green"
            else:
                process_status.value = "⚠️ Ошибка HTTP от GoPro"
        except Exception as err:
            process_status.value = f"❌ Ошибка скачивания: {err}"
            process_status.color = "red"
        page.update()

    rec_btn = ft.ElevatedButton("НАЧАТЬ ЗАПИСЬ", bgcolor="green", color="white", on_click=toggle_record)

    # 2. ФАЙЛЫ
    video_input = ft.TextField(label="Имя видеофайла (в папке Download)", value="input.mp4")
    music_input = ft.TextField(label="Имя музыки (в папке Music, необязательно)", value="")

    # 3. НАСТРОЙКИ ОБРАБОТКИ
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

    def process_video(e):
        filename = video_input.value.strip()
        if not filename:
            process_status.value = "❌ Введите имя видеофайла!"
            process_status.color = "red"
        else:
            full_path = os.path.join(download_dir, filename)
            process_status.value = f"⚙️ Файл подготовлен: {full_path}"
            process_status.color = "cyan"
        page.update()

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
                ft.Text("Файлы для обработки", size=18, weight="bold"),
                video_input,
                music_input,
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
                process_status,
                ft.ElevatedButton("Обработать и сохранить", bgcolor="#00d2ff", color="black", on_click=process_video)
            ]),
            padding=15, border_radius=10, bgcolor="#1e1e24"
        )
    )

ft.app(target=main)
