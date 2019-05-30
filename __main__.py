from debug import *
from config import *
from datetime import date
import time as Time
import pygame
from pygame import *
import os
import subprocess
import numpy
import urllib.request
import urllib.error
from loading import *
from keyboard import *
from jsonWeather import *
import pywifi
import wifi
from wifiprofile import *
from wifi import Cell, Scheme
from schemeWPA import *
try:
    from StringIO import BytesIO
except ImportError:
    from io import BytesIO
from PIL import Image

day_names = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]

sleeping = False
last_motion = None

#os.environ["SDL_FBDEV"] = "/dev/fb0"
#os.environ["SDL_MOUSEDRV"] = "TSLIB"
#os.environ["SDL_MOUSEDEV"] = "/dev/input/touchscreen"


class MouseTmp:
    def __init__(self, x, y):
        self.x = x
        self.y = y


LEFT = 1
RIGHT = 3
if not DEBUG:
    status = "check connected"
#status = "search wifi"
status = "check connected"
BLACK = 0, 0, 0
WHITE = 255, 255, 255
GRAY = 78, 78, 78
red = 255, 0, 0
green = 0, 255, 0
blue = 0, 0, 255

pygame.init()
WIDTH = 800  # 480
HEIGHT = 480  # 320
if DEBUG:
    size = (WIDTH, HEIGHT)
    screen = pygame.display.set_mode(size, pygame.SRCALPHA)
else:
    size = (WIDTH, HEIGHT)
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

pygame.display.flip()

mouse_pos = MouseTmp(-1000, - 1000)
mouse_pos_old = MouseTmp(-1000, - 1000)
mouse_pos_down = MouseTmp(-1000, - 1000)
mouse_pos_down_old = MouseTmp(-1000, - 1000)
mouse_pos_up = MouseTmp(-1000, - 1000)
mouse_down = False
mouse_up = False

pygame.font.init()
clock = pygame.time.Clock()

wifi_index = 0
wifi_changing = False

start_time = None


def internet_on():
    try:
        p = urllib.request.urlopen('http://www.google.com', timeout=3)
        #print("reason", p.reason)
        return True
    except urllib.error.URLError as err:
            #print(err)
            try:
                p = urllib.request.urlopen('http://www.google.com', timeout=10)
                #print("reason", p.reason)
                return True
            except urllib.error.URLError as err:
                return False


def hex_to_RGB(hex):
    ''' "#FFFFFF" -> [255,255,255] '''
    # Pass 16 to the integer function for change of base
    return [int(hex[i:i + 2], 16) for i in range(1, 6, 2)]


def RGB_to_hex(RGB):
    ''' [255,255,255] -> "#FFFFFF" '''
    # Components need to be integers for hex to make sense
    RGB = [int(x) for x in RGB]
    return "#" + "".join(["0{0:x}".format(v) if v < 16 else
                          "{0:x}".format(v) for v in RGB])


def color_dict(gradient):
    ''' Takes in a list of RGB sub-lists and returns dictionary of
    colors in RGB and hex form for use in a graphing function
    defined later on '''
    return {"hex": [RGB_to_hex(RGB) for RGB in gradient], "r": [RGB[0] for RGB in gradient],
            "g": [RGB[1] for RGB in gradient], "b": [RGB[2] for RGB in gradient]}


def linear_gradient(start_hex, finish_hex="#FFFFFF", n=10):
    ''' returns a gradient list of (n) colors between
    two hex colors. start_hex and finish_hex
    should be the full six-digit color string,
    inlcuding the number sign ("#FFFFFF") '''
    # Starting and ending colors in RGB form
    s = hex_to_RGB(start_hex)
    f = hex_to_RGB(finish_hex)
    # Initilize a list of the output colors with the starting color
    RGB_list = [s]
    # Calcuate a color at each evenly spaced value of t from 1 to n
    for t in range(1, n):
        # Interpolate RGB vector for color at the current value of t
        curr_vector = [
            int(s[j] + (float(t) / (n - 1)) * (f[j] - s[j]))
            for j in range(3)
        ]
        # Add it to our list of output colors
        RGB_list.append(curr_vector)

    return color_dict(RGB_list)


