import os
import sys
import platform

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle
from kivy.uix.widget import Widget


def get_archive_dir():
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
        # screens/ is one level down — go up to project root
        base = os.path.dirname(base)

    archive = os.path.join(base, "gamla_offerter")
    os.makedirs(archive, exist_ok=True)
    return archive


class Divider(Widget):
    def __init__(self, color=(0.85, 0.85, 0.85, 1), **kwargs):
        super().__init__(size_hint_y=None, height=1, **kwargs)
        with self.canvas:
            Color(*color)
            self._line = Rectangle(pos=self.pos, size=(self.width, 1))
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *args):
        self._line.pos  = self.pos
        self._line.size = (self.width, 1)


class GamlaOfferterScreen(MDScreen):

    def on_enter(self):
        self.build_ui()

    # ─────────────────────────────────────────
    # UI
    # ─────────────────────────────────────────
    def build_ui(self):
        self.clear_widgets()

        root = MDBoxLayout(orientation="vertical", padding=10, spacing=8)

        # ── Title ─────────────────────────────────
        title = MDLabel(
            text="Gamla Offerter",
            bold=True,
            font_size=18,
            size_hint_y=None,
            height=36,
            halign="center"
        )
        root.add_widget(title)
        root.add_widget(Divider(color=(0, 0, 0, 1)))

        # ── Scrollable list ───────────────────────
        scroll = MDScrollView(size_hint=(1, 1))

        self.list_layout = MDBoxLayout(
            orientation="vertical",
            spacing=6,
            size_hint_y=None,
            padding=[0, 6, 0, 6]
        )
        self.list_layout.bind(minimum_height=self.list_layout.setter("height"))

        scroll.add_widget(self.list_layout)
        root.add_widget(scroll)

        # ── Bottom buttons ────────────────────────
        bottom = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=50,
            spacing=10,
            padding=[10, 0, 10, 0]
        )

        bottom.add_widget(MDRaisedButton(
            text="Rensa alla",
            md_bg_color=(0.8, 0.1, 0.1, 1),
            on_release=lambda x: self.confirm_delete_all()
        ))

        bottom.add_widget(MDRaisedButton(
            text="Tillbaka",
            on_release=lambda x: self.go_back()
        ))

        root.add_widget(bottom)
        self.add_widget(root)

        self.load_invoices()

    # ─────────────────────────────────────────
    # LOAD LIST
    # ─────────────────────────────────────────
    def load_invoices(self):
        self.list_layout.clear_widgets()

        archive_dir = get_archive_dir()
        files       = sorted(
            [f for f in os.listdir(archive_dir) if f.endswith(".pdf")],
            reverse=True   # newest first
        )

        if not files:
            self.list_layout.add_widget(MDLabel(
                text="Inga sparade offerter.",
                halign="center",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=40
            ))
            return

        for filename in files:
            filepath = os.path.join(archive_dir, filename)

            row = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=48,
                spacing=8,
                padding=[4, 0, 4, 0]
            )

            # ── Display name: strip prefix and extension ──
            display = filename.replace("offert_", "").replace(".pdf", "")
            # format "20250430_143022" → "2025-04-30  14:30:22"
            try:
                date_part, time_part = display.split("_")
                display = (
                    f"{date_part[:4]}-{date_part[4:6]}-{date_part[6:]}  "
                    f"{time_part[:2]}:{time_part[2:4]}:{time_part[4:]}"
                )
            except Exception:
                pass   # keep raw name if parsing fails

            name_lbl = MDLabel(
                text=display,
                size_hint_x=1,
                halign="left",
                valign="middle"
            )
            name_lbl.bind(size=name_lbl.setter("text_size"))

            open_btn = MDRaisedButton(
                text="Visa",
                size_hint_x=None,
                width=70,
                on_release=lambda x, fp=filepath: self.open_pdf(fp)
            )

            delete_btn = MDRaisedButton(
                text="Ta bort",
                size_hint_x=None,
                width=90,
                md_bg_color=(0.8, 0.1, 0.1, 1),
                on_release=lambda x, fp=filepath, fn=filename: self.confirm_delete_one(fp, fn)
            )

            row.add_widget(name_lbl)
            row.add_widget(open_btn)
            row.add_widget(delete_btn)

            self.list_layout.add_widget(row)
            self.list_layout.add_widget(Divider())

    # ─────────────────────────────────────────
    # OPEN PDF
    # ─────────────────────────────────────────
    def open_pdf(self, filepath):
        if not os.path.exists(filepath):
            self.show_message("Filen hittades inte.")
            return

        if platform.system() == "Windows":
            os.startfile(filepath)
        elif platform.system() == "Darwin":
            os.system(f'open "{filepath}"')
        else:
            os.system(f'xdg-open "{filepath}"')

    # ─────────────────────────────────────────
    # DELETE ONE — confirm popup
    # ─────────────────────────────────────────
    def confirm_delete_one(self, filepath, filename):
        layout = MDBoxLayout(orientation="vertical", padding=16, spacing=12)

        layout.add_widget(MDLabel(
            text=f"Ta bort\n{filename}?",
            halign="center",
            size_hint_y=None,
            height=60
        ))

        btn_row = MDBoxLayout(size_hint_y=None, height=50, spacing=10)

        popup = Popup(
            title="Bekräfta",
            content=layout,
            size_hint=(0.8, 0.35),
            background="",
            background_color=(1, 1, 1, 1),
            title_color=(0, 0, 0, 1),
            separator_color=(0.8, 0.1, 0.1, 1)
        )

        btn_row.add_widget(MDRaisedButton(
            text="Avbryt",
            on_release=lambda x: popup.dismiss()
        ))
        btn_row.add_widget(MDRaisedButton(
            text="Ta bort",
            md_bg_color=(0.8, 0.1, 0.1, 1),
            on_release=lambda x: self.delete_one(filepath, popup)
        ))

        layout.add_widget(btn_row)
        popup.open()

    def delete_one(self, filepath, popup):
        popup.dismiss()
        try:
            os.remove(filepath)
        except Exception as e:
            self.show_message(f"Kunde inte ta bort filen:\n{e}")
            return
        self.load_invoices()

    # ─────────────────────────────────────────
    # DELETE ALL — confirm popup
    # ─────────────────────────────────────────
    def confirm_delete_all(self):
        archive_dir = get_archive_dir()
        files       = [f for f in os.listdir(archive_dir) if f.endswith(".pdf")]

        if not files:
            self.show_message("Inga offerter att rensa.")
            return

        layout = MDBoxLayout(orientation="vertical", padding=16, spacing=12)

        layout.add_widget(MDLabel(
            text=f"Är du säker? Detta tar bort\nalla {len(files)} sparade offerter.",
            halign="center",
            size_hint_y=None,
            height=60
        ))

        btn_row = MDBoxLayout(size_hint_y=None, height=50, spacing=10)

        popup = Popup(
            title="Rensa alla",
            content=layout,
            size_hint=(0.8, 0.35),
            background="",
            background_color=(1, 1, 1, 1),
            title_color=(0, 0, 0, 1),
            separator_color=(0.8, 0.1, 0.1, 1)
        )

        btn_row.add_widget(MDRaisedButton(
            text="Avbryt",
            on_release=lambda x: popup.dismiss()
        ))
        btn_row.add_widget(MDRaisedButton(
            text="Rensa alla",
            md_bg_color=(0.8, 0.1, 0.1, 1),
            on_release=lambda x: self.delete_all(popup)
        ))

        layout.add_widget(btn_row)
        popup.open()

    def delete_all(self, popup):
        popup.dismiss()
        archive_dir = get_archive_dir()

        for f in os.listdir(archive_dir):
            if f.endswith(".pdf"):
                try:
                    os.remove(os.path.join(archive_dir, f))
                except Exception:
                    pass

        self.load_invoices()

    # ─────────────────────────────────────────
    # SIMPLE MESSAGE POPUP
    # ─────────────────────────────────────────
    def show_message(self, text):
        layout = MDBoxLayout(orientation="vertical", padding=16, spacing=12)
        layout.add_widget(MDLabel(
            text=text,
            halign="center",
            size_hint_y=None,
            height=60
        ))

        popup = Popup(
            title="Info",
            content=layout,
            size_hint=(0.75, 0.3),
            background="",
            background_color=(1, 1, 1, 1),
            title_color=(0, 0, 0, 1),
            separator_color=(0.2, 0.45, 0.75, 1)
        )

        layout.add_widget(MDRaisedButton(
            text="OK",
            pos_hint={"center_x": 0.5},
            size_hint_x=0.4,
            on_release=lambda x: popup.dismiss()
        ))

        popup.open()

    def go_back(self):
        self.manager.current = "home"