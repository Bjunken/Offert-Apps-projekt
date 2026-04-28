from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.label import MDLabel

from materials import add_material, get_materials, delete_material, update_material


class MaterialsScreen(MDScreen):

    def on_enter(self):
        self.selected_material_id = None
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()

        root = MDBoxLayout(orientation="vertical", padding=10, spacing=10)

        # INPUTS
        self.name_input = MDTextField(hint_text="Material namn")
        self.price_input = MDTextField(hint_text="Pris")

        root.add_widget(self.name_input)
        root.add_widget(self.price_input)

        # KNAPPAR
        self.save_btn = MDRaisedButton(
            text="Lägg till material",
            on_release=lambda x: self.save_material()
        )

        root.add_widget(self.save_btn)

        # SCROLL LISTA
        scroll = MDScrollView()
        self.list_layout = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None
        )
        self.list_layout.bind(minimum_height=self.list_layout.setter("height"))

        scroll.add_widget(self.list_layout)
        root.add_widget(scroll)

        root.add_widget(MDRaisedButton(
            text="Tillbaka",
            on_release=lambda x: self.go_back()
        ))

        self.add_widget(root)

        self.load_materials()

    def load_materials(self):
        self.list_layout.clear_widgets()

        for m in get_materials():
            row = MDBoxLayout(size_hint_y=None, height=40)

            row.add_widget(MDLabel(text=f"{m.name} - {m.price} kr"))

            row.add_widget(MDRaisedButton(
                text="Redigera",
                size_hint_x=0.3,
                on_release=lambda x, m=m: self.fill_form(m)
            ))

            row.add_widget(MDRaisedButton(
                text="Ta bort",
                size_hint_x=0.3,
                on_release=lambda x, m=m: self.delete_material(m.id)
            ))

            self.list_layout.add_widget(row)

    def fill_form(self, material):
        self.selected_material_id = material.id

        self.name_input.text = material.name
        self.price_input.text = str(material.price)

        self.save_btn.text = "Spara ändring"

    def save_material(self):
        name = self.name_input.text.strip()

        try:
            price = float(self.price_input.text)
        except:
            return

        if self.selected_material_id:
            update_material(self.selected_material_id, name, price)
        else:
            add_material(name, price)

        # töm fälten
        self.selected_material_id = None
        self.name_input.text = ""
        self.price_input.text = ""
        self.save_btn.text = "Lägg till material"

        self.load_materials()

    def delete_material(self, material_id):
        delete_material(material_id)
        self.load_materials()

    def go_back(self):
        self.manager.current = "home"