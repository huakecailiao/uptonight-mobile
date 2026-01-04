import threading
# Force Matplotlib to use a non-interactive backend to avoid conflict with Kivy (SDL2)
import matplotlib
matplotlib.use('Agg')
from datetime import datetime
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDFillRoundFlatButton, MDIconButton, MDFlatButton, MDFillRoundFlatIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.selectioncontrol import MDSwitch, MDCheckbox
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.tab import MDTabsBase, MDTabs
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.list import MDList, TwoLineAvatarIconListItem, IconLeftWidget
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog
from kivymd.uix.dialog import MDDialog
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.card import MDCard
from kivymd.uix.screenmanager import MDScreenManager
# MDIcon is usually just an MDLabel with a specific font, but let's try importing it if available, 
# or use MDLabel with theme_text_color='Custom'

import update_targets
import requests
import json
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Rectangle, Ellipse
from kivy.metrics import dp, sp
from kivy.clock import Clock
from kivy.properties import StringProperty

# Register Chinese Font EARLY (before any widgets are created)
from kivy.core.text import LabelBase
FONT_PATH = 'C:\\Windows\\Fonts\\msyh.ttc'
LabelBase.register(name='Roboto', fn_regular=FONT_PATH, fn_bold=FONT_PATH, fn_italic=FONT_PATH, fn_bolditalic=FONT_PATH)
LabelBase.register(name='Roboto-Bold', fn_regular=FONT_PATH, fn_bold=FONT_PATH, fn_italic=FONT_PATH, fn_bolditalic=FONT_PATH)
LabelBase.register(name='Roboto-Light', fn_regular=FONT_PATH, fn_bold=FONT_PATH, fn_italic=FONT_PATH, fn_bolditalic=FONT_PATH)
LabelBase.register(name='Roboto-Medium', fn_regular=FONT_PATH, fn_bold=FONT_PATH, fn_italic=FONT_PATH, fn_bolditalic=FONT_PATH)
LabelBase.register(name='Roboto-Regular', fn_regular=FONT_PATH, fn_bold=FONT_PATH, fn_italic=FONT_PATH, fn_bolditalic=FONT_PATH)
LabelBase.register(name='Roboto-Thin', fn_regular=FONT_PATH, fn_bold=FONT_PATH, fn_italic=FONT_PATH, fn_bolditalic=FONT_PATH)

from engine import calculate_best_targets

# --- Translation Dictionary ---
TRANSLATIONS = {
    # UI Text
    "UpTonight Mobile Planner": "UpTonight 天文规划",
    "Latitude": "纬度",
    "Longitude": "经度",
    "Select Date": "选择日期",
    "Ignore Moon?": "忽略月光影响?",
    "Start Calculation": "开始计算",
    "Deep Sky": "深空天体 (DSO)",
    "Solar System": "太阳系天体",
    "Comets": "彗星",
    "No targets found": "未找到适合的目标",
    "No Data": "无数据",
    "Constellation": "星座",
    "Transit": "过中天时间",
    "Duration": "可拍摄时长",
    "Altitude Curve (18:00 - 06:00)": "高度变化曲线 (18:00 - 06:00)",
    "CLOSE": "关闭",
    "Calculating...": "计算中...",
    
    # Object Types
    "Asterism": "星群",
    "Group/Asterism": "星群",
    "Dark Nebula": "暗星云",
    "DN": "暗星云",
    "Diffuse Nebula": "弥漫星云",
    "Double Star": "双星",
    "**": "双星",
    "*": "恒星",
    "Galaxy": "星系",
    "Spiral Galaxy": "旋涡星系",
    "Elliptical Galaxy": "椭圆星系",
    "Irregular Galaxy": "不规则星系",
    "Lenticular (S0) Galaxy": "透镜状星系",
    "Galaxy Cluster": "星系团",
    "GGroup": "星系群",
    "Galaxy Group": "星系群",
    "Galaxy Pair": "星系对",
    "Galaxy Duo": "星系对",
    "GTrpl": "星系三重奏",
    "Globular Cluster": "球状星团",
    "Open Cluster": "疏散星团",
    "CL+N": "星团+星云",
    "N+CL": "星团+星云",
    "BN+OC": "星团+星云",
    "Planetary Nebula": "行星状星云",
    "Reflection Nebula": "反射星云",
    "Emission Nebula": "发射星云",
    "EmN": "发射星云",
    "HII Emission Nebula": "H-II区",
    "HII region": "H-II区",
    "Supernova Remnant": "超新星遗迹",
    "Star": "恒星",
    "Variable Star": "变星",
    "Comet": "彗星",
    "Planet": "行星",
    "Moon": "月球",
    "Preplanetary Nebula": "原行星云",
    "Wolf-Rayet Nebula": "沃尔夫-拉叶星云",
    "Molecular Cloud": "分子云",
    "Star Cloud": "恒星云",
    "Cl+N Emission Nebula": "星团+发射星云",
    "Cluster Nebulosity": "星团星云",
    "Nova": "新星",
    "Variable Nebula": "变光星云"
}

