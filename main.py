
import threading
from queue import Queue
import time
import cantools
from pprint import pprint
import kivy
import re
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.properties import NumericProperty
from kivy.properties import DictProperty
from kivy.core.window import Window
from kivy.event import EventDispatcher
from kivy.lang import Builder
from kivy.clock import Clock

from gauge import Gauge
from meter import VMeter

#from kivy.config import Config
#Config.set("kivy", "keyboard_mode", 'systemanddock')
#Config.write()

import zmq

Builder.load_string('''
#:import Matrix kivy.graphics.transformation.Matrix
<ConnectScreen>:
  server_address: server_address
  server_port: server_port
  transport_spinner: transport_spinner
  FloatLayout:
    BoxLayout:
      orientation: 'vertical'
      size_hint: 0.8, 0.8
      pos_hint: {"x": 0.1, "y": 0.1}
      padding: "5sp"
      spacing: "5sp"
      Label:
        size_hint_y: 0.15
        text: "ZeroMQ Connection Properties"
      BoxLayout:
        orientation: "horizontal"
        size_hint_y: 0.1
        padding: "5sp"
        Label:
          text: "Transport:"
        Spinner:
          id: transport_spinner
          values: "TCP", "UDP", "IPC"
          text: "TCP"
      BoxLayout:
        orientation: "horizontal"
        size_hint_y: 0.1
        padding: "5sp"
        Label:
          text: "Server Address:"
        TextInput:
          id: server_address
          text: "127.0.0.1"
      BoxLayout:
        orientation: "horizontal"
        size_hint_y: 0.1
        padding: "5sp"
        Label:
          text: "Server Port:"
        PortInput:
          id: server_port
          text: "7373"
      Widget:
        size_hint_y: 0.1
      BoxLayout:
        orientation: "horizontal"
        size_hint_y: 0.1
        Button:
          text: "Exit"
          on_release: root.on_exit()
        Button:
          text: "Connect"
          on_release: root.on_connect()
<StatusPage>:
  FloatLayout:
    GridLayout:
      cols: 4
      size_hint: 0.95, 0.95
      pos_hint: {"x": 0.025, "y": 0.025}
      padding: "5sp"
      spacing: "5sp"
      Label:
        text: "Engine RPM"
        font_size: '20sp'
      AnchorLayout:
        anchor_x: 'center'
        Gauge:
          value: app.canData.EEC1_EngRPM
          value_str: "%03.0f" % (app.canData.EEC1_EngRPM,)
          size_hint_x: None
          size_hint_y: 1
          width: self.height
          min_value: 0
          max_value: 2800
          low_warn_value: 500
          low_alarm_value: 200
          high_warn_value: 2500
          high_alarm_value: 2550
      Label:
        text: "Fuel Rate"
        font_size: '20sp'
      AnchorLayout:
        anchor_x: 'center'
        VMeter:
          value: app.canData.LFE1_EngFuelRate
          value_str: "%01.1f" % (app.canData.LFE1_EngFuelRate/3.785,)
          size_hint_x: None
          size_hint_y: 1
          width: self.height
          min_value: 0
          max_value: 10
          high_warn_value: 7
          high_alarm_value: 9
          flip: True
      #Label:
      #  text: "%0.1f" % (app.canData.LFE1_EngFuelRate,) + ' ' + app.canData.Unit_LFE1_EngFuelRate
      Label:
        text: "Engine Load"
        font_size: '20sp'
      AnchorLayout:
        anchor_x: 'center'
        Gauge:
          value: app.canData.EEC2_EngPctLoad
          size_hint_x: None
          size_hint_y: 1
          width: self.height
          low_warn_value: 0
          low_alarm_value: 0
          high_warn_value: 85
          high_alarm_value: 95
      #Label:
      #  text: "%0.1f" % (app.canData.EEC2_EngPctLoad,) + app.canData.Unit_EEC2_EngPctLoad
      Label:
        text: "Coolant Temp"
        font_size: '20sp'
      AnchorLayout:
        anchor_x: 'center'
        Gauge:
          value: app.canData.ET1_CoolantTemp * (9/5) + 32
          size_hint_x: None
          size_hint_y: 1
          width: self.height
          min_value: -20
          max_value: 250
          low_warn_value: 32
          low_alarm_value: 0
          high_warn_value: 215
          high_alarm_value: 230
      Label:
        text: "CCVS1 Speed"
        font_size: '20sp'
      Label:
        text: "%0.1f" % (app.canData.CCVS1_WBVS/1.609,) + ' MPH'
        font_size: '40sp'
      Label:
        text: "HEUI Press"
        font_size: '20sp'
      AnchorLayout:
        anchor_x: 'center'
        VMeter:
          value: app.canData.EFLP2_IAP * 145
          value_str: "%04.0f" % (app.canData.EFLP2_IAP*145,)
          size_hint_x: None
          size_hint_y: 1
          width: self.height
          min_value: 0
          max_value: 3000
          low_warn_value: 700
          low_alarm_value: 500
          high_warn_value: 2100
          high_alarm_value: 2500
          flip: True
      Button:
        size_hint_y: None
        height: 60
        text: "ABS"
        on_release:
          root.manager.transition.direction = 'left'
          root.manager.current = 'abs'
      Button:
        size_hint_y: None
        height: 60
        text: "Exit"
        on_release: root.on_exit()

<AbsPage>:
  FloatLayout:
    BoxLayout:
      orientation: 'vertical'
      padding: "5sp"
      spacing: "5sp"
      size_hint: 0.98, 0.98
      pos_hint: {"x": 0.025, "y": 0.025}
      BoxLayout:
        orientation: 'horizontal'
        size_hint_y: 0.15
        Button:
          size_hint_x: 0.2
          size_hint_y: None
          height: 50
          text: "Back"
          on_release:
            root.manager.transition.direction = 'right'
            root.manager.current = 'status'
        Label:
          text: "Wheel Slip"
          font_size: 26
      BoxLayout:
        orientation: 'vertical'
        BoxLayout:
          size_hint_y: 0.3
          orientation: 'horizontal'
          AnchorLayout:
            anchor_x: 'center'
            size_hint_x: 0.35
            VMeter:
              value: (app.canData.EBC2_RelSpdFR+7.8125)/15.625
              value_str: "%03.1f" % (100*app.canData.EBC2_RelSpdFR/7.8125,)
              size_hint_x: None
              size_hint_y: 1
              width: self.height
              min_value: 0
              max_value: 1
              low_warn_value: 0.25
              low_alarm_value: 0.1
              high_warn_value: 0.75
              high_alarm_value: 0.9
          Label:
            size_hint_x: 0.3
            text: "Curb Side"
            font_size: '25sp'
          AnchorLayout:
            anchor_x: 'center'
            size_hint_x: 0.35
            VMeter:
              value: (app.canData.EBC2_RelSpdR1R+7.8125)/15.625
              value_str: "%03.1f" % (100*app.canData.EBC2_RelSpdR1R/7.8125,)
              size_hint_x: None
              size_hint_y: 1
              width: self.height
              min_value: 0
              max_value: 1
              low_warn_value: 0.25
              low_alarm_value: 0.1
              high_warn_value: 0.75
              high_alarm_value: 0.9
              flip: True
        AnchorLayout:
          anchor_x: 'center'
          anchor_y: 'center'
          RelativeLayout:
            Image:
              pos_hint: {'x':0, 'y':0}
              source: 'top_view.png'
            Label:
              pos_hint: {'center_x': 0.65, 'center_y': 0.5}
              text: "ABS Measured Speed: %02.1f MPH" % (app.canData.EBC2_FtAxSpd/1.609,)
              font_size: '22sp'
        BoxLayout:
          orientation: 'horizontal'
          size_hint_y: 0.3
          AnchorLayout:
            anchor_x: 'center'
            size_hint_x: 0.35
            VMeter:
              value: (app.canData.EBC2_RelSpdFL+7.8125)/15.625
              value_str: "%03.1f" % (100*app.canData.EBC2_RelSpdFL/7.8125,)
              size_hint_x: None
              size_hint_y: 1
              width: self.height
              min_value: 0
              max_value: 1
              low_warn_value: 0.25
              low_alarm_value: 0.1
              high_warn_value: 0.75
              high_alarm_value: 0.9
          Label:
            size_hint_x: 0.3
            text: "Road Side"
            font_size: '25sp'
          AnchorLayout:
            anchor_x: 'center'
            size_hint_x: 0.35
            VMeter:
              value: (app.canData.EBC2_RelSpdR1L+7.8125)/15.625
              value_str: "%03.1f" % (100*app.canData.EBC2_RelSpdR1L/7.8125,)
              size_hint_x: None
              size_hint_y: 1
              width: self.height
              min_value: 0
              max_value: 1
              low_warn_value: 0.25
              low_alarm_value: 0.1
              high_warn_value: 0.75
              high_alarm_value: 0.9
              flip: True
        
''')

