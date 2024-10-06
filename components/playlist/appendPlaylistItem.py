from kivy.lang import Builder
from kivy.properties import StringProperty
from kivymd.uix.card import MDCard

kv = """
<Add_Item>:
    orientation: "vertical"
    spacing: 5
    radius: 5
    height: "40dp"
    size_hint_y: None
    on_press: app.manager.add_playlist_Item(root.name)
    MDBoxLayout:
        root_id: root_id
        orientation: "horizontal"
        padding: [5, 0, 0, 0]
        MDIcon:
            icon: "playlist-music-outline"
            font_size: "30dp"
            pos_hint: {"center_x": .5, "center_y": .5}
        MDLabel:
            id: root_id
            text: str(root.name)
            size_hint: 1, 1
            padding: [5, 0, 5, 0]
            halign: "left"
            font_size: 14
"""
Builder.load_string(kv)
item_list = {}
class Add_Item(MDCard):
    name = StringProperty()
