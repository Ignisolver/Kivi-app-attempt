from kivy.uix.screenmanager import ScreenManager
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from kivymd.uix.label import MDIcon
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.toolbar import MDToolbar
from kivymd.uix.list import OneLineAvatarIconListItem, IRightBodyTouch


class WelcomeScreen(Screen):
    pass


class LoginScreen(Screen):
    pass


class MainAppScreen(Screen):
    pass


class ZbarcamScreen(Screen):
    pass


class WindowManager(ScreenManager):
    pass


class EditScreen(Screen):
    pass


class AddRemoveScreen(Screen):
    pass



class BasicToolbar(MDToolbar):
    pass


class MenuItem(OneLineAvatarIconListItem):
    icon_ = StringProperty()

class RightItem(MDIcon):
    pass

class IconRightSampleWidget(IRightBodyTouch, MDCheckbox):
    pass