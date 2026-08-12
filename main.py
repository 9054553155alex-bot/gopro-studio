        else:
            video_dd.options = [ft.dropdown.Option("none", "Нет видео в Download")]
            video_dd.value = "none"

        music_dd.options = [ft.dropdown.Option("no_music", "Без музыки")] + [ft.dropdown.Option(f, f) for f in m_list]
        music_dd.value = "no_music"

        page.update()

    card_files = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Text("Файлы для обработки", weight="bold", size=16),
                ft.IconButton(icon=ft.icons.REFRESH, icon_color=CYAN_ACCENT, on_click=scan_files, tooltip="Обновить список")
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=4),
            video_dd,
            ft.Container(height=16),
            music_dd,
        ], spacing=0),
        bgcolor=CARD_BG,
        padding=16,
        border_radius=12,
    )

    # 3. НАСТРОЙКА СКОРОСТИ
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
        height=45,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=20),
            text_style=ft.TextStyle(weight="bold")
        )
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

    header = ft.Text("Alex Slow Mo Studio", size=22, weight="bold", color=CYAN_ACCENT)

    page.add(
        header,
        card_gopro,
        card_files,
        card_settings,
        progress_bar
    )

    # Первичная загрузка списка файлов
    scan_files()

ft.app(target=main)
