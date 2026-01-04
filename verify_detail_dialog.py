
import os
import sys
import kivy
from kivy.config import Config
from kivy.core.window import Window

# Configure Kivy for headless/debug run
Config.set('graphics', 'backend', 'sdl2') 
# Try to avoid showing window if possible, but SDL2 might show it. 
# We focus on capturing stderr.

import matplotlib
matplotlib.use('Agg')

from main import PlannerScreen, UpTonightApp, AltitudeChart
from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.metrics import dp
import traceback

class VerifyDetailFontApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Indigo"
        print("DEBUG: Building App...")
        self.screen = PlannerScreen()
        return self.screen

    def on_start(self):
        print("DEBUG: App started. Scheduling simulated dialog open in 1s...")
        Clock.schedule_once(self.open_detail_dialog, 1)

    def open_detail_dialog(self, dt):
        print("DEBUG: Opening Detail Dialog manually...")
        try:
            # Simulate data for a target
            dummy_data = {
                'id': 'Test Target',
                'target name': 'Test Target',
                'type': 'Galaxy',
                'mag': 5.5,
                'aging_duration': '2h',
                'altitude_curve': [10, 20, 35, 50, 45, 30, 15] # Dummy curve
            }
            
            # Inject dummy moon curve into screen
            self.screen.moon_curve = [5, 10, 15, 20, 25, 30, 35]
            
            # Use the screen's show_detail method
            # We must trick it into displaying a Chinese title to verify the fix
            # The show_detail method uses: title=f"{name} - 高度变化曲线"
            # So name='Uranus' will result in "Uranus - 高度变化曲线" which is what failed before.
            dummy_data['id'] = 'Uranus' 
            
            self.screen.show_detail(dummy_data)
            
            print("DEBUG: Dialog opened. taking screenshot in 1s...")
            Clock.schedule_once(self.take_screenshot, 1)
        except Exception:
            traceback.print_exc()
            self.stop()

    def take_screenshot(self, dt):
        if self.screen.dialog:
            print(f"DEBUG: Dialog Title: {self.screen.dialog.title}")
            print("DEBUG: Taking screenshot...")
            Window.screenshot("verify_detail_screenshot.png")
            print("DEBUG: Screenshot saved to verify_detail_screenshot.png")
        else:
             print("DEBUG: FAILURE? No dialog found.")

        print("DEBUG: Exiting app.")
        self.stop()

if __name__ == "__main__":
    try:
        VerifyDetailFontApp().run()
    except Exception:
        print("CRASH TRACEBACK (MAIN):")
        traceback.print_exc()
