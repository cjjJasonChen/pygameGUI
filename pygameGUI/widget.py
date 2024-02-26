import pygame
from pygame.locals import *
from pygameGUI import Group, PG_Error

class Widget:
    """所有组件的基类"""
    
    def __init__(self, group=None):
        """
        获得主组
        加入主组
        
        """
        if type(group) == Group: # 是group
            self.group = group
            group.add(self)
        elif hasattr(type(group),"frame"): # 是frame 注意，或许这里与上面不同，或许是静态传参
            self.master = group
            self.group = self.master.widgets
            self.master.widgets.add(self)
        else:
            raise PG_Error("group参数错误！")
        
    

    def update(self,*args,**kwargs):
        """
        在主循环中，自动被每帧调用

        """
        pass

    def draw(self, screen):
        """绘制函数"""
        pass

    def delete(self):
        """
        在主组中删除自己
        
        """
        self.group.widgets.remove(self)

    def set_pos(self,location="center",position=[0,0]):
        """
        更灵活的设置位置

        """
        if type(position) == type or type(position) == list:
            if location == "center":
                self.rect.center = position
            elif location == "topleft":
                self.rect.topleft = position
            elif location == "topright":
                self.rect.topright = position
            elif location == "bottomleft":
                self.rect.bottomleft = position
            elif location == "bottomright":
                self.rect.bottomright = position
            else:
                raise PG_Error(f"""\n==============================
可能是location值错误:{repr(location)}
    (应是"center"、"topleft"、
    "bottomleft"、"bottomright"、
    "top"、"bottom"、"right"或"left")
或由于position值错误:{repr(position)}
    (应是list、tuple或int)""")
        elif type(position) == int:
            if location == "top":
                self.rect.top = position

            elif location == "bottom":
                self.rect.bottom = position

            elif location == "right":
                self.rect.right = position

            elif location == "left":
                self.rect.left = position
            else:
                raise PG_Error(f"""\n==============================
可能是location值错误:{repr(location)}
    (应是"center"、"topleft"、
    "bottomleft"、"bottomright"、
    "top"、"bottom"、"right"或"left")
或由于position值错误:{repr(position)}
    (应是list、tuple或int)""")
        else:
            raise PG_Error(f"""\n==============================
position值错误:{repr(position)} \n\t(应是list、tuple或int)""")

    def get_rect(self):
        """在最近的非frame组件之中的rect位置"""
        if hasattr(self, "master"):
            rect = [self.rect[0]+self.master.get_rect()[0],
                    self.rect[1]+self.master.get_rect()[1],
                    self.rect[2],
                    self.rect[3]]
            return pygame.Rect(rect)
        else:
            return self.rect
            

    def __str__(self):
        return "widget"

