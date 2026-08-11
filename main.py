import flet as ft
import requests

def main(page: ft.Page):
    page.title = "Alex Slow Mo"
    page.theme_mode = ft.ThemeMode.DARK
    
    status_text = ft.Text("Подключи GoPro к Wi-Fi", color="yellow")

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

    page.add(
        ft.Text("Alex Slow Mo Studio", size=30, weight="bold", color="#00d2ff"),
        status_text,
        ft.ElevatedButton("Проверить камеру", on_click=check_connection),
        ft.ElevatedButton("Начать запись (🔴)", bgcolor="red", color="white")
    )

ft.app(target=main)
