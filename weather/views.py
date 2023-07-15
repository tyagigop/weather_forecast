from django.shortcuts import render
import requests
from .models import *
import datetime
import time


# Create your views here.


def home(request):
    if request.method == "POST":
        lat = request.POST.get("lat")
        lon = request.POST.get("lon")
        detail =request.POST.get("detailing_type")

        data = get_weather(lat, lon,detail)
    else:
        lat = 33.44  # Default latitude
        lon = -94.04  # Default longitude
        detail ='daily'
        data = get_weather(lat, lon,detail)


    if(detail == 'minute'):
        forecast_type = 'Minutly Forecast for one hour'
    elif(detail=='hourly'):
        forecast_type = 'Hourly Forecast for 48 hours'
    else:
        forecast_type = 'Daily Forecast for 7 days'



    if(detail=='minute'):
        detail = 'minutely'
    weather_data = get_data(data,detail)

    if(detail == 'hourly' ):
        dat ='Time'
    else:
        dat = 'Date'
    
    city = data['timezone']


    temp = round(data['current']['temp'] - 273, 2)
    feels_like = round(data['current']['feels_like'] - 273, 2)
    desc = data['current']['weather'][0]['description'].capitalize()
    x1=datetime.datetime.fromtimestamp(data['current']['sunrise'])
    x2=datetime.datetime.fromtimestamp(data['current']['sunset'])
    sunrise = x1.strftime('%H:%M:%S')
    sunset = x2.strftime('%H:%M:%S')


    current_weather = {
        'temp' : temp,
        'feels_like' : feels_like,
        'pressure'   : data['current']['pressure'],
        'humidity'   : data['current']['humidity'],
        'visibility' : data['current']['visibility'],
        
        'description' : desc,
        'icon' : data['current']['weather'][0]['icon'],
        'sunrise' : sunrise,
        'sunset' : sunset,

    }


    context = {'weather_data' : weather_data,
            'dat' : dat,
            'city' : city,
            'forecast_type' : forecast_type,
            'detail' : detail,
            'current_weather' : current_weather,

        }


    return render(request,'index.html', context)


def get_data(data,detail):
    weather_data = []

    for i in data[detail]:
        x=datetime.datetime.fromtimestamp(i['dt'])
        if(detail == 'hourly'):
            temp = round(i['temp'] - 273, 2)
            date = x.strftime('%H:%M:%S')

        elif(detail == 'daily'):
            temp = round(i['temp']['day'] - 273, 2)
            
            date = x.strftime('%Y-%m-%d')
        else:
            date = x.strftime('%H:%M:%S')


        if(detail == 'minutely'):
            dic = {
                'date' : date,
                'precipitation' : i['precipitation']
            }
        else:

            dic = {
                'date' : date,
                'temp' : temp,
                'pressure' : i['pressure'],
                'humidity' : i['humidity'],
                'wind_speed' : i['wind_speed'],
                'description' : i['weather'][0]['description'],
                'icon' : i['weather'][0]['icon'],
            }
        weather_data.append(dic)
    
    return weather_data




def get_weather(lat,lon,detailing_type):
    time_limit = datetime.datetime.now() - datetime.timedelta(minutes=10)

    try:
        weather_data = WeatherData.objects.get(lat=lat, lon=lon, last_updated__gte=time_limit)
        data = weather_data.data
    except WeatherData.DoesNotExist:


        if detailing_type == 'minute':
            api_url = f'https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=hourly,daily&appid=efd72217fe5988c3d1de1fe44d6e9ebd'
            exclude = 'current,minutely,hourly,daily'
        elif detailing_type == 'hourly':
            api_url = f'https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=minutely,daily&appid=efd72217fe5988c3d1de1fe44d6e9ebd'
            exclude = 'current,minutely,daily'
        elif detailing_type == 'daily':
            api_url = f'https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=minutely,hourly&appid=efd72217fe5988c3d1de1fe44d6e9ebd'
            exclude = 'current,minutely,hourly'
        else:
            # Handle invalid detailing type
            return None

        response = requests.get(api_url.format(lat,lon))

        response = requests.get(api_url)
        data = response.json()
        weather_data = WeatherData(lat=lat, lon=lon, data=data, last_updated=datetime.datetime.now())
        weather_data.save()

    return data