class Button(Widget):
    """
    按钮
    """
    def __init__(
            self,
            group         =None,
            pos           =(0, 0),
            size          =(100, 50),
            active_texture=(240, 240, 240), 
            init_texture  =(250, 250, 250),
            down_texture  =(230, 230, 230),
            block         =True,
            unblock       =False,
            mouse_button  =1,
            down_command  =None,
            command       =None,
            active_command=None,
            repeat        =-1,
        ):
        """
        初始化
        
        :param group: 加入到哪个Group中，该组件通常是Frame
        :param pos: 组件的位置 (x, y)
        :param size: 组件的大小 (w, h)
        :param active_texture: 接受一个元组/列表或函数，代表按钮上的图案
        :param init_texture: 接受一个元组/列表或函数，代表按钮上的图案
        :param down_texture: 接受一个元组/列表或函数，代表按钮上的图案
        :param block: 当鼠标位于上方时是否打开阻断
        :param unblock: 是否免疫阻断
        :param mouse_button: 响应哪个鼠标按钮（1左2中3右）
        :param down_command: 按钮被按下时调用的函数
        :param command: 按钮被抬起时调用的函数
        :param active_command: 一直按着按钮时调用的函数
        :param repeat: 长按时按照多少帧的间隔调用command
        """
        
        super().__init__(group)
        self.unblock = unblock
        self.block = block
        self.active_command = active_command
        self.down_command = down_command
        self.command = command
        self.mouse_button = mouse_button
        self.repeat,self.repeat_copy = repeat,repeat

        # 生成图像
        self.width ,self.height = size
        self.active_image = self.__draw_texture(active_texture,size)
        self.__image = self.__init_image = self.__draw_texture(init_texture,size)
        self.down_image = self.__draw_texture(down_texture,size)
        
        # 得到矩形位置
        self.rect = self.__image.get_rect()
        self.rect.x, self.rect.y = pos

        # 判定
        self.down = False
        
    def update(self,args,kwargs):
        if (not Group.block_start or self.unblock) \
           and pygame.Rect(self.get_rect()).collidepoint(kwargs["pos"]):
            # 是否按下鼠标
            if not pygame.mouse.get_pressed()[self.mouse_button-1]:
                self.__image = self.active_image
                self.__replace_rect(self.rect,self.__image)
                if self.active_command:
                    self.active_command()
            else:
                self.__image = self.down_image
                self.__replace_rect(self.rect,self.__image)
                
            # 打开阻断
            if self.block == True:
                Group.block_start = True
                
            # 迭代操作
            for event in kwargs["events"]:
                if event.type == MOUSEBUTTONDOWN:
                    if event.button == self.mouse_button:
                        self.down = True
                        if self.down_command:
                            self.down_command()
                elif event.type == MOUSEBUTTONUP:
                    if event.button == self.mouse_button and self.down:
                        self.__image = self.active_image
                        self.__replace_rect(self.rect,self.__image)
                        # 长按
                        if self.repeat >= 0: # 防止松开重复调用
                            self.repeat = self.repeat_copy
                        if self.command:
                            self.command()
                        self.down = False
                        break
            if self.down:
                if self.repeat < 0 or (not pygame.mouse.get_pressed()[self.mouse_button-1]):
                    pass
                elif self.repeat == 0:
                    self.repeat = self.repeat_copy
                    self.command()
                else:
                    self.repeat -= 1

        else:
            # 常规状态
            self.__image = self.__init_image
            self.__replace_rect(self.rect,self.__image)
            for event in kwargs["events"]:
                if event.type == MOUSEBUTTONUP:
                    if event.button == self.mouse_button and self.down:
                        self.down = False
            
                
    def __draw_texture(self,texture,size):
        """绘制纹理"""
        image = pygame.Surface(size, pygame.SRCALPHA)
        if type(texture) == tuple or type(texture) == list:
            image.fill(texture)
        else:
            image = texture(image)
        return image
    
    def __replace_rect(self,rect,image):
        """用于改变纹理之后刷新rect"""
        x,y = rect.center
        self.rect = image.get_rect()
        self.rect.center = x,y
    
    def draw(self, surface):
        """绘制"""
        surface.blit(self.__image,[self.rect.x,self.rect.y])

    def set_image(self,state="init",size = [100,100],texture=None):
        """设置图片"""
        image = pygame.Surface(size, pygame.SRCALPHA)
        if state == "init":
            self.__init_image = texture(image)
        elif state == "active":
            self.active_image = texture(image)
        elif state == "down":
            self.down_image = texture(image)
            
    def __str__(self):
        return F"Button"

    @property  # init_image
    def init_image(self):
        return self.__init_image
    @init_image.setter
    def init_image(self,image):
        self.__init_image = image
        self.__image=self.__init_image
        self.__replace_rect(self.rect,image)


