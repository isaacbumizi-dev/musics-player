from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivymd.uix.card import MDCard

Kv = """
<MenuTile>:
    size_hint_y: None
    height: "200dp"
    md_bg_color: 0, 1, 0, .3
    padding: 0.5
    radius: 3
    on_press: 
        app.manager.change_background_theme(root.tile_image)
        app.manager.pop()
    FitImage:
        source: root.tile_image
        radius: 3
"""
Builder.load_string(Kv)
theme_tile_list = []
class MenuTile(MDCard):
    tile_image = ObjectProperty()