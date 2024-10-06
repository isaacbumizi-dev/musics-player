#-----------------------------------------------------------------------------------
# Python 3.10                                                                       |
# Kivy                                                                              |
# pygame                                                                            |
# mutagen                                                                           |
# Kivymd 1.2.0                                                                      |
# Copyright (c), 22/06/2024, Developped by Isaac Bumizi                             |
# ! Pour éxecuter placez des fichiers audio dans le repertoire music(cfr ligne 160) |
#------------------------------------------------------------------------------------

import os
import pygame
import random
import pickle
import pathlib
from typing import Annotated

from mutagen.id3 import ID3
from mutagen.mp3 import MP3
from mutagen.wave import WAVE
from mutagen.flac import FLAC

from screen_manager import MyScreenManager

import components.menu.menu_tile
import components.album.album_init
import components.folder.folder_init
import components.artist.artist_init
import components.playlist.playlist_init
import components.playlist.createPlaylist
import components.playlist.appendPlaylistItem

from kivy.metrics import dp
from kivymd.app import MDApp
from kivy.clock import Clock
from kivy.utils import platform
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivymd.uix.label import MDLabel
from kivy.uix.rst import RstDocument
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.dialog import MDDialog
from kivymd.uix.snackbar import MDSnackbar
from kivy.utils import get_color_from_hex
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import OneLineListItem
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivy.properties import ObjectProperty, StringProperty, NumericProperty, ListProperty


pygame.mixer.init()
if platform == "android":
    reperExec = os.getcwd()
else:
    reperExec = os.path.dirname(os.path.abspath(__file__))
    # reperExec: répertoire temporaire dans lequel l'apk s'execute
formated_path = lambda instance: instance.replace("\\", "/")

class ScrollLabel(OneLineListItem):
    def __init__(self, **kwargs):
        super(ScrollLabel, self).__init__(**kwargs)
        Clock.schedule_interval(self.scroll_text, 0.4)
    def scroll_text(self, *args):
        self.text = self.text[1:] + self.text[0]

class PlaylistCustomOneLineIconListItem(MDBoxLayout):
    music_name = StringProperty()
    playlist_name = StringProperty()

    
class CustomOneLineIconListItem(MDBoxLayout):
    name = StringProperty()

class Tab(MDFloatLayout, MDTabsBase):
    pass