class Frame(Widget):
    """
    Frame -> 框架结构
    各种的组件都是由它组织起来的
    内部有一个内置的组(Group)，用于管理其他组件
    """
    frame = True # 表示这是一个框架结构
    
    def __init__(self, group=None, # 组
                 pos = [0,0],size=[0,0], # 位置，大小
                 texture=(190,190,190), # 纹理
                 block=True, # 是否阻断
                 command = None, # 当位于鼠标下方时连续调用(被阻断时无效
                 unblock = False, # 是否免疫阻断
                 ):
        """初始化"""
        
        super().__init__(group)
        self.block = block
        self.unblock = unblock
        self.command=command

        # 生成图像
        self.size = self.width ,self.height = size
        self.__image = self.__draw_texture(texture,size)
        
        # 得到矩形位置
        self.rect = self.__image.get_rect()
        self.rect.x, self.rect.y = pos

        # 内置组
        self.widgets = Group(master = False)

    def __draw_texture(self,texture,size):
        """绘制纹理"""
        image = pygame.Surface(size, pygame.SRCALPHA)
        if type(texture) == tuple or type(texture) == list:
            image.fill(texture)
        else:
            image = texture(image)
        return image

    def __replace_rect(self,rect,image):
        """用于改变纹理之后刷新rect"""
        x,y = rect.center
        self.rect = image.get_rect()
        self.rect.center = x,y
        
    def update(self,args,kwargs):
        "刷新"
        for widget in self.widgets[::-1]: # 注：这里不能使用self.widgets.update() 由于万能参数的传参格式
            widget.update(args,kwargs)
        if (not Group.block_start or self.unblock) \
           and pygame.Rect(self.get_rect()).collidepoint(kwargs["pos"]):
            if self.block == True:
                Group.block_start = True
            if self.command:
                self.command()
            
    def draw(self, surface):
        "绘制"
        image = self.__image.copy()
        self.widgets.draw(image)
        surface.blit(image,[self.rect.x,self.rect.y])

    def set_image(self, size=[500,500], texture=None):
        "设置图片，注意要重新设置位置"
        image = pygame.Surface(size, pygame.SRCALPHA)
        self.__image = texture(image)
        x,y = self.rect.center
        self.rect = image.get_rect()
        self.rect.center = x,y

    def delete(self):
        for w in self.widgets:
            w.delete()
        super().delete()
            
    def __str__(self):
        return f"Frame"

    @property
    def image(self):
        return self.__image
    @image.setter
    def image(self, image):
        self.__image = image
        self.__replace_rect(self.rect,image)

