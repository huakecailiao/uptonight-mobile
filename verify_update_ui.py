
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

from main import PlannerScreen, UpTonightApp
from kivy.clock import Clock
from kivymd.app import MDApp
import traceback

class VerifyUpdateApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Indigo"
        print("DEBUG: Building App...")
        self.screen = PlannerScreen()
        return self.screen

    def on_start(self):
        print("DEBUG: App started. Scheduling simulated click on Update button in 1s...")
        Clock.schedule_once(self.simulate_update_click, 1)

    def simulate_update_click(self, dt):
        print("DEBUG: Simulating 'Update Data' button press...")
        try:
            # Trigger the update thread directly or simulate the button press
            # self.screen.update_btn.trigger_action() # This might need touch setup, simpler to call method
            self.screen.start_update_thread(None)
            
            print("DEBUG: Update thread started. Polling for completion...")
            Clock.schedule_interval(self.check_status, 1)
        except Exception:
            traceback.print_exc()
            self.stop()

    def check_status(self, dt):
        # Check if spinner is active
        spinner = self.screen.spinner
        if not spinner.active:
            print("DEBUG: Spinner inactive. Checking for dialog...")
            
            # Check if dialog is open (though in unit test environment dialogs might be tricky)
            # We can check self.screen.dialog
            if self.screen.dialog:
                print(f"DEBUG: Dialog detected! Title: {self.screen.dialog.title}, Text: {self.screen.dialog.text}")
                if "成功" in self.screen.dialog.title or "Success" in self.screen.dialog.title:
                     print("DEBUG: SUCCESS! Update success dialog shown.")
                else:
                     print(f"DEBUG: Warning - Dialog title is '{self.screen.dialog.title}'")
            else:
                print("DEBUG: FAILURE? No dialog found.")
            
            print("DEBUG: Taking screenshot...")
            Window.screenshot("verify_update_screenshot.png")
            print("DEBUG: Screenshot saved to verify_update_screenshot.png")
            
            print("DEBUG: Exiting app.")
            self.stop()
        else:
            print("DEBUG: Still updating...")

if __name__ == "__main__":
    try:
        VerifyUpdateApp().run()
    except Exception:
        print("CRASH TRACEBACK (MAIN):")
        traceback.print_exc()
