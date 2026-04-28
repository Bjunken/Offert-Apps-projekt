from kivymd.uix.screen import MDScreen
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivy.uix.popup import Popup

from services import get_services
from materials import get_materials
from pdf_generator import generate_pdf
from settings import load_settings


class QuoteScreen(MDScreen):

    def on_enter(self):
        self.selected_services = []
        self.selected_materials = []
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()

        layout = MDBoxLayout(orientation="vertical", padding=10, spacing=10)

        # 🕒 timmar
        self.hours_input = MDTextField(
            hint_text="Antal timmar",
            text="1",
            size_hint_y=None,
            height=50,
            opacity=0
        )
        self.hours_input.bind(text=lambda *args: self.calculate_total())
        layout.add_widget(self.hours_input)

        # 📋 tjänster
        self.services_layout = MDBoxLayout(orientation="vertical", spacing=5)
        layout.add_widget(self.services_layout)

        # 🔘 toggle material
        self.use_materials_checkbox = MDCheckbox()
        self.use_materials_checkbox.bind(active=self.toggle_material_visibility)

        toggle_row = MDBoxLayout(size_hint_y=None, height=40)
        toggle_row.add_widget(MDLabel(text="Använd material"))
        toggle_row.add_widget(self.use_materials_checkbox)

        layout.add_widget(toggle_row)

        # 📦 material lista
        self.material_layout = MDBoxLayout(
            orientation="vertical",
            spacing=5,
            opacity=0
        )
        layout.add_widget(self.material_layout)

        # 💰 totals
        self.total_label = MDLabel(text="Summa: 0 kr", halign="center")
        self.moms_label = MDLabel(text="MOMS: 0 kr", halign="center")
        self.total_with_moms_label = MDLabel(
            text="Totalt: 0 kr",
            halign="center",
            bold=True
        )

        layout.add_widget(self.total_label)
        layout.add_widget(self.moms_label)
        layout.add_widget(self.total_with_moms_label)

        # 🔘 knappar
        layout.add_widget(MDRaisedButton(
            text="Förhandsvisa offert",
            on_release=lambda x: self.show_preview()
        ))

        layout.add_widget(MDRaisedButton(
            text="Tillbaka",
            on_release=lambda x: self.go_back()
        ))

        self.add_widget(layout)

        self.load_services()
        self.load_materials()

    # =========================
    # SERVICES
    # =========================

    def load_services(self):
        self.services_layout.clear_widgets()

        for s in get_services():
            row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=40)

            checkbox = MDCheckbox()
            checkbox.bind(active=self.create_toggle_callback(s))

            label = MDLabel(text=f"{s.name} ({s.price_type}) - {s.price} kr")

            row.add_widget(checkbox)
            row.add_widget(label)

            self.services_layout.add_widget(row)

    def create_toggle_callback(self, service):
        def callback(_, value):
            self.toggle_service(service, value)
        return callback

    def toggle_service(self, service, is_active):
        if is_active:
            self.selected_services.append(service)
        else:
            self.selected_services = [
                s for s in self.selected_services if s.id != service.id
            ]

        self.update_hours_visibility()
        self.calculate_total()

    def update_hours_visibility(self):
        has_hour = any(s.price_type == "timme" for s in self.selected_services)
        self.hours_input.opacity = 1 if has_hour else 0

    # =========================
    # MATERIAL
    # =========================

    def load_materials(self):
        self.material_layout.clear_widgets()

        for m in get_materials():
            row = MDBoxLayout(size_hint_y=None, height=40)

            checkbox = MDCheckbox()
            checkbox.bind(active=lambda cb, val, mat=m: self.toggle_material(mat, val))

            label = MDLabel(text=f"{m.name} - {m.price} kr")

            row.add_widget(checkbox)
            row.add_widget(label)

            self.material_layout.add_widget(row)

    def toggle_material(self, material, is_active):
        if is_active:
            self.selected_materials.append(material)
        else:
            self.selected_materials = [
                m for m in self.selected_materials if m.id != material.id
            ]

        self.calculate_total()

    def toggle_material_visibility(self, checkbox, value):
        if value:
            self.material_layout.opacity = 1
        else:
            self.material_layout.opacity = 0
            self.selected_materials = []
            self.calculate_total()

    # =========================
    # TOTAL
    # =========================

    def calculate_total(self):
        try:
            hours = float(self.hours_input.text or 1)
        except:
            hours = 1

        total = 0

        # tjänster
        for s in self.selected_services:
            if s.price_type == "engång":
                total += s.price
            else:
                total += s.price * hours

        # material
        for m in self.selected_materials:
            total += m.price

        settings = load_settings()
        moms_rate = settings.get("moms", 25) / 100

        moms = total * moms_rate
        total_with_moms = total + moms

        self.total_label.text = f"Summa: {total:.2f} kr"
        self.moms_label.text = f"MOMS ({settings.get('moms',25)}%): {moms:.2f} kr"
        self.total_with_moms_label.text = f"Totalt: {total_with_moms:.2f} kr"

    # =========================
    # PREVIEW
    # =========================

    def show_preview(self):
        from kivymd.uix.scrollview import MDScrollView
        from kivymd.uix.card import MDCard
        from kivy.uix.image import Image
        from datetime import datetime
        import os

        settings = load_settings()

        try:
            hours = float(self.hours_input.text or 1)
        except:
            hours = 1

        total = 0
        offert_nr = datetime.now().strftime("%Y%m%d%H%M")

        popup = Popup(title="Förhandsvisning", size_hint=(0.95, 0.95))

        root = MDBoxLayout(orientation="vertical")

        scroll = MDScrollView()
        card = MDCard(
            orientation="vertical",
            padding=20,
            spacing=10,
            size_hint_y=None
        )
        card.bind(minimum_height=card.setter("height"))

        def label(text, bold=False, align="center", height=30):
            return MDLabel(text=text, bold=bold, halign=align, size_hint_y=None, height=height)

        # HEADER
        if settings.get("logo_path") and os.path.exists(settings["logo_path"]):
            card.add_widget(Image(source=settings["logo_path"], size_hint=(None, None), size=(120, 60)))

        card.add_widget(label(settings.get("company_name", ""), True))
        card.add_widget(label(f"OFFERT #{offert_nr}", True))
        card.add_widget(label(f"Datum: {datetime.now().strftime('%Y-%m-%d')}"))

        # TJÄNSTER
        engang = [s for s in self.selected_services if s.price_type == "engång"]
        tim = [s for s in self.selected_services if s.price_type == "timme"]

        def add_section(title, services):
            nonlocal total
            if not services:
                return

            card.add_widget(label(title, True, "left"))

            for s in services:
                row = MDBoxLayout(size_hint_y=None, height=70)

                if s.price_type == "engång":
                    amount = "-"
                    price = s.price
                else:
                    amount = str(hours)
                    price = s.price * hours

                total += price

                service_layout = MDBoxLayout(orientation="vertical")
                service_layout.add_widget(label(s.name, True, "left"))

                if s.description:
                    service_layout.add_widget(label(f"• {s.description}", False, "left"))

                row.add_widget(service_layout)
                row.add_widget(label(amount))
                row.add_widget(label(f"{s.price} kr"))
                row.add_widget(label(f"{price:.2f} kr"))

                card.add_widget(row)

        add_section("Engångspriser", engang)
        add_section("Timpris", tim)

        # MATERIAL
        if self.selected_materials:
            card.add_widget(label("Material", True, "left"))

            for m in self.selected_materials:
                total += m.price
                card.add_widget(label(f"{m.name} - {m.price} kr", False, "left"))

        # TOTAL
        moms_rate = settings.get("moms", 25) / 100
        moms = total * moms_rate
        total_with_moms = total + moms

        card.add_widget(label("────────────"))
        card.add_widget(label(f"Summa: {total:.2f} kr", False, "right"))
        card.add_widget(label(f"MOMS: {moms:.2f} kr", False, "right"))
        card.add_widget(label(f"Totalt: {total_with_moms:.2f} kr", True, "right"))

        scroll.add_widget(card)

        # KNAPPAR (FIXEN 🔥)
        btn_layout = MDBoxLayout(size_hint_y=None, height=60, spacing=10)

        btn_layout.add_widget(MDRaisedButton(
            text="Skapa PDF",
            on_release=lambda x: self.confirm_pdf(popup)
        ))

        btn_layout.add_widget(MDRaisedButton(
            text="Stäng",
            on_release=lambda x: popup.dismiss()
        ))

        root.add_widget(scroll)
        root.add_widget(btn_layout)

        popup.content = root
        popup.open()

    # =========================
    # PDF
    # =========================

    def confirm_pdf(self, popup):
        popup.dismiss()

        try:
            hours = float(self.hours_input.text or 1)
        except:
            hours = 1

        total = sum(
            s.price if s.price_type == "engång" else s.price * hours
            for s in self.selected_services
        )

        for m in self.selected_materials:
            total += m.price

        settings = load_settings()
        moms = total * (settings.get("moms", 25) / 100)
        total_with_moms = total + moms

        filename = generate_pdf(
            self.selected_services,
            total,
            moms,
            total_with_moms,
            hours,
            materials=self.selected_materials
        )

        import os, platform
        from kivymd.toast import toast

        toast("PDF skapad!")

        if platform.system() == "Windows":
            os.startfile(filename)
        elif platform.system() == "Darwin":
            os.system(f"open {filename}")
        else:
            os.system(f"xdg-open {filename}")

    def go_back(self):
        self.manager.current = "home"