class Label(Widget):
    """
    单行文本
    """
    def __init__(self,
                 group=None, # 加入到哪个Group中，该组件通常是Frame
                 pos = [0,0], # 位置
                 text="...文本...", # 文本 
                 font=("arialms",25), # 字体字号
                 color=[0,0,0], # 前景色（字体颜色）
                 bg=None, # 背景色
                 alpha=255, # 不透明度
                 bold = False, # 加粗
                 italic = False, # 斜体
                 underline = False, # 下划线
                 antialias=True, # 抗锯齿
                 ):
        """初始化"""
        if group:
            super().__init__(group)
        self.__text = text
        self.__font = font
        self.__antialias = antialias
        self.__color = color
        self.__background = bg
        self.__alpha = alpha
        self.__italic = italic
        self.__bold = bold
        self.__underline = underline
        #self.__style = "样式"

        #生成image
        self.__render_image()
        
        # 得到矩形位置
        self.rect = self.__image.get_rect()
        self.rect.x, self.rect.y = pos
        
    def draw(self, surface):
        """绘制"""
        surface.blit(self.__image,[self.rect.x,self.rect.y])

    def __replace_rect(self,rect,image):
        """用于改变纹理之后刷新rect"""
        x,y = rect.center
        self.rect = image.get_rect()
        self.rect.center = x,y

    def __set_style(self,font,bold,italic,underline):
        """设置字体字形"""
        # 生成字体对象
        try:
            self.__style = pygame.font.Font(font[0],font[1])
        except:
            self.__style = pygame.font.SysFont(font[0],font[1],bold,italic)

        # 下划线 如果字体没有加粗/斜体，强行加粗/倾斜  
        self.__style.set_underline(underline)
        if not self.__style.get_bold():
            self.__style.set_bold(bold)
        if not self.__style.get_italic():
            self.__style.set_italic(italic)

    def __render_image(self):
        """生成图片"""
        # 绘制
        self.__set_style(self.__font,self.__bold,self.__italic,self.__underline)

        # 生成image
        self.__image = self.__style.render(self.__text,self.__antialias,self.__color,self.__background)
        self.__image.set_alpha(self.__alpha)
        
            
    def __str__(self):
        return f"Label : {self.__text}"

    def set(self, **kwargs):
        """在需要同时修改多个属性时，相比“xx=xx”该方法效率更高"""
        for key in kwargs:
            if key == "text":
                self.__text = kwargs["text"]
            elif key == "font":
                self.__font = kwargs["font"]
            elif key == "color":
                self.__color = kwargs["color"]
            elif key == "bg":
                self.__background = kwargs["bg"]
            elif key == "bold":
                self.__bold = kwargs["bold"]
            elif key == "italic":
                self.__italic = kwargs["italic"]
            elif key == "underline":
                self.__underline = kwargs["underline"]
            elif key == "antialias":
                self.__antialias = kwargs["antialias"]
        self.__set_style(self.__font,self.__bold,self.__italic,self.__underline)
        # 生成image
        self.__image = self.__style.render(self.__text,self.__antialias,self.__color,self.__background)
        self.__image.set_alpha(self.__alpha)
        # 刷新rect
        self.__replace_rect(self.rect,self.__image)

        
    @property  # text
    def text(self):
        return self.__text
    @text.setter
    def text(self,value):
        self.__text = value
        # 生成image
        self.__image = self.__style.render(self.__text,self.__antialias,self.__color,self.__background)
        self.__image.set_alpha(self.__alpha)
        # 刷新rect
        self.__replace_rect(self.rect,self.__image)

    @property # font
    def font(self):
        return self.__font
    @font.setter
    def font(self,value):
        self.__font = value
        self.__set_style(self.__font,self.__bold,self.__italic,self.__underline)
        # 生成image
        self.__image = self.__style.render(self.__text,self.__antialias,self.__color,self.__background)
        self.__image.set_alpha(self.__alpha)
        # 刷新rect
        self.__replace_rect(self.rect,self.__image)

    @property # color
    def color(self):
        return self.__color
    @color.setter
    def color(self,value):
        self.__color = value
        # 生成image
        self.__image = self.__style.render(self.__text,self.__antialias,self.__color,self.__background)
        self.__image.set_alpha(self.__alpha)

    @property # background
    def bg(self):
        return self.__background
    @bg.setter
    def bg(self,value):
        self.__background = value
        # 生成image
        self.__image = self.__style.render(self.__text,self.__antialias,self.__color,self.__background)
        self.__image.set_alpha(self.__alpha)

    @property # alpha
    def alpha(self):
        return self.__alpha
    @alpha.setter
    def alpha(self,value):
        self.__alpha = value
        # 生成image
        self.__image.set_alpha(self.__alpha)

    @property # bold
    def bold(self):
        return self.__bold
    @bold.setter
    def bold(self,value):
        self.__bold = value
        self.__set_style(self.__font,self.__bold,self.__italic,self.__underline)
        # 生成image
        self.__image = self.__style.render(self.__text,self.__antialias,self.__color,self.__background)
        self.__image.set_alpha(self.__alpha)
        # 刷新rect
        self.__replace_rect(self.rect,self.__image)

    @property # italic
    def italic(self):
        return self.__italic
    @italic.setter
    def italic(self,value):
        self.__italic = value
        self.__set_style(self.__font,self.__bold,self.__italic,self.__underline)
        # 生成image
        self.__image = self.__style.render(self.__text,self.__antialias,self.__color,self.__background)
        self.__image.set_alpha(self.__alpha)
        # 刷新rect
        self.__replace_rect(self.rect,self.__image)

    @property # underline
    def underline(self):
        return self.__underline
    @underline.setter
    def underline(self,value):
        self.__underline = value
        self.__set_style(self.__font,self.__bold,self.__italic,self.__underline)
        # 生成image
        self.__image = self.__style.render(self.__text,self.__antialias,self.__color,self.__background)
        self.__image.set_alpha(self.__alpha)
        # 刷新rect
        self.__replace_rect(self.rect,self.__image)

    @property # antialias
    def antialias(self):
        return self.__antialias
    @antialias.setter
    def antialias(self,value):
        self.__antialias = value
        self.__set_style(self.__font,self.__bold,self.__italic,self.__underline)
        # 生成image
        self.__image = self.__style.render(self.__text,self.__antialias,self.__color,self.__background)
        self.__image.set_alpha(self.__alpha)
        # 刷新rect
        self.__replace_rect(self.rect,self.__image)

    @property # image
    def image(self):
        return self.__image

    @property # style
    def style(self):
        return self.__style

