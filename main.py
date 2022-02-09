import random
import time

import ujson
from machine import UART, Pin, SPI
from ili9341 import Display, color565
from xglcd_font import XglcdFont

BL = 13
DC = 8
RST = 12
MOSI = 11
SCK = 10
CS = 9
# font = None
display: Display = None
first_message = False

font_dict = {
    'big': XglcdFont('fonts/Agency_FB21x40.c', 21, 40),
    'little': XglcdFont('fonts/Agency_FB11x22.c', 11, 22),
    'mid': XglcdFont('fonts/Agency_FB14x25.c', 14, 25),
}

title_dict = {
              'cpu_usage':          {'desc': 'CPU Usage', 'suffix': '%', 'x': 80, 'y': 35, 'width': 35, 'height': 24, 'font': font_dict['mid']},
              'cpu_frequency':      {'desc': 'CPU Frequency:', 'suffix': ' MHz', 'x': 80, 'y': 11, 'width': 66, 'height': 24, 'font': font_dict['mid']},
              'cpu_temperature':    {'desc': 'CPU Temperature:', 'suffix': '', 'x': 135, 'y': 35, 'width': 28, 'height': 24, 'font': font_dict['mid']},
              'cpu_power':          {'desc': 'CPU Power:', 'suffix': ' Watts', 'x': 80, 'y': 58, 'width': 63, 'height': 17, 'font': font_dict['mid']},
              'mem_total':          {'desc': 'Memory Total:', 'suffix': 'G', 'x': 80, 'y': 90, 'width': 50, 'height': 24, 'font': font_dict['mid']},
              'mem_usage':          {'desc': 'Memory Usage:', 'suffix': '%', 'x': 80, 'y': 115, 'width': 50, 'height': 24, 'font': font_dict['mid']},
              'disk_usage':         {'desc': 'Disk Usage:', 'suffix': '%', 'x': 80, 'y': 195, 'width': 66, 'height': 24, 'font': font_dict['mid']},
              'disk_total':         {'desc': 'Disk Total:', 'suffix': 'G', 'x': 80, 'y': 169, 'width': 66, 'height': 24, 'font': font_dict['mid']},
              'gpu_usage':          {'desc': 'GPU Usage', 'suffix': '%', 'x': 80, 'y': 194, 'width': 66, 'height': 24, 'font': font_dict['mid']},
              'date':          {'desc': '', 'suffix': '', 'x': 199, 'y': 52, 'width': 100, 'height': 22, 'font': font_dict['little']},
              'time':          {'desc': '', 'suffix': '', 'x': 199, 'y': 15, 'width': 100, 'height': 38, 'font': font_dict['big']},
              }


def print_cpu_name(cpu_name, line_height, top):
    display.draw_text(x=5, y=top, font=font, text=cpu_name, color=color565(255, 255, 255))
    display.draw_line(x1=0, y1=top+line_height, x2=318, y2=top+line_height, color=color565(255, 255, 255))
    display.draw_line(x1=0, y1=top+line_height+5, x2=318, y2=top+line_height+5, color=color565(255, 255, 255))


def print_pc_info(pc_info, key, line_height, top, refresh_title):
    map_dict = title_dict[key]
    if map_dict is None:
        return
    if key in pc_info:
        text = str(pc_info[key]) + map_dict['suffix']
        display.fill_rectangle(x=map_dict['x'], y=map_dict['y'], w=map_dict['width'], h=map_dict['height'], color=color565(0, 0, 0))
        display.draw_text(x=map_dict['x'], y=map_dict['y'], font=map_dict['font'], text=text, color=color565(17, 241, 20))


def init_display():
    global font, display
    Pin(BL, Pin.OUT).value(1)
    spi = SPI(1, baudrate=800_000_000, sck=Pin(SCK), mosi=Pin(MOSI))
    display = Display(spi, dc=Pin(DC), cs=Pin(CS), rst=Pin(RST), rotation=90, width=320, height=240)
    display.draw_image('img/bg.raw', 0, 0, 320, 240)
    # font = XglcdFont('fonts/Noto_Sans_CJK_Medium15x18.c', 15, 18)
    # display.draw_text(x=50, y=100, font=font, text='No Message From PC', color=color565(255, 125, 0))


def init_uart():
    uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))
    temp_str = ''
    while True:
        data = uart.readline()
        if data is not None:
            # print(data)
            temp_str = temp_str + (data.decode('utf-8'))
            if temp_str.endswith('___'):
                process(temp_str.replace('___', ''))
                temp_str = ''


def process(data):
    global first_message
    top = 5
    line_height = 20
    line_top = top
    pc_info = ujson.loads(data)
    # print(pc_info)
    if first_message:
        display.clear()
        print_cpu_name(pc_info['cpu_name'], line_height, line_top)
    line_top += line_height + 10
    for key in sorted(title_dict.keys()):
        print_pc_info(pc_info, key, line_height, line_top, first_message)
        line_top += line_height + 2
    first_message = False


if __name__ == '__main__':
    init_display()
    init_uart()
