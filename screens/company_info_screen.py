import os
import sys

from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle
from kivy.uix.widget import Widget
from PIL import Image as PILImage

from company_info import load_settings, save_settings


def get_data_dir():
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
        base = os.path.dirname(base)

    data_dir = os.path.join(base, "data")
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


LOGO_WIDTH  = 132
LOGO_HEIGHT = 68

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp"}


# ── Simple white-background row widget ────────────────────
class BrowserRow(MDBoxLayout):
    def __init__(self, text, icon, on_tap, selected=False, **kwargs):
        super().__init__(
            orientation="horizontal",
            size_hint_y=None,
            height=40,
            spacing=8,
            padding=[8, 0, 8, 0],
            **kwargs
        )

        bg = (0.85, 0.92, 1.0, 1) if selected else (1, 1, 1, 1)
        with self.canvas.before:
            Color(*bg)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._upd, size=self._upd)

        icon_lbl = MDLabel(
            text=icon,
            size_hint_x=None,
            width=28,
            theme_text_color="Custom",
            text_color=(0.2, 0.2, 0.2, 1),
            halign="center",
            valign="middle"
        )
        icon_lbl.bind(size=icon_lbl.setter("text_size"))

        name_lbl = MDLabel(
            text=text,
            theme_text_color="Custom",
            text_color=(0, 0, 0, 1),
            halign="left",
            valign="middle"
        )
        name_lbl.bind(size=name_lbl.setter("text_size"))

        self.add_widget(icon_lbl)
        self.add_widget(name_lbl)

        self.bind(on_touch_up=lambda w, t: on_tap() if w.collide_point(*t.pos) else None)

    def _upd(self, *args):
        self._bg.pos  = self.pos
        self._bg.size = self.size


class Divider(Widget):
    def __init__(self, **kwargs):
        super().__init__(size_hint_y=None, height=1, **kwargs)
        with self.canvas:
            Color(0.88, 0.88, 0.88, 1)
            self._line = Rectangle(pos=self.pos, size=(self.width, 1))
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *args):
        self._line.pos  = self.pos
        self._line.size = (self.width, 1)


