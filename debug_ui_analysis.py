
import os
import kivy
from kivy.config import Config

# Set specific window size for 10:16 Aspect Ratio (Mobile/Tablet Portrait)
# 16:10 is 1.6. Let's use 800x1280
Config.set('graphics', 'width', '500')
Config.set('graphics', 'height', '800')
Config.set('graphics', 'backend', 'sdl2') 

import matplotlib
matplotlib.use('Agg')

from main import UpTonightApp
from kivy.clock import Clock
from kivymd.app import MDApp
from kivy.core.window import Window
import traceback

class UIAnalysisApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Indigo"
        # Font Override
        for style in self.theme_cls.font_styles:
            self.theme_cls.font_styles[style][0] = "Roboto"
            
        # Import InputScreen and ResultScreen from main (which now has UpTonightApp)
        # But we want to use the UpTonightApp logic for Screens.
        # Actually, let's just use UpTonightApp's structure.
        from main import UpTonightApp as MainApp
        # We need to replicate MainApp.build logic but return the result
        from kivymd.uix.screenmanager import MDScreenManager
        from main import InputScreen, ResultScreen

        self.sm = MDScreenManager()
        self.input_screen = InputScreen(name='input')
        self.result_screen = ResultScreen(name='result')
        
        self.sm.add_widget(self.input_screen)
        self.sm.add_widget(self.result_screen)
        
        return self.sm

    # We need to monkey patch UpTonightApp.get_running_app() because Logic uses it.
    # Logic in InputScreen calls: MDApp.get_running_app().show_result(results)
    # So we must implement show_result, show_input in THIS App class.

    def show_result(self, results):
        print("DEBUG: show_result called. Switching to ResultScreen...")
        self.result_screen.update_results(results)
        self.sm.current = 'result'

    def show_input(self):
        print("DEBUG: show_input called. Switching to InputScreen...")
        self.sm.current = 'input'

    def on_start(self):
        print("DEBUG: App started. Starting calculation in 2s...")
        Clock.schedule_once(self.start_calc, 2)

    def start_calc(self, dt):
        print("DEBUG: Triggering 'Start Calculation' on InputScreen...")
        self.input_screen.start_calculation_thread(None)
        Clock.schedule_interval(self.check_status, 1)

    def check_status(self, dt):
        if not self.input_screen.spinner.active:
            # Check if we switched to result screen
            if self.sm.current == 'result':
                # Check if results are populated
                if len(self.result_screen.dso_list.children) > 0:
                    print("DEBUG: Results rendered on ResultScreen. Taking screenshot...")
                    Window.screenshot("ui_analysis_result_screen.png")
                    print("DEBUG: Screenshot saved to ui_analysis_result_screen.png")
                    self.stop()
                else:
                    print("DEBUG: On ResultScreen but waiting for list...")
            else:
                 # Spinner inactive but still on input? Maybe just finished or error?
                 pass
        else:
            print("DEBUG: Calculating...", end='\r')

if __name__ == "__main__":
    try:
        UIAnalysisApp().run()
    except Exception:
        traceback.print_exc()