def draw_background_surface(start, end, width, height, alpha_start=255, alpha_end=255):
    alpha = alpha_start
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    colors = linear_gradient(start, end, height)
    y = height
    for r, g, b in zip(colors["r"], colors["g"], colors["b"]):
        if alpha_end != 255 and alpha_start > alpha_end:
            alpha = int(alpha_start*y/height)
            if alpha < 0:
                alpha = 0
            vertical_line = pygame.Surface((width, 1), pygame.SRCALPHA)
            vertical_line.fill((r, g, b, 255-alpha))
            surf.blit(vertical_line, (0, y))
        elif alpha_start != 255 and alpha_start < alpha_end:
            alpha = int(alpha_end * y / height)
            if alpha < 0:
                alpha = 0
            vertical_line = pygame.Surface((width, 1), pygame.SRCALPHA)
            vertical_line.fill((r, g, b, alpha))
            surf.blit(vertical_line, (0, y))
        else:
            pygame.draw.line(surf, (r, g, b), (0, y), (width, y), 1)
        y = y - 1
    return surf


def get_wifi_list():
    ssids = []
    if DEBUG:
        results = subprocess.check_output(["netsh", "wlan", "show", "network"])
        results = results.decode("utf-8")
        results = results.replace("\r", "")
        ls = results.split("\n")
        ls = ls[4:]
        x = 0
        ssids.append("repeat : Reload search")
        while x < len(ls):
            if x % 5 == 0 and ls[x] != "":
                ssids.append(ls[x])
            x += 1
    else:
        #pygame.mouse.set_visible(False)
        # TODO on Raspian check how it works
        #print(Cell.all('wlan0').ssid)
        ssids.append("repeat : Reload search")
        for c in Cell.all('wlan0'):
            ssids.append(c.mode + " : " + c.ssid)
    x = 0
    y = 100
    wifi_list = []
    if DEBUG:
        font = pygame.font.Font('C:\Windows\Fonts\MyriadPro-Light.ttf', 30)
    else:
        font = pygame.font.Font('MyriadPro-Light.ttf', 30)
    for w in ssids:
        if w.replace(" : ", ":").split(':').__len__() == 2:
            # print(w.replace(" ", "").split(':'), w.replace(" ", "").split(':').__len__())
            wifi_list.append(w.replace(" : ", ":").split(':')[1])
    return wifi_list


def get_wifi_list_surface(wifi_list, ind=0):
    global DEBUG, WIDTH, HEIGHT, WHITE
    surf = pygame.Surface(size, pygame.SRCALPHA)
    h_button = 40
    i = 0
    x = 0
    y = (HEIGHT/2 - 20) - ind * h_button

    if DEBUG:
        font = pygame.font.Font('C:\Windows\Fonts\MyriadPro-Light.ttf', 30)
    else:
        font = pygame.font.Font('MyriadPro-Light.ttf', 30)
    for wifi in wifi_list:
        textSurface = font.render(wifi, True, WHITE)
        textRect = textSurface.get_rect()
        textRect.center = (int(WIDTH / 2), int(HEIGHT / 2))
        surf.blit(textSurface, (textRect.left, y))
        y = y + h_button
        i = i + 1
    return surf


def save_img(surf, name):
    data = pygame.image.tostring(surf, 'RGBA')
    img = Image.frombytes('RGBA', surf.get_size(), data)
    if DEBUG:
        img.save("C:\\Users\\marco\\PycharmProjects\\Weather\\" + name + ".png")
    else:
        img.save(name + ".png")


def match_wifi_list(full, new):
    add_list = []
    for n in new:
        if n not in full:
            add_list.append(n)
    if len(add_list) > 0:
        full.extend(add_list)
    return full


def check_hit(mouse_pos, wifi_index, wifi_list, wifi_list_profile):
    global status
    if status == "select_wifi":
        if wifi_index == 0:
            status = "search wifi"
            if len(wifi_list) > 0:
                del wifi_list[:]
                del wifi_list_profile[:]
        else:
            if DEBUG:
                font = pygame.font.Font('C:\\Windows\\Fonts\\MyriadPro-Light.ttf', 30)
            else:
                font = pygame.font.Font('MyriadPro-Light.ttf', 30)
            text = wifi_list[wifi_index]
            textSurface = font.render(text, True, WHITE)
            textRect = textSurface.get_rect()
            textRect.center = (int(WIDTH / 2), int(HEIGHT / 2))

            print(mouse_pos.x, mouse_pos.y, textRect)
            if textRect.collidepoint(mouse_pos.x, mouse_pos.y):
                status = "insert_password_wifi"
                return True
    return False


