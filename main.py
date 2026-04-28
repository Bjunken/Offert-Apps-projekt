from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager

# 📦 Screens
from screens.home_screen import HomeScreen
from screens.quote_screen import QuoteScreen
from screens.services_screen import ServicesScreen
from screens.materials_screen import MaterialsScreen
from screens.settings_screen import SettingsScreen

# 🗄 Databas
from services import create_table
from materials import create_table as create_material_table


class OffertApp(MDApp):

    def build(self):
        self.theme_cls.primary_palette = "Blue"

        # 🔥 SKAPA DATABAS TABELLER
        create_table()              # services
        create_material_table()     # materials

        sm = ScreenManager()

        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(QuoteScreen(name="quote"))
        sm.add_widget(ServicesScreen(name="services"))
        sm.add_widget(MaterialsScreen(name="materials"))
        sm.add_widget(SettingsScreen(name="settings"))

        return sm


if __name__ == "__main__":
    OffertApp().run()