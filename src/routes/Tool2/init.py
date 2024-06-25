from shiny import ui

from src.layouts.layout_definition import SidebarOptions, BaseLogicView, BasicCardItem, SimpleLayout
from src.utils.base_tab import BaseTab
from src.utils.constants import HTMLBody


class Tab2(BaseTab):
    def __init__(self) -> None:
        super().__init__()

    def init_component(self) -> HTMLBody:
        return self._create_layout()

    def _create_layout(self) -> HTMLBody:
        sidebar: SidebarOptions = SidebarOptions()
        sidebar.add_section("header1", "Header 1")
        sidebar.add_slider("slider1_1", "Slider 1", 0, 100, 50)
        sidebar.add_slider("slider2", "Slider 2", 0, 100, 50)
        sidebar.add_slider("slider3", "Slider 3", 0, 100, 50)
        sidebar.add_slider("slider4", "Slider 4", 0, 100, 50)
        sidebar.add_slider("slider5", "Slider 5", 0, 100, 50)

        logic_view = BaseLogicView("Updated Results", [
            BasicCardItem("Updated Card 12", "This is an updated card 1"),
            BasicCardItem("Updated Card 2", "This is an updated card 2"),
            BasicCardItem("Updated Card 3", "This is an updated card 3"),
            BasicCardItem("Updated Card 4", "This is an updated card 4"),
        ], ui.div(id="plot_view"))

        content = logic_view.apply()
        simple_layout = SimpleLayout(content, sidebar.apply())
        self.component = simple_layout.apply()
        return self.component