def check_hit_back(mouse_pos):
    global status
    if status == "insert_password_wifi":
        button = pygame.Rect(4,55, int(WIDTH / 2) - 8, 60)
        if button.collidepoint(mouse_pos.x, mouse_pos.y):
            status = "select_wifi"
            return True
    return False


def check_hit_confirm(mouse_pos, password):
    global status
    if status == "insert_password_wifi":
        if len(password) > 0:
            button = pygame.Rect(4+int(WIDTH / 2), 55, int(WIDTH / 2) - 8, 60)
            if button.collidepoint(mouse_pos.x, mouse_pos.y):
                status = "check_password_wifi"
                return True
    return False


def check_hit_confirm_configuration(mouse_pos):
    global start_time
    start_time = None
    if mouse_pos.x <= int(WIDTH/2):
        return "show weather"
    else:
        print(mouse_pos.x)
        return "check connected"


def draw_background(status):
    global screen, WIDTH, HEIGHT, WHITE, DEBUG
    if DEBUG:
        font = pygame.font.Font('C:\\Windows\\Fonts\\MyriadPro-Light.ttf', 30)
    else:
        font = pygame.font.Font('MyriadPro-Light.ttf', 30)

    if status in ("search wifi", "select_wifi"):
        screen.fill(BLACK)
        screen.blit(draw_background_surface("#68c4ff", "#d1f4ff", WIDTH, HEIGHT), (0, 0))
    elif status in ("insert password wifi"):
        screen.fill(BLACK)
        screen.blit(draw_background_surface("#68c4ff", "#d1f4ff", WIDTH, HEIGHT), (0, 0))
    elif status in ("check_password_wifi"):
        screen.fill(BLACK)
        screen.blit(draw_background_surface("#68c4ff", "#d1f4ff", WIDTH, HEIGHT), (0, 0))
    elif status in ("authenticating_password_wifi"):
        screen.fill(BLACK)
        screen.blit(draw_background_surface("#68c4ff", "#d1f4ff", WIDTH, HEIGHT), (0, 0))
        textSurface = font.render("Verifying authentication...", True, WHITE)
        textRect = textSurface.get_rect()
        textRect.center = (int(WIDTH / 2), int(HEIGHT / 2))
        screen.blit(textSurface, (textRect.left, textRect.top))
    elif status in ("check_password_wifi_wrong"):
        screen.fill(BLACK)
        screen.blit(draw_background_surface("#68c4ff", "#d1f4ff", WIDTH, HEIGHT), (0, 0))
        textSurface = font.render("Wrong password", True, WHITE)
        textRect = textSurface.get_rect()
        textRect.center = (int(WIDTH / 2), int(HEIGHT / 2))
        screen.blit(textSurface, (textRect.left, textRect.top))
    elif status in ("password_wifi_wrong"):
        screen.fill(BLACK)
        screen.blit(draw_background_surface("#68c4ff", "#d1f4ff", WIDTH, HEIGHT), (0, 0))
        textSurface = font.render("Wrong password", True, WHITE)
        textRect = textSurface.get_rect()
        textRect.center = (int(WIDTH / 2), int(HEIGHT / 2))
        screen.blit(textSurface, (textRect.left, textRect.top))
    elif status in ("connected"):
        screen.fill(BLACK)
        screen.blit(draw_background_surface("#68c4ff", "#d1f4ff", WIDTH, HEIGHT), (0, 0))
        textSurface = font.render("Connected", True, WHITE)
        textRect = textSurface.get_rect()
        textRect.center = (int(WIDTH / 2), int(HEIGHT / 2))
        screen.blit(textSurface, (textRect.left, textRect.top))


