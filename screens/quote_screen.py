from kivymd.uix.screen import MDScreen
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.scrollview import MDScrollView
from kivy.uix.popup import Popup

from services import get_services
from materials import get_materials
from pdf_generator import generate_pdf
from settings import load_settings


class QuoteScreen(MDScreen):

    def build_ui(self):
        self.clear_widgets()

        root = MDBoxLayout(
            orientation="vertical",
            padding=10,
            spacing=5  # 🔥 mindre spacing globalt
        )

        # 🔽 STOR scroll (huvuddelen av skärmen)
        scroll = MDScrollView(size_hint=(1, 0.78))

        self.services_layout = MDBoxLayout(
            orientation="vertical",
            spacing=15,
            size_hint_y=None
        )
        self.services_layout.bind(minimum_height=self.services_layout.setter("height"))

        scroll.add_widget(self.services_layout)
        root.add_widget(scroll)

        # 📦 MATERIAL knapp (centrerad)
        root.add_widget(MDRaisedButton(
            text="Välj material",
            pos_hint={"center_x": 0.5},
            size_hint_x=0.6,
            on_release=lambda x: self.open_material_popup()
        ))

        # 💰 TOTALS (tight spacing)
        self.total_label = MDLabel(text="Summa: 0 kr", halign="center", height=25)
        self.moms_label = MDLabel(text="MOMS: 0 kr", halign="center", height=25)
        self.total_with_moms_label = MDLabel(
            text="Totalt: 0 kr",
            halign="center",
            bold=True,
            height=30
        )

        root.add_widget(self.total_label)
        root.add_widget(self.moms_label)
        root.add_widget(self.total_with_moms_label)

        # 🔘 KNAPPAR (centrerade)
        btn_row = MDBoxLayout(
            size_hint_y=None,
            height=50,
            spacing=10,
            padding=[50, 0, 50, 0]  # 🔥 centrerar visuellt
        )

        btn_row.add_widget(MDRaisedButton(
            text="Förhandsvisa offert",
            pos_hint={"center_x": 0.5},
            on_release=lambda x: self.show_preview()
        ))

        btn_row.add_widget(MDRaisedButton(
            text="Tillbaka",
            pos_hint={"center_x": 0.5},
            on_release=lambda x: self.go_back()
        ))

        root.add_widget(btn_row)

        self.add_widget(root)

        self.load_services()

    # -----------------------------------
    # 📋 LADDA TJÄNSTER (NY STRUKTUR)
    # -----------------------------------
    def load_services(self):
        from materials import get_materials

        self.services_layout.clear_widgets()
        all_materials = get_materials()

        services = get_services()

        engang = [s for s in services if s.price_type == "engång"]
        tim = [s for s in services if s.price_type == "timme"]

        def add_section(title, service_list):
            if not service_list:
                return

            # 🔹 SEKTIONSTITEL med spacing
            self.services_layout.add_widget(MDLabel(
                text=title,
                bold=True,
                halign="center",
                size_hint_y=None,
                height=30
            ))

            for s in service_list:

                # 🔲 HELA TJÄNST BLOCK
                container = MDBoxLayout(
                    orientation="vertical",
                    size_hint_y=None,
                    spacing=5,
                    padding=5
                )
                container.bind(minimum_height=container.setter("height"))

                # 🔹 RAD 1 (checkbox + namn + pris)
                row = MDBoxLayout(size_hint_y=None, height=40)

                checkbox = MDCheckbox()
                checkbox.bind(active=self.create_toggle_callback(s))

                name = MDLabel(text=s.name)
                price = MDLabel(text=f"{s.price} kr")

                row.add_widget(checkbox)
                row.add_widget(name)
                row.add_widget(price)

                container.add_widget(row)

                # 🔹 TIM INPUT
                if s.price_type == "timme":
                    hours_input = MDTextField(
                        hint_text="Antal timmar",
                        text="1",
                        size_hint_y=None,
                        height=40,
                        opacity=0
                    )

                    hours_input.bind(
                        text=lambda inst, val, sid=s.id: self.update_hours(sid, val)
                    )

                    container.add_widget(hours_input)
                    self.service_hours[s.id] = hours_input

                # 🔹 MATERIAL (med spacing)
                if hasattr(s, "materials") and s.materials:
                    container.add_widget(MDLabel(
                        text="Material:",
                        bold=True,
                        halign="center",
                        size_hint_y=None,
                        height=25
                    ))

                    for mat_id in s.materials:
                        mat = next((m for m in all_materials if m.id == mat_id), None)

                        if mat:
                            container.add_widget(MDLabel(
                                text=f"• {mat.name} ({mat.price} kr)",
                                halign="center",
                                size_hint_y=None,
                                height=25
                            ))

                # 🔥 SPACING mellan tjänster
                container.add_widget(MDLabel(text="", size_hint_y=None, height=10))

                self.services_layout.add_widget(container)

            # 🔥 SPACING mellan sektioner
            self.services_layout.add_widget(MDLabel(text="", size_hint_y=None, height=15))

        add_section("Engångspriser", engang)
        add_section("Timpris", tim)

    # -----------------------------------
    def create_toggle_callback(self, service):
        def callback(_, value):
            self.toggle_service(service, value)
        return callback

    def toggle_service(self, service, active):
        if active:
            self.selected_services.append(service)
        else:
            self.selected_services = [
                s for s in self.selected_services if s.id != service.id
            ]

        # visa timmarfält
        if service.price_type == "timme":
            field = self.service_hours.get(service.id)
            if field:
                field.opacity = 1 if active else 0

        self.calculate_total()

    def update_hours(self, service_id, value):
        self.calculate_total()

    # -----------------------------------
    # 💰 TOTAL
    # -----------------------------------
    def calculate_total(self):
        total = 0

        for s in self.selected_services:
            if s.price_type == "engång":
                total += s.price
            else:
                hours = 1
                field = self.service_hours.get(s.id)
                if field:
                    try:
                        hours = float(field.text or 1)
                    except:
                        hours = 1

                total += s.price * hours

            # ➕ MATERIAL kopplat till tjänst
            if hasattr(s, "materials"):
                all_materials = get_materials()

                if hasattr(s, "materials"):
                    for mat_id in s.materials:
                        mat = next((m for m in all_materials if m.id == mat_id), None)
                        if mat:
                            total += mat.price

        # ➕ EXTRA MATERIAL
        for m in self.selected_materials:
            total += m.price

        settings = load_settings()
        moms = total * (settings.get("moms", 25) / 100)
        total_with_moms = total + moms

        self.total_label.text = f"Summa: {total:.2f} kr"
        self.moms_label.text = f"MOMS: {moms:.2f} kr"
        self.total_with_moms_label.text = f"Totalt: {total_with_moms:.2f} kr"

    # -----------------------------------
    # 📦 MATERIAL POPUP
    # -----------------------------------
    def open_material_popup(self):
        materials = get_materials()

        layout = MDBoxLayout(orientation="vertical", padding=10, spacing=10)

        scroll = MDScrollView()
        list_layout = MDBoxLayout(orientation="vertical", size_hint_y=None)
        list_layout.bind(minimum_height=list_layout.setter("height"))

        self.material_checks = {}

        for m in materials:
            row = MDBoxLayout(size_hint_y=None, height=40)

            checkbox = MDCheckbox()
            self.material_checks[m.id] = checkbox

            row.add_widget(checkbox)
            row.add_widget(MDLabel(text=f"{m.name} ({m.price} kr)"))

            list_layout.add_widget(row)

        scroll.add_widget(list_layout)
        layout.add_widget(scroll)

        btn_row = MDBoxLayout(size_hint_y=None, height=50, spacing=10)

        btn_row.add_widget(MDRaisedButton(
            text="Avbryt",
            on_release=lambda x: popup.dismiss()
        ))

        btn_row.add_widget(MDRaisedButton(
            text="Lägg till",
            on_release=lambda x: self.apply_materials(popup)
        ))

        layout.add_widget(btn_row)

        popup = Popup(
            title="Välj material",
            content=layout,
            size_hint=(0.9, 0.9),
            background_color=(1, 1, 1, 0.95)
        )

        popup.open()

    def apply_materials(self, popup):
        materials = get_materials()
        self.selected_materials = [
            m for m in materials if self.material_checks[m.id].active
        ]

        popup.dismiss()
        self.calculate_total()

    # -----------------------------------
    def go_back(self):
        self.manager.current = "home"

    def show_preview(self):
        print("Preview coming next step")