class HomeScreen(MyScreenManager):
    H_OBJECT_NAME = StringProperty(None)
    H_MUSIC_LENGHT = StringProperty(None)
    H_OBJECT_NUMBER = StringProperty(None)
    H_MUSIC_PICTURE = StringProperty(None)
    H_MAX_SLIDER_VALUE = NumericProperty(0)
    H_PLAY_LABEL_OPACITY = NumericProperty(0)
    H_CURRENT_MUSIC_POSITION = NumericProperty(0)
    H_MUSIC_PROGRESSION_TIME = StringProperty("0:00")
    H_CURRENT_MUSIC_PLAYING_LABEL = StringProperty(None)
    H_FAVORITE_ICON_BUTTON = StringProperty("star-outline")
    H_MUSIC_PLAYING_MODE_ICON = StringProperty("shuffle-disabled")
    H_MUSIC_PLAYING_STATE_ICON = StringProperty("pause-circle-outline")
    H_MUSIC_PLAYING_STATE_ICON_SECONDARY = StringProperty("pause")

    MySnackBar = ObjectProperty(None)
    piste_label_opacity = NumericProperty(1)
    album_label_opacity = NumericProperty(1)
    artist_label_opacity = NumericProperty(1)
    favorite_label_opacity = NumericProperty(1)
    playlist_label_opacity = NumericProperty(1)
    playlistItemLabelOpacity = NumericProperty(1)
    background_image = ObjectProperty(formated_path(f"{reperExec}\\images\\bg12.png"))
    background_font = ObjectProperty(formated_path(f"{reperExec}\\font\\font_name.ttf"))
    object_background_image = ObjectProperty(formated_path(f"{reperExec}\\images\\_cover.png"))
    theme_background_image_font = ListProperty(
        [
            formated_path(f"{reperExec}\\images\\bg1.png"),
            formated_path(f"{reperExec}\\images\\bg2.png"),
            formated_path(f"{reperExec}\\images\\bg3.png"),
            formated_path(f"{reperExec}\\images\\bg4.png"),
            formated_path(f"{reperExec}\\images\\bg5.png"),
            formated_path(f"{reperExec}\\images\\bg6.png"),
            formated_path(f"{reperExec}\\images\\bg7.png"),
            formated_path(f"{reperExec}\\images\\bg8.png"),
            formated_path(f"{reperExec}\\images\\bg9.png"),
            formated_path(f"{reperExec}\\images\\bg10.png"),
            formated_path(f"{reperExec}\\images\\bg11.png"),
            formated_path(f"{reperExec}\\images\\bg12.png"),
        ]
    )

    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)

        self.sorted_music_list = []
        self.music_dictionnary = {}
        self.current_music_list = []
        self.current_music_name = None
        self.favorite_music_dictionnary = {}
        self.playingMusic_in_progress = False
        self.musicPlaying_mode = "Boucler Tout"
        self.background_tile_image = [
            formated_path(f"{reperExec}\\images\\_cover.png"),
            formated_path(f"{reperExec}\\images\\_cover.png")
        ]
        """
        L'attribut qui suive nous permet de stocker les propriété des widget des certains éléments
        [0]: Playlist
        [1]: folders
        [2]: album
        [3]: artist 
        """
        self.currentRecycleViewWidget_list = [[],[],[],[]]
        self.lastReadItem = str() # cette variable permet de stocker la dernière piste lue
        self.music_picture_source = formated_path(f"{reperExec}\\images\\_icon.png")

        Clock.schedule_interval(self.update_music_progression, 1.0)


    def on_touch_up(self, touch):
        return None
    def on_touch_move(self, touch):
        return None

    def load_musics_from_disk(self):
        """
        Cette methode se charger de chercher tous les fichiers audio sur le disque et de les ajoutés
        dans le dictionnaire self.music_dictionnary
        :return:
        """
        data_path = "/storage/emulated/0/" if platform == "android" else  f"{os.getenv('USERPROFILE')}/Music/"
        self.music_dictionnary.clear(); self.sorted_music_list.clear()

        for path, dirs, files in os.walk(formated_path(data_path)):
            for file in files:
                if (file[-4:]).lower() in [".mp3", ".wav", ".mid",  ".ogg", "flac"]:
                    self.music_dictionnary[str(file)] = formated_path(f"{path}\\{file}")

                    folder_name = str(path.split("/")[-1])
                    if os.listdir(path) and folder_name not in components.folder.folder_init.folder_music_dictionary:
                        components.folder.folder_init.folder_music_dictionary[str(folder_name)] = path

        self.sorted_music_list = sorted(self.music_dictionnary)
        self.piste_label_opacity = 0 if len(self.sorted_music_list) > 0 else 1

    def sort_recycleView_item(self, dt: str):
        """
        Cette methode se charge de trié les éléments de la recycleView sous l'action du bouton Trié par:
        :param dt: le mode de tri(de a-z ou z-a)
        :return:
        """
        if dt == "nom[z-a]":
            self.ids.id_recycle_view.data = []
            self.sorted_music_list.sort(reverse=True)
            self.init_principalScreen_recycleView_items()
        else:
            self.ids.id_recycle_view.data = []
            self.sorted_music_list.sort(reverse=False)
            self.init_principalScreen_recycleView_items()

    def init_principalScreen_recycleView_items(self):
        """
        Cette methode se charge d'afficher les musiques dans un recycleView à l'ecran principal sous le tab Pistes.:
        :return:
        """
        self.ids.id_recycle_view.data = []
        for name in self.sorted_music_list:
            self.ids.id_recycle_view.data.append(
                {
                    "viewclass": "CustomOneLineIconListItem",
                    "name": name,
                }
            )
    def set_list_recherche_recycleView(self, text: str="", search: bool=False):
        """
        Cette methode se charge de la rechercher l'ajout d'un élément dans un  le recycleView de l'écran recherche
        :param text: le text saisit dans la bare de recherche
        :param search:
        :return:
        """
        def add_recherche_recycleview_item(name):
            self.ids.rv.data.append(
                {
                    "viewclass": "CustomOneLineIconListItem",
                    "name": name
                }
            )
        self.ids.rv.data = []
        for music_name in self.sorted_music_list:
            if search:
                if text.lower() in music_name.lower():
                    add_recherche_recycleview_item(music_name)
            else:
                add_recherche_recycleview_item(music_name)

    def add_favorite_music(self, dt, init_item: bool=False):
        """
        cette methode se charge de l'ajout d'un élément dans la liste de favories
        :param dt: le nom de l'icon de la bouton add-favorite
        :param init_item: Si False il permet d'ajouter un titre dans les favoris et sinon il permet de charger des
                        favoris enregistrer dans un fichier
        :return:
        """
        def add_recherche_recycleview_item(name):
            self.ids.favorite.data.append(
                {
                    "viewclass": "CustomOneLineIconListItem",
                    "name": name
                }
            )

        if init_item is True:
            self.ids.favorite.data = []
            if len(self.favorite_music_dictionnary) > 0:
                self.favorite_label_opacity = 0
                for name in self.favorite_music_dictionnary:
                    if name in self.music_dictionnary:
                        add_recherche_recycleview_item(name)
        else:
            view = {
                'viewclass': 'CustomOneLineIconListItem',
                'name': self.current_music_name
            }
            if dt.icon == "star-outline" and view not in self.ids.favorite.data:
                self.favorite_music_dictionnary[self.current_music_name] = None
                add_recherche_recycleview_item(self.current_music_name)
            elif dt.icon == "star" and view in self.ids.favorite.data:
                del self.favorite_music_dictionnary[self.current_music_name]
                self.ids.favorite.data.remove(view)

            #changement d'Etat de l'icon de l'ajout des favori
            dt.icon_color = [0, 1, 0, 1] if dt.icon_color == [1, 1, 1, 1] else [1, 1, 1, 1]
            self.H_FAVORITE_ICON_BUTTON = "star" if dt.icon_color == [0, 1, 0, 1] else "star-outline"
            self.favorite_label_opacity = 0 if len(self.ids.favorite.data) > 0 else 1
            self.back_up_all_data(type="favori")

    def load_all_album_from_disk(self):
        """
        Cette methode a pour fonction de charger les album et les affihcer sous le tab Album
        :return:
        """
        def add_tile(album_name, music_path):
            try:
                id3 = ID3(music_path)
                for tag in id3.keys():
                    if "APIC" in tag:
                        tile_image = formated_path(f"{reperExec}\\images\\tempExec\\{album_name}.png")
                        with open(tile_image, "wb") as f:
                            f.write(id3[tag].data)
                        self.background_tile_image[0] = tile_image
                        del tile_image
            except:
                self.background_tile_image[0] = self.object_background_image
            finally:
                components.album.album_init.album_music_dictionnary[str(album_name)] = [music_path.split("/")[-1]]
                albumWidget = components.album.album_init.Album_layout(
                        album_name=str(album_name),
                        album_picture=self.background_tile_image[0]
                    )
                self.ids.album_item.add_widget(albumWidget)
                self.currentRecycleViewWidget_list[2].append(albumWidget)
                self.background_tile_image[0] = self.object_background_image

        components.album.album_init.album_music_dictionnary.clear()
        for albumWidget in self.currentRecycleViewWidget_list[2]:
            self.ids.album_item.remove_widget(albumWidget)
        for name in self.music_dictionnary.values():
            try:
                album = ID3(name).get("TALB")
                if album:
                    if str(album) not in components.album.album_init.album_music_dictionnary:
                        add_tile(album, name)
                    else:
                        if name.split("/")[-1] not in components.album.album_init.album_music_dictionnary[str(album)]:
                            components.album.album_init.album_music_dictionnary[str(album)].append(name.split("/")[-1])
                else:
                    if "<inconnu>" not in components.album.album_init.album_music_dictionnary.keys():
                        add_tile("<inconnu>", name)
                    else:
                        if name.split("/")[-1] not in components.album.album_init.album_music_dictionnary[str("<inconnu>")]:
                            components.album.album_init.album_music_dictionnary[str("<inconnu>")].append(name.split("/")[-1])
            except Exception:
                pass
        self.album_label_opacity = 0 if len(components.album.album_init.album_music_dictionnary) > 0 else 1

    def init_album_screen(self, dt):
        """
        Cette methode gere l'ajout des contenu lors de l'ouverture d'un album
        :param dt:
        :return:
        """
        self.H_OBJECT_NAME = dt
        self.ids.album.data = []
        MyScreenManager.push(self,"albumScreen")
        for music_name in components.album.album_init.album_music_dictionnary[dt]:
            self.ids.album.data.append(
                {
                    "viewclass": "CustomOneLineIconListItem",
                    "name": music_name.split("/")[-1]
                }
            )
        self.H_OBJECT_NUMBER = f"{len(self.ids.album.data)} musique(s)"
        self.screenCurrent.clear(); self.screenCurrent = ["AlbumScreen", str(dt)]
    def load_all_artist_from_disk(self):
        """
        Cette methode a pour fonction de charger les artist et les affihcer sous le tab Artist
        :return:
        """

        def add_tile(artist_name, music_path):
            try:
                id3 = ID3(music_path)
                for tag in id3.keys():
                    if "APIC" in tag:
                        tile_image = formated_path(f"{reperExec}\\images\\tempExec\\{artist_name}.png")
                        with open(tile_image, "wb") as f:
                            f.write(id3[tag].data)
                        self.background_tile_image[1] = tile_image
                        del tile_image
            except:
                self.background_tile_image[1] = self.object_background_image
            finally:
                components.artist.artist_init.artist_music_dictionnary[str(artist_name)] = [music_path.split("/")[-1]]
                widget =  components.artist.artist_init.Artist_layout(
                        artist_name=str(artist_name),
                        artist_picture=self.background_tile_image[1]
                    )
                self.ids.artist_item.add_widget(widget)
                self.currentRecycleViewWidget_list[3].append(widget)
                self.background_tile_image[1] = self.object_background_image

        components.artist.artist_init.artist_music_dictionnary.clear()
        for artistWidget in self.currentRecycleViewWidget_list[3]:
            self.ids.artist_item.remove_widget(artistWidget)
        for name in self.music_dictionnary.values():
            try:
                artist = ID3(name).get("TPE1")
                if artist:
                    if str(artist) not in components.artist.artist_init.artist_music_dictionnary.keys():
                        add_tile(artist, name)
                    else:
                        if name.split("/")[-1] not in components.artist.artist_init.artist_music_dictionnary[str(artist)]:
                            components.artist.artist_init.artist_music_dictionnary[str(artist)].append(name.split("/")[-1])
                else:
                    if "<inconnu>" not in components.artist.artist_init.artist_music_dictionnary.keys():
                        add_tile("<inconnu>", name)
                    else:
                        if name.split("/")[-1] not in components.artist.artist_init.artist_music_dictionnary[str("<inconnu>")]:
                            components.artist.artist_init.artist_music_dictionnary[str("<inconnu>")].append(name.split("/")[-1])
            except Exception:
                pass
        self.artist_label_opacity = 0 if len(components.artist.artist_init.artist_music_dictionnary) > 0 else 1
    def init_artist_screen(self, dp):
        """
        Cette methode gere l'ajout des contenu lors de l'ouverture d'un artist
        :param dp:
        :return:
        """
        self.H_OBJECT_NAME = dp
        self.ids.artist.data = []
        MyScreenManager.push(self,"artistScreen")
        for music_name in components.artist.artist_init.artist_music_dictionnary[dp]:
            self.ids.artist.data.append(
                {
                    "viewclass": "CustomOneLineIconListItem",
                    "name": music_name.split("/")[-1]
                }
            )
        self.H_OBJECT_NUMBER = f"{len(self.ids.artist.data)} musique(s)"
        self.screenCurrent.clear(); self.screenCurrent = ["ArtistScreen", str(dp)]
    def load_all_folder_from_disk(self):
        """
        Cette methode se charge de récuperer les dossiers des differents musiques sur le disque
        :return:
        """
        for playlistObject in self.currentRecycleViewWidget_list[1]:
            self.ids.folder.remove_widget(playlistObject)
        for name in components.folder.folder_init.folder_music_dictionary.items():
            try:
                for p in pathlib.Path(name[1]).iterdir():
                    if (str(p)[-4:]).lower() in [".mp3", ".wav", ".mid",  ".ogg", "flac"]:
                        widget = components.folder.folder_init.Folder_layout(
                            folder_name=str(name[0])
                        )
                        self.ids.folder.add_widget(widget)
                        self.currentRecycleViewWidget_list[1].append(widget)
                        break
            except Exception:
                continue
    def init_folder_content(self, dt):
        """
        Cette methode permet d'ajouter le contenu d'un dossier
        :return:
        """
        self.H_OBJECT_NAME = dt
        self.ids.folder_id.data = []
        components.folder.folder_init.folder_music_list.clear()
        MyScreenManager.push(self,"folderScreen")
        for file in pathlib.Path(components.folder.folder_init.folder_music_dictionary[dt]).iterdir():
            file = formated_path(str(file))
            if (file[-4:]).lower() in [".mp3", ".wav", ".mid",  ".ogg", "flac"]:
                self.ids.folder_id.data.append(
                    {
                        "viewclass": "CustomOneLineIconListItem",
                        "name": file.split("/")[-1]
                    }
                )
                components.folder.folder_init.folder_music_list.append(file.split("/")[-1])
        self.H_OBJECT_NUMBER = f"{len(self.ids.folder_id.data)} musique(s)"
        self.screenCurrent.clear(); self.screenCurrent = ["FolderScreen", str(dt)]

    @staticmethod
    def open_playlist_PopUp():
        """
        Cette methode nous permet d'ouvrir une fênetre PopUp  enfin de créer un nouvel playlist
        :return:
        """
        Popup(
            title = "Créer une playlist",
            title_align = "left",
            title_color = (1, 1, 1, 1),
            title_size=14,
            size_hint=(.9, .3),
            separator_color = (1, 1, 1, 1),
            background_color = get_color_from_hex("#606060"),
            auto_dismiss=True,
            content = components.playlist.createPlaylist.Playlist_popup()
        ).open()
    def create_playlist_tile(self, dt, init_item: bool=False):
        """
        Cette methode nous permet de créer une tile de la playlist
        :param dt: le nom de la playlist
        :param init_item: permet de charger les éléments enregistrer dans un fichier
        :return:
        """
        if init_item and len(components.playlist.playlist_init.playlist_music_dictionnary) > 0:
            for playlistObject in self.currentRecycleViewWidget_list[0]:
                self.ids.playlist_item.remove_widget(playlistObject)
            self.playlist_label_opacity = 0
            for name in components.playlist.playlist_init.playlist_music_dictionnary.keys():
                playlistWidget = components.playlist.playlist_init.Playlist_Layout(
                        playlist_name=name
                    )
                self.ids.playlist_item.add_widget(playlistWidget)
                self.currentRecycleViewWidget_list[0].append(playlistWidget)
        else:
            if dt in components.playlist.playlist_init.playlist_music_dictionnary:
                MDSnackbar(
                    MDLabel(
                        text="Cette Playlist existe déjà",
                        halign="center",
                        valign="center"
                    ),
                    duration=3,
                    elevation=0,
                    size_hint=(.95, 1),
                    radius=[5, 5, 5, 5],
                    _no_ripple_effect = True,
                    pos_hint={"center_x": 0.5, "center_y": .15},
                ).open()
            else:
                playlist = components.playlist.playlist_init.Playlist_Layout(
                    playlist_name=dt
                )
                self.ids.playlist_item.add_widget(playlist)
                self.currentRecycleViewWidget_list[0].append(playlist)
                components.playlist.playlist_init.playlist_music_dictionnary[dt] = [] #ajout d'une clé dans le dictionnaire palylist portant le nom  du playlist
                self.playlist_label_opacity = 0
                self.back_up_all_data(type="playlist")
    def init_playlist_Items(self, dt):
        """
        Cette methode nous permet d'ouvrir une nouvelle fêntre enfin d'ajouter des nouveaux items(musics) dans la playlist
        :param dt: le nom de la playlist
        :return:
        """
        if not isinstance(dt, list):
            """
            Cette prémière condition nous permet de charger les items de la recycleView
            """
            self.ids.add_playlist_items.data = []
            MyScreenManager.push(self,"AddPlaylist_Items_Screen")
            for name in self.sorted_music_list:
                if name not in components.playlist.playlist_init.playlist_music_dictionnary[dt]:
                    self.ids.add_playlist_items.data.append(
                        {
                            "viewclass": "Add_Items",
                            "music_name": name,
                            "playlist_name": dt
                        }
                    )
        else:
            """
            Cette deuxieme condtion permet d'ajouter le titre séléctionné dans le dictionnaire playlist
            """
            self.ids.add_playlist_items.data.remove({
                    "viewclass": "Add_Items",
                    "music_name": dt[0],
                    "playlist_name": dt[1]
                }
            )
            components.playlist.playlist_init.playlist_music_dictionnary[dt[1]].append(dt[0])
            self.back_up_all_data(type="playlist")
    def init_playlist_content(self, dt):
        """
        Cette methode permet de charger les éléments d'une playlist
        :param dt:
        :return:
        """
        self.ids.playlist_id.data = []
        self.H_OBJECT_NAME = dt
        self.screenCurrent.clear(); self.screenCurrent = ["PlaylistScreen", str(dt)]
        self.playlistItemLabelOpacity = 0 if len(components.playlist.playlist_init.playlist_music_dictionnary[dt]) > 0 else 1
        for items in components.playlist.playlist_init.playlist_music_dictionnary[dt]:
            try:
                if items in self.sorted_music_list:
                    self.ids.playlist_id.data.append(
                        {
                            "viewclass": "PlaylistCustomOneLineIconListItem",
                            "music_name": items,
                            "playlist_name": dt
                        }
                    )
            except Exception:
                components.playlist.playlist_init.playlist_music_dictionnary[dt].remove(items)
                continue
    def delete_playlist_Item(self, music_name: str, playlist_name: str):
        """
        Cette methode permet de supprimer un élement(Item) d'un playlist
        :param music_name:
        :param playlist_name:
        :return:
        """
        if music_name == self.H_CURRENT_MUSIC_PLAYING_LABEL:
            pygame.mixer.music.stop(); pygame.mixer.music.unload()
        components.playlist.playlist_init.playlist_music_dictionnary[playlist_name].remove(music_name)
        self.ids.playlist_id.data.remove({
                "viewclass": "PlaylistCustomOneLineIconListItem",
                "music_name": music_name,
                "playlist_name": playlist_name
            }
        )
        self.back_up_all_data(type="playlist")
        self.playlistItemLabelOpacity = 0 if len(components.playlist.playlist_init.playlist_music_dictionnary[playlist_name]) > 0 else 1
    def delete_playlist(self, dt):
        """
        Cette methode nous permet de supprimer un playlist
        :param dt: Le nom du playlist
        :return:
        """

        for i in range(len(self.currentRecycleViewWidget_list[0])):
            if self.currentRecycleViewWidget_list[0][i].playlist_name == dt:
                self.ids.playlist_item.remove_widget(self.currentRecycleViewWidget_list[0][i])
                del components.playlist.playlist_init.playlist_music_dictionnary[dt]
                del self.currentRecycleViewWidget_list[0][i]
                if len(components.playlist.appendPlaylistItem.item_list) != 0:
                    self.ids.add_to.remove_widget(components.playlist.appendPlaylistItem.item_list[dt])
                break
        self.playlist_label_opacity = 0 if len(components.playlist.playlist_init.playlist_music_dictionnary) > 0 else 1
        self.back_up_all_data(type="playlist")

    def rename_playlist(self, dt: str, name: str):
        """
        Cette methode nous permet de renommer un playlist
        :param dt: le nouveau nom du playlist
        :param name: l'acien nom du playlist
        :return:
        """
        for i in range(len(self.currentRecycleViewWidget_list[0])):
            if self.currentRecycleViewWidget_list[0][i].playlist_name == name:
                self.currentRecycleViewWidget_list[0][i].playlist_name = dt
        playlist_value = components.playlist.playlist_init.playlist_music_dictionnary.pop(name)
        components.playlist.playlist_init.playlist_music_dictionnary[dt] = playlist_value
        self.back_up_all_data(type="playlist")

    def show_curent_music_list(self):
        """
        Cette methode permet d'afficher la liste des musics en attente d'être lues
        :return:
        """
        def add_recycleview_item(name):
            self.ids.music_list_id.data.append(
                {
                    "viewclass": "CustomOneLineIconListItem",
                    "name": name
                }
            )
        def add_current_musics_list_recycle_View_items():
            for name in self.sorted_music_list:
                add_recycleview_item(name)

        self.ids.music_list_id.data = []
        MyScreenManager.push(self, "music_list")
        if len(self.screenCurrent) == 0:
            add_current_musics_list_recycle_View_items()
        else:
            match self.screenCurrent[0]:
                case "AlbumScreen":
                    for music_name in components.album.album_init.album_music_dictionnary[self.screenCurrent[1]]:
                        add_recycleview_item(music_name.split('/')[-1])
                case "ArtistScreen":
                    for music_name in components.artist.artist_init.artist_music_dictionnary[self.screenCurrent[1]]:
                        add_recycleview_item(music_name.split('/')[-1])
                case "PlaylistScreen":
                    try:
                        for music_name in components.playlist.playlist_init.playlist_music_dictionnary[self.screenCurrent[1]]:
                            add_recycleview_item(music_name.split('/')[-1])
                    except Exception:
                        add_current_musics_list_recycle_View_items()
                case "FolderScreen":
                    try:
                        for music_name in self.ids.folder_id.data:
                            add_recycleview_item(music_name["name"])
                    except Exception:
                        add_current_musics_list_recycle_View_items()
    def open_music_menu(self):
        """
        Cette methode permet d'exécuter les actions de la menu sous l'écran principal de la lecture audio
        :return:
        """
        def menu_callback(arg):
            HomeScreen.menu.dismiss()
            match arg:
                case "Ajouter à":
                    MyScreenManager.push(self, "AddTo_Screen")
                    for p in components.playlist.playlist_init.playlist_music_dictionnary.keys():
                        if p in components.playlist.appendPlaylistItem.item_list:
                            continue
                        else:
                            playlistWidget = components.playlist.appendPlaylistItem.Add_Item(
                                name=str(p)
                            )
                            components.playlist.appendPlaylistItem.item_list[p] = playlistWidget
                            self.ids.add_to.add_widget(playlistWidget)

                case "supprimer":
                    MyScreenManager.push(self, "principalScreen")
                    try:
                        pygame.mixer.music.stop()
                        pygame.mixer.music.unload()
                        self.H_MAX_SLIDER_VALUE, self.H_PLAY_LABEL_OPACITY = "0", 0
                        os.remove(self.music_dictionnary[self.H_CURRENT_MUSIC_PLAYING_LABEL])
                    except Exception:
                        MDSnackbar(
                            MDLabel(
                                text="Erreur lors de la suppression du fichier"
                            ),
                            duration=3,
                            elevation=0,
                            size_hint=(.95, 1),
                            radius=[5, 5, 5, 5],
                            _no_ripple_effect=True,
                            pos_hint={"center_x": 0.5, "center_y": .15},
                        ).open()
                    else:
                        for p in components.playlist.playlist_init.playlist_music_dictionnary.items():
                            if self.H_CURRENT_MUSIC_PLAYING_LABEL in p[1]:
                                p[1].remove(self.H_CURRENT_MUSIC_PLAYING_LABEL)
                                self.init_playlist_content(p[0])

                        self.playingMusic_in_progress = False
                        self.load_musics_from_disk()
                        self.init_principalScreen_recycleView_items()
                        self.load_all_album_from_disk()
                        self.load_all_artist_from_disk()
                        self.load_all_folder_from_disk()
                        self.back_up_all_data(type="all")
                        self.load_all_data()
                        self.set_list_recherche_recycleView()

                        MDSnackbar(
                            MDLabel(
                                text="Fichier supprimé"
                            ),
                            duration=3,
                            elevation=0,
                            size_hint=(.95, 1),
                            radius=[5, 5, 5, 5],
                            _no_ripple_effect=True,
                            pos_hint={"center_x": 0.5, "center_y": .15},
                        ).open()

                        self.piste_label_opacity = 0 if len(self.sorted_music_list) > 0 else 1
                        self.favorite_label_opacity = 0 if len(self.ids.favorite.data) > 0 else 1
                        self.album_label_opacity = 0 if len(components.album.album_init.album_music_dictionnary) > 0 else 1
                        self.artist_label_opacity = 0 if len(components.artist.artist_init.artist_music_dictionnary) > 0 else 1
                        self.playlist_label_opacity = 0 if len(components.playlist.playlist_init.playlist_music_dictionnary) > 0 else 1

                case "Informations":
                    album, artist = None, None
                    try:
                        album = ID3(self.music_dictionnary[self.H_CURRENT_MUSIC_PLAYING_LABEL]).get("TALB")
                        artist = ID3(self.music_dictionnary[self.H_CURRENT_MUSIC_PLAYING_LABEL]).get("TPE1")
                    except Exception:
                        album = "None"
                        artist = "None"
                    finally:
                        taille = os.path.getsize(self.music_dictionnary[self.H_CURRENT_MUSIC_PLAYING_LABEL])
                        MDDialog(
                            title="Informations sur le fichier",
                            elevation=0,
                            type="custom",
                            auto_dismiss=True,
                            content_cls=MDGridLayout(
                                MDBoxLayout(
                                    MDLabel(text="Titre: ", bold=True, halign="left"),
                                    MDLabel(text="Artist: ", bold=True, halign="left"),
                                    MDLabel(text="Album: ", bold=True, halign="left"),
                                    MDLabel(text="Taille: ", bold=True, halign="left"),
                                    MDLabel(text="Chémin: ", bold=True, halign="left"),
                                    orientation="vertical",
                                    size_hint=(.4, 1),
                                    spacing=2,
                                ),
                                MDBoxLayout(
                                    MDLabel(text=str(self.H_CURRENT_MUSIC_PLAYING_LABEL), halign="left"),
                                    MDLabel(text=str(artist), halign="left"),
                                    MDLabel(text=str(album), halign="left"),
                                    MDLabel(text=" %.2f Mo" % (taille / (1024 * 1024)), halign="left"),
                                    MDLabel(text=str(self.music_dictionnary[self.H_CURRENT_MUSIC_PLAYING_LABEL]), halign="left"),
                                    orientation="vertical",
                                    spacing=2,
                                ),
                                cols=2,
                                size_hint_y=None,
                                height="450dp",
                                padding=[3, 3, 3, 3]
                            )

                        ).open()

        HomeScreen.menu = MDDropdownMenu(
            caller=self.ids.music_menu,
            width_mult=3,
            max_height=160,
            items=[
                {
                    "divider": None,
                    "text": "Ajouter à",
                    "viewclass": "OneLineListItem",
                    "on_release": lambda: menu_callback("Ajouter à"),
                },
                {
                    "divider": None,
                    "text": "Supprimer",
                    "viewclass": "OneLineListItem",
                    "on_release": lambda: menu_callback("supprimer"),
                },
                {
                    "divider": None,
                    "text": "Informations",
                    "viewclass": "OneLineListItem",
                    "on_release": lambda: menu_callback("Informations"),
                }
            ],
        )
        HomeScreen.menu.open()
    def add_playlist_Item(self, playlist_name):
        """
        Cette methode nous permet d'ajouter un item dans une playlist à partir de "Ajouter à"
        :param playlist_name:
        :return:
        """
        if (self.H_CURRENT_MUSIC_PLAYING_LABEL in
                components.playlist.playlist_init.playlist_music_dictionnary[playlist_name]):
            MDSnackbar(
                MDLabel(
                    text="Déjà dans la playlist"
                ),
                duration=2,
                elevation=0,
                size_hint=(.95, 1),
                radius=[5, 5, 5, 5],
                _no_ripple_effect=True,
                pos_hint={"center_x": 0.5, "center_y": .15},
            ).open()
        else:
            MyScreenManager.pop(self)
            components.playlist.playlist_init.playlist_music_dictionnary[playlist_name].append(
                self.H_CURRENT_MUSIC_PLAYING_LABEL)
            MDSnackbar(
                MDLabel(
                    text="Piste ajoutée"
                ),
                duration=2,
                elevation=0,
                size_hint=(.95, 1),
                radius=[5, 5, 5, 5],
                _no_ripple_effect=True,
                pos_hint={"center_x": 0.5, "center_y": .15},
            ).open()

            self.back_up_all_data(type="playlist")

    #-----------------------Les fonctions qui ses charge de la lecture des fichiers audio--------
    @staticmethod
    def control_Music_volume_wiht_muteButton(dt):
        """
        Cette methode permet d'arrêter ou de mettre en marche de son de la lecture
        :param dt:
        :return:
        """
        if dt == "volume-high":
            pygame.mixer.music.set_volume(1)
        else:
            pygame.mixer.music.set_volume(0)
    def get_current_music_list(self):
        """
        Cette methode retourne la liste de music auquel est tiré la chanson en cour de lecture
        :return:
        """
        if len(self.screenCurrent) == 0 or \
                self.current == "principalScreen" or self.current == "researchScreen":
            self.screenCurrent.clear()
            return self.sorted_music_list
        else:
            match self.screenCurrent[0]:
                case "AlbumScreen":
                    return components.album.album_init.album_music_dictionnary[self.screenCurrent[1]]
                case "ArtistScreen":
                    return components.artist.artist_init.artist_music_dictionnary[self.screenCurrent[1]]
                case "PlaylistScreen":
                    return components.playlist.playlist_init.playlist_music_dictionnary[self.screenCurrent[1]]
                case "FolderScreen":
                    return components.folder.folder_init.folder_music_list
                case _:
                    return self.sorted_music_list
    def init_musicPlaying_Mode(self):
        """
        Cette methode s'occupde de definir la maniere de la lecture des musiques, soit lire les musiques par
        ordre alphabetique, les lire aleatoirement ou bouclé sur un seul audio
        :return:
        """

        match self.H_MUSIC_PLAYING_MODE_ICON:
            case "shuffle":
                self.musicPlaying_mode = "Répéter le courant"
                self.H_MUSIC_PLAYING_MODE_ICON = "rotate-left"
            case "rotate-left":
                self.musicPlaying_mode = "Boucler Tout"
                self.H_MUSIC_PLAYING_MODE_ICON = "shuffle-disabled"
            case "shuffle-disabled":
                self.musicPlaying_mode = "Tout mélanger"
                self.H_MUSIC_PLAYING_MODE_ICON = "shuffle"
        MDSnackbar(
            MDLabel(
                text= self.musicPlaying_mode
            ),
            duration=1,
            elevation=0,
            size_hint=(.95, 1),
            radius=[5, 5, 5, 5],
            _no_ripple_effect=True,
            pos_hint={"center_x": 0.5, "center_y": .05},
        ).open()

        self.back_up_all_data(type="object")

    def control_music_state(self, dt):
        """
        Cette methode permet de controle l'appui sur le bouton pause and play
        :param dt:
        :return:
        """
        if dt == "pause-circle-outline" or dt == "pause":
            pygame.mixer.music.pause()
            self.playingMusic_in_progress = False
            self.H_MUSIC_PLAYING_STATE_ICON = "play-circle-outline"
            self.H_MUSIC_PLAYING_STATE_ICON_SECONDARY = "play-outline"
        else:
            pygame.mixer.music.unpause()
            self.playingMusic_in_progress = True
            self.H_MUSIC_PLAYING_STATE_ICON = "pause-circle-outline"
            self.H_MUSIC_PLAYING_STATE_ICON_SECONDARY = "pause"
    def update_musicPlaying_Position(self, dt):
        """
        Cette methode permet de modifier la position de la lecture audio grâce aux event
        des boutons fast-forward-10 et rewind-10
        :param dt:
        :return:
        """
        if pygame.mixer.music.get_busy():
            if dt == "fast-forward-10" and self.H_CURRENT_MUSIC_POSITION < (self.H_MAX_SLIDER_VALUE - 10):
                self.H_CURRENT_MUSIC_POSITION += 10
                pygame.mixer.music.set_pos(int(self.H_CURRENT_MUSIC_POSITION))
                self.H_MUSIC_PROGRESSION_TIME = "%d : %.2d" % (
                self.H_CURRENT_MUSIC_POSITION // 60, self.H_CURRENT_MUSIC_POSITION % 60)
            else:
                if dt == "rewind-10" and self.H_CURRENT_MUSIC_POSITION > 10:
                    self.H_CURRENT_MUSIC_POSITION -= 10
                    pygame.mixer.music.set_pos(int(self.H_CURRENT_MUSIC_POSITION))
                    self.H_MUSIC_PROGRESSION_TIME = "%d : %.2d" % (
                    self.H_CURRENT_MUSIC_POSITION // 60, self.H_CURRENT_MUSIC_POSITION % 60)
                else:
                    self.H_CURRENT_MUSIC_POSITION = 0
                    pygame.mixer.music.set_pos(int(self.H_CURRENT_MUSIC_POSITION))
                    self.H_MUSIC_PROGRESSION_TIME = "%d : %.2d" % (
                        self.H_CURRENT_MUSIC_POSITION // 60, self.H_CURRENT_MUSIC_POSITION % 60)

    def update_musicPlaying_Position_with_MDSlider(self, sec):
        """
        Cette methode permet de controle la position de l'audo grâce au slider
        :param sec: le parametre nombre des secondes
        :return:
        """
        if pygame.mixer.music.get_busy():
            self.H_CURRENT_MUSIC_POSITION = int(sec)
            self.H_MUSIC_PROGRESSION_TIME = "%d : %.2d" % (
                self.H_CURRENT_MUSIC_POSITION // 60, self.H_CURRENT_MUSIC_POSITION % 60)
            pygame.mixer.music.set_pos(int(sec))
    def _update_currentMusic_playing(self):
        """
        Cette methode permet de lancer une nouvelle piste à la fin de la lecture du piste précedent
        :return:
        """
        self.playingMusic_in_progress = False
        match self.musicPlaying_mode:
            case "Répéter le courant":
                self.init_musicPlaying_Parameters(self.H_CURRENT_MUSIC_PLAYING_LABEL)
            case "Boucler Tout":
                self.init_musicPlaying_Parameters(self.H_CURRENT_MUSIC_PLAYING_LABEL, "next")
            case "Tout mélanger":
                self.init_musicPlaying_Parameters(random.choice(self.get_current_music_list()))
    def update_music_progression(self, *args):
        """
        Cette methode permet de mettre à jour l'affichage de la progression de la piste en cours
        :param args:
        :return:
        """
        if self.playingMusic_in_progress is True:
            self.H_CURRENT_MUSIC_POSITION += 1
            self.H_MUSIC_PROGRESSION_TIME = "%d : %.2d" % (
                self.H_CURRENT_MUSIC_POSITION // 60, self.H_CURRENT_MUSIC_POSITION % 60)
            if self.H_CURRENT_MUSIC_POSITION >= self.H_MAX_SLIDER_VALUE:
                pygame.mixer.music.stop(); pygame.mixer.music.unload()
                self._update_currentMusic_playing()
        elif not pygame.mixer.music.get_busy() and self.H_CURRENT_MUSIC_POSITION != self.H_MAX_SLIDER_VALUE != 0:
            if self.H_CURRENT_MUSIC_POSITION >= self.H_MAX_SLIDER_VALUE - 2:
                self._update_currentMusic_playing()
    def add_music_screen_settings(self, name: str, openPlayingScreen: bool):
        """
        Cette methode permet de charger la durée, l'icon du fichier audio
        :param name:
        :param openPlayingScreen:
        :return:
        """
        def init_MDSlider_lenght(audio):
            self.H_MAX_SLIDER_VALUE, self.H_PLAY_LABEL_OPACITY = "0", 1
            if (audio[-4:]).lower() == ".wav": max_lenght = (WAVE(audio)).info.length
            elif (audio[-4:]).lower() == ".mp3": max_lenght = (MP3(audio)).info.length
            elif (audio[-5:]).lower() == ".flac": max_lenght = (FLAC(audio)).info.length
            else:
                sound = pygame.mixer.Sound(audio)
                max_lenght = sound.get_length()


            self.H_MUSIC_LENGHT = "%d : %.2d" % (max_lenght // 60, max_lenght % 60)
            self.H_MAX_SLIDER_VALUE = str(max_lenght // 1)

        self.H_CURRENT_MUSIC_PLAYING_LABEL = self.current_music_name = str(name)
        try:
            init_MDSlider_lenght(self.music_dictionnary[str(name)])
            id3 = ID3(self.music_dictionnary[str(name)])
            for tag in id3.keys():
                if "APIC" in tag:
                    path = formated_path(f"{reperExec}\\images\\tempExec\\{name}.png")
                    with open(path, "wb") as image_file:
                        image_file.write(id3[tag].data)
                    self.H_MUSIC_PICTURE = path
                else:
                    self.H_MUSIC_PICTURE = self.music_picture_source
        except Exception:
            self.H_MUSIC_PICTURE = self.music_picture_source
        finally:
            self.H_MUSIC_PLAYING_STATE_ICON_SECONDARY = "pause"
            self.H_MUSIC_PLAYING_STATE_ICON = "pause-circle-outline"
            MyScreenManager.push(self,"musicPlayScreen") if openPlayingScreen is True else None
            if name in self.favorite_music_dictionnary:
                self.H_FAVORITE_ICON_BUTTON = "star"
            else:
                self.H_FAVORITE_ICON_BUTTON = "star-outline"
    def init_musicPlaying_Parameters(self, music_name, mode = None, openPlayingScreen = False):
        """
        Cette methode nous permet de lancer la fênetre de la lecture d'un fichier audio
        :param music_name: le nom du fichier audio
        :param mode: le mode(prev, next ou lecture du fichier reçu enu parametre)
        :param openPlayingScreen: Si True on ouvre l'ecran de la lecture
        :return:
        """
        if len(self.current_music_list) == 0:
            self.current_music_list = self.sorted_music_list
        else:
            self.current_music_list = self.get_current_music_list()

        try:
            index = self.current_music_list.index(music_name)
            self.H_CURRENT_MUSIC_POSITION = 0
            self.H_MUSIC_PROGRESSION_TIME = "0:00"
            match mode:
                case "prev":
                    previousMusic = self.current_music_list[int(index) - 1]
                    self.add_music_screen_settings(previousMusic, openPlayingScreen)
                    self.play_audio(name=previousMusic)
                case "next":
                    if (index + 1) == len(self.get_current_music_list()): index = -1
                    nextMusic = self.current_music_list[int(index) + 1]
                    self.add_music_screen_settings(nextMusic, openPlayingScreen)
                    self.play_audio(name=nextMusic)
                case _:
                    self.add_music_screen_settings(music_name, openPlayingScreen)
                    self.play_audio(name=music_name)
        except Exception:
           pass

    def play_audio(self, name):
        """
        Cette methode nous permet de charger et de jouer le son du fichier audio
        :param name:
        :return:
        """
        self.lastReadItem = name
        self.back_up_all_data(type="object")
        if pygame.mixer.music.get_busy(): pygame.mixer.music.stop()
        try:
            pygame.mixer.music.load(self.music_dictionnary[name])
        except Exception as e:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            self.playingMusic_in_progress = False
            def snackBar_callback(*args):
                self.init_musicPlaying_Parameters(self.H_CURRENT_MUSIC_PLAYING_LABEL, "next", True)
            Clock.schedule_once(snackBar_callback, 4)

            self.MySnackBar = MDSnackbar(
                MDLabel(
                        text=str(e)
                    ),
                    duration=3,
                    elevation=0,
                    size_hint=(.95, 1),
                    radius=[5, 5, 5, 5],
                    _no_ripple_effect=True,
                    pos_hint={"center_x": .5, "center_y": .16}
                )
            self.MySnackBar.open()
        else:
            pygame.mixer.music.play()
            pygame.mixer.music.set_volume(1)
            self.playingMusic_in_progress = True


    #------------------------------------------------------------------------------------------------
    def init_theme_tile(self):
        """
        Cette methode permet de charger la liste des background
        :return:
        """
        for background_font in self.theme_background_image_font:
            if background_font in components.menu.menu_tile.theme_tile_list:
                continue
            components.menu.menu_tile.theme_tile_list.append(background_font)
            self.ids.theme_tile.add_widget(components.menu.menu_tile.MenuTile(
                tile_image=background_font)
            )
    def change_background_theme(self, dt):
        """
        Cette methode permet de changer le background de l'application
        :param dt:
        :return:
        """
        self.background_image = self.theme_background_image_font[
            self.theme_background_image_font.index(dt)
        ]
        self.back_up_all_data(type="object")
    def open_parameters_menu(self):
        """
        Cette methode permet de capturer les évenements du menu
        :return:
        """
        def menu_callback(arg):
            HomeScreen.menu.dismiss()
            match arg:
                case "Thème":
                    MyScreenManager.push(self,"themeScreen")
                case "Rafrîchir la liste":
                    self.load_musics_from_disk()
                    self.init_principalScreen_recycleView_items()
                    self.load_all_album_from_disk()
                    self.load_all_artist_from_disk()
                    self.load_all_folder_from_disk()
                    self.load_all_data()
                case "Dernière lecture":
                    if not self.lastReadItem or self.lastReadItem not in self.music_dictionnary:
                        MDSnackbar(
                            MDLabel(
                                text="Impossible de récuperer la dernière lecture"
                            ),
                            duration=3,
                            elevation=0,
                            size_hint=(.95, 1),
                            radius=[5, 5, 5, 5],
                            _no_ripple_effect=True,
                            pos_hint={"center_x": .5, "center_y": .16}
                        ).open()
                    else:
                        self.init_musicPlaying_Parameters(self.lastReadItem, openPlayingScreen=True)
                case "A Propos":
                    Popup(
                        title="Musics Player",
                        title_align="center",
                        title_color=(1, 1, 1, 1),
                        title_size=14,
                        size_hint=(.9, .6),
                        separator_color=(1, 1, 1, 1),
                        background_color=get_color_from_hex("#606060"),
                        auto_dismiss=True,
                        content=RstDocument(
                                text="""
                                        **Fonctionnalités de l'application**\n  
                                        **-** Lecture de fichiers audio en haute qualité, offrant une expérience sonore immersive pour les utilisateurs exigeants.\n
                                        **-** Possibilité de créer des playlists personnalisées, permettant aux utilisateurs de regrouper leurs chansons préférées en fonction de leurs humeurs et de leurs activités.\n
                                        **Formats de fichiers audio pris en charge:** MP3_, WAV_, OGG_, MID_, FLAC_\n
                                        **Conditions d'utilisation**\n
                                        L'utilisation de cette application est gratuite et destinée à un usage personnel uniquement. Toute utilisation commerciale est interdite.\n
                                        **Cette application a été conçue et développée par** Isaac_ Bumizi_\n
                                        """,
                                do_scroll_x=False,
                        )
                    ).open()


        HomeScreen.menu = MDDropdownMenu(
            caller=self.ids.paramater_ids_menu,
            width_mult=4.3,
            max_height=210,
            items=[
                {
                    "divider": None,
                    "text": "Thème",
                    "viewclass": "OneLineListItem",
                    "on_release": lambda: menu_callback("Thème")
                },
                {
                    "divider": None,
                    "text": "Rafraîchir la liste",
                    "viewclass": "OneLineListItem",
                    "on_release": lambda: menu_callback("Rafrîchir la liste")
                },
                {
                    "divider": None,
                    "text": "Dernière lecture",
                    "viewclass": "OneLineListItem",
                    "on_release": lambda: menu_callback("Dernière lecture")
                },
                {
                    "divider": None,
                    "text": "A Propos",
                    "viewclass": "OneLineListItem",
                    "on_release": lambda: menu_callback("A Propos")
                }
            ],
        )
        HomeScreen.menu.open()
    #-------------------------------------------------------------------------------------------------

    def back_up_all_data(self, type: Annotated[str, "l'object à sauvegarder"]):
        """
        Cette methode nous permet d'enregistrer les données sur des fichier
        :param type:
        :return:
        """
        def save(file_type, data):
            with open(file_type, "wb") as object_file:
                object_file.truncate(0)
                pick = pickle.Pickler(object_file)
                pick.dump(data)

        object_file_path = [
            formated_path(f"{reperExec}\\data\\.favoriteObject_data.dt"),
            formated_path(f"{reperExec}\\data\\.playlistObject_data.dt"),
            formated_path(f"{reperExec}\\data\\.thObject_data.dt")
        ]
        theme_path = self.background_image.split("/")[-2:]
        theme_path.insert(1, "/")
        theme_path = "".join(theme_path)

        match type:
            case "favori":
                try: save(object_file_path[0], self.favorite_music_dictionnary)
                except Exception: pass
            case "playlist":
                try: save(object_file_path[1], components.playlist.playlist_init.playlist_music_dictionnary)
                except Exception: pass
            case "object":
                try: save(object_file_path[2],{
                                "theme": theme_path,
                                "lastReadItem": self.lastReadItem,
                                "musicPlaying_Mode": self.musicPlaying_mode
                                }
                          )
                except Exception: pass
            case "all":
                for i in range(len(object_file_path)):
                    try:
                        match i:
                            case 0:
                                save(object_file_path[0], self.favorite_music_dictionnary)
                            case 1:
                                save(object_file_path[1], components.playlist.playlist_init.playlist_music_dictionnary)
                            case 2:
                                save(object_file_path[2], {
                                    "theme": theme_path,
                                    "lastReadItem": self.lastReadItem,
                                    "musicPlaying_Mode": self.musicPlaying_mode
                                    }
                                )
                    except Exception:
                        continue
    def load_all_data(self):
        """
        Cette fonction nous permet de recuper les données enregistre sur les fihciers
        :return:
        """
        object_file_path = [
            formated_path(f"{reperExec}\\data\\.favoriteObject_data.dt"),
            formated_path(f"{reperExec}\\data\\.playlistObject_data.dt"),
            formated_path(f"{reperExec}\\data\\.thObject_data.dt")
        ]
        for i in range(len(object_file_path)):
            try:
                with open(object_file_path[i], "rb") as object_file:
                    pick = pickle.Unpickler(object_file)
                    match i:
                        case 0:
                            self.favorite_music_dictionnary = pick.load()
                            self.add_favorite_music(dt=None, init_item=True)
                        case 1:
                            components.playlist.playlist_init.playlist_music_dictionnary = pick.load()
                            self.create_playlist_tile(dt=None, init_item=True)
                        case 2:
                            data = pick.load()
                            background_image = formated_path(f"{reperExec}\\{data['theme']}")
                            if background_image in self.theme_background_image_font:
                                self.background_image = background_image
                            else:
                                self.background_image = self.theme_background_image_font[-1]
                            self.lastReadItem = data["lastReadItem"]
                            self.musicPlaying_mode = data["musicPlaying_Mode"]
                            match self.musicPlaying_mode:
                                case "Répéter le courant": self.H_MUSIC_PLAYING_MODE_ICON = "rotate-left"
                                case "Boucler Tout": self.H_MUSIC_PLAYING_MODE_ICON = "shuffle-disabled"
                                case "Tout mélanger": self.H_MUSIC_PLAYING_MODE_ICON = "shuffle"
            except Exception:
                continue


class musicsplayerApp(MDApp):
    manager = ObjectProperty()
    Window.size = (350, 650)
    def build(self):
        self.title = "Music Player"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Green"

        Clock.schedule_once(self.changeScreen, 15)

        self.manager = HomeScreen()
        return  self.manager
    def changeScreen(self, *args):
        self.manager.push("principalScreen")

    def on_start(self):
        self.manager.load_musics_from_disk()
        self.manager.init_principalScreen_recycleView_items()
        self.manager.load_all_album_from_disk()
        self.manager.load_all_artist_from_disk()
        self.manager.load_all_folder_from_disk()
        self.manager.load_all_data()
        self.manager.set_list_recherche_recycleView()

    def on_stop(self):
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        pygame.mixer.quit()
        self.manager.back_up_all_data(type="all")
        for path, dirs, files in os.walk(formated_path(f"{reperExec}\\images\\tempExec\\")):
            for file in files:
                try:
                    os.remove(os.path.join(path, file))
                except Exception:
                    continue

if __name__ == "__main__":
    musicsplayerApp().run()
