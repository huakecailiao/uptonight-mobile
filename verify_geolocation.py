
import os
import sys
import kivy
from kivy.config import Config
from kivy.core.window import Window
from unittest.mock import MagicMock
import requests

# Configure Kivy for headless/debug run
Config.set('graphics', 'backend', 'sdl2') 

import matplotlib
matplotlib.use('Agg')

from main import PlannerScreen, UpTonightApp
from kivy.clock import Clock
from kivymd.app import MDApp
import traceback

class VerifyGeoApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Indigo"
        # Override fonts as before
        for style in self.theme_cls.font_styles:
            self.theme_cls.font_styles[style][0] = "Roboto"
        print("DEBUG: Building App...")
        self.screen = PlannerScreen()
        return self.screen

    def on_start(self):
        print("DEBUG: App started. Mocking requests and clicking Locate...")
        
        # Mock requests.get
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'status': 'success',
            'lat': 40.7128,
            'lon': -74.0060, # New York coordinates
            'country': 'United States'
        }
        requests.get = MagicMock(return_value=mock_response)
        
        Clock.schedule_once(self.simulate_locate_click, 1)

    def simulate_locate_click(self, dt):
        print("DEBUG: Simulating 'Locate' button press...")
        try:
            # Trigger the thread
            self.screen.start_location_thread(None)
            print("DEBUG: Location thread started. Polling for completion...")
            Clock.schedule_interval(self.check_status, 1)
        except Exception:
            traceback.print_exc()
            self.stop()

    def check_status(self, dt):
        # Check if button text reverted (indicates finish)
        btn_text = self.screen.locate_btn.text
        if btn_text == "定位当前位置":
            print("DEBUG: Locate process finished.")
            
            # Check fields
            lat = self.screen.lat_field.text
            lon = self.screen.lon_field.text
            
            print(f"DEBUG: Lat Field: {lat}")
            print(f"DEBUG: Lon Field: {lon}")
            
            if lat == "40.7128" and lon == "-74.006":
                 print("DEBUG: SUCCESS! Coordinates updated correctly.")
            else:
                 print("DEBUG: FAILURE? Coordinates mismatch.")
            
            # Check dialog
            if self.screen.dialog:
                print(f"DEBUG: Dialog Title: {self.screen.dialog.title}")
                if "定位成功" in self.screen.dialog.title:
                    print("DEBUG: SUCCESS! Success dialog shown.")
            
            print("DEBUG: Taking screenshot...")
            Window.screenshot("verify_geolocation_screenshot.png")
            print("DEBUG: Screenshot saved.")
            
            self.stop()
        else:
            print(f"DEBUG: Still locating (Btn text: {btn_text})...")

if __name__ == "__main__":
    try:
        VerifyGeoApp().run()
    except Exception:
        print("CRASH TRACEBACK (MAIN):")
        traceback.print_exc()
