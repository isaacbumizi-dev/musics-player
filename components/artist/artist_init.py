from kivy.lang import Builder
from kivy.properties import StringProperty
from kivymd.uix.card import MDCard

kv = """
<Artist_layout>:
    orientation: "vertical"
    radius: 3
    elevation: 0
    size_hint_y: None
    height: "70dp"
    on_press: app.manager.init_artist_screen(root.artist_name)
    MDBoxLayout:
        orientation: "horizontal"
        spacing: 5
        FitImage:
            source: root.artist_picture
            size_hint: .5, 1
            radius: 5
        MDLabel:
            size_hint: 1, 1
            padding: [5, 0, 5, 0]
            text: str(root.artist_name)
            halign: "left"
            bold: True
            font_size: 12

"""
Builder.load_string(kv)
artist_music_dictionnary =  {}
class Artist_layout(MDCard):
    artist_picture = StringProperty()
    artist_name = StringProperty()