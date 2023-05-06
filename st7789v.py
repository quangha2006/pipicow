# document: https://www.coderdojotc.org/micropython/displays/graph/14-lcd-st7789V/#uploading-the-st7789v-python-firmware
# https://github.com/russhughes/st7789_mpy
import st7789

import vga2_8x16 as font
import vga2_16x32 as font_L
import vga2_bold_16x32 as font_L_B
import vga2_16x16 as font_M


class TFTDisplay:
    def __init__(self, spi, width=240, height=320, dc=None, reset=None, cs=None, backlight=None, rotation=4):
        self.tft = st7789.ST7789(
            spi, width, height, dc=dc, reset=reset, cs=cs, backlight=backlight, rotation=rotation)
        self.tft.init()
        self.FillBlack()

    def Render(self, text, screen_x, screen_y, font_size=None, color=[255, 255, 255], bg=[0, 0, 0]):
        size = font
        if font_size == "LB":
            size = font_L_B
        elif font_size == "M":
            size = font_M
        
        self.tft.text(size, text, screen_x, screen_y, st7789.color565(
            color[0], color[1], color[2]), st7789.color565(bg[0], bg[1], bg[2]))
        #self.tft.text(font, text, 60,0,st7789.WHITE ,st7789.RED)

    def RenderRec(self, x, y, width, height, color=[255, 255, 255]):
        self.tft.fill_rect(x, y, width, height, st7789.color565(
            color[0], color[1], color[2]))

    def FillBlack(self):
        self.tft.fill(st7789.BLACK)

