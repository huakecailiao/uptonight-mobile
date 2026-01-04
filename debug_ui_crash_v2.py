
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

class DebugCrashApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Indigo"
        print("DEBUG: Building App...")
        self.screen = PlannerScreen()
        return self.screen

    def on_start(self):
        print("DEBUG: App started. Scheduling simulated click in 1s...")
        Clock.schedule_once(self.simulate_click, 1)

    def simulate_click(self, dt):
        print("DEBUG: Simulating 'Start Calculation' button press...")
        try:
            self.screen.start_calculation_thread(None)
            print("DEBUG: Thread started. Polling for completion...")
            Clock.schedule_interval(self.check_status, 1)
        except Exception:
            traceback.print_exc()
            self.stop()

    def check_status(self, dt):
        # Check if spinner is active
        spinner = self.screen.spinner
        if not spinner.active:
            print("DEBUG: Spinner inactive. Checking results...")
            
            # Check results
            dso_count = len(self.screen.dso_list.children)
            print(f"DEBUG: DSO List Children Count: {dso_count}")
            
            if dso_count > 0:
                print("DEBUG: SUCCESS! Items rendered.")
            else:
                print("DEBUG: FAILURE? No items rendered (or empty results).")
            
            if dso_count > 0:
                print("DEBUG: SUCCESS! Items rendered.")
            else:
                print("DEBUG: FAILURE? No items rendered (or empty results).")
            
            print("DEBUG: Taking screenshot...")
            Window.screenshot("debug_screenshot.png")
            print("DEBUG: Screenshot saved to debug_screenshot.png")
            
            print("DEBUG: Exiting app.")
            self.stop()
        else:
            print("DEBUG: Still calculating...")

if __name__ == "__main__":
    try:
        DebugCrashApp().run()
    except Exception:
        print("CRASH TRACEBACK (MAIN):")
        traceback.print_exc()