def draw_input_password(width, height, x, y, text):
    global WIDTH, HEIGHT
    password_field = pygame.Surface((width, height), pygame.SRCALPHA)
    rect = password_field.get_rect()
    rect.center = (WIDTH / 2, height / 2)
    pygame.draw.rect(password_field, (153, 153, 153), rect, 0)
    rect2 = rect.copy()
    rect2.left = rect.left + 1
    rect2.top = rect.top + 1
    rect2.width = rect.width - 2
    rect2.height = rect.height - 2
    pygame.draw.rect(password_field, (255, 255, 255), rect2)

    screen.blit(password_field, (0, 0))

    if DEBUG:
        font = pygame.font.Font('C:\Windows\Fonts\MyriadPro-Light.ttf', 30)
    else:
        font = pygame.font.Font('MyriadPro-Light.ttf', 30)
    if len(text) > 0:
        textSurface = font.render(text, True, GRAY)
        screen.blit(textSurface, (5, 5))


def draw_blinking_input_password(width, height, x, y, text):
    if len(text) == 0:
        sec = int(round(Time.time() * 1000) / 1000)
        if sec % 2 == 0:
            blinking = pygame.Surface((2, height-8), pygame.SRCALPHA)
            rect = blinking.get_rect()
            pygame.draw.rect(blinking, (153, 153, 153), rect, 0)
            screen.blit(blinking, (4, 4))


def draw_back_button(status):
    global WIDTH, HEIGHT
    if status in ("insert password wifi"):
        button = pygame.Surface((int(WIDTH/2)-8, 60), pygame.SRCALPHA)
        rect = button.get_rect()
        pygame.draw.rect(button, (153, 153, 153), rect, 0)
        screen.blit(button, (4, 55))
        if DEBUG:
            font = pygame.font.Font('C:\Windows\Fonts\MyriadPro-Light.ttf', 30)
        else:
            font = pygame.font.Font('MyriadPro-Light.ttf', 30)
        textSurface = font.render("Back", True, WHITE)
        textRect = textSurface.get_rect()
        textRect.center = (int(WIDTH/4), 55+int(rect.height/2))
        screen.blit(textSurface, (textRect.left, textRect.top))


def draw_confirm_button(status):
    global WIDTH, HEIGHT
    if status in ("insert password wifi"):
        button = pygame.Surface((int(WIDTH / 2) - 8, 60), pygame.SRCALPHA)
        rect = button.get_rect()
        pygame.draw.rect(button, (153, 153, 153), rect, 0)
        screen.blit(button, (4+int(WIDTH / 2), 55))
        if DEBUG:
            font = pygame.font.Font('C:\Windows\Fonts\MyriadPro-Light.ttf', 30)
        else:
            font = pygame.font.Font('MyriadPro-Light.ttf', 30)
        textSurface = font.render("Confirm", True, WHITE)
        textRect = textSurface.get_rect()
        textRect.center = (WIDTH - int(WIDTH/4), 55+int(rect.height/2))
        screen.blit(textSurface, (textRect.left, textRect.top))


def position_close(val1, val2):
    if val1 == val2:
        return True
    if val1 > val2:
        return val1-val2 < 15
    elif val1 < val2:
        return val2-val1 < 15
    return False


def check_password(wifiprofile, password):
    scheme = SchemeWPA('wlan0', wifiprofile.ssid, {"ssid": wifiprofile.ssid, "psk": password, "key_mgmt": "WPA-PSK"})
    scheme.save()
    return scheme


def check_connection(scheme):
    Time.sleep(10)
    try:
        if internet_on():
            os.system("sudo ifdown wlan0")
        conn = scheme.activate()
        #print(dump(conn))
        #print("connection: ", conn)
    except:
        print("exception!!")

    if internet_on():
        return True
    else:
        scheme.delete()
        return False


