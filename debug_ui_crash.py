
import os
import sys
import kivy
from kivy.config import Config
# Force headless-ish or avoid window creation if possible, 
# although KivyMd might need Window.
# We will try to run just the logic first.
Config.set('graphics', 'backend', 'headless') 

sys.path.append(os.getcwd())

from main import PlannerScreen, UpTonightApp
from engine import calculate_best_targets
from kivy.core.window import Window
from kivymd.app import MDApp
from kivy.clock import Clock

class DebugApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        # Return a simple widget, we don't want to show the full UI if we don't have to
        # But we need PlannerScreen to test its methods
        return PlannerScreen()

    def on_start(self):
        print("DEBUG: App started. Running calculation...")
        # Simulate logic
        lat = "31.17"
        lon = "115.01"
        date_str = "01/04/26"
        ignore_moon = True
        
        try:
            results = calculate_best_targets(lat, lon, date_str, ignore_moon)
            print(f"DEBUG: Calculation done. Found {len(results.get('targets', []))} targets.")
            
            screen = self.root
            print("DEBUG: Calling update_ui...")
            screen.update_ui(results)
            print("DEBUG: update_ui finished successfully.")
            
            # If we reached here, maybe the crash is in the drawing or Kivy loop?
            # Let's force a frame dispatch (simulate draw)
            # Clock.tick() 
            print("DEBUG: Test passed (logic executed). Stopping app.")
            self.stop()
            
        except Exception as e:
            print("DEBUG: CRASH DETECTED!")
            import traceback
            traceback.print_exc()
            self.stop()

if __name__ == "__main__":
    try:
        DebugApp().run()
    except Exception as e:
        print("DEBUG: App Run Crash!")
        import traceback
        traceback.print_exc()
