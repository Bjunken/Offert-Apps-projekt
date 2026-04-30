from kivymd.uix.screen import MDScreen
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.scrollview import MDScrollView
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle
from kivy.uix.widget import Widget

from services import get_services
from materials import get_materials
from pdf_generator import generate_pdf
from company_info import load_settings


class WhiteCard(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self._rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size


class TableRow(MDBoxLayout):
    def __init__(self, col1, col2, col3, col4, is_header=False, bg_color=None, **kwargs):
        super().__init__(
            orientation="horizontal",
            size_hint_y=None,
            height=32,
            **kwargs
        )
        bg = bg_color or (1, 1, 1, 1)
        with self.canvas.before:
            Color(*bg)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._upd, size=self._upd)

        text_color = (1, 1, 1, 1) if is_header else (0, 0, 0, 1)

        for text, width in [(col1, 0.45), (col2, 0.15), (col3, 0.2), (col4, 0.2)]:
            lbl = MDLabel(
                text=str(text),
                size_hint_x=width,
                theme_text_color="Custom",
                text_color=text_color,
                bold=is_header,
                padding_x=6,
                halign="left",
                valign="middle"
            )
            lbl.bind(size=lbl.setter("text_size"))
            self.add_widget(lbl)

    def _upd(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size


class MaterialRow(MDBoxLayout):
    def __init__(self, name, price, **kwargs):
        super().__init__(
            orientation="horizontal",
            size_hint_y=None,
            height=24,
            **kwargs
        )
        with self.canvas.before:
            Color(0.97, 0.97, 0.97, 1)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._upd, size=self._upd)

        lbl = MDLabel(
            text=f"    • {name}",
            size_hint_x=0.6,
            theme_text_color="Custom",
            text_color=(0.3, 0.3, 0.3, 1),
            halign="left",
            valign="middle"
        )
        lbl.bind(size=lbl.setter("text_size"))

        price_lbl = MDLabel(
            text=f"{price:.2f} kr",
            size_hint_x=0.4,
            theme_text_color="Custom",
            text_color=(0.3, 0.3, 0.3, 1),
            halign="right",
            valign="middle"
        )
        price_lbl.bind(size=price_lbl.setter("text_size"))

        self.add_widget(lbl)
        self.add_widget(price_lbl)

    def _upd(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size


class Divider(Widget):
    def __init__(self, color=(0.8, 0.8, 0.8, 1), **kwargs):
        super().__init__(size_hint_y=None, height=1, **kwargs)
        with self.canvas:
            Color(*color)
            self._line = Rectangle(pos=self.pos, size=(self.width, 1))
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *args):
        self._line.pos = self.pos
        self._line.size = (self.width, 1)


class CategoryHeader(MDBoxLayout):
    def __init__(self, text, **kwargs):
        super().__init__(
            orientation="horizontal",
            size_hint_y=None,
            height=32,
            padding=[6, 4, 6, 0],
            **kwargs
        )
        lbl = MDLabel(
            text=text,
            bold=True,
            font_size=14,
            theme_text_color="Primary",
            halign="left",
            valign="middle"
        )
        lbl.bind(size=lbl.setter("text_size"))
        self.add_widget(lbl)


class ServiceRow(MDBoxLayout):
    def __init__(self, service, toggle_cb, hours_dict, **kwargs):
        super().__init__(
            orientation="horizontal",
            size_hint_y=None,
            height=44,
            padding=[4, 2, 4, 2],
            spacing=6,
            **kwargs
        )

        checkbox = MDCheckbox(size_hint_x=None, width=40)
        checkbox.bind(active=toggle_cb)

        name_lbl = MDLabel(
            text=service.name,
            size_hint_x=0.5,
            halign="left",
            valign="middle"
        )
        name_lbl.bind(size=name_lbl.setter("text_size"))

        price_lbl = MDLabel(
            text=f"{service.price} kr",
            size_hint_x=0.25,
            halign="right",
            valign="middle"
        )
        price_lbl.bind(size=price_lbl.setter("text_size"))

        self.add_widget(checkbox)
        self.add_widget(name_lbl)
        self.add_widget(price_lbl)

        if service.price_type == "timme":
            hours_field = MDTextField(
                hint_text="h",
                text="1",
                size_hint_x=0.2,
                size_hint_y=None,
                height=40
            )
            hours_dict[service.id] = hours_field
            self.add_widget(hours_field)