def tr(key):
    """Translate key to Chinese if exists, else return key."""
    # Case insensitive exact match try
    if key in TRANSLATIONS:
        return TRANSLATIONS[key]
        
    # Partial matches or fallbacks
    # e.g. "Spiral Galaxy" map to "Galaxy" if specific not found?
    # For now, just return key
    return key

# --- Altitude Chart Widget ---
from kivy.core.text import Label as CoreLabel
from kivy.graphics import Mesh

class AltitudeChart(Widget):
    def __init__(self, curve_data, moon_curve_data=None, **kwargs):
        super().__init__(**kwargs)
        self.curve_data = curve_data
        self.moon_curve_data = moon_curve_data
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.canvas.clear()
        
        if not self.curve_data:
            return

        # Margins
        margin_left = dp(28)
        margin_bottom = dp(18)  # Space for X-axis labels
        margin_top = dp(5)
        
        graph_x = self.x + margin_left
        graph_y = self.y + margin_bottom
        graph_w = self.width - margin_left - dp(5)
        graph_h = self.height - margin_bottom - margin_top

        if graph_w <= 0 or graph_h <= 0:
            return

        with self.canvas:
            # Background (Dark Navy Blue)
            Color(0.09, 0.11, 0.18, 1)
            Rectangle(pos=(graph_x, graph_y), size=(graph_w, graph_h))

            # Horizontal Grid Lines (every 10°, from 10 to 90)
            Color(1, 1, 1, 0.12)
            for y_val in range(10, 100, 10):
                y_pos = graph_y + (y_val / 90.0) * graph_h
                Line(points=[graph_x, y_pos, graph_x + graph_w, y_pos], width=1)
            
            # Y-Axis Labels (10, 20, 30, ... 90)
            for y_val in range(10, 100, 10):
                y_pos = graph_y + (y_val / 90.0) * graph_h
                core_lbl = CoreLabel(text=str(y_val), font_size=sp(10), color=(0.55, 0.55, 0.6, 1))
                core_lbl.refresh()
                tex = core_lbl.texture
                Color(1, 1, 1, 1)
                Rectangle(texture=tex, pos=(self.x + dp(2), y_pos - tex.height / 2), size=tex.size)

            # Draw Moon Curve (Dashed)
            if self.moon_curve_data and len(self.moon_curve_data) >= 2:
                moon_num_points = len(self.moon_curve_data)
                moon_step_x = graph_w / (moon_num_points - 1)
                moon_points = []
                for i, alt in enumerate(self.moon_curve_data):
                    x = graph_x + i * moon_step_x
                    y = graph_y + (max(0, min(alt, 90)) / 90.0) * graph_h
                    moon_points.extend([x, y])
                
                Color(0.5, 0.5, 0.5, 0.4) # Grey, more transparent
                Line(points=moon_points, width=dp(1.0), dash_length=dp(3), dash_offset=dp(3))

            # --- Legend ---
            # Position: Top Right
            legend_x = graph_x + graph_w - dp(70)
            legend_y = graph_y + graph_h - dp(10)
            
            # 1. Target Legend
            Color(0.3, 0.85, 0.95, 1) # Cyan
            Line(points=[legend_x, legend_y, legend_x + dp(15), legend_y], width=dp(1.2))
            
            core_lbl = CoreLabel(text=tr("Target") if "Target" != tr("Target") else "目标", font_size=sp(10), color=(1,1,1,1))
            core_lbl.refresh()
            tex = core_lbl.texture
            Color(1, 1, 1, 1)
            Rectangle(texture=tex, pos=(legend_x + dp(20), legend_y - tex.height/2), size=tex.size)
            
            # 2. Moon Legend
            legend_y -= dp(12) # Move down
            Color(0.5, 0.5, 0.5, 0.6) # Grey
            Line(points=[legend_x, legend_y, legend_x + dp(15), legend_y], width=dp(1.0), dash_length=dp(3), dash_offset=dp(3))
            
            core_lbl = CoreLabel(text=tr("Moon") if "Moon" != tr("Moon") else "月亮", font_size=sp(10), color=(0.8,0.8,0.8,1))
            core_lbl.refresh()
            tex = core_lbl.texture
            Color(1, 1, 1, 1)
            Rectangle(texture=tex, pos=(legend_x + dp(20), legend_y - tex.height/2), size=tex.size)

            # X-Axis Labels (5 labels)
            x_labels = ["18:00", "21:00", "00:00", "03:00", "06:00"]
            for i, txt in enumerate(x_labels):
                ratio = i / (len(x_labels) - 1)
                x_pos = graph_x + ratio * graph_w
                
                # Vertical grid line (subtle)
                Color(1, 1, 1, 0.08)
                Line(points=[x_pos, graph_y, x_pos, graph_y + graph_h], width=1)
                
                # Label
                core_lbl = CoreLabel(text=txt, font_size=sp(9), color=(0.55, 0.55, 0.6, 1))
                core_lbl.refresh()
                tex = core_lbl.texture
                Color(1, 1, 1, 1)
                Rectangle(texture=tex, pos=(x_pos - tex.width / 2, self.y + dp(2)), size=tex.size)

            # Prepare curve points
            num_points = len(self.curve_data)
            if num_points < 2: return
            
            step_x = graph_w / (num_points - 1)
            curve_points = []
            
            for i, alt in enumerate(self.curve_data):
                x = graph_x + i * step_x
                y = graph_y + (max(0, min(alt, 90)) / 90.0) * graph_h
                curve_points.append((x, y))

            # Fill under curve (Semi-transparent gradient effect using Mesh)
            # Create vertices for a filled polygon: curve + bottom edge
            vertices = []
            indices = []
            
            # Add bottom-left corner
            vertices.extend([graph_x, graph_y, 0, 0]) # Index 0
            
            # Add curve points
            for (x, y) in curve_points:
                vertices.extend([x, y, 0, 0]) # Indices 1 to num_points
            
            # Add bottom-right corner
            vertices.extend([graph_x + graph_w, graph_y, 0, 0]) # Index num_points + 1
            
            # Create indices for triangle fan from bottom-left
            # The fan starts from the bottom-left corner (index 0)
            # and connects to each point on the curve and the next point on the curve.
            # This forms triangles like (0, 1, 2), (0, 2, 3), ..., (0, N, N+1)
            # where N is the last curve point and N+1 is the bottom-right point.
            for i in range(1, num_points + 1): # Iterate from first curve point to last curve point + bottom-right
                indices.extend([0, i, i + 1])
            
            Color(0.2, 0.7, 0.85, 0.25)  # Semi-transparent cyan
            Mesh(vertices=vertices, indices=indices, mode='triangles')

            # Draw Curve Line (Thinner)
            Color(0.3, 0.85, 0.95, 1)  # Cyan
            line_points = []
            for (x, y) in curve_points:
                line_points.extend([x, y])
            Line(points=line_points, width=dp(1.2))