class Message(Widget):
    """
    单行文本
    """
    def __init__(self,
                 group=None, # 加入到哪个Group中，该组件通常是Frame
                 pos = [0,0], # 位置
                 text="""...文本...""", # 文本 
                 font=("arialms",25), # 字体字号
                 color=[0,0,0], # 前景色（字体颜色）
                 bg=None, # 背景色
                 alpha=255, # 不透明度
                 bold = False, # 加粗
                 italic = False, # 斜体
                 underline = False, # 下划线
                 antialias=True, # 抗锯齿
                 width=0, # 限定文本宽度
                 align = "left", # 文本对其方向
                 ):
        """初始化"""
        if group:
            super().__init__(group=group)
        self.__text = text
        self.__font = font
        self.__antialias = antialias
        self.__color = color
        self.__background = bg
        self.__alpha = alpha
        self.__italic = italic
        self.__bold = bold
        self.__underline = underline
        self.width = width
        self.align = align
        #self.__style = "样式"

        #生成image
        self.__render_image()
        
        # 得到矩形位置
        self.rect = self.__image.get_rect()
        self.rect.x, self.rect.y = pos

    def draw(self, surface):
        """绘制"""
        surface.blit(self.__image,[self.rect.x,self.rect.y])
                
    def __replace_rect(self,rect,image):
        """用于改变纹理之后刷新rect"""
        x,y = rect.center
        self.rect = image.get_rect()
        self.rect.center = x,y

    def __set_style(self,font,bold,italic,underline):
        # 生成字体对象
        try:
            self.__style = pygame.font.Font(font[0],font[1])
        except:
            self.__style = pygame.font.SysFont(font[0],font[1],bold,italic)

        # 下划线 如果字体没有加粗/斜体，强行加粗/倾斜  
        self.__style.set_underline(underline)
        if not self.__style.get_bold():
            self.__style.set_bold(bold)
        if not self.__style.get_italic():
            self.__style.set_italic(italic)

    def __render_image(self):
        """生成图片"""
        image_list = []
        line_text = ""

        # 设置字体字形
        self.__set_style(self.__font,self.__bold,self.__italic,self.__underline)
        # 多行
        for word in self.text:
            if self.__style.size(line_text)[0] <= self.width or self.width <= 0:

                if word == "\n": # 手动换行符
                    image_list.append(self.__style.render(line_text,self.__antialias,self.__color,self.__background))
                    line_text = ""
                else: # 将word添加到line_word中
                    line_text += word
            elif not self.width <= 0: # 自动换行
                last_word = line_text[-1]
                line_text = line_text[0:-1]
                image_list.append(self.__style.render(line_text,self.__antialias,self.__color,self.__background))
                line_text = ""
                line_text += last_word
                line_text += word
        if line_text: # 最后一次自动换行的剩余
            image_list.append(self.__style.render(line_text,self.__antialias,self.__color,self.__background))
            
        # 生成透明image
        height = self.__style.get_height()
        if self.width <= 0:
            width = max([image.get_rect()[2] for image in image_list])
        else:
            width = self.width
        height = height * len(image_list)
        self.__image = pygame.Surface([width,height], pygame.SRCALPHA)

        # 填充文本
        for image in image_list:
            if self.align == "left":
                self.__image.blit(image,[0,
                                         image_list.index(image)*self.__style.get_height()])
                
            elif self.align == "right":
                self.__image.blit(image,[self.width-image.get_rect()[2],
                                         image_list.index(image)*self.__style.get_height()])
                
            elif self.align == "center":
                self.__image.blit(image,[(self.width-image.get_rect()[2])/2,
                                          image_list.index(image)*self.__style.get_height()])



        #self.__image = self.__style.render(self.__text,self.__antialias,self.__color,self.__background)
        self.__image.set_alpha(self.__alpha)

            
    def __str__(self):
        return f"Label : {self.__text}"

    def set(self, **kwargs):
        """在需要同时修改多个属性时，相比“xx=xx”该方法效率更高"""
        for key in kwargs:
            if key == "text":
                self.__text = kwargs["text"]
            elif key == "font":
                self.__font = kwargs["font"]
            elif key == "color":
                self.__color = kwargs["color"]
            elif key == "bg":
                self.__background = kwargs["bg"]
            elif key == "bold":
                self.__bold = kwargs["bold"]
            elif key == "italic":
                self.__italic = kwargs["italic"]
            elif key == "underline":
                self.__underline = kwargs["underline"]
            elif key == "antialias":
                self.__antialias = kwargs["antialias"]
        # 生成image
        self.__render_image()
        # 刷新rect
        self.__replace_rect(self.rect,self.__image)

        
    @property  # text
    def text(self):
        return self.__text
    @text.setter
    def text(self,value):
        self.__text = value
        # 生成image
        self.__render_image()
        # 刷新rect
        self.__replace_rect(self.rect,self.__image)

    @property # font
    def font(self):
        return self.__font
    @font.setter
    def font(self,value):
        self.__font = value
        # 生成image
        self.__render_image()
        # 刷新rect
        self.__replace_rect(self.rect,self.__image)

    @property # color
    def color(self):
        return self.__color
    @color.setter
    def color(self,value):
        self.__color = value
        # 生成image
        self.__render_image()

    @property # background
    def bg(self):
        return self.__background
    @bg.setter
    def bg(self,value):
        self.__background = value
        # 生成image
        self.__render_image()

    @property # alpha
    def alpha(self):
        return self.__alpha
    @alpha.setter
    def alpha(self,value):
        self.__alpha = value
        # 生成image
        self.__render_image()

    @property # bold
    def bold(self):
        return self.__bold
    @bold.setter
    def bold(self,value):
        self.__bold = value
        # 生成image
        self.__render_image()
        # 刷新rect
        self.__replace_rect(self.rect,self.__image)

    @property # italic
    def italic(self):
        return self.__italic
    @italic.setter
    def italic(self,value):
        self.__italic = value
        # 生成image
        self.__render_image()
        # 刷新rect
        self.__replace_rect(self.rect,self.__image)

    @property # underline
    def underline(self):
        return self.__underline
    @underline.setter
    def underline(self,value):
        self.__underline = value
        # 生成image
        self.__render_image()
        # 刷新rect
        self.__replace_rect(self.rect,self.__image)

    @property # antialias
    def antialias(self):
        return self.__antialias
    @antialias.setter
    def antialias(self,value):
        self.__antialias = value
        # 生成image
        self.__render_image()
        # 刷新rect
        self.__replace_rect(self.rect,self.__image)

    @property # image
    def image(self):
        return self.__image

