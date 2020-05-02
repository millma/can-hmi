
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.graphics import Color
from kivy.graphics import Ellipse
from kivy.graphics import Rectangle
from kivy.graphics import Line
from kivy.properties import NumericProperty
from kivy.properties import StringProperty
import math


class Gauge(Widget):
  value = NumericProperty(50.0)
  value_str = StringProperty()
  max_value = NumericProperty(100.0)
  min_value = NumericProperty(0.0)
  
  low_warn_value = NumericProperty(10.0)
  high_warn_value = NumericProperty(90.0)
   
  low_alarm_value = NumericProperty(5.0)
  high_alarm_value = NumericProperty(95.0)
  
  warn_color = [0.75,0.75,0]
  normal_color = [0.5, 0.5, 0.5]
  alarm_color = [0.75,0,0]
    
  def __init__(self, **kwargs):
    super(Gauge, self).__init__(**kwargs)
    with self.canvas:
      self.fill_color = Color(rgb=[0.5, 0.5, 0.5])
      self.fill_ellipse = Ellipse(pos=self.pos, size=self.size, angle_start=90, angle_end=195)
      Color(rgb=[1,1,1])
      self.outer_line = Line(ellipse=[self.pos[0], self.pos[1], self.size[0], self.size[1], 93, 302], width=1.5)
      self.val_bbox = Line(rectangle=[50,50,50,30])
      self.value_line = Line(points=[0, 0, 0, 0], width=1.5)
      self.data_label = Label(halign='center', valign='middle', pos=self.pos, size=[0,0], font_size=30)
      #self.lbl_image = Image(size=[50, 30], pos=[50,50])
      
      Color(rgb=self.warn_color)
      self.warn_tick = Line(width=1.5)
      
      Color(rgb=self.alarm_color)
      self.alarm_tick = Line(width=1.5)
    
    self.bind(pos=self.update_ui)
    self.bind(size=self.update_ui)
    
    self.bind(high_warn_value=self.update_val)
    self.bind(high_alarm_value=self.update_val)
    self.bind(value=self.update_val)
    self.bind(min_value=self.update_val)
    self.bind(max_value=self.update_val)
  
  def update_ui(self, *args):
    self.fill_ellipse.pos = self.pos
    self.fill_ellipse.size = self.size
    self.outer_line.ellipse = (self.pos[0], self.pos[1], self.size[0], self.size[1], 93, 302)
    centerx = self.pos[0] + self.size[0]/2
    centery = self.pos[1] + self.size[1]/2
    self.val_bbox.rectangle = [centerx, centery, self.size[0]/2, self.size[1]/4]
    
    self.data_label.pos = [centerx+2.5, centery+2.5]
    self.data_label.size = [self.size[0]/2-5, self.size[1]/4-5]
    self.data_label.font_size = self.size[1]/4-3
    self.update_val(*args)
  
  def update_val(self, *args):
    if self.value < self.low_alarm_value or self.value > self.high_alarm_value:
      self.fill_color.rgb = self.alarm_color
    elif self.value < self.low_warn_value or self.value > self.high_warn_value:
      self.fill_color.rgb = self.warn_color
    else:
      self.fill_color.rgb = self.normal_color
    self.fill_ellipse.angle_end = ((self.value - self.min_value) / self.max_value) * 210.0 + 90
    centerx = self.pos[0] + self.size[0]/2
    centery = self.pos[1] + self.size[1]/2
    self.value_line.points = [centerx, centery, centerx+(math.sin(self.fill_ellipse.angle_end * math.pi/180)*self.size[0]/2), centery+(math.cos(self.fill_ellipse.angle_end * math.pi/180)*self.size[1]/2)]
    self.data_label.text = "%03.1f" % (self.value,) if self.value_str == "" else self.value_str
    #self.data_label.texture_update()
    #self.lbl_image.texture = self.data_label.texture
    
    warn_angle = ((self.high_warn_value - self.min_value) / self.max_value) * 210.0 + 90
    self.warn_tick.points = [centerx+(math.sin(warn_angle * math.pi/180)*self.size[0]/2), centery+(math.cos(warn_angle * math.pi/180)*self.size[1]/2), centerx+(math.sin(warn_angle * math.pi/180)*(self.size[0]/2-10)), centery+(math.cos(warn_angle * math.pi/180)*(self.size[1]/2-10))]
    alarm_angle = ((self.high_alarm_value - self.min_value) / self.max_value) * 210.0 + 90
    self.alarm_tick.points = [centerx+(math.sin(alarm_angle * math.pi/180)*self.size[0]/2), centery+(math.cos(alarm_angle * math.pi/180)*self.size[1]/2), centerx+(math.sin(alarm_angle * math.pi/180)*(self.size[0]/2-10)), centery+(math.cos(alarm_angle * math.pi/180)*(self.size[1]/2-10))]