def get_weather():
    global start_time, status, sleeping
    sleeping = not check_movements()
    if sleeping:
        draw_background_sleeping(screen)
    if start_time is None or Time.time() - start_time >= 3600:
        if internet_on():
            hours_now = int(datetime.datetime.now().hour)
            start_time = Time.time()
            jsonWeather = JsonWeather("http://api.openweathermap.org/data/2.5/forecast?id=6542283&appid=" + API_KEY_W + "&units=metric")
            weathers = jsonWeather.get_weathers()
            if not weathers[0] is None:

                ''' weathers[0] today
                # weathers[1] tomorrow
                # weathers[2] now '''
                icon_degree = weathers[0].get_icon_degree()
                icon_today = weathers[0].get_icon_weather(hours_now)
                icon_temp = weathers[0].get_icon_temperature()
                temp_today = weathers[0].get_temperature()
                draw_background_weather(hours_now)
                windy_icon = None
                if weathers[0].is_windy():
                    windy_icon = weathers[0].get_windy_icon()
                if not sleeping:
                    draw_today_info(icon_today, icon_degree, icon_temp, temp_today, windy_icon)

                icon_now = weathers[2].get_icon_weather(hours_now)
                temp_now = weathers[0].get_temperature()
                if not sleeping:
                    draw_now_info(icon_now, temp_now, icon_degree)

                icon_tomorrow = weathers[1].get_icon_weather()
                temp_tomorrow = weathers[1].get_temperature()
                if not sleeping:
                    draw_tomorrow_info(icon_tomorrow, temp_tomorrow, icon_degree)
                #  print(icon_today, icon_tomorrow, icon_now)
            if sleeping:
                draw_background_sleeping(screen)
        else:
            status = "search wifi"


def check_movements():
    global last_motion, start_time, SLEEPING_TIME
    if last_motion is None:
        last_motion = Time.time()

    if Time.time() - last_motion >= SLEEPING_TIME:
        # todo check motion sensor here
        # if motion last_motion = Time.time(), start_time = None return True else return False
        return False

    return True


def draw_background_sleeping(screen):
    global WIDTH, HEIGHT, BLACK, day_names
    pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, HEIGHT))

    # time
    time = datetime.datetime.now().strftime("%H:%M:%S")
    time = time.split(":")
    time = time[0] + ":" + time[1]
    font = get_font_surface(160)
    textSurface = font.render(time, True, GRAY)
    img_rect = textSurface.get_rect()
    img_rect.center = (int(WIDTH/2), int(HEIGHT/2))
    screen.blit(textSurface, (img_rect.left, img_rect.top))
    last_top = img_rect.top + img_rect.height

    # day of week name
    today = date.today()
    day_name = day_names[today.weekday()] + " " + translate(datetime.datetime.now().strftime("%d %B %Y"))
    font = get_font_surface(30)
    textSurface = font.render(day_name, True, GRAY)
    img_rect = textSurface.get_rect()
    img_rect.center = (int(WIDTH / 2), int(HEIGHT / 2))
    screen.blit(textSurface, (img_rect.left, last_top + img_rect.height))


def translate(string):
    months = ["January","February","March","April","May","June","July","August","September","October","November","December"]
    months_italian = ["Gennaio","Febbraio","Marzo","Aprile","Maggio","Giugno","Luglio","Agosto","Settembre","Ottobre","Novembre","Dicembre"]
    i = 0
    for k in months:
        if string.find(k) > -1:
            string = string.replace(k, months_italian[i])
        i = i + 1

    return string

def draw_today_info(icon_weather, icon_degree, icon_temp, temperature, windy_icon):
    global WIDTH, HEIGHT, DEBUG

    if DEBUG:
        url = "C:\\Users\\marco\\PycharmProjects\\Weather\\img\\icons\\"
    else:
        mypath = os.path.dirname(os.path.realpath(__file__))
        url = os.path.join(mypath, 'img/icons/')

    # draw main weather icon
    img_rect = draw_image(screen, url + icon_weather, 0.8, 0.8, -70, -40, True)

    x_end = int(WIDTH/2+img_rect.width/2) - 40
    y_start = img_rect.top

    # draw main temperature
    font = get_font_surface(80)
    textSurface = font.render(str(temperature), True, WHITE)
    img_rect = textSurface.get_rect()
    screen.blit(textSurface, (x_end, y_start))
    img_rect = draw_image(screen, url + icon_degree, 0.1, 0.1, x_end + img_rect.left + img_rect.width, y_start-5, False)
    img_rect = draw_image(screen, url + icon_temp, 0.2, 0.2, img_rect.left + img_rect.width - 20, y_start-5, False)
    if not windy_icon is None:
        img_rect = draw_image(screen, url + windy_icon, 0.2, 0.2, x_end , y_start + 100, False)