class PortInput(TextInput):
    pat = re.compile('[^0-9]')
    def insert_text(self, substring, from_undo=False):
      s = re.sub(self.pat, '', substring)
      if int(self.text + s) > 65535:
        s = ''
      return super(PortInput, self).insert_text(s, from_undo)
    def _keyboard_close(self):
        pass
    def setup_keyboard(self):
        kb = Window.request_keyboard(self._keyboard_close, self, 'number')
        if kb.widget: # Is this a VKeyboard?
            kb.widget.layout = 'numeric.json'

class ConnectScreen(Screen):
  server_address = ObjectProperty()
  server_port = ObjectProperty()
  transport_spinner = ObjectProperty()
  
  def process_msg(self, dt):
    msg = self.dataQueue.get()
    frame_str = msg.split('-')
    frame_id = int(frame_str[2] + frame_str[1], 16)
    
    if int(frame_str[3]) > 0:
      App.get_running_app().canData.on_update(frame_id, bytes([int(x, 16) for x in frame_str[4:]]))
    else:
      App.get_running_app().canData.on_update(frame_id, b'')
  
  def on_pre_enter(self, *args):
    pass
  
  def msgCallback(self):
    Clock.schedule_once(self.process_msg)
  
  def on_connect(self):
    server = self.server_address.text
    port = self.server_port.text
    transport = self.transport_spinner.text.lower()
    conStr = transport + "://" + server + ":" + port
    print("Connecting to: " + conStr)
    
    self.dataQueue = Queue()
    threading.Thread(target=zmq_run, args=(conStr,self.dataQueue,self.msgCallback)).start()
    
    self.manager.current = 'status'
    
  def on_exit(self):
    #pprint(App.get_running_app().gauge_image)
    stopFlag.set()
    exit()
            
