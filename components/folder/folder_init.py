from kivy.lang import Builder
from kivy.properties import StringProperty
from kivymd.uix.card import MDCard

kv = """
<Folder_layout>:
    orientation: "vertical"
    spacing: 5
    padding: 0
    radius: 3
    elevation: 0
    height: "50dp"
    size_hint_y: None
    on_press: app.manager.init_folder_content(root.folder_name)
    MDBoxLayout:
        orientation: "horizontal"
        padding: [5, 0, 5, 0]
        spacing: 10
        MDIcon:
            icon: "folder-music"
            font_size: "35dp"
            pos_hint: {"center_x": .5, "center_y": .5}
        MDLabel:
            size_hint: 1, 1
            halign: "left"
            bold: True
            font_size: 13
            text: str(root.folder_name)


"""
Builder.load_string(kv)
folder_music_list = list()
folder_music_dictionary = dict()
class Folder_layout(MDCard):
    folder_name = StringProperty()