from kivy.lang import Builder
from kivy.properties import StringProperty
from kivymd.uix.boxlayout import MDBoxLayout

kv = """
<Playlist_popup>:
    textField_id: textField_id
    orientation: "vertical"
    padding: [10, 0, 10, 5]
    spacing: 5
    MDTextField:
        id: textField_id
        text: "<inconnu>"
        mode: 'rectangle'
        multiline: False
    MDRaisedButton:
        text: "Créer"
        size_hint: 1, .0
        pos_hint: {"center_x": .5, "center_y": .5}
        on_press:
            app.manager.create_playlist_tile(textField_id.text)
            self.parent.parent.parent.parent.dismiss()

<Add_Items>:
    MDBoxLayout:
        orientation: "horizontal"
        padding: [3, 10, 5, 5]
        spacing: 7
        MDIcon:
            icon: "music"
            font_size: "30dp"
            color: 0, 1, 0, .3
            pos_hint: {"center_x": .5, "center_y": .5}
        MDLabel:
            text: str(root.music_name)
            halign: "left"
            valign: "center"
            font_size: 14
        MDIconButton:
            icon: "check-circle"
            size_hint: .1, 1
            _no_ripple_effect: True
            on_press: app.manager.init_playlist_Items([root.music_name, root.playlist_name])

"""
Builder.load_string(kv)

class Playlist_popup(MDBoxLayout):
    pass

class Add_Items(MDBoxLayout):
    music_name = StringProperty()
    playlist_name = StringProperty()