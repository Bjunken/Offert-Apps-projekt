from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton


class HomeScreen(MDScreen):

    def on_enter(self):
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()

        layout = MDBoxLayout(
            orientation="vertical",
            padding=20,
            spacing=15
        )

        buttons = [
            ("Skapa Offert",        "quote"),
            ("Gamla Offerter",      "gamla_offerter"),
            ("Tjänster",            "services"),
            ("Material",            "materials"),
            ("Företags Information","settings"),
            ("Inställningar",       "installningar"),
        ]

        for text, screen in buttons:
            layout.add_widget(MDRaisedButton(
                text=text,
                on_release=lambda x, s=screen: self.go_to(s)
            ))

        self.add_widget(layout)

    def go_to(self, screen_name):
        self.manager.current = screen_name