from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDCheckbox
from kivy.uix.popup import Popup
from kivymd.uix.scrollview import MDScrollView

from services import add_service, get_services, update_service
from materials import get_materials


class ServicesScreen(MDScreen):

    def on_enter(self):
        self.selected_materials = []
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()

        layout = MDBoxLayout(orientation="vertical", padding=10, spacing=10)

        self.name_input        = MDTextField(hint_text="Tjänst namn")
        self.price_input       = MDTextField(hint_text="Pris")
        self.description_input = MDTextField(hint_text="Beskrivning")

        layout.add_widget(self.name_input)
        layout.add_widget(self.price_input)
        layout.add_widget(self.description_input)

        btn_row         = MDBoxLayout(size_hint_y=None, height=50, spacing=10)
        self.price_type = "engång"

        btn_row.add_widget(MDRaisedButton(
            text="Engång",
            on_release=lambda x: self.set_price_type("engång")
        ))
        btn_row.add_widget(MDRaisedButton(
            text="Timpris",
            on_release=lambda x: self.set_price_type("timme")
        ))
        layout.add_widget(btn_row)

        layout.add_widget(MDRaisedButton(
            text="Lägg till material",
            on_release=lambda x: self.open_material_popup()
        ))

        layout.add_widget(MDRaisedButton(
            text="Spara tjänst",
            on_release=lambda x: self.save_service()
        ))

        self.list_layout = MDBoxLayout(orientation="vertical", spacing=5)
        layout.add_widget(self.list_layout)

        layout.add_widget(MDRaisedButton(
            text="Tillbaka",
            on_release=lambda x: self.go_back()
        ))

        self.add_widget(layout)
        self.load_services()

    def set_price_type(self, ptype):
        self.price_type = ptype

    def load_services(self):
        self.list_layout.clear_widgets()

        for s in get_services():
            row = MDBoxLayout(size_hint_y=None, height=40)
            row.add_widget(MDLabel(text=f"{s.name} - {s.price} kr"))
            row.add_widget(MDRaisedButton(
                text="Redigera",
                size_hint_x=0.3,
                on_release=lambda x, s=s: self.edit_service(s)
            ))
            self.list_layout.add_widget(row)

    def save_service(self):
        name = self.name_input.text.strip()
        try:
            price = float(self.price_input.text)
        except:
            print("Pris fel")
            return

        description = self.description_input.text.strip()
        add_service(name, price, self.price_type, description, self.selected_materials)

        self.name_input.text        = ""
        self.price_input.text       = ""
        self.description_input.text = ""
        self.selected_materials     = []

        self.load_services()

    def edit_service(self, service):
        self.name_input.text        = service.name
        self.price_input.text       = str(service.price)
        self.description_input.text = service.description or ""
        self.price_type             = service.price_type
        self.selected_materials     = service.materials or []

        def save_edit(*args):
            name = self.name_input.text.strip()
            try:
                price = float(self.price_input.text)
            except:
                print("Pris fel")
                return

            update_service(
                service.id, name, price,
                self.price_type,
                self.description_input.text,
                self.selected_materials
            )
            self.load_services()

        self.add_widget(MDRaisedButton(text="Spara ändringar", on_release=save_edit))

    # ─────────────────────────────────────────
    # MATERIAL POPUP
    # ─────────────────────────────────────────
    def open_material_popup(self):
        materials = get_materials()

        main_layout = MDBoxLayout(orientation="vertical", padding=15, spacing=15)

        scroll  = MDScrollView()
        content = MDBoxLayout(orientation="vertical", spacing=10, size_hint_y=None)
        content.bind(minimum_height=content.setter("height"))

        selected = set(self.selected_materials)

        for m in materials:
            row      = MDBoxLayout(size_hint_y=None, height=50, spacing=10)
            checkbox = MDCheckbox(active=(m.id in selected), size_hint_x=None, width=40)
            label    = MDLabel(
                text=f"{m.name} - {m.price} kr",
                theme_text_color="Primary"
            )

            def toggle(_, value, mat=m):
                if value:
                    selected.add(mat.id)
                else:
                    selected.discard(mat.id)

            checkbox.bind(active=toggle)
            row.add_widget(checkbox)
            row.add_widget(label)
            content.add_widget(row)

        scroll.add_widget(content)
        main_layout.add_widget(scroll)

        btn_row = MDBoxLayout(size_hint_y=None, height=50, spacing=10)

        popup = Popup(
            title="Välj material",
            size_hint=(0.9, 0.75),
            background="",
            background_color=(1, 1, 1, 1),
            title_color=(0, 0, 0, 1),
            separator_color=(0.2, 0.45, 0.75, 1)
        )

        def save_materials(*args):
            self.selected_materials = list(selected)
            popup.dismiss()

        btn_row.add_widget(MDRaisedButton(text="Avbryt", on_release=lambda x: popup.dismiss()))
        btn_row.add_widget(MDRaisedButton(text="Spara",  on_release=save_materials))

        main_layout.add_widget(btn_row)
        popup.content = main_layout
        popup.open()

    def go_back(self):
        self.manager.current = "home"