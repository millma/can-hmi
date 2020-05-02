
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.graphics import Color
from kivy.graphics import Ellipse
from kivy.graphics import Rectangle
from kivy.graphics import Line
from kivy.graphics import Scale
from kivy.properties import NumericProperty
from kivy.properties import StringProperty
from kivy.properties import BooleanProperty
import math


class VMeter(Widget):
  value = NumericProperty(50.0)
  value_str = StringProperty()
  max_value = NumericProperty(100.0)
  min_value = NumericProperty(0.0)
  
  flip = BooleanProperty(False)
  
  low_warn_value = NumericProperty(None)
  high_warn_value = NumericProperty(None)
   
  low_alarm_value = NumericProperty(None)
  high_alarm_value = NumericProperty(None)
  
  warn_color = [0.75,0.75,0]
  normal_color = [1, 1, 1]
  alarm_color = [0.75,0,0]
    
  def __init__(self, **kwargs):
    super(VMeter, self).__init__(**kwargs)
    with self.canvas:
      Color(rgb=[1,1,1])
      #self.data_label = Label(valign='middle', pos=[35, 10], text_size=[None, None], texture_size=[65, 40], font_size=60)
      self.flipScale = Scale(xyz=(-1,1,1), origin=self.center)
      
      self.lbl_image = Image(size=[50, 30], pos=[50,50])
      
      self.face_line = Line(points=[20, 4, 20, 96], width=1.5) # Vertical gauge face
      self.val_bbox = Line(rectangle=[35,35,65,40], width=1.2)
      
      self.val_color = Color(rgb=[1,1,1])
      self.value_tri = Line(points=[15, 4, 2, 6, 2, 2], width=1.5, close=True)
      
      Color(rgb=self.warn_color)
      self.warn_tick = Line(points=[20, 65, 5, 65], width=1.5)
      self.warn_tick_low = Line(points=[20, 65, 5, 65], width=1.5)
      
      Color(rgb=self.alarm_color)
      self.alarm_tick = Line(points=[20, 80, 5, 80], width=1.5)
      self.alarm_tick_low = Line(points=[20, 80, 5, 80], width=1.5)
      
      self.unflipScale = Scale(xyz=(-1, 1, 1), origin=self.center)
    
    self.data_label = Label(valign='middle', pos=[35, 10], text_size=[None, None], texture_size=[65, 40], font_size=60)
    
    self.bind(pos=self.update_ui)
    self.bind(size=self.update_ui)
    
    self.bind(high_warn_value=self.update_ui)
    self.bind(high_alarm_value=self.update_ui)
    self.bind(value=self.update_val)
    self.bind(value_str=self.update_val)
    self.bind(min_value=self.update_ui)
    self.bind(max_value=self.update_ui)
    self.bind(flip=self.update_ui)
  
  def update_ui(self, *args):
    self.flipScale.origin = self.to_local(*self.center)
    self.unflipScale.origin = self.to_local(*self.center)
    if self.flip:
      self.flipScale.x = -1.0
      self.unflipScale.x = -1.0
      self.lbl_image.texture.flip_horizontal()
    else:
      self.flipScale.x = 1.0
      self.unflipScale.x = 1.0
    x = self.pos[0]
    y = self.pos[1]
    self.face_line.points = (x+0.2*self.width, y+.04*self.height, x+0.2*self.width, y+.96*self.height)
    
    centerx = self.pos[0] + self.size[0]/2
    centery = self.pos[1] + self.size[1]/2
    
    #self.data_label.font_size = .4*self.height-3
    #self.data_label.texture_update()
    
    #self.val_bbox.rectangle = [.35*self.width+x, centery-.2*self.height, .65*self.width, .4*self.height]
    #self.val_bbox.rectangle = [.35*self.width+x, centery-.2*self.height, self.data_label.texture_size[1]+10, .4*self.height]
    
    # High alarm values
    if self.high_warn_value is not None:
      warn_y = ((self.high_warn_value - self.min_value) / self.max_value) * (.94*self.height) + (.04*self.height)
      self.warn_tick.points = (x+0.2*self.width, y+warn_y, x+0.05*self.width, y+warn_y)
    if self.high_alarm_value is not None:
      alarm_y = ((self.high_alarm_value - self.min_value) / self.max_value) * (.94*self.height) + (.04*self.height)
      self.alarm_tick.points = (x+0.2*self.width, y+alarm_y, x+0.05*self.width, y+alarm_y)
    
    #Low alarm values
    if self.low_warn_value is not None:
      warn_y = ((self.low_warn_value - self.min_value) / self.max_value) * (.94*self.height) + (.04*self.height)
      self.warn_tick_low.points = (x+0.2*self.width, y+warn_y, x+0.05*self.width, y+warn_y)
    if self.low_alarm_value is not None:
      alarm_y = ((self.low_alarm_value - self.min_value) / self.max_value) * (.94*self.height) + (.04*self.height)
      self.alarm_tick_low.points = (x+0.2*self.width, y+alarm_y, x+0.05*self.width, y+alarm_y)
    
    self.update_val(*args)
  
  def update_val(self, *args):
    if (self.low_alarm_value is not None and self.value <= self.low_alarm_value) or (self.high_alarm_value is not None and self.value >= self.high_alarm_value):
      self.val_color.rgb = self.alarm_color
    elif (self.low_warn_value is not None and self.value < self.low_warn_value) or (self.high_warn_value is not None and self.value > self.high_warn_value):
      self.val_color.rgb = self.warn_color
    else:
      self.val_color.rgb = self.normal_color
    
    x = self.pos[0]
    y = self.pos[1]
    val_y = ((self.value - self.min_value) / self.max_value) * (.94*self.height) + (.04*self.height)
    self.value_tri.points = [x+0.15*self.width, y+val_y, x+0.02*self.width, y+val_y+.02*self.height, x+0.02*self.width, y+val_y-.02*self.height]
    
    self.lbl_image.size = [.65*self.width, .40*self.height]
    self.data_label.text = "%03.1f" % (self.value,) if self.value_str == "" else self.value_str
    
    centerx = self.pos[0] + self.size[0]/2
    centery = self.pos[1] + self.size[1]/2
    self.lbl_image.pos = [.40*self.width+x, centery-.2*self.height]
    self.data_label.font_size = .4*self.height
    self.data_label.padding = [5,5]
    #self.data_label.texture_size[0] = .65*self.width
    self.data_label.texture_update()
    self.lbl_image.texture = self.data_label.texture
    if self.flip:
      self.lbl_image.texture.flip_horizontal()
    
    self.val_bbox.rectangle = [self.lbl_image.pos[0], self.lbl_image.pos[1], self.lbl_image.size[0], .4*self.height]
    
    