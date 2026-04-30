from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager

from screens.home_screen import HomeScreen
from screens.quote_screen import QuoteScreen
from screens.services_screen import ServicesScreen
from screens.materials_screen import MaterialsScreen
from screens.company_info_screen import CompanyInfoScreen
from screens.gamla_offerter_screen import GamlaOfferterScreen
from screens.installningar_screen import InstallningarScreen

from services import create_table
from materials import create_table as create_material_table


class OffertApp(MDApp):

    def build(self):
        self.theme_cls.primary_palette = "Blue"

        create_table()
        create_material_table()

        sm = ScreenManager()

        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(QuoteScreen(name="quote"))
        sm.add_widget(ServicesScreen(name="services"))
        sm.add_widget(MaterialsScreen(name="materials"))
        sm.add_widget(CompanyInfoScreen(name="settings"))
        sm.add_widget(GamlaOfferterScreen(name="gamla_offerter"))
        sm.add_widget(InstallningarScreen(name="installningar"))

        return sm


if __name__ == "__main__":
    OffertApp().run()