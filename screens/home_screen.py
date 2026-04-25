from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout

from services import get_services

class HomeScreen(MDScreen):
    def on_enter(self):
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()

        layout = MDBoxLayout(
            orientation="vertical",
            padding=20,
            spacing=20
        )

        # Titel
        title = MDLabel(
            text="Offert App",
            halign="center",
            font_style="H4"
        )

        # Info
        services = get_services()
        info = MDLabel(
            text=f"Du har {len(services)} tjänster sparade",
            halign="center"
        )

        # Knappar
        btn_quote = MDRaisedButton(
            text="Skapa offert",
            pos_hint={"center_x": 0.5},
            on_release=lambda x: self.go_to_quote()
        )

        btn_services = MDRaisedButton(
            text="Hantera tjänster",
            pos_hint={"center_x": 0.5},
            on_release=lambda x: self.go_to_services()
        )

        btn_settings = MDRaisedButton(
            text="Inställningar",
            pos_hint={"center_x": 0.5},
            on_release=lambda x: self.go_to_settings()
        )

        layout.add_widget(title)
        layout.add_widget(info)
        layout.add_widget(btn_quote)
        layout.add_widget(btn_services)
        layout.add_widget(btn_settings)

        self.add_widget(layout)

    def go_to_services(self):
        self.manager.current = "services"

    def go_to_quote(self):
        self.manager.current = "quote"
    
    def go_to_settings(self):
        self.manager.current = "settings"