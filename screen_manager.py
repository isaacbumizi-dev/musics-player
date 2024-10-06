from kivy.uix.screenmanager import ScreenManager, NoTransition

class MyScreenManager(ScreenManager):
    list_screen = []
    screenCurrent = []
    def push(self, screenName):
        self.list_screen.append(self.current)
        self.transition = NoTransition()
        self.current = screenName
    def pop(self):
        if len(self.list_screen) > 0:
            screen = self.list_screen[-1]
            del self.list_screen[-1]
            self.current = screen