from kivymd.uix.screen import MDScreen
from kivymd.uix.list import OneLineListItem
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.boxlayout import MDBoxLayout

from services import add_service, get_services, update_service


class ServicesScreen(MDScreen):
    def on_enter(self):
        self.selected_service_id = None
        self.selected_price_type = "engång"
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()

        layout = MDBoxLayout(orientation="vertical", padding=10, spacing=10)

        self.name_input = MDTextField(hint_text="Tjänst")
        self.desc_input = MDTextField(hint_text="Beskrivning")
        self.price_input = MDTextField(hint_text="Pris")

        # Dropdown för pristyp
        self.price_type_btn = MDRaisedButton(
            text=f"Pristyp: {self.selected_price_type}",
            on_release=self.open_menu
        )

        menu_items = [
            {"text": "engång", "on_release": lambda x="engång": self.set_price_type(x)},
            {"text": "timme", "on_release": lambda x="timme": self.set_price_type(x)},
        ]

        self.menu = MDDropdownMenu(
            caller=self.price_type_btn,
            items=menu_items,
            width_mult=3,
        )

        self.save_btn = MDRaisedButton(
            text="Spara tjänst",
            on_release=lambda x: self.save_service()
        )

        self.list_layout = MDBoxLayout(orientation="vertical", spacing=5)

        back_btn = MDRaisedButton(
            text="Tillbaka",
            on_release=lambda x: self.go_back()
        )

        layout.add_widget(self.name_input)
        layout.add_widget(self.desc_input)
        layout.add_widget(self.price_input)
        layout.add_widget(self.price_type_btn)
        layout.add_widget(self.save_btn)
        layout.add_widget(self.list_layout)
        layout.add_widget(back_btn)

        self.add_widget(layout)

        self.load_services()

    # Dropdown
    def open_menu(self, *args):
        self.menu.open()

    def set_price_type(self, value):
        self.selected_price_type = value
        self.price_type_btn.text = f"Pristyp: {value}"
        self.menu.dismiss()

    # Spara / uppdatera
    def save_service(self):
        try:
            name = self.name_input.text
            desc = self.desc_input.text
            price = float(self.price_input.text)

            if self.selected_service_id:
                update_service(
                    self.selected_service_id,
                    name,
                    desc,
                    price,
                    self.selected_price_type
                )
            else:
                add_service(
                    name,
                    desc,
                    price,
                    self.selected_price_type
                )

            self.reset_form()
            self.load_services()

        except:
            print("Fel input")

    def load_services(self):
        self.list_layout.clear_widgets()

        services = get_services()

        for s in services:
            item = OneLineListItem(
                text=f"{s.name} ({s.price_type}) - {s.price} kr",
                on_release=lambda x, service=s: self.edit_service(service)
            )
            self.list_layout.add_widget(item)

    # Klick → redigera
    def edit_service(self, service):
        self.selected_service_id = service.id
        self.name_input.text = service.name
        self.desc_input.text = service.description
        self.price_input.text = str(service.price)

        self.selected_price_type = service.price_type
        self.price_type_btn.text = f"Pristyp: {service.price_type}"

    def reset_form(self):
        self.selected_service_id = None
        self.name_input.text = ""
        self.desc_input.text = ""
        self.price_input.text = ""
        self.selected_price_type = "engång"
        self.price_type_btn.text = "Pristyp: engång"

    def go_back(self):
        self.manager.current = "home"