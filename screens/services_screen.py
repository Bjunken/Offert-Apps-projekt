from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView

from services import add_service, get_services, update_service, delete_service


class ServicesScreen(MDScreen):

    def on_enter(self):
        self.selected_service_id = None
        self.price_type = "engång"  # ✅ default
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()

        root = MDBoxLayout(orientation="vertical", padding=10, spacing=10)

        # 🔽 INPUTS
        self.name_input = MDTextField(hint_text="Tjänst namn")
        self.price_input = MDTextField(hint_text="Pris")
        self.desc_input = MDTextField(hint_text="Beskrivning")

        root.add_widget(self.name_input)
        root.add_widget(self.price_input)
        root.add_widget(self.desc_input)

        # 💰 PRISTYP VAL
        price_type_layout = MDBoxLayout(size_hint_y=None, height=50, spacing=10)

        self.engang_btn = MDRaisedButton(
            text="Engång",
            on_release=lambda x: self.set_price_type("engång")
        )

        self.hour_btn = MDRaisedButton(
            text="Timpris",
            on_release=lambda x: self.set_price_type("timme")
        )

        price_type_layout.add_widget(self.engang_btn)
        price_type_layout.add_widget(self.hour_btn)

        root.add_widget(price_type_layout)

        # 🔘 SAVE
        self.save_btn = MDRaisedButton(
            text="Lägg till tjänst",
            on_release=lambda x: self.save_service()
        )
        root.add_widget(self.save_btn)

        # 📋 LISTA
        scroll = MDScrollView()

        self.list_layout = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=5
        )
        self.list_layout.bind(minimum_height=self.list_layout.setter("height"))

        scroll.add_widget(self.list_layout)
        root.add_widget(scroll)

        # 🔙
        root.add_widget(MDRaisedButton(
            text="Tillbaka",
            on_release=lambda x: self.go_back()
        ))

        self.add_widget(root)

        self.load_services()

    # 🎯 SET PRISTYP
    def set_price_type(self, ptype):
        self.price_type = ptype

        # 🔥 VISUELL FEEDBACK
        if ptype == "engång":
            self.engang_btn.md_bg_color = (0, 0.5, 1, 1)
            self.hour_btn.md_bg_color = (0.3, 0.3, 0.3, 1)
        else:
            self.hour_btn.md_bg_color = (0, 0.5, 1, 1)
            self.engang_btn.md_bg_color = (0.3, 0.3, 0.3, 1)

    # 📋 LADDA
    def load_services(self):
        self.list_layout.clear_widgets()

        for s in get_services():
            row = MDBoxLayout(size_hint_y=None, height=50, spacing=10)

            row.add_widget(MDLabel(
                text=f"{s.name} ({s.price_type}) - {s.price} kr"
            ))

            row.add_widget(MDRaisedButton(
                text="Redigera",
                on_release=lambda x, s=s: self.load_into_form(s)
            ))

            row.add_widget(MDRaisedButton(
                text="Ta bort",
                on_release=lambda x, s=s: self.remove_service(s.id)
            ))

            self.list_layout.add_widget(row)

    # ✏️ LOAD
    def load_into_form(self, service):
        self.selected_service_id = service.id

        self.name_input.text = service.name
        self.price_input.text = str(service.price)
        self.desc_input.text = service.description or ""

        self.set_price_type(service.price_type)

        self.save_btn.text = "Spara ändringar"

    # 💾 SAVE
    def save_service(self):
        name = self.name_input.text.strip()
        price_text = self.price_input.text.strip()
        description = self.desc_input.text.strip()

        if not name or not price_text:
            print("Fyll i namn och pris")
            return

        try:
            price = float(price_text)
        except:
            print("Fel pris")
            return

        if self.selected_service_id is None:
            add_service(name, price, self.price_type, description, [])
        else:
            update_service(
                self.selected_service_id,
                name,
                price,
                self.price_type,
                description,
                []
            )

        # 🔄 RESET
        self.selected_service_id = None
        self.price_type = "engång"

        self.name_input.text = ""
        self.price_input.text = ""
        self.desc_input.text = ""

        self.save_btn.text = "Lägg till tjänst"

        self.set_price_type("engång")

        self.load_services()

    # 🗑 DELETE
    def remove_service(self, service_id):
        delete_service(service_id)
        self.load_services()

    def go_back(self):
        self.manager.current = "home"