class QuoteScreen(MDScreen):

    def on_enter(self):
        self.selected_services  = []
        self.selected_materials = []
        self.service_hours      = {}
        self.discount_value     = 0
        self.discount_type      = "percent"   # "percent" or "kr"
        self.discount_active    = False
        self.build_ui()

    # ─────────────────────────────────────────
    # UI
    # ─────────────────────────────────────────
    def build_ui(self):
        self.clear_widgets()

        root = MDBoxLayout(orientation="vertical", padding=10, spacing=6)

        # ── Scrollable service list ───────────────
        scroll = MDScrollView(size_hint=(1, 1))

        self.services_layout = MDBoxLayout(
            orientation="vertical",
            spacing=2,
            size_hint_y=None
        )
        self.services_layout.bind(minimum_height=self.services_layout.setter("height"))

        scroll.add_widget(self.services_layout)
        root.add_widget(scroll)

        # ── Fixed bottom controls ─────────────────
        bottom = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=210,
            spacing=4
        )

        bottom.add_widget(MDRaisedButton(
            text="Välj material",
            pos_hint={"center_x": 0.5},
            size_hint_x=0.7,
            on_release=lambda x: self.open_material_popup()
        ))

# ── Discount row ──────────────────────────
        self.discount_row = MDBoxLayout(
            size_hint_y=None,
            height=44,
            spacing=6,
            padding=[4, 0, 4, 0]
        )

        self.discount_checkbox = MDCheckbox(
            size_hint_x=None,
            width=40
        )
        self.discount_checkbox.bind(active=self.on_discount_toggled)

        self.discount_label = MDLabel(
            text="Rabatt",
            size_hint_x=None,
            width=60,
            halign="left",
            valign="middle"
        )
        self.discount_label.bind(size=self.discount_label.setter("text_size"))

        self.discount_input = MDTextField(
            hint_text="0",
            text="",
            size_hint_x=0.3,
            size_hint_y=None,
            height=40,
            input_filter="float"
        )
        self.discount_input.bind(text=lambda *a: self.calculate_total())

        self.discount_type_btn = MDRaisedButton(
            text="%",
            size_hint_x=None,
            width=60,
            on_release=lambda x: self.toggle_discount_type()
        )

        # Only checkbox + label shown initially
        self.discount_row.add_widget(self.discount_checkbox)
        self.discount_row.add_widget(self.discount_label)

        bottom.add_widget(self.discount_row)

        # ── Totals ────────────────────────────────
        self.discount_line_label = MDLabel(
            text="",
            halign="center",
            size_hint_y=None,
            height=20,
            theme_text_color="Custom",
            text_color=(0.8, 0.1, 0.1, 1)   # red so it stands out
        )

        self.total_label = MDLabel(
            text="Summa: 0 kr", halign="center", size_hint_y=None, height=22
        )
        self.moms_label = MDLabel(
            text="MOMS: 0 kr", halign="center", size_hint_y=None, height=22
        )
        self.total_with_moms_label = MDLabel(
            text="Totalt: 0 kr", halign="center",
            bold=True, size_hint_y=None, height=26
        )

        bottom.add_widget(self.discount_line_label)
        bottom.add_widget(self.total_label)
        bottom.add_widget(self.moms_label)
        bottom.add_widget(self.total_with_moms_label)

        btn_row = MDBoxLayout(
            size_hint_y=None, height=45, spacing=10, padding=[20, 0, 20, 0]
        )
        btn_row.add_widget(MDRaisedButton(
            text="Förhandsvisa offert",
            on_release=lambda x: self.show_preview()
        ))
        btn_row.add_widget(MDRaisedButton(
            text="Tillbaka",
            on_release=lambda x: self.go_back()
        ))
        bottom.add_widget(btn_row)

        root.add_widget(bottom)
        self.add_widget(root)
        self.load_services()

    # ─────────────────────────────────────────
    # DISCOUNT CONTROLS
    # ─────────────────────────────────────────
    def on_discount_toggled(self, checkbox, active):
            self.discount_active = active

            if active:
                self.discount_row.add_widget(self.discount_input)
                self.discount_row.add_widget(self.discount_type_btn)
            else:
                if self.discount_input in self.discount_row.children:
                    self.discount_row.remove_widget(self.discount_input)
                if self.discount_type_btn in self.discount_row.children:
                    self.discount_row.remove_widget(self.discount_type_btn)
                self.discount_input.text = ""

            self.calculate_total()

    def toggle_discount_type(self):
        if self.discount_type == "percent":
            self.discount_type          = "kr"
            self.discount_type_btn.text = "kr"
        else:
            self.discount_type          = "percent"
            self.discount_type_btn.text = "%"
        self.calculate_total()

    # ─────────────────────────────────────────
    # LOAD SERVICES
    # ─────────────────────────────────────────
    def load_services(self):
        self.services_layout.clear_widgets()
        self.service_hours = {}

        services      = get_services()
        all_materials = get_materials()

        engång  = [s for s in services if s.price_type == "engång"]
        timpris = [s for s in services if s.price_type == "timme"]

        def add_group(label, group):
            if not group:
                return

            self.services_layout.add_widget(CategoryHeader(label))

            for s in group:
                row = ServiceRow(
                    s,
                    toggle_cb=self.create_toggle_callback(s),
                    hours_dict=self.service_hours
                )
                if s.id in self.service_hours:
                    self.service_hours[s.id].bind(
                        text=lambda *a: self.calculate_total()
                    )
                self.services_layout.add_widget(row)

                for mat_id in s.materials:
                    mat = next((m for m in all_materials if m.id == mat_id), None)
                    if mat:
                        sub = MDLabel(
                            text=f"     • {mat.name}  ({mat.price} kr)",
                            size_hint_y=None,
                            height=18,
                            font_style="Caption",
                            theme_text_color="Secondary",
                            halign="left"
                        )
                        sub.bind(size=sub.setter("text_size"))
                        self.services_layout.add_widget(sub)

        add_group("Engångspris", engång)
        add_group("Timpris", timpris)

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

    # ─────────────────────────────────────────
    # TOTAL
    # ─────────────────────────────────────────
    def calculate_total(self):
        subtotal      = 0
        all_materials = get_materials()

        for s in self.selected_services:
            if s.price_type == "engång":
                subtotal += s.price
            else:
                hours = 1
                field = self.service_hours.get(s.id)
                if field:
                    try:
                        hours = float(field.text or 1)
                    except:
                        hours = 1
                subtotal += s.price * hours

            for mat_id in s.materials:
                mat = next((m for m in all_materials if m.id == mat_id), None)
                if mat:
                    subtotal += mat.price

        for m in self.selected_materials:
            subtotal += m.price

        # ── Apply discount ────────────────────────
        discount_amount = 0
        if self.discount_active:
            try:
                val = float(self.discount_input.text or 0)
            except:
                val = 0

            if self.discount_type == "percent":
                discount_amount = subtotal * (val / 100)
            else:
                discount_amount = val

            # clamp — can't discount more than the subtotal
            discount_amount = min(discount_amount, subtotal)
            self.discount_value = val
        else:
            self.discount_value = 0

        total_after_discount = subtotal - discount_amount

        settings        = load_settings()
        moms            = total_after_discount * (settings.get("moms", 25) / 100)
        total_with_moms = total_after_discount + moms

        # Update discount line label
        if discount_amount > 0:
            if self.discount_type == "percent":
                self.discount_line_label.text = (
                    f"Rabatt ({self.discount_value:.0f}%): -{discount_amount:.2f} kr"
                )
            else:
                self.discount_line_label.text = (
                    f"Rabatt: -{discount_amount:.2f} kr"
                )
        else:
            self.discount_line_label.text = ""

        self.total_label.text           = f"Summa: {subtotal:.2f} kr"
        self.moms_label.text            = f"MOMS: {moms:.2f} kr"
        self.total_with_moms_label.text = f"Totalt: {total_with_moms:.2f} kr"

        return subtotal, discount_amount, moms, total_with_moms

    # ─────────────────────────────────────────
    # MATERIAL POPUP
    # ─────────────────────────────────────────
    def open_material_popup(self):
        materials = get_materials()

        layout      = MDBoxLayout(orientation="vertical", padding=10, spacing=8)
        scroll      = MDScrollView()
        list_layout = MDBoxLayout(orientation="vertical", size_hint_y=None, spacing=4)
        list_layout.bind(minimum_height=list_layout.setter("height"))

        self.material_checks = {}

        for m in materials:
            row      = MDBoxLayout(size_hint_y=None, height=42, spacing=8)
            checkbox = MDCheckbox(size_hint_x=None, width=40)
            self.material_checks[m.id] = checkbox
            row.add_widget(checkbox)
            row.add_widget(MDLabel(
                text=f"{m.name}  ({m.price} kr)",
                theme_text_color="Primary"
            ))
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
            size_hint=(0.9, 0.75),
            background="",
            background_color=(1, 1, 1, 1),
            title_color=(0, 0, 0, 1),
            separator_color=(0.2, 0.45, 0.75, 1)
        )
        popup.open()

    def apply_materials(self, popup):
        materials               = get_materials()
        self.selected_materials = [
            m for m in materials if self.material_checks[m.id].active
        ]
        popup.dismiss()
        self.calculate_total()

    # ─────────────────────────────────────────
    # PREVIEW
    # ─────────────────────────────────────────
    def show_preview(self):
        services_data, subtotal, discount_amount, moms, total_with_moms = self.build_invoice_data()
        settings = load_settings()

        from datetime import datetime
        offert_nr = datetime.now().strftime("%Y%m%d%H%M")
        date_str  = datetime.now().strftime("%Y-%m-%d")

        popup = Popup(
            title="Förhandsvisning",
            size_hint=(0.97, 0.97),
            background="",
            background_color=(0.95, 0.95, 0.95, 1),
            title_color=(0, 0, 0, 1),
            separator_color=(0.2, 0.45, 0.75, 1)
        )

        outer_scroll = MDScrollView()

        card = WhiteCard(
            orientation="vertical",
            padding=24,
            spacing=10,
            size_hint_y=None
        )
        card.bind(minimum_height=card.setter("height"))

        def lbl(text, size=13, bold=False, color=(0, 0, 0, 1), halign="left", height=22):
            l = MDLabel(
                text=text,
                font_size=size,
                bold=bold,
                theme_text_color="Custom",
                text_color=color,
                halign=halign,
                valign="middle",
                size_hint_y=None,
                height=height
            )
            l.bind(size=l.setter("text_size"))
            return l

        # Header
        card.add_widget(lbl(settings.get("company_name", ""), size=16, bold=True, height=28))
        card.add_widget(lbl(settings.get("address", ""),      size=11, color=(0.3, 0.3, 0.3, 1)))
        card.add_widget(lbl(settings.get("phone", ""),        size=11, color=(0.3, 0.3, 0.3, 1)))
        card.add_widget(lbl(settings.get("email", ""),        size=11, color=(0.3, 0.3, 0.3, 1)))
        card.add_widget(Divider(color=(0, 0, 0, 1)))

        # Offert nr + date
        card.add_widget(lbl(f"OFFERT #{offert_nr}", size=15, bold=True, height=26))
        card.add_widget(lbl(f"Datum: {date_str}", size=11, color=(0.4, 0.4, 0.4, 1)))
        card.add_widget(Widget(size_hint_y=None, height=8))

        # Table
        card.add_widget(TableRow(
            "Tjänst", "Antal", "Pris", "Summa",
            is_header=True, bg_color=(0.1, 0.1, 0.1, 1)
        ))

        for i, s in enumerate(services_data):
            row_bg = (0.96, 0.96, 0.96, 1) if i % 2 == 0 else (1, 1, 1, 1)
            antal  = "-" if s["hours"] == "-" else f"{s['hours']} h"
            pris   = (f"{s['unit_price']:.2f} kr" if s["hours"] == "-"
                      else f"{s['unit_price']:.2f} kr/h")

            card.add_widget(TableRow(
                s["name"], antal, pris, f"{s['service_subtotal']:.2f} kr",
                bg_color=row_bg
            ))
            for mat in s["materials"]:
                card.add_widget(MaterialRow(mat.name, mat.price))

        if self.selected_materials:
            card.add_widget(TableRow(
                "Övrigt material", "", "", "",
                bg_color=(0.93, 0.93, 0.93, 1)
            ))
            for mat in self.selected_materials:
                card.add_widget(MaterialRow(mat.name, mat.price))

        card.add_widget(Divider())

        # Totals
        moms_pct   = settings.get("moms", 25)
        totals_box = MDBoxLayout(
            orientation="vertical", size_hint_y=None,
            height=80 + (22 if discount_amount > 0 else 0),
            padding=[0, 4, 0, 4], spacing=4
        )
        totals_box.add_widget(lbl(f"Summa:  {subtotal:.2f} kr",
                                   size=12, halign="right", height=20))

        if discount_amount > 0:
            if self.discount_type == "percent":
                disc_text = f"Rabatt ({self.discount_value:.0f}%):  -{discount_amount:.2f} kr"
            else:
                disc_text = f"Rabatt:  -{discount_amount:.2f} kr"
            totals_box.add_widget(lbl(disc_text,
                                      size=12, halign="right", height=20,
                                      color=(0.8, 0.1, 0.1, 1)))

        totals_box.add_widget(lbl(f"MOMS ({moms_pct}%):  {moms:.2f} kr",
                                   size=12, halign="right", height=20))
        totals_box.add_widget(lbl(f"Totalt:  {total_with_moms:.2f} kr",
                                   size=14, bold=True, halign="right", height=26))
        card.add_widget(totals_box)

        card.add_widget(Divider())
        card.add_widget(Widget(size_hint_y=None, height=8))

        # Payment
        card.add_widget(lbl("Betalningsvillkor", size=12, bold=True, height=22))
        card.add_widget(lbl(
            settings.get("payment_terms", "30 dagar netto"),
            size=11, color=(0.3, 0.3, 0.3, 1)
        ))
        if settings.get("payment_info"):
            card.add_widget(lbl(
                settings.get("payment_info", ""),
                size=11, color=(0.3, 0.3, 0.3, 1)
            ))

        card.add_widget(Widget(size_hint_y=None, height=16))
        card.add_widget(Divider())

        # Footer
        card.add_widget(lbl(
            f"{settings.get('company_name','')}  |  "
            f"{settings.get('email','')}  |  "
            f"{settings.get('phone','')}",
            size=10, color=(0.5, 0.5, 0.5, 1), halign="center", height=20
        ))
        card.add_widget(Widget(size_hint_y=None, height=16))

        # Buttons
        btn_row = MDBoxLayout(size_hint_y=None, height=50, spacing=10)
        btn_row.add_widget(MDRaisedButton(
            text="Avbryt",
            on_release=lambda x: popup.dismiss()
        ))
        btn_row.add_widget(MDRaisedButton(
            text="Skapa PDF",
            on_release=lambda x: self.confirm_pdf(popup)
        ))
        card.add_widget(btn_row)

        outer_scroll.add_widget(card)
        popup.content = outer_scroll
        popup.open()

    def confirm_pdf(self, popup):
        popup.dismiss()
        subtotal, discount_amount, moms, total_with_moms = self.calculate_total()[0], \
            self.calculate_total()[1], self.calculate_total()[2], self.calculate_total()[3]

        filename = generate_pdf(
            self.selected_services,
            subtotal,
            moms,
            total_with_moms,
            self.service_hours,
            self.discount_value,
            self.discount_type
        )
        import os, platform
        if platform.system() == "Windows":
            os.startfile(filename)

    def go_back(self):
        self.manager.current = "home"

    # ─────────────────────────────────────────
    # BUILD INVOICE DATA
    # ─────────────────────────────────────────
    def build_invoice_data(self):
        services_data = []
        subtotal      = 0
        all_materials = get_materials()

        for s in self.selected_services:
            if s.price_type == "engång":
                hours            = "-"
                service_subtotal = s.price
            else:
                field = self.service_hours.get(s.id)
                try:
                    hours = float(field.text or 1)
                except:
                    hours = 1
                service_subtotal = s.price * hours

            materials_list = []
            for mat_id in s.materials:
                mat = next((m for m in all_materials if m.id == mat_id), None)
                if mat:
                    materials_list.append(mat)
                    service_subtotal += mat.price

            subtotal += service_subtotal
            services_data.append({
                "name":             s.name,
                "hours":            hours,
                "unit_price":       s.price,
                "service_subtotal": service_subtotal,
                "materials":        materials_list
            })

        for m in self.selected_materials:
            subtotal += m.price

        # ── Discount ──────────────────────────────
        discount_amount = 0
        if self.discount_active:
            try:
                val = float(self.discount_input.text or 0)
            except:
                val = 0
            if self.discount_type == "percent":
                discount_amount = subtotal * (val / 100)
            else:
                discount_amount = val
            discount_amount = min(discount_amount, subtotal)

        total_after_discount = subtotal - discount_amount

        settings        = load_settings()
        moms            = total_after_discount * (settings.get("moms", 25) / 100)
        total_with_moms = total_after_discount + moms

        return services_data, subtotal, discount_amount, moms, total_with_moms