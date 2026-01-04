
import os
import sys
import kivy
from kivy.config import Config
from kivy.core.window import Window

# Configure Kivy for headless/debug run
Config.set('graphics', 'backend', 'sdl2') 
# Try to avoid showing window if possible
# Config.set('graphics', 'window_state', 'hidden') 

import matplotlib
matplotlib.use('Agg')

from main import PlannerScreen, UpTonightApp
from kivy.clock import Clock
from kivymd.app import MDApp
import traceback

class VerifyIntegrationApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Indigo"
        print("DEBUG: Building App...")
        self.screen = PlannerScreen()
        return self.screen

    def on_start(self):
        print("DEBUG: App started. Starting calculation in 1s...")
        Clock.schedule_once(self.start_calc, 1)

    def start_calc(self, dt):
        print("DEBUG: Triggering 'Start Calculation'...")
        try:
            # Simulate button press logic manually to ensure inputs are read
            self.screen.start_calculation_thread(None)
            print("DEBUG: Calculation thread started. Polling for completion...")
            Clock.schedule_interval(self.check_status, 1)
        except Exception:
            traceback.print_exc()
            self.stop()

    def check_status(self, dt):
        # 1. Check if spinner is active (meaning calculation is running)
        spinner = self.screen.spinner
        if spinner.active:
            print("DEBUG: Still calculating...", end='\r')
            return

        print("\nDEBUG: Spinner inactive. Checking results...")
        
        # 2. Check for Moon Curve data
        if self.screen.moon_curve:
            print(f"DEBUG: SUCCESS! Moon curve data present. Points: {len(self.screen.moon_curve)}")
            print(f"DEBUG: Sample data: {self.screen.moon_curve[:5]}...")
        else:
            print("DEBUG: FAILURE! Moon curve data is empty or None.")

        # 3. Check for Targets
        dso_list = self.screen.dso_list
        if len(dso_list.children) > 0:
            print(f"DEBUG: Found {len(dso_list.children)} targets.")
            
            # 4. Open Detail for the first target
            # Children are usually in reverse order of addition, but list items are just items.
            # Let's pick the last child (top of list visually)
            first_item = dso_list.children[-1] 
            print(f"DEBUG: Opening details for target: {first_item.text}")
            
            # The item has .data attribute because we passed it in TargetItem
            if hasattr(first_item, 'data'):
                self.screen.show_detail(first_item.data)
                print("DEBUG: Detail dialog requested. Taking screenshot in 2s...")
                Clock.schedule_once(self.take_screenshot, 2)
            else:
                print("DEBUG: FAILURE? First item has no data?")
                self.stop()
        else:
            print("DEBUG: FAILURE? No targets found.")
            self.stop()
            
        # Stop checking status
        return False

    def take_screenshot(self, dt):
        if self.screen.dialog:
            print(f"DEBUG: Dialog Open. Title: {self.screen.dialog.title}")
            print("DEBUG: Taking screenshot...")
            Window.screenshot("verify_integration_screenshot.png")
            print("DEBUG: Screenshot saved to verify_integration_screenshot.png")
        else:
             print("DEBUG: FAILURE? No dialog found.")

        print("DEBUG: Exiting app.")
        self.stop()

if __name__ == "__main__":
    try:
        VerifyIntegrationApp().run()
    except Exception:
        print("CRASH TRACEBACK (MAIN):")
        traceback.print_exc()