def draw_now_info(icon_weather, temperature, icon_degree):
    global WIDTH, HEIGHT, DEBUG

    if DEBUG:
        url = "C:\\Users\\marco\\PycharmProjects\\Weather\\img\\icons\\"
    else:
        mypath = os.path.dirname(os.path.realpath(__file__))
        url = os.path.join(mypath, 'img/icons/')

    # draw weather icon
    img_rect = draw_image(screen, url + icon_weather, 0.3, 0.3, 50, HEIGHT - 150, False)

    x_end = img_rect.width + 60
    y_start = 330

    # draw main temperature
    font = get_font_surface(70)
    textSurface = font.render(str(temperature), True, WHITE)
    img_rect = textSurface.get_rect()
    screen.blit(textSurface, (x_end, y_start))
    img_rect = draw_image(screen, url + icon_degree, 0.1, 0.1, x_end + img_rect.width, HEIGHT - 150, False)


def draw_tomorrow_info(icon_weather, temperature, icon_degree):
    global WIDTH, HEIGHT, DEBUG

    if DEBUG:
        url = "C:\\Users\\marco\\PycharmProjects\\Weather\\img\\icons\\"
    else:
        mypath = os.path.dirname(os.path.realpath(__file__))
        url = os.path.join(mypath, 'img/icons/')

    # draw weather icon
    img_rect = draw_image(screen, url + icon_weather, 0.3, 0.3, WIDTH - 280, HEIGHT - 150, False)

    x_end = img_rect.left + img_rect.width + 10
    y_start = 330

    # draw main temperature
    font = get_font_surface(70)
    textSurface = font.render(str(temperature), True, WHITE)
    img_rect = textSurface.get_rect()
    screen.blit(textSurface, (x_end, y_start))
    img_rect = draw_image(screen, url + icon_degree, 0.1, 0.1, x_end + img_rect.width, HEIGHT - 150, False)


def draw_fill(surf_dest, color, size):
    pygame.draw.rect(surf_dest, color, size)


def draw_image(surf_dest, url, scale_x=1, scale_y=1, padding_left=0, padding_top=0, centered=False):
    img_surf = pygame.image.load(url)
    img_rect = img_surf.get_rect()
    img_surf = pygame.transform.smoothscale(img_surf, (int(img_rect.width * scale_x), int(img_rect.height * scale_y)))
    img_rect = img_surf.get_rect()
    if centered:
        img_rect.center = (int(WIDTH / 2), int(HEIGHT / 2))
    img_rect.left = img_rect.left + padding_left
    img_rect.top = img_rect.top + padding_top
    surf_dest.blit(img_surf, (img_rect.left, img_rect.top))
    return img_rect


def get_font_surface(size):
    global DEBUG
    if DEBUG:
        font = pygame.font.Font('C:\Windows\Fonts\MyriadPro-Light.ttf', size)
    else:
        font = pygame.font.Font('MyriadPro-Light.ttf', size)
    return font


def draw_background_weather(hours):
    global screen, WIDTH, HEIGHT
    if DEBUG:
        font = pygame.font.Font('C:\\Windows\\Fonts\\MyriadPro-Light.ttf', 30)
    else:
        font = pygame.font.Font('MyriadPro-Light.ttf', 30)
    col1 = "#001f45"
    col2 = "#003c87"
    if hours > 6 and hours < 18:
        col1 = "#b1fff9"
        col2 = "#8cbfff"
    screen.fill(BLACK)
    screen.blit(draw_background_surface(col1, col2, WIDTH, HEIGHT), (0, 0))


def draw_background_configuration():
    global screen, GRAY
    screen.fill(GRAY)
    if DEBUG:
        url = "C:\\Users\\marco\\PycharmProjects\\Weather\\img\\utils\\"
    else:
        mypath = os.path.dirname(os.path.realpath(__file__))
        url = os.path.join(mypath, 'img/utils/')

    # back icon
    img_surf = pygame.image.load(url + "left-arrow.png")
    img_rect = img_surf.get_rect()
    img_surf = pygame.transform.smoothscale(img_surf, (int(img_rect.width * 0.5), int(img_rect.height * 0.5)))
    img_rect = img_surf.get_rect()
    img_rect.center = (int(WIDTH / 4), int(HEIGHT / 2))
    #img_rect.left = img_rect.left + padding_left
    #img_rect.top = img_rect.top + padding_top
    screen.blit(img_surf, (img_rect.left, img_rect.top))

    # wifi icon
    img_surf = pygame.image.load(url + "wifi.png")
    img_rect = img_surf.get_rect()
    img_surf = pygame.transform.smoothscale(img_surf, (int(img_rect.width * 0.5), int(img_rect.height * 0.5)))
    img_rect = img_surf.get_rect()
    img_rect.center = (int(WIDTH / 2)+int(WIDTH / 4), int(HEIGHT / 2))
    # img_rect.left = img_rect.left + padding_left
    # img_rect.top = img_rect.top + padding_top
    screen.blit(img_surf, (img_rect.left, img_rect.top))


