from kivy.lang import Builder
from kivy.properties import StringProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu

kv = """
<Playlist_Layout>:
    orientation: "vertical"
    radius: 3
    spacing: 5
    height: "40dp"
    size_hint_y: None
    on_press:
        app.manager.push("playlistScreen")
        app.manager.init_playlist_content(root.playlist_name)
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
            text: str(root.playlist_name)
            size_hint: 1, 1
            padding: [5, 0, 5, 0]
            halign: "left"
            font_size: 14
        MDIconButton:
            id: playlist_item_menu
            icon: "dots-vertical"
            icon_size: "20dp"
            ripple_alpha: 0.1
            pos_hint: {"center_x": .5, "center_y": .5}
            on_release: root.open_playlist_Item_menu()

<DialogContent>:
    orientation: "vertical"
    spacing: "30dp"
    size_hint_y: None
    height: "80dp"
    MDTextField:
        id: textField_id
        hint_text: "Nouveau nom"
    MDBoxLayout:
        orientation: "horizontal"
        Widget:
        MDFlatButton:
            text: "ANNULER"
            theme_text_color: "Custom"
            text_color: self.theme_cls.primary_color
            on_release: self.parent.parent.parent.parent.parent.dismiss()
        MDFlatButton:
            text: "OK"
            theme_text_color: "Custom"
            text_color: self.theme_cls.primary_color
            on_release:
                app.manager.rename_playlist(textField_id.text, self.parent.parent.parent.parent.parent.title)\
                    if textField_id.text  else None 
                self.parent.parent.parent.parent.parent.dismiss()
                
<Suppress_content>:
    orientation: "vertical"
    orientation: "vertical"
    spacing: "30dp"
    size_hint_y: None
    height: "70dp"
    MDLabel:
        text: "Voulez-vous supprimer cette playlist ?"
    MDBoxLayout:
        orientation: "horizontal"
        Widget:
        MDFlatButton:
            text: "ANNULER"
            theme_text_color: "Custom"
            text_color: self.theme_cls.primary_color
            on_release: self.parent.parent.parent.parent.parent.dismiss()
        MDFlatButton:
            text: "CONFIRMER"
            theme_text_color: "Custom"
            text_color: self.theme_cls.primary_color
            on_release:
                app.manager.delete_playlist(self.parent.parent.parent.parent.parent.title)
                self.parent.parent.parent.parent.parent.dismiss()    
"""
Builder.load_string(kv)
playlist_music_dictionnary = {}
class Playlist_Layout(MDCard):
    playlist_name = StringProperty()

    def open_playlist_Item_menu(self):
        menu_items = [
            {
                "divider": None,
                "text": "Renommer",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.menu_callback("Renommer"),
            },
            {
                "divider": None,
                "text": "Supprimer",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.menu_callback("Supprimer"),
            }
        ]
        Playlist_Layout.menu = MDDropdownMenu(
            caller=self.ids.playlist_item_menu,
            items=menu_items,
            width_mult=3,
            max_height=105,
        )
        Playlist_Layout.menu.open()


    def menu_callback(self, text_item):
        match text_item:
            case "Renommer":
                self.menu.dismiss()
                MDDialog(
                    title=self.playlist_name,
                    auto_dismiss=True,
                    type="custom",
                    content_cls=DialogContent()
                    ).open()
            case "Supprimer":
                self.menu.dismiss()
                MDDialog(
                    title=self.playlist_name,
                    auto_dismiss=True,
                    type="custom",
                    content_cls=Suppress_content()
                ).open()

class DialogContent(MDBoxLayout):
    pass
class Suppress_content(MDBoxLayout):
    pass