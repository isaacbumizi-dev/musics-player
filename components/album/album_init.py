from kivy.lang import Builder
from kivy.properties import StringProperty
from kivymd.uix.card import MDCard

kv = """
<Album_layout>:
    orientation: "vertical"
    radius: 5
    spacing: 5
    elevation: 0
    padding: 0
    size_hint_y: None
    height: "200dp"
    on_press: app.manager.init_album_screen(root.album_name)
    MDBoxLayout:
        orientation: "vertical"
        FitImage:
            source: root.album_picture
            radius: [5, 5, 0, 0]
        MDLabel:
            size_hint: 1, 1
            padding: [7, 0, 7, 0]
            text: str(root.album_name)
            halign: "left"
            bold: True
            font_size: 12
"""
Builder.load_string(kv)
album_music_dictionnary = dict()
class Album_layout(MDCard):
    album_picture = StringProperty()
    album_name = StringProperty()