class StatusPage(Screen):
  
  def on_stuff(self):
    print("doing stuff..." + str(type(App.get_running_app().gauge_image['EEC1_EngRPM'].value)))
    App.get_running_app().gauge_image['EEC1_EngRPM'].value.set(self,'999')
  
  def on_exit(self):
    #pprint(App.get_running_app().gauge_image)
    #from IPython import embed
    #embed()
    stopFlag.set()
    exit()
  
  def on_pre_enter(self, *args):
    #App.get_running_app().msg_dispatchers_by_name['EEC1'].bind(EEC1_EngRPM=App.get_running_app().setter('eng_rpm_str'))
    pass

class AbsPage(Screen):
  pass
    
class CanMsgDispatcher(EventDispatcher):
  def __init__(self, path, **kwargs):
    super(CanMsgDispatcher, self).__init__(**kwargs)
    self.db = cantools.database.load_file(path, frame_id_mask=0xFFFFFF)
    self._sigProps = {}
    for m in self.db.messages:
      self._sigProps.update({s.name : NumericProperty() if s.choices is None else StringProperty("NODATA") for s in m.signals})
      self._sigProps.update({'Unit_' + s.name : StringProperty(s.unit) for s in m.signals})
    self.apply_property(**self._sigProps)
    self.register_event_type('on_update')
  
  def on_update(self, frame_id, msgData):
    try:
      msgObj = self.db.get_message_by_frame_id(frame_id)
    except KeyError:
      return # We don't know about this message. Drop it.
    
    msg_dec = msgObj.decode(msgData)
    
    for k,v in msg_dec.items():
      if isinstance(v, str):
        self.setter(k)(self, v)
      else:
        self.setter(k)(self, v) # TODO: This is a hack
  
    
class GaugeWidget(Widget):
  #value = StringProperty('?', rebind=True)
  #unit = StringProperty(rebind=True)
  #signal = ObjectProperty(rebind=True)
  
  def __init__(self, sig, unit, **kwargs):
    super(GaugeWidget, self).__init__(**kwargs)
    self.signal = sig
    self.unit = unit
    self.value = StringProperty('?', rebind=True)

class MFDApp(App):
  sm = None
  
  canData = CanMsgDispatcher('FMTV_A1.dbc')
  
  #msg_dispatchers = {m.frame_id & 0xFFFFFF : CanMsgDispatcher(m) for m in db.messages}
  #msg_dispatchers_by_name = {m._msg.name : m for m in msg_dispatchers.values()}
  #eec1_disp = msg_dispatchers_by_name['EEC1']
  #eng_rpm_str = StringProperty()
  
  #gauge_image = {}
  #for msg in db.messages:
  #  for sig in msg.signals:
  #    gauge_image[sig.name] = {'sig': sig, 'unit': StringProperty(sig.unit), 'value': StringProperty('<' + sig.name + '>')}
  
  def on_stop(self):
    stopFlag.set()
  
  def build(self):
    
    self.sm = ScreenManager()
    self.sm.add_widget(ConnectScreen(name="connect"))
    self.sm.add_widget(StatusPage(name="status"))
    self.sm.add_widget(AbsPage(name='abs'))
    
    self.sm.current= 'connect'
    return self.sm
  
  
def zmq_run(connectString, dataQueue, pushCallback):
  print("I'm in the ZMQ Thread!")
  context = zmq.Context()
  sock = context.socket(zmq.SUB)
  sock.connect(connectString)
  
  poller = zmq.Poller()
  poller.register(sock, zmq.POLLIN)
  
  sock.setsockopt_string(zmq.SUBSCRIBE, 'can0')
  
  print("Entering ZMQ Loop")
  while True:
    if stopFlag.is_set():
      print("Exiting ZMQ Thread")
      context.destroy()
      return
    #time.sleep(1)
    evts = dict(poller.poll(1))
    if sock in evts:
      msg = sock.recv_string()
      #print("Got CAN Message: " + msg)
      dataQueue.put(msg)
      pushCallback()

stopFlag = threading.Event()
if __name__ == "__main__":
  MFDApp().run()