class CompanyInfoScreen(MDScreen):

    def on_enter(self):
        self.settings = load_settings()
        self.build_ui()

    # ─────────────────────────────────────────
    # UI
    # ─────────────────────────────────────────
    def build_ui(self):
        self.clear_widgets()

        outer_scroll = MDScrollView()

        layout = MDBoxLayout(
            orientation="vertical",
            padding=16,
            spacing=12,
            size_hint_y=None
        )
        layout.bind(minimum_height=layout.setter("height"))

        layout.add_widget(MDLabel(
            text="Företags Information",
            bold=True,
            font_size=18,
            size_hint_y=None,
            height=36,
            halign="center"
        ))

        # ── Text fields ───────────────────────────
        self.name_field    = MDTextField(hint_text="Företagsnamn",      text=self.settings.get("company_name", ""))
        self.address       = MDTextField(hint_text="Adress",            text=self.settings.get("address", ""))
        self.phone         = MDTextField(hint_text="Telefon",           text=self.settings.get("phone", ""))
        self.email         = MDTextField(hint_text="Email",             text=self.settings.get("email", ""))
        self.moms          = MDTextField(hint_text="MOMS (%)",          text=str(self.settings.get("moms", 25)))
        self.payment_info  = MDTextField(hint_text="Betalningsinfo (konto, swish etc)", text=self.settings.get("payment_info", ""))
        self.payment_terms = MDTextField(hint_text="Betalningsvillkor", text=self.settings.get("payment_terms", ""))

        for field in [
            self.name_field, self.address, self.phone, self.email,
            self.moms, self.payment_info, self.payment_terms
        ]:
            layout.add_widget(field)

        # ── Logo section ──────────────────────────
        layout.add_widget(MDLabel(
            text="Företagslogga",
            bold=True,
            size_hint_y=None,
            height=28
        ))

        self.logo_preview = Image(
            size_hint=(None, None),
            size=(LOGO_WIDTH * 2, LOGO_HEIGHT * 2),
            pos_hint={"center_x": 0.5},
            allow_stretch=True,
            keep_ratio=True
        )
        self._refresh_logo_preview()
        layout.add_widget(self.logo_preview)

        self.logo_status = MDLabel(
            text=self._logo_status_text(),
            halign="center",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=24
        )
        layout.add_widget(self.logo_status)

        logo_btn_row = MDBoxLayout(size_hint_y=None, height=48, spacing=10)
        logo_btn_row.add_widget(MDRaisedButton(
            text="Välj logga",
            on_release=lambda x: self.open_file_browser()
        ))
        self.remove_logo_btn = MDRaisedButton(
            text="Ta bort logga",
            md_bg_color=(0.8, 0.1, 0.1, 1),
            on_release=lambda x: self.remove_logo(),
            disabled=not bool(self.settings.get("logo_path"))
        )
        logo_btn_row.add_widget(self.remove_logo_btn)
        layout.add_widget(logo_btn_row)

        # ── Save / back ───────────────────────────
        layout.add_widget(MDRaisedButton(
            text="Spara",
            pos_hint={"center_x": 0.5},
            size_hint_x=0.6,
            on_release=lambda x: self.save()
        ))
        layout.add_widget(MDRaisedButton(
            text="Tillbaka",
            pos_hint={"center_x": 0.5},
            size_hint_x=0.6,
            on_release=lambda x: self.go_back()
        ))

        outer_scroll.add_widget(layout)
        self.add_widget(outer_scroll)

    # ─────────────────────────────────────────
    # LOGO HELPERS
    # ─────────────────────────────────────────
    def _logo_status_text(self):
        path = self.settings.get("logo_path", "")
        if path and os.path.exists(path):
            return f"Logga: {os.path.basename(path)}"
        return "Ingen logga uppladdad"

    def _refresh_logo_preview(self):
        path = self.settings.get("logo_path", "")
        if path and os.path.exists(path):
            self.logo_preview.source  = path
            self.logo_preview.opacity = 1
        else:
            self.logo_preview.source  = ""
            self.logo_preview.opacity = 0

    # ─────────────────────────────────────────
    # CUSTOM FILE BROWSER
    # ─────────────────────────────────────────
    def open_file_browser(self):
        self._browser_path     = os.path.expanduser("~")
        self._selected_file    = None

        # ── Popup shell ──────────────────────────
        self._browser_popup = Popup(
            title="Välj logga",
            size_hint=(0.95, 0.92),
            background="",
            background_color=(1, 1, 1, 1),
            title_color=(0, 0, 0, 1),
            separator_color=(0.2, 0.45, 0.75, 1)
        )

        outer = MDBoxLayout(orientation="vertical", spacing=6, padding=6)

        # ── Path bar ──────────────────────────────
        self._path_label = MDLabel(
            text=self._browser_path,
            size_hint_y=None,
            height=26,
            font_size=11,
            theme_text_color="Custom",
            text_color=(0.3, 0.3, 0.3, 1),
            halign="left",
            shorten=True,
            shorten_from="left"
        )
        self._path_label.bind(size=self._path_label.setter("text_size"))
        outer.add_widget(self._path_label)
        outer.add_widget(Divider())

        # ── File list (scrollable) ────────────────
        self._file_scroll = MDScrollView(size_hint=(1, 1))
        self._file_list   = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=1
        )
        self._file_list.bind(minimum_height=self._file_list.setter("height"))

        self._file_scroll.add_widget(self._file_list)
        outer.add_widget(self._file_scroll)

        outer.add_widget(Divider())

        # ── Selected file bar ─────────────────────
        self._sel_label = MDLabel(
            text="Ingen fil vald",
            size_hint_y=None,
            height=26,
            font_size=12,
            bold=True,
            theme_text_color="Custom",
            text_color=(0.1, 0.4, 0.8, 1),
            halign="left"
        )
        self._sel_label.bind(size=self._sel_label.setter("text_size"))
        outer.add_widget(self._sel_label)

        # ── Buttons ───────────────────────────────
        btn_row = MDBoxLayout(size_hint_y=None, height=50, spacing=10)
        btn_row.add_widget(MDRaisedButton(
            text="Avbryt",
            on_release=lambda x: self._browser_popup.dismiss()
        ))
        btn_row.add_widget(MDRaisedButton(
            text="Välj",
            on_release=lambda x: self._confirm_file()
        ))
        outer.add_widget(btn_row)

        self._browser_popup.content = outer
        self._browser_popup.open()

        # Populate initial directory
        self._populate_browser(self._browser_path)

    def _populate_browser(self, path):
        self._browser_path       = path
        self._path_label.text    = path
        self._selected_file      = None
        self._sel_label.text     = "Ingen fil vald"
        self._file_list.clear_widgets()

        # ── Up one level ──────────────────────────
        parent = os.path.dirname(path)
        if parent != path:
            self._file_list.add_widget(BrowserRow(
                text=".. (upp en nivå)",
                icon="⬆",
                on_tap=lambda: self._populate_browser(parent)
            ))
            self._file_list.add_widget(Divider())

        try:
            entries = sorted(os.scandir(path), key=lambda e: (not e.is_dir(), e.name.lower()))
        except PermissionError:
            self._file_list.add_widget(MDLabel(
                text="Ingen åtkomst till den här mappen.",
                theme_text_color="Custom",
                text_color=(0.8, 0.1, 0.1, 1),
                size_hint_y=None,
                height=40,
                halign="center"
            ))
            return

        for entry in entries:
            if entry.name.startswith("."):
                continue

            if entry.is_dir():
                name = entry.name
                full = entry.path
                self._file_list.add_widget(BrowserRow(
                    text=name,
                    icon="📁",
                    on_tap=lambda p=full: self._populate_browser(p)
                ))
                self._file_list.add_widget(Divider())

            elif entry.is_file():
                ext = os.path.splitext(entry.name)[1].lower()
                if ext in IMAGE_EXTENSIONS:
                    name = entry.name
                    full = entry.path
                    self._file_list.add_widget(BrowserRow(
                        text=name,
                        icon="🖼",
                        on_tap=lambda p=full, n=name: self._select_file(p, n)
                    ))
                    self._file_list.add_widget(Divider())

        if not self._file_list.children:
            self._file_list.add_widget(MDLabel(
                text="Inga bildfiler hittades i den här mappen.",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=40,
                halign="center"
            ))

    def _select_file(self, filepath, filename):
        self._selected_file   = filepath
        self._sel_label.text  = f"Vald: {filename}"

    def _confirm_file(self):
        if not self._selected_file:
            return
        self._browser_popup.dismiss()
        self.process_and_save_logo(self._selected_file)

    # ─────────────────────────────────────────
    # PROCESS LOGO
    # ─────────────────────────────────────────
    def process_and_save_logo(self, src_path):
        try:
            img = PILImage.open(src_path).convert("RGBA")
            img.thumbnail((LOGO_WIDTH, LOGO_HEIGHT), PILImage.LANCZOS)

            background = PILImage.new("RGBA", (LOGO_WIDTH, LOGO_HEIGHT), (255, 255, 255, 0))
            offset = (
                (LOGO_WIDTH  - img.width)  // 2,
                (LOGO_HEIGHT - img.height) // 2
            )
            background.paste(img, offset, img)

            dest_path = os.path.join(get_data_dir(), "logo.png")
            background.save(dest_path, "PNG")

            self.settings["logo_path"]    = dest_path
            self.logo_preview.source      = dest_path
            self.logo_preview.reload()
            self.logo_preview.opacity     = 1
            self.logo_status.text         = "Logga: logo.png"
            self.remove_logo_btn.disabled = False

        except Exception as e:
            self.logo_status.text = f"Fel vid uppladdning: {e}"

    # ─────────────────────────────────────────
    # REMOVE LOGO
    # ─────────────────────────────────────────
    def remove_logo(self):
        logo_path = self.settings.get("logo_path", "")
        if logo_path and os.path.exists(logo_path):
            try:
                os.remove(logo_path)
            except Exception:
                pass

        self.settings["logo_path"]    = ""
        self.logo_preview.source      = ""
        self.logo_preview.opacity     = 0
        self.logo_status.text         = "Ingen logga uppladdad"
        self.remove_logo_btn.disabled = True

    # ─────────────────────────────────────────
    # SAVE
    # ─────────────────────────────────────────
    def save(self):
        data = {
            "company_name":  self.name_field.text,
            "address":       self.address.text,
            "phone":         self.phone.text,
            "email":         self.email.text,
            "logo_path":     self.settings.get("logo_path", ""),
            "moms":          float(self.moms.text or 25),
            "payment_info":  self.payment_info.text,
            "payment_terms": self.payment_terms.text,
            "qr_path":       self.settings.get("qr_path", "")
        }
        save_settings(data)
        self.logo_status.text = "Sparat!"

    def go_back(self):
        self.manager.current = "home"