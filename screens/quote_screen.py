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

    def on_enter(self):
        self.selected_services = []
        self.selected_materials = []
        self.service_hours = {}
        self.discount_value = 0
        self.discount_type = None
        self.build_ui()

    # -----------------------------------
    # UI
    # -----------------------------------
    def build_ui(self):
        self.clear_widgets()

        root = MDBoxLayout(
            orientation="vertical",
            padding=10,
            spacing=2  # 🔥 FIX spacing
        )

        # 🔽 STÖRRE LISTA
        scroll = MDScrollView(size_hint=(1, 0.88))  # 🔥 FIX height

        self.services_layout = MDBoxLayout(
            orientation="vertical",
            spacing=8,
            size_hint_y=None
        )
        self.services_layout.bind(minimum_height=self.services_layout.setter("height"))

        scroll.add_widget(self.services_layout)
        root.add_widget(scroll)

        # 📦 MATERIAL
        root.add_widget(MDRaisedButton(
            text="Välj material",
            pos_hint={"center_x": 0.5},
            size_hint_x=0.7,
            on_release=lambda x: self.open_material_popup()
        ))

        # 💰 TOTALS (tight)
        self.total_label = MDLabel(text="Summa: 0 kr", halign="center", size_hint_y=None, height=20)
        self.moms_label = MDLabel(text="MOMS: 0 kr", halign="center", size_hint_y=None, height=20)
        self.total_with_moms_label = MDLabel(
            text="Totalt: 0 kr",
            halign="center",
            bold=True,
            size_hint_y=None,
            height=25
        )

        root.add_widget(self.total_label)
        root.add_widget(self.moms_label)
        root.add_widget(self.total_with_moms_label)

        # 🔘 KNAPPAR
        btn_row = MDBoxLayout(
            size_hint_y=None,
            height=45,
            spacing=10,
            padding=[40, 0, 40, 0]
        )

        btn_row.add_widget(MDRaisedButton(
            text="Förhandsvisa offert",
            on_release=lambda x: self.show_preview()
        ))

        btn_row.add_widget(MDRaisedButton(
            text="Tillbaka",
            on_release=lambda x: self.go_back()
        ))

        root.add_widget(btn_row)

        self.add_widget(root)

        self.load_services()

    # -----------------------------------
    # TJÄNSTER
    # -----------------------------------
    def load_services(self):
        self.services_layout.clear_widgets()

        services = get_services()
        all_materials = get_materials()

        for s in services:

            container = MDBoxLayout(
                orientation="vertical",
                size_hint_y=None,
                spacing=3,
                padding=5
            )
            container.bind(minimum_height=container.setter("height"))

            row = MDBoxLayout(size_hint_y=None, height=40)

            checkbox = MDCheckbox()
            checkbox.bind(active=self.create_toggle_callback(s))

            row.add_widget(checkbox)
            row.add_widget(MDLabel(text=s.name))
            row.add_widget(MDLabel(text=f"{s.price} kr"))

            # 🕒 TIMMAR INLINE (FIX)
            if s.price_type == "timme":
                hours = MDTextField(
                    hint_text="h",
                    text="1",
                    size_hint_x=0.25
                )

                # 🔥 FIX: bind update
                hours.bind(text=lambda *args: self.calculate_total())

                self.service_hours[s.id] = hours
                row.add_widget(hours)

            container.add_widget(row)

            # 📦 MATERIAL
            for mat_id in s.materials:
                mat = next((m for m in all_materials if m.id == mat_id), None)
                if mat:
                    container.add_widget(MDLabel(
                        text=f"• {mat.name} ({mat.price} kr)",
                        halign="center",
                        size_hint_y=None,
                        height=18
                    ))

            self.services_layout.add_widget(container)

    # -----------------------------------
    def create_toggle_callback(self, service):
        def callback(_, active):
            if active:
                self.selected_services.append(service)
            else:
                self.selected_services = [
                    s for s in self.selected_services if s.id != service.id
                ]

            self.calculate_total()

        return callback

    # -----------------------------------
    # TOTAL
    # -----------------------------------
    def calculate_total(self):
        total = 0
        all_materials = get_materials()

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

            # material
            for mat_id in s.materials:
                mat = next((m for m in all_materials if m.id == mat_id), None)
                if mat:
                    total += mat.price

        # extra material
        for m in self.selected_materials:
            total += m.price

        settings = load_settings()
        moms = total * (settings.get("moms", 25) / 100)
        total_with_moms = total + moms

        self.total_label.text = f"Summa: {total:.2f} kr"
        self.moms_label.text = f"MOMS: {moms:.2f} kr"
        self.total_with_moms_label.text = f"Totalt: {total_with_moms:.2f} kr"

        return total, moms, total_with_moms

    # -----------------------------------
    # MATERIAL POPUP
    # -----------------------------------
    def open_material_popup(self):
        materials = get_materials()

        layout = MDBoxLayout(orientation="vertical", padding=10)

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

        popup = Popup(
            title="Material",
            content=layout,
            size_hint=(0.9, 0.9),
            background_color=(1, 1, 1, 0.95)
        )

        btn_row = MDBoxLayout(size_hint_y=None, height=50)

        btn_row.add_widget(MDRaisedButton(
            text="Avbryt",
            on_release=lambda x: popup.dismiss()
        ))

        btn_row.add_widget(MDRaisedButton(
            text="Lägg till",
            on_release=lambda x: self.apply_materials(popup)
        ))

        layout.add_widget(btn_row)

        popup.open()

    def apply_materials(self, popup):
        materials = get_materials()

        self.selected_materials = [
            m for m in materials if self.material_checks[m.id].active
        ]

        popup.dismiss()
        self.calculate_total()

    # -----------------------------------
    # 👁️ PREVIEW (FIX – ingen PDF)
    # -----------------------------------
    def show_preview(self):
        services, total, moms, total_with_moms = self.build_invoice_data()

        popup = Popup(title="Förhandsvisning", size_hint=(0.95, 0.95))

        scroll = MDScrollView()
        layout = MDBoxLayout(
            orientation="vertical",
            padding=20,
            spacing=10,
            size_hint_y=None
        )
        layout.bind(minimum_height=layout.setter("height"))

        # HEADER
        layout.add_widget(MDLabel(text="OFFERT", halign="center", bold=True))
        layout.add_widget(MDLabel(text="────────────────────────"))

        # TJÄNSTER
        for s in services:
            layout.add_widget(MDLabel(
                text=f"{s['name']} ({s['hours']})",
                bold=True
            ))

            for m in s["materials"]:
                layout.add_widget(MDLabel(
                    text=f"  • {m.name} ({m.price} kr)"
                ))

            layout.add_widget(MDLabel(
                text=f"Summa: {s['total']:.2f} kr"
            ))

            layout.add_widget(MDLabel(text=""))

        # TOTAL
        layout.add_widget(MDLabel(text="────────────────────────"))
        layout.add_widget(MDLabel(text=f"Summa: {total:.2f} kr"))
        layout.add_widget(MDLabel(text=f"MOMS: {moms:.2f} kr"))
        layout.add_widget(MDLabel(
            text=f"Totalt: {total_with_moms:.2f} kr",
            bold=True
        ))

        # KNAPPAR
        btn_row = MDBoxLayout(size_hint_y=None, height=50)

        btn_row.add_widget(MDRaisedButton(
            text="Avbryt",
            on_release=lambda x: popup.dismiss()
        ))

        btn_row.add_widget(MDRaisedButton(
            text="Skapa PDF",
            on_release=lambda x: self.confirm_pdf(popup)
        ))

        layout.add_widget(btn_row)

        scroll.add_widget(layout)
        popup.content = scroll
        popup.open()

    # -----------------------------------
    def confirm_pdf(self, popup):
        popup.dismiss()

        total, moms, total_with_moms = self.calculate_total()

        filename = generate_pdf(
            self.selected_services,
            total,
            moms,
            total_with_moms,
            self.service_hours,
            self.discount_value,
            self.discount_type
        )

        import os, platform

        if platform.system() == "Windows":
            os.startfile(filename)

    # -----------------------------------
    def go_back(self):
        self.manager.current = "home"

    def build_invoice_data(self):
        services_data = []
        total = 0

        all_materials = get_materials()

        for s in self.selected_services:

            if s.price_type == "engång":
                hours = "-"
                price = s.price
            else:
                field = self.service_hours.get(s.id)
                try:
                    hours = float(field.text or 1)
                except:
                    hours = 1

                price = s.price * hours

            # material
            materials_list = []
            for mat_id in s.materials:
                mat = next((m for m in all_materials if m.id == mat_id), None)
                if mat:
                    materials_list.append(mat)
                    price += mat.price

            total += price

            services_data.append({
                "name": s.name,
                "hours": hours,
                "unit_price": s.price,
                "total": price,
                "materials": materials_list
            })

        # extra material
        for m in self.selected_materials:
            total += m.price

        settings = load_settings()
        moms = total * (settings.get("moms", 25) / 100)
        total_with_moms = total + moms

        return services_data, total, moms, total_with_moms