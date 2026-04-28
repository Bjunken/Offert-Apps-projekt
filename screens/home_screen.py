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

        # 🏠 Titel (valfri, kan stylas senare)
        layout.add_widget(
            MDRaisedButton(
                text="Skapa Offert",
                on_release=lambda x: self.go_to("quote")
            )
        )

        layout.add_widget(
            MDRaisedButton(
                text="Tjänster",
                on_release=lambda x: self.go_to("services")
            )
        )

        layout.add_widget(
            MDRaisedButton(
                text="Material",
                on_release=lambda x: self.go_to("materials")
            )
        )

        layout.add_widget(
            MDRaisedButton(
                text="Inställningar",
                on_release=lambda x: self.go_to("settings")
            )
        )

        self.add_widget(layout)

    def go_to(self, screen_name):
        self.manager.current = screen_name