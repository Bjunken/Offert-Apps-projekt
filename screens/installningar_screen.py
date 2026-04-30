from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel


class InstallningarScreen(MDScreen):

    def on_enter(self):
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()

        layout = MDBoxLayout(
            orientation="vertical",
            padding=20,
            spacing=20
        )

        layout.add_widget(MDLabel(
            text="Inställningar",
            bold=True,
            font_size=20,
            halign="center",
            size_hint_y=None,
            height=40
        ))

        layout.add_widget(MDLabel(
            text="Coming Soon",
            font_size=16,
            halign="center",
            theme_text_color="Secondary"
        ))

        layout.add_widget(MDRaisedButton(
            text="Tillbaka",
            pos_hint={"center_x": 0.5},
            size_hint_x=0.5,
            on_release=lambda x: self.go_back()
        ))

        self.add_widget(layout)

    def go_back(self):
        self.manager.current = "home"