# --- Custom List Item ---
from kivymd.uix.list import TwoLineListItem

class TargetItem(TwoLineListItem):
    def __init__(self, data, callback, **kwargs):
        super().__init__(**kwargs)
        self.data = data
        self.callback = callback
        
        # Translate Key Fields
        raw_name = data.get('id') or data.get('target name') or "?"
        raw_type = data.get('type', '-')
        
        # Translate Type
        display_type = tr(raw_type)
            
        self.text = raw_name
        
        # Subtext
        mag = data.get('mag') or data.get('visual magnitude') or "-"
        # size = str(data.get('size', '-')) 
        duration = data.get('imaging_duration', '-')
        
        # Format: Type | Mag: X | Dur: X
        self.secondary_text = f"{display_type} | 亮度: {mag} | 时长: {duration}"
        
        # Removed IconLeftWidget
        
    def on_release(self):
        if self.callback:
            self.callback(self.data)

class Tab(MDFloatLayout, MDTabsBase):
    pass

class ResultScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.moon_curve = []
        
        # Root Layout
        self.main_layout = MDBoxLayout(orientation='vertical', padding=0, spacing=0)
        
        # 1. Top App Bar (With Back Button)
        self.toolbar = MDTopAppBar(
            title=tr("Calculation Results"),
            elevation=4,
            pos_hint={"top": 1},
            left_action_items=[["arrow-left", lambda x: MDApp.get_running_app().show_input()]]
        )
        self.main_layout.add_widget(self.toolbar)
        
        # 2. Results Tabs
        self.tabs = MDTabs()
        # Create Tabs
        self.dso_tab = Tab(title=tr("Deep Sky"))
        self.bodies_tab = Tab(title=tr("Solar System"))
        self.comets_tab = Tab(title=tr("Comets"))
        
        # Lists for Tabs
        self.dso_list = MDList()
        self.bodies_list = MDList()
        self.comets_list = MDList()
        
        # ScrollViews
        scroll_dso = MDScrollView()
        scroll_dso.add_widget(self.dso_list)
        self.dso_tab.add_widget(scroll_dso)
        
        scroll_bodies = MDScrollView()
        scroll_bodies.add_widget(self.bodies_list)
        self.bodies_tab.add_widget(scroll_bodies)
        
        scroll_comets = MDScrollView()
        scroll_comets.add_widget(self.comets_list)
        self.comets_tab.add_widget(scroll_comets)
        
        self.tabs.add_widget(self.dso_tab)
        self.tabs.add_widget(self.bodies_tab)
        self.tabs.add_widget(self.comets_tab)
        
        self.main_layout.add_widget(self.tabs)
        self.add_widget(self.main_layout)

    def update_results(self, results):
        self.moon_curve = results.get('moon_curve', [])
        
        try:
            if 'targets' in results: self.render_list(results['targets'], self.dso_list)
            else: self.dso_list.clear_widgets()

            if 'bodies' in results: self.render_list(results['bodies'], self.bodies_list)
            else: self.bodies_list.clear_widgets()

            if 'comets' in results: self.render_list(results['comets'], self.comets_list)
            else: self.comets_list.clear_widgets()
        except Exception as e:
            print("CRASH IN UPDATE_UI:")
            import traceback
            traceback.print_exc()
            
    def render_list(self, data_list, list_widget):
        list_widget.clear_widgets()
        if not data_list:
            list_widget.add_widget(MDLabel(text=tr("No targets found"), halign="center"))
            return

        for item in data_list:
            list_widget.add_widget(TargetItem(data=item, callback=self.show_detail))
    
    def show_detail(self, item_data):
        name = item_data.get('id') or item_data.get('target name')
        
        # Content: Just the chart
        content = MDBoxLayout(orientation="vertical", size_hint_y=None, height=dp(220), padding=[0, dp(10), 0, 0])
        
        # Chart (Takes full height now)
        curve = item_data.get('altitude_curve', [])
        chart = AltitudeChart(curve_data=curve, moon_curve_data=self.moon_curve, size_hint=(1, 1))
        content.add_widget(chart)

        self.dialog = MDDialog(
            title=f"{name} - 高度变化曲线",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text=tr("CLOSE"), on_release=lambda x: self.dialog.dismiss())
            ],
        )
        self.dialog.open()

class InputScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        
        # Root Layout (Vertical)
        self.main_layout = MDBoxLayout(orientation='vertical', padding=0, spacing=0)
        
        # 1. Top App Bar
        self.toolbar = MDTopAppBar(
            title=tr("UpTonight Mobile Planner"),
            elevation=4,
            pos_hint={"top": 1},
            right_action_items=[["refresh", lambda x: self.start_update_thread(x)]]
        )
        self.main_layout.add_widget(self.toolbar)
        
        # 2. Input Section
        input_scroll = MDScrollView() # Takes remaining space before button
        input_content = MDBoxLayout(orientation='vertical', padding=[dp(15), dp(15), dp(15), dp(15)], spacing=dp(15), size_hint_y=None)
        input_content.bind(minimum_height=input_content.setter('height'))
        
        # --- Card 1: Location ---
        loc_card = MDCard(orientation='vertical', padding=dp(15), spacing=dp(10), size_hint_y=None, height=dp(200), radius=[15], elevation=2)
        
        # Card Header
        header1 = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30), spacing=dp(10))
        header1.add_widget(MDLabel(text="📍 观测地点 (Observation Site)", bold=True, theme_text_color="Primary"))
        loc_card.add_widget(header1)
        
        # Inputs
        coords_box = MDBoxLayout(orientation='horizontal', spacing=dp(10))
        self.lat_field = MDTextField(text="31.17", hint_text=tr("Latitude"), mode="rectangle")
        self.lon_field = MDTextField(text="115.01", hint_text=tr("Longitude"), mode="rectangle")
        coords_box.add_widget(self.lat_field)
        coords_box.add_widget(self.lon_field)
        loc_card.add_widget(coords_box)
        
        # Locate Button
        self.locate_btn = MDFillRoundFlatIconButton(
            text="定位当前位置", icon="crosshairs-gps",
            pos_hint={'center_x': 0.5},
            on_release=self.start_location_thread,
            font_name=FONT_PATH
        )
        loc_card.add_widget(self.locate_btn)
        input_content.add_widget(loc_card)
        
        # --- Card 2: Time & Conditions ---
        time_card = MDCard(orientation='vertical', padding=dp(15), spacing=dp(10), size_hint_y=None, height=dp(140), radius=[15], elevation=2)
        
        header2 = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30), spacing=dp(10))
        header2.add_widget(MDLabel(text="🕒 时间与条件 (Time & Conditions)", bold=True, theme_text_color="Primary"))
        time_card.add_widget(header2)
        
        time_row = MDBoxLayout(orientation='horizontal', spacing=dp(10))
        # Date
        self.date_btn = MDFillRoundFlatButton(text=tr("Select Date"), on_release=self.show_date_picker)
        self.date_label = MDLabel(text=datetime.now().strftime("%m/%d/%y"), halign="center")
        
        time_row.add_widget(self.date_btn)
        time_row.add_widget(self.date_label)
        time_card.add_widget(time_row)
        
        # Moon Switch
        moon_row = MDBoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(40))
        moon_row.add_widget(MDLabel(text=tr("Ignore Moon?")))
        self.moon_switch = MDSwitch()
        Clock.schedule_once(lambda x: setattr(self.moon_switch, 'active', True), 0)
        moon_row.add_widget(self.moon_switch)
        time_card.add_widget(moon_row)
        
        input_content.add_widget(time_card)
        
        # --- Card 3: Targets ---
        target_card = MDCard(orientation='vertical', padding=dp(15), spacing=dp(10), size_hint_y=None, height=dp(100), radius=[15], elevation=2)
        
        header3 = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30), spacing=dp(10))
        header3.add_widget(MDLabel(text="🔭 目标筛选 (Targets)", bold=True, theme_text_color="Primary"))
        target_card.add_widget(header3)
        
        type_row = MDBoxLayout(orientation='horizontal', spacing=dp(5))
        
        # Helpers for Checkboxes
        def make_chk(lbl, active):
            box = MDBoxLayout(orientation='horizontal')
            chk = MDCheckbox(active=active, size_hint=(None, None), size=(dp(30), dp(30)), pos_hint={'center_y': 0.5})
            box.add_widget(chk)
            box.add_widget(MDLabel(text=lbl))
            return box, chk

        dso_box, self.chk_dso = make_chk("DSO", True)
        solar_box, self.chk_bodies = make_chk("Solar", True)
        comet_box, self.chk_comets = make_chk("Comets", False)
        
        type_row.add_widget(dso_box)
        type_row.add_widget(solar_box)
        type_row.add_widget(comet_box)
        
        target_card.add_widget(type_row)
        input_content.add_widget(target_card)
        
        # Add Input Content to Scroll
        input_scroll.add_widget(input_content)
        self.main_layout.add_widget(input_scroll)
        
        # 3. Calculate Button Area (Fixed at bottom)
        action_bar = MDBoxLayout(padding=dp(10), size_hint_y=None, height=dp(80))
        self.calc_btn = MDFillRoundFlatIconButton(
            text=tr("Start Calculation"), 
            icon="rocket-launch",
            font_size=sp(18),
            size_hint_x=0.9,
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            on_release=self.start_calculation_thread
        )
        self.spinner = MDSpinner(size_hint=(None, None), size=(dp(30), dp(30)), active=False, pos_hint={'center_y': .5})
        
        # Wrap button to center it
        action_bar.add_widget(Widget(size_hint_x=0.05))
        action_bar.add_widget(self.calc_btn)
        action_bar.add_widget(self.spinner)
        
        self.main_layout.add_widget(action_bar)
        self.add_widget(self.main_layout)
        
    def show_date_picker(self, _):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_date_save)
        date_dialog.open()

    def on_date_save(self, instance, value, date_range):
        self.date_label.text = value.strftime("%m/%d/%y")

    def start_update_thread(self, _):
        self.spinner.active = True
        # self.update_btn.disabled = True
        self.calc_btn.disabled = True
        threading.Thread(target=self.run_update).start()

    def start_location_thread(self, _):
        self.locate_btn.disabled = True
        self.locate_btn.text = "定位中..."
        threading.Thread(target=self.run_location_update).start()

    def run_location_update(self):
        try:
            # Use ip-api.com for IP-based geolocation
            response = requests.get("http://ip-api.com/json/", timeout=5)
            data = response.json()
            if data.get('status') == 'success':
                lat = str(data.get('lat'))
                lon = str(data.get('lon'))
                Clock.schedule_once(lambda dt: self.update_location_fields(lat, lon))
            else:
                msg = "Location failed: " + data.get('message', 'Unknown error')
                Clock.schedule_once(lambda dt: self.location_error(msg))
        except Exception as e:
            Clock.schedule_once(lambda dt: self.location_error(f"Network error: {e}"))

    def update_location_fields(self, lat, lon):
        self.lat_field.text = lat
        self.lon_field.text = lon
        self.locate_btn.disabled = False
        self.locate_btn.text = "定位当前位置"
        
        self.dialog = MDDialog(
            title="定位成功",
            text=f"已更新坐标:\n纬度: {lat}\n经度: {lon}",
            buttons=[MDFlatButton(text="OK", on_release=lambda _: self.dialog.dismiss())]
        )
        self.dialog.open()

    def location_error(self, msg):
        self.locate_btn.disabled = False
        self.locate_btn.text = "定位当前位置"
        self.dialog = MDDialog(
            title="定位失败",
            text=str(msg),
            buttons=[MDFlatButton(text="OK", on_release=lambda _: self.dialog.dismiss())]
        )
        self.dialog.open()

    def run_update(self):
        try:
            update_targets.update_all()
            result = "Success"
        except Exception as e:
            result = f"Error: {e}"
        Clock.schedule_once(lambda dt: self.update_finished(result))

    def update_finished(self, result):
        self.spinner.active = False
        # self.update_btn.disabled = False
        self.calc_btn.disabled = False
        
        title = "更新成功" if result == "Success" else "更新失败"
        text = "所有天体数据已更新。" if result == "Success" else str(result)
        
        self.dialog = MDDialog(
            title=title,
            text=text,
            buttons=[MDFlatButton(text="OK", on_release=lambda _: self.dialog.dismiss())]
        )
        self.dialog.open()

    def start_calculation_thread(self, _):
        self.spinner.active = True
        self.calc_btn.disabled = True
        
        lat = self.lat_field.text
        lon = self.lon_field.text
        date_str = self.date_label.text
        ignore_moon = self.moon_switch.active
        
        # Get target types
        calc_dso = self.chk_dso.active
        calc_bodies = self.chk_bodies.active
        calc_comets = self.chk_comets.active
        
        threading.Thread(target=self.run_calculation, args=(lat, lon, date_str, ignore_moon, calc_dso, calc_bodies, calc_comets)).start()

    def run_calculation(self, lat, lon, date_str, ignore_moon, calc_dso, calc_bodies, calc_comets):
        print(f"Calculating for {lat}, {lon}, {date_str} (DSO:{calc_dso}, Solar:{calc_bodies}, Comets:{calc_comets})")
        results = calculate_best_targets(
            longitude=lon,
            latitude=lat,
            date_str=date_str,
            ignore_moonlight=ignore_moon,
            calc_objects=calc_dso,
            calc_bodies=calc_bodies,
            calc_comets=calc_comets
        )
        Clock.schedule_once(lambda dt: self.update_ui(results))

    def update_ui(self, results):
        self.spinner.active = False
        self.calc_btn.disabled = False
        MDApp.get_running_app().show_result(results)

class UpTonightApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Indigo"
        
        # Override all font styles to use 'Roboto' (which we mapped to Chinese font)
        for style in self.theme_cls.font_styles:
            self.theme_cls.font_styles[style][0] = "Roboto"
            
        self.sm = MDScreenManager()
        self.input_screen = InputScreen(name='input')
        self.result_screen = ResultScreen(name='result')
        
        self.sm.add_widget(self.input_screen)
        self.sm.add_widget(self.result_screen)
        
        return self.sm

    def show_result(self, results):
        self.result_screen.update_results(results)
        self.sm.current = 'result'

    def show_input(self):
        self.sm.current = 'input'

if __name__ == '__main__':
    UpTonightApp().run()