class Slider(Widget):
    """
    滑块: 看起来没什么用，但再复合组件中，他会发生巨大作用
            注意！请勿将其固定然后当作按钮使用，他的效率不如按钮
    """
    def __init__(self,
                 group=None, # 加入到哪个Group中，该组件通常是Frame
                 pos = [0,0],size=[100,50], # 位置、大小
                 active_texture = (240,240,240), # 接受一个元组/列表或函数，代表按钮上的图案
                 init_texture = (250,250,250),# 接受一个元组/列表或函数，代表按钮上的图案
                 down_texture = (230,230,230),# 接受一个元组/列表或函数，代表按钮上的图案
                 block = True, # 当鼠标位于上方时是否打开阻断
                 unblock=False, # 是否免疫阻断
                 mouse_button = 1, # 响应哪个按钮
                 down_command = None, # 当按钮被点击时调用(按下时)
                 command = None, # 当按钮被点击时调用(抬起时)
                 active_command = None, # 当按钮处于鼠标下方时，反复调用
                 orient=[True,True], # 允许的移动方向[x, y]
                 repeat = 1, # 重复
                 ):
        """初始化"""
        
        super().__init__(group)
        self.unblock = unblock
        self.block = block
        self.active_command = active_command
        self.down_command = down_command
        self.command = command
        self.orient = orient
        self.mouse_button = mouse_button
        self.repeat,self.repeat_copy = repeat,repeat

        # 生成图像
        self.width ,self.height = size
        self.active_image = self.__draw_texture(active_texture,size)
        self.__image = self.__init_image = self.__draw_texture(init_texture,size)
        self.down_image = self.__draw_texture(down_texture,size)
        
        # 得到矩形位置
        self.rect = self.__image.get_rect()
        self.rect.x, self.rect.y = pos

        self.move = False # 滑块是否正在移动
        self.last_rect = []  # 鼠标按下时，储存自身位置数据
        self.mouse_pos = [] # 鼠标按下时，储存鼠标位置数据
        self.down = False # 判定

        
    def update(self,args,kwargs):
        if (not Group.block_start or self.unblock) \
           and pygame.Rect(self.get_rect()).collidepoint(kwargs["pos"]):
            # 是否按下
            if not pygame.mouse.get_pressed()[self.mouse_button-1]: # 活动
                self.__image = self.active_image
                self.__replace_rect(self.rect,self.__image)
                if self.active_command:
                    self.active_command()

            # 打开阻断
            if self.block == True:
                Group.block_start = True
            
            # 检测事件
            for event in kwargs["events"]:
                if event.type == MOUSEBUTTONDOWN:
                    if event.button == self.mouse_button:
                        self.down = True
                        if self.down_command:
                            self.down_command()
                        self.mouse_pos = kwargs["pos"]
                        self.last_rect = self.rect
                        self.move = True
                        break
                    
        else:
            self.__image = self.__init_image
            self.__replace_rect(self.rect,self.__image)
            
        if self.move: # 长按
            self.__image = self.down_image
            self.__replace_rect(self.rect,self.__image)
            if self.orient[0]:
                self.rect.center = self.last_rect.center[0]+ kwargs["pos"][0] - self.mouse_pos[0], self.rect.center[1]
            if self.orient[1]:
                self.rect.center =  self.rect.center[0], self.last_rect.center[1]+ kwargs["pos"][1] - self.mouse_pos[1]
            if self.down:
                for event in kwargs["events"]:
                    if event.type == MOUSEBUTTONUP:
                        if event.button == self.mouse_button:
                            self.move = False
                            self.__image = self.active_image
                            self.__replace_rect(self.rect,self.__image)
                            if self.command:
                                self.command()
                            self.down = False
                        break
            # 打开阻断
            if self.block == True:
                Group.block_start = True

            # 重复
            if self.down:
                if self.repeat < 0 or (not pygame.mouse.get_pressed()[self.mouse_button-1]):
                    return
                elif self.repeat == 0:
                    self.repeat = self.repeat_copy
                    if self.command:
                        self.command()
                else:
                    self.repeat -= 1
            
    
                
    def __draw_texture(self,texture,size):
        """绘制纹理"""
        image = pygame.Surface(size, pygame.SRCALPHA)
        if type(texture) == tuple or type(texture) == list:
            image.fill(texture)
        else:
            image = texture(image)
        return image
    
    def __replace_rect(self,rect,image):
        """用于改变纹理之后刷新rect"""
        x,y = rect.center
        self.rect = image.get_rect()
        self.rect.center = x,y
    
    def draw(self, surface):
        """绘制"""
        surface.blit(self.__image,[self.rect.x,self.rect.y])

    def set_image(self,state="init",size = [100,100],texture=None):
        """设置图片"""
        image = pygame.Surface(size, pygame.SRCALPHA)
        if state == "init":
            self.__init_image = texture(image)
        elif state == "active":
            self.active_image = texture(image)
        elif state == "down":
            self.down_image = texture(image)
            
    def __str__(self):
        return F"Slider"

    @property  # init_image
    def init_image(self):
        return self.__init_image
    @init_image.setter
    def init_image(self,image):
        self.__init_image = image
        self.__image=self.__init_image
        self.__replace_rect(self.rect,image)