def main():
    global DEBUG, status, mouse_down, mouse_up, mouse_pos_down, mouse_pos_down_old, mouse_pos, mouse_pos_old, \
        mouse_pos_up, wifi_changing, wifi_index, WAITING_SCREEN_END

    '''if not DEBUG:
        pygame.mouse.set_visible(False)'''
    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[0]
    schema = None
    wifi_list = []
    wifi_list_profile = []
    loading = group = None
    check_wifi = 0
    clicked = False
    keyboard = None
    waiting_screen = None
    pygame.mouse.set_pos(int(WIDTH/2), int(HEIGHT/2))
    while True:
        mouse_up = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
                mouse_down = True
                mouse_up = False
                clicked = False

                if mouse_pos_down_old.y == -1000:
                    mouse_pos_down_old.y = event.pos[0]
                    mouse_pos_down_old.x = event.pos[1]
                    mouse_pos_down.x = event.pos[0]
                    mouse_pos_down.y = event.pos[1]
                else:
                    mouse_pos_down_old.y = mouse_pos_down.x
                    mouse_pos_down_old.x = mouse_pos_down.y
                    mouse_pos_down.x = event.pos[0]
                    mouse_pos_down.y = event.pos[1]
            elif event.type == pygame.MOUSEMOTION:
                if mouse_pos.y == -1000:
                    mouse_pos_old.x = event.pos[0]
                    mouse_pos_old.y = event.pos[1]
                    mouse_pos.x = event.pos[0]
                    mouse_pos.y = event.pos[1]
                else:
                    mouse_pos_old.x = mouse_pos.x
                    mouse_pos_old.y = mouse_pos.y
                    mouse_pos.x = event.pos[0]
                    mouse_pos.y = event.pos[1]
            elif event.type == pygame.MOUSEBUTTONUP and event.button == LEFT:
                mouse_down = False
                mouse_up = True
                mouse_pos_up.x = event.pos[0]
                mouse_pos_up.y = event.pos[1]
                mouse_pos.x = event.pos[0]
                mouse_pos.y = event.pos[1]

                if position_close(mouse_pos_down.y, mouse_pos_up.y):
                    clicked = True

                mouse_pos_down_old.y = -1000
                mouse_pos_down_old.x = -1000
                mouse_pos_down.x = -1000
                mouse_pos_down.y = -1000

        if status == "check connected":
            if internet_on():
                status = "connected"
                waiting_screen = Time.time()
            else:
                status = "search wifi"
        elif status == "search wifi":
            if loading is None:
                loading = Loading()
                loading.set_position(int(WIDTH/2), int(HEIGHT/2))
                group = pygame.sprite.Group(loading)

            while check_wifi < 30:
                iface.scan()
                check_wifi = check_wifi + 1
                if check_wifi % 2 == 0:
                    group.update()
                    draw_background(status)
                    group.draw(screen)
                    pygame.display.update()
                    pygame.display.flip()

            res_wifi = iface.scan_results()
            for wf in res_wifi:
                if not wf.ssid in wifi_list:
                    wifi_list.append(wf.ssid)
                    if DEBUG:
                        wifi_list_profile.append(Wifiprofile(wf.ssid, wf.auth[0], wf.akm[0], wf.cipher))
                    else:
                        wifi_list_profile.append(Wifiprofile(wf.ssid, wf.auth, wf.akm, wf.cipher))

            if len(wifi_list) > 0 and check_wifi >= 10:
                wifi_list.insert(0, "Search WiFi again")
                wifi_list_profile.insert(0, "Search WiFi again")
                status = "select_wifi"
                check_wifi = 0
            else:
                check_wifi = 0
        elif status == "select_wifi":
            draw_background(status)
            if clicked:
                check_hit(mouse_pos, wifi_index, wifi_list, wifi_list_profile)
                clicked = False
            elif mouse_up and not wifi_changing and mouse_pos.y != mouse_pos_old.y and mouse_pos.y != -1000 and \
                    mouse_pos_old.y != -1000:
                if mouse_pos.y > mouse_pos_old.y:
                    diff = mouse_pos.y - mouse_pos_old.y
                    if diff > 10:
                        wifi_index = wifi_index - 1
                        if wifi_index < 0:
                            wifi_index = 0
                else:
                    diff = mouse_pos_old.y - mouse_pos.y
                    if diff > 10:
                        wifi_index = wifi_index + 1
                        if wifi_index > len(wifi_list) - 1:
                            wifi_index = len(wifi_list) - 1

            wifi_surface = get_wifi_list_surface(wifi_list, wifi_index)

            # MASK TOP
            mask_surf_top = draw_background_surface("#FFFFFF", "#FFFFFF", WIDTH, 70, 0, 255)
            save_img(mask_surf_top, "mask_surf_top")
            # MASK BOTTOM
            mask_surf_bottom = draw_background_surface("#FFFFFF", "#FFFFFF", WIDTH, 70, 255, 0)
            save_img(mask_surf_bottom, "mask_surf_bottom")

            # PLACE THE MASK
            mask_container = pygame.Surface(size, pygame.SRCALPHA)
            mask_container.blit(mask_surf_top, (0, int(HEIGHT/2-20)-40))
            mask_container.blit(mask_surf_bottom, (0, int(HEIGHT / 2 - 20)))

            wifi_surface.blit(mask_container, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            screen.blit(wifi_surface, (0, 0, WIDTH, HEIGHT))
            wifi_changing = False
        elif status == "insert password wifi":
            draw_background(status)
            if keyboard is None:
                keyboard = Keyboard(screen, WIDTH, HEIGHT, WIDTH-2, 200)
            keyboard.draw_keyboard_surface()
            draw_back_button(status)
            draw_confirm_button(status)
            if clicked:
                keyboard.check_hit(mouse_pos.x, mouse_pos.y)
                check_hit_back(mouse_pos)
                if check_hit_confirm(mouse_pos, keyboard.get_password()):
                    password = keyboard.get_password()
                    keyboard.clean_password()
                clicked = False
            draw_input_password(WIDTH, 50, 0, 0, keyboard.get_password())
            draw_blinking_input_password(WIDTH, 50, 0, 0, keyboard.get_password())
        elif status == "check_password_wifi":
            draw_background(status)
            schema = check_password(wifi_list_profile[wifi_index], password)
            if not schema is None:
                status = "authenticating_password_wifi"
            else:
                print("no a correct Schema")
        elif status == "authenticating_password_wifi":
            draw_background(status)
            pygame.display.update()
            pygame.display.flip()
            if check_connection(schema):
                status = "connected"
                waiting_screen = Time.time()
            else:
                status = "password_wifi_wrong"
                waiting_screen = Time.time()
        elif status == "password_wifi_wrong":
            draw_background(status)
            if clicked or Time.time() - waiting_screen > WAITING_SCREEN_END:
                status = "search wifi"
                clicked = False
                waiting_screen = None
        elif status == "connected":
            draw_background(status)
            if Time.time() - waiting_screen > WAITING_SCREEN_END:
                status = "show weather"
                waiting_screen = None
        elif status == "show weather":
            if clicked:
                status = "show configuration"
                clicked = False
            else:
                get_weather()
        elif status == "show configuration":
            draw_background_configuration()
            if clicked:
                status = check_hit_confirm_configuration(mouse_pos)
                clicked = False
        elif status == "disconnected":
            print("disconnected")
            status = "search wifi"

        pygame.display.update()
        pygame.display.flip()
        # --- Limit to 60 frames per second
        clock.tick(60)
    return False


if __name__ == '__main__':
    try:
        # device = get_device()
        main()
    except KeyboardInterrupt:
        pass

