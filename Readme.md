# Weather

This project is for a Raspberry Weather station for bikers that need to know they have to prepare for the raining/snow, cold dresses...
The station will inform you with the middle weather of the day (if there is a rain or snow situation it will inform you), average temperature for the day and the same for tomorrow.
Finally it give the current weather and temperature such as the standard weather station as well.

It's necessary to fill the configuration.py file with these settings:

> API_KEY_W = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
>
> SLEEPING_TIME = 60  # sec
>
> WAITING_SCREEN_END = 2[/code]


Weather API provided by openweathermap.org

#### Run
> sudo Python3 \__main__.py