from kivymd.uix.screen import MDScreen
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.card import MDCard
from kivy.uix.popup import Popup

from services import get_services
from materials import get_materials
from settings import load_settings
from pdf_generator import generate_pdf


class QuoteScreen(MDScreen):

    def on_enter(self):
        self.selected_services = []
        self.selected_materials = []
        self.service_hours = {}
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()

        root = MDBoxLayout(orientation="vertical", padding=10, spacing=10)

        # 🧾 TJÄNST BOX (STOR + RAM)
        box = MDCard(
            orientation="vertical",
            size_hint=(1, 0.75),
            padding=10,
            elevation=3
        )

        scroll = MDScrollView()

        self.services_layout = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=5
        )
        self.services_layout.bind(minimum_height=self.services_layout.setter("height"))

        scroll.add_widget(self.services_layout)
        box.add_widget(scroll)
        root.add_widget(MDLabel(
            text="Tjänster",
            halign="left",
            bold=True,
            size_hint_y=None,
            height=30
        ))
        root.add_widget(box)

        # 📦 MATERIAL BUTTON
        root.add_widget(MDRaisedButton(
            text="Välj material",
            pos_hint={"center_x": 0.5},
            on_release=lambda x: self.show_material_popup()
        ))

        # 💰 TOTALS
        self.total_label = MDLabel(
            text="Summa: 0 kr",
            halign="center",
            size_hint_y=None,
            height=25
        )

        self.moms_label = MDLabel(
            text="MOMS: 0 kr",
            halign="center",
            size_hint_y=None,
            height=25
        )

        self.total_with_moms_label = MDLabel(
            text="Totalt: 0 kr",
            halign="center",
            bold=True,
            size_hint_y=None,
            height=30
        )

        root.add_widget(self.total_label)
        root.add_widget(self.moms_label)
        root.add_widget(self.total_with_moms_label)

        # 🔘 KNAPPAR
        root.add_widget(MDRaisedButton(
            text="Förhandsvisa offert",
            pos_hint={"center_x": 0.5},
            on_release=self.show_preview
        ))

        root.add_widget(MDRaisedButton(
            text="Tillbaka",
            pos_hint={"center_x": 0.5},
            on_release=lambda x: self.go_back()
        ))

        self.add_widget(root)

        self.load_services()

    # 📋 TJÄNSTER
    def load_services(self):
        self.services_layout.clear_widgets()

        for s in get_services():
            row = MDBoxLayout(size_hint_y=None, height=60, spacing=10)

            checkbox = MDCheckbox()

            hours_input = MDTextField(
                hint_text="timmar",
                size_hint_x=0.3,
                opacity=0
            )

            def toggle(_, value, s=s, hours_input=hours_input):
                if value:
                    self.selected_services.append(s)

                    if s.price_type == "timme":
                        hours_input.opacity = 1
                        hours_input.text = "1"
                        self.service_hours[s.id] = 1
                else:
                    self.selected_services = [
                        x for x in self.selected_services if x.id != s.id
                    ]
                    hours_input.opacity = 0

                self.calculate_total()

            checkbox.bind(active=toggle)

            # 🔁 timmar update
            hours_input.bind(
                text=lambda inst, val, s=s: self.update_hours(s.id, val)
            )

            row.add_widget(checkbox)
            row.add_widget(MDLabel(text=s.name))
            row.add_widget(hours_input)

            self.services_layout.add_widget(row)

    def update_hours(self, service_id, value):
        try:
            self.service_hours[service_id] = float(value)
        except:
            self.service_hours[service_id] = 1

        self.calculate_total()

    # 📦 MATERIAL POPUP (LJUS FIX)
    def show_material_popup(self):
        popup = Popup(
            title="Material",
            size_hint=(0.9, 0.9),
            background_color=(1, 1, 1, 0.95)  # ✅ LJUST
        )

        root = MDBoxLayout(orientation="vertical", padding=10, spacing=10)

        scroll = MDScrollView()
        list_layout = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None
        )
        list_layout.bind(minimum_height=list_layout.setter("height"))

        for m in get_materials():
            row = MDBoxLayout(size_hint_y=None, height=40)

            checkbox = MDCheckbox()

            def toggle(_, val, m=m):
                if val:
                    self.selected_materials.append(m)
                else:
                    self.selected_materials = [
                        x for x in self.selected_materials if x.id != m.id
                    ]

                self.calculate_total()

            checkbox.bind(active=toggle)

            row.add_widget(checkbox)
            row.add_widget(MDLabel(text=f"{m.name} - {m.price} kr"))

            list_layout.add_widget(row)

        scroll.add_widget(list_layout)
        root.add_widget(scroll)

        # 🔘 KNAPPAR
        btns = MDBoxLayout(size_hint_y=None, height=50, spacing=10)

        btns.add_widget(MDRaisedButton(
            text="Avbryt",
            on_release=lambda x: popup.dismiss()
        ))

        btns.add_widget(MDRaisedButton(
            text="Lägg till",
            on_release=lambda x: popup.dismiss()
        ))

        root.add_widget(btns)

        popup.content = root
        popup.open()

    # 💰 CALC
    def calculate_total(self):
        total = 0

        for s in self.selected_services:
            if s.price_type == "engång":
                total += s.price
            else:
                hours = self.service_hours.get(s.id, 1)
                total += s.price * hours

        # MATERIAL
        for m in self.selected_materials:
            total += m.price

        settings = load_settings()
        moms = total * (settings.get("moms", 25) / 100)
        total_with_moms = total + moms

        self.total_label.text = f"Summa: {total:.2f} kr"
        self.moms_label.text = f"MOMS: {moms:.2f} kr"
        self.total_with_moms_label.text = f"Totalt: {total_with_moms:.2f} kr"

    # 📄 PREVIEW (FIX + AVBRYT)
    def show_preview(self, *args):
        popup = Popup(title="Förhandsvisning", size_hint=(0.9, 0.9))

        layout = MDBoxLayout(orientation="vertical", padding=10, spacing=10)

        layout.add_widget(MDLabel(text="Förhandsvisning OK"))

        btns = MDBoxLayout(size_hint_y=None, height=50, spacing=10)

        btns.add_widget(MDRaisedButton(
            text="Avbryt",
            on_release=lambda x: popup.dismiss()
        ))

        btns.add_widget(MDRaisedButton(
            text="Skapa PDF",
            on_release=lambda x: self.confirm_pdf(popup)
        ))

        layout.add_widget(btns)

        popup.content = layout
        popup.open()

    def confirm_pdf(self, popup):
        popup.dismiss()

        total = 0

        for s in self.selected_services:
            if s.price_type == "engång":
                total += s.price
            else:
                total += s.price * self.service_hours.get(s.id, 1)

        for m in self.selected_materials:
            total += m.price

        settings = load_settings()
        moms = total * (settings.get("moms", 25) / 100)
        total_with_moms = total + moms

        generate_pdf(
            self.selected_services,
            total,
            moms,
            total_with_moms,
            1
        )

    def go_back(self):
        self.manager.current = "home"