class Switch(Widget):
    """
    开关
    """
    def __init__(self,
                 group=None, # 加入到哪个Group中，该组件通常是Frame
                 pos = [0,0],size=[100,50], # 位置、大小
                 active_textures = [(240,240,240),], # 接受一个元组/列表或函数，代表按钮上的图案
                 init_textures = [(250,250,250),], # 接受一个元组/列表或函数，代表按钮上的图案
                 down_textures = [(230,230,230),], # 接受一个元组/列表或函数，代表按钮上的图案
                 block = True, # 当鼠标位于上方时是否打开阻断
                 unblock=False, # 是否免疫阻断
                 mouse_button = 1, # 响应哪个按钮
                 down_commands = [None,], # 当按钮被点击时调用(按下时)
                 commands = [None,], # 当按钮被点击时调用(抬起时)
                 active_commands = [None,], # 当按钮处于鼠标下方时，反复调用
                 repeat=-1, # 长按时按照多少帧的间隔调用command
                 ):
        """初始化"""
        super().__init__(group)
        self.unblock = unblock
        self.block = block
        if not (len(active_textures)==len(init_textures)==len(down_textures)\
                ==len(active_commands)==len(down_commands)==len(commands)):
            raise PG_Error("传入的图片、回调函数可能数量不一致哦~")
        self.active_commands = active_commands
        self.down_commands = down_commands
        self.commands = commands
        self.mouse_button = mouse_button
        self.repeat,self.repeat_copy = repeat,repeat
        self.index=0
        
        # 生成图像
        self.active_images = [self.__draw_texture(image,size) for image in active_textures]
        self.init_images = [self.__draw_texture(image,size) for image in init_textures]
        self.image = self.init_images[0]
        self.down_images = [self.__draw_texture(image,size) for image in down_textures]

        # 得到矩形位置
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos

        # 判定
        self.down = False

    def update(self,args,kwargs):
        if (not Group.block_start or self.unblock) \
           and pygame.Rect(self.get_rect()).collidepoint(kwargs["pos"]):
            # 是否按下鼠标
            if not pygame.mouse.get_pressed()[self.mouse_button-1]:
                self.image = self.active_images[self.index]
                self.__replace_rect(self.rect,self.image)
                if self.active_commands[self.index]:
                    self.active_commands[self.index]()
            else:
                self.image = self.down_images[self.index]
                self.__replace_rect(self.rect,self.image)

            # 打开阻断
            if self.block == True:
                Group.block_start = True
                
            # 迭代操作
            for event in kwargs["events"]:
                if event.type == MOUSEBUTTONDOWN:
                    if event.button == self.mouse_button:
                        self.down = True
                        if self.down_commands[self.index]:
                            self.down_commands[self.index]()
                elif event.type == MOUSEBUTTONUP:
                    if event.button == self.mouse_button and self.down:
                        self.image = self.active_images[self.index]
                        self.__replace_rect(self.rect,self.image)
                        # 长按
                        if self.repeat >= 0:
                            self.repeat = self.repeat_copy
                        if self.commands[self.index]:
                            self.commands[self.index]()
                        self.index += 1
                        if self.index > len(self.active_images)-1:
                            self.index=0
                        self.down = False
                        break
            if self.down:
                if self.repeat < 0 or (not pygame.mouse.get_pressed()[self.mouse_button-1]):
                    pass
                elif self.repeat == 0:
                    self.repeat = self.repeat_copy
                    if self.commands[self.index]:
                        self.commands[self.index]()
                    self.index += 1
                    if self.index > len(self.active_images)-1:
                        self.index=0
                else:
                    self.repeat -= 1

        else:
            # 常规状态
            self.image = self.init_images[self.index]
            self.__replace_rect(self.rect,self.image)
            for event in kwargs["events"]:
                if event.type == MOUSEBUTTONUP:
                    if event.button == self.mouse_button and self.down:
                        self.down = False

    def __draw_texture(self,texture,size):
        """绘制纹理"""
        image = pygame.Surface(size, pygame.SRCALPHA)
        if type(texture) == tuple or type(texture) == list:
            image.fill(texture)
        else:
            image = texture(image)
        return image

    def __replace_rect(self,rect,image):
        """用于改变纹理之后刷新rect"""
        x,y = rect.center
        self.rect = image.get_rect()
        self.rect.center = x,y
    
    def draw(self, surface):
        """绘制"""
        surface.blit(self.image,[self.rect.x,self.rect.y])

    def set_image(self,state="init",size = [100,100],index=0,texture=None):
        """设置图片"""
        length = len(self.active_images)
        if index >= length-1:
            self.active_images = self.active_images+[None for i in range(index-length+1)]
            self.init_images = self.init_images+[None for i in range(index-length+1)]
            self.down_images = self.down_images+[None for i in range(index-length+1)]
            self.active_commands = self.active_commands+[None for i in range(index-length+1)]
            self.down_commands = self.down_commands+[None for i in range(index-length+1)]
            self.commands = self.commands+[None for i in range(index-length+1)]
        image = pygame.Surface(size, pygame.SRCALPHA)
        if state == "init":
            self.init_images[index] = texture(image)
        elif state == "active":
            self.active_images[index] = texture(image)
        elif state == "down":
            self.down_images[index] = texture(image)

    def pop(self,index=-1):
        """根据索引删除一列"""
        self.active_images.pop(index)
        self.init_images.pop(index)
        self.down_images.pop(index)
        self.active_command.pop(index)
        self.down_command.pop(index)
        self.command.pop(index)

    def __str__(self):
        return f"Switch"
