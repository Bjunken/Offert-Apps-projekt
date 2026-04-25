from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from screens.quote_screen import QuoteScreen

from kivymd.app import MDApp

from db import init_db
from screens.home_screen import HomeScreen
from screens.services_screen import ServicesScreen
from screens.settings_screen import SettingsScreen

KV = """
ScreenManager:
    HomeScreen:
    ServicesScreen:
"""

class OffertApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"

        init_db()  # initiera databas

        sm = Builder.load_string(KV)
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(ServicesScreen(name="services"))
        sm.add_widget(QuoteScreen(name="quote"))
        sm.add_widget(SettingsScreen(name="settings"))

        return sm

if __name__ == "__main__":
    OffertApp().run()