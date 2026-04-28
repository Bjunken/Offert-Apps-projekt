from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel

from materials import get_materials, add_material, update_material, delete_material


class MaterialsScreen(MDScreen):

    def on_enter(self):
        self.editing_material = None
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()

        layout = MDBoxLayout(orientation="vertical", padding=10, spacing=10)

        self.name_input = MDTextField(hint_text="Material namn")
        self.price_input = MDTextField(hint_text="Pris")

        layout.add_widget(self.name_input)
        layout.add_widget(self.price_input)

        self.save_btn = MDRaisedButton(
            text="Lägg till material",
            on_release=lambda x: self.save_material()
        )

        layout.add_widget(self.save_btn)

        self.materials_layout = MDBoxLayout(
            orientation="vertical",
            spacing=5
        )

        layout.add_widget(self.materials_layout)

        layout.add_widget(MDRaisedButton(
            text="Tillbaka",
            on_release=lambda x: self.go_back()
        ))

        self.add_widget(layout)

        self.load_materials()

    def load_materials(self):
        self.materials_layout.clear_widgets()

        for m in get_materials():
            row = MDBoxLayout(size_hint_y=None, height=40)

            label = MDLabel(text=f"{m.name} - {m.price} kr")

            edit_btn = MDRaisedButton(
                text="Redigera",
                on_release=lambda x, mat=m: self.edit_material(mat)
            )

            delete_btn = MDRaisedButton(
                text="Ta bort",
                on_release=lambda x, mat=m: self.delete_material(mat)
            )

            row.add_widget(label)
            row.add_widget(edit_btn)
            row.add_widget(delete_btn)

            self.materials_layout.add_widget(row)

    def save_material(self):
        name = self.name_input.text
        try:
            price = float(self.price_input.text)
        except:
            price = 0

        if not name:
            return

        if self.editing_material:
            update_material(self.editing_material.id, name, price)
            self.editing_material = None
            self.save_btn.text = "Lägg till material"
        else:
            add_material(name, price)

        self.name_input.text = ""
        self.price_input.text = ""

        self.load_materials()

    def edit_material(self, material):
        self.editing_material = material

        self.name_input.text = material.name
        self.price_input.text = str(material.price)

        self.save_btn.text = "Uppdatera material"

    def delete_material(self, material):
        delete_material(material.id)
        self.load_materials()

    def go_back(self):
        self.manager.current = "home"