class Weather:
    temp_min = None
    temp_max = None
    humidity = None
    weather = None
    cloud_perc = None
    wind_speed = None
    rain_volume = []
    rain_high = False
    snow_volume = []
    snow_high = False
    # check these if necessary
    clouds = []
    winds = []
    is_today = False

    def __init__(self, is_today=False):
        self.is_today = is_today

    def is_day_time(self, hours):
        return hours >= 6 and hours < 18

    def get_icon_weather(self, hours=None):
        # print(self.weather)
        if self.is_today and hours is None:
            print("is today you need to indicate hours")
            return None
        if self.weather == "snow":
            if self.is_today:
                if self.is_day_time(hours):
                    if self.cloud_perc < 15:
                        return "neve_sole.png"
                    else:
                        return "neve.png"
                else:
                    if self.cloud_perc < 15:
                        return "neve_luna.png"
                    else:
                        return "neve.png"
            else:
                return "neve_sole.png"
        elif self.weather == "mist":
            return "nebbia.png"
        elif self.weather == "thunderstorm":
            if self.is_today:
                if self.is_day_time(hours):
                    if self.cloud_perc < 15:
                        return "temporale_sole.png"
                    else:
                        return "temporale.png"
                else:
                    if self.cloud_perc < 15:
                        return "temporale_luna.png"
                    else:
                        return "temporale.png"
            else:
                return "temporale_sole.png"
        elif self.weather == "rain" or self.weather == "shower rain":
            if self.is_today:
                if self.is_day_time(hours):
                    if self.cloud_perc < 15:
                        if self.rain_high:
                            return "pioggia_sole.png"
                        else:
                            return "pioggerella_sole.png"
                    else:
                        if self.rain_high:
                            return "pioggia.png"
                        else:
                            return "pioggerella.png"
                else:
                    if self.cloud_perc < 15:
                        if self.rain_high:
                            return "pioggia_luna.png"
                        else:
                            return "pioggerella_luna.png"
                    else:
                        if self.rain_high:
                            return "pioggia.png"
                        else:
                            return "pioggerella.png"
            else:
                if self.rain_high:
                    return "pioggia_sole.png"
                else:
                    return "pioggerella_sole.png"
        elif self.weather == "broken clouds" or self.weather == "scattered clouds" or self.weather == "clouds":
            if self.is_today:
                if self.is_day_time(hours):
                    return "nuvoloso.png"
                else:
                    return "nuvoloso.png"
            else:
                return "nuvoloso.png"
        elif self.weather == "few clouds":
            if self.is_today:
                if self.is_day_time(hours):
                    if self.cloud_perc < 15:
                        return "nuvoloso_sole.png"
                    else:
                        return "nuvoloso.png"
                else:
                    if self.cloud_perc < 15:
                        return "nuvoloso_luna.png"
                    else:
                        return "nuvoloso.png"
            else:
                return "nuvoloso_sole.png"
        elif self.weather == "clear sky" or self.weather == "clear":
            if self.is_today:
                if self.is_day_time(hours):
                    if self.wind_speed < 8:
                        return "sole.png"
                    else:
                        return "vento_sole.png"
                else:
                    if self.wind_speed < 8:
                        return "luna.png"
                    else:
                        return "vento_luna.png"
            else:
                return "sole.png"

    def get_icon_temperature(self):
        temp = self.get_temperature()
        if temp <= 0:
            return "temp_0.png"
        elif temp <= 10:
            return "temp_1.png"
        elif temp <= 15:
            return "temp_2.png"
        elif temp <= 25:
            return "temp_3.png"
        elif temp <= 30:
            return "temp_4.png"
        else:
            return "temp_5.png"

    def get_temperature(self):
        return int((self.temp_min + self.temp_max)/2)

    def get_icon_degree(self):
        return "gradi.png"

    def is_windy(self):
        return self.wind_speed > 8

    def get_windy_icon(self):
        return "vento.png"

