from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel

from settings import load_settings, save_settings


class SettingsScreen(MDScreen):

    def on_enter(self):
        self.name = "settings"  # Set the screen name as a string
        self.settings = load_settings()
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()

        layout = MDBoxLayout(orientation="vertical", padding=10, spacing=10)

        self.name_field = MDTextField(hint_text="Företagsnamn", text=self.settings["company_name"])
        self.address = MDTextField(hint_text="Adress", text=self.settings["address"])
        self.phone = MDTextField(hint_text="Telefon", text=self.settings["phone"])
        self.email = MDTextField(hint_text="Email", text=self.settings["email"])

        self.moms = MDTextField(
            hint_text="MOMS (%)",
            text=str(self.settings.get("moms", 25))
        )

        self.payment_info = MDTextField(
            hint_text="Betalningsinfo (konto, swish etc)",
            text=self.settings.get("payment_info", "")
        )

        self.payment_terms = MDTextField(
            hint_text="Betalningsvillkor",
            text=self.settings.get("payment_terms", "")
        )

        save_btn = MDRaisedButton(text="Spara", on_release=lambda x: self.save())
        back_btn = MDRaisedButton(text="Tillbaka", on_release=lambda x: self.go_back())

        layout.add_widget(self.name_field)
        layout.add_widget(self.address)
        layout.add_widget(self.phone)
        layout.add_widget(self.email)
        layout.add_widget(self.moms)
        layout.add_widget(self.payment_info)
        layout.add_widget(self.payment_terms)
        layout.add_widget(save_btn)
        layout.add_widget(back_btn)

        self.add_widget(layout)

    def save(self):
        data = {
            "company_name": self.name_field.text,
            "address": self.address.text,
            "phone": self.phone.text,
            "email": self.email.text,
            "logo_path": self.settings.get("logo_path", ""),
            "moms": float(self.moms.text or 25),
            "payment_info": self.payment_info.text,
            "payment_terms": self.payment_terms.text,
            "qr_path": self.settings.get("qr_path", "")
        }

        save_settings(data)

    def go_back(self):
        self.manager.current = "home"
