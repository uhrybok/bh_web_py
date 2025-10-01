import requests

ICONS = {
    "clear": "https://cdn-icons-png.freepik.com/128/11742/11742559.png",
    "cloudy": "https://cdn-icons-png.freepik.com/128/11742/11742562.png",
    "overcast": "https://cdn-icons-png.freepik.com/128/11742/11742566.png",
    "rain": "https://cdn-icons-png.freepik.com/128/11742/11742614.png",
    "thundershower": "https://cdn-icons-png.freepik.com/128/11742/11742575.png",
    "snow": "https://cdn-icons-png.freepik.com/128/11742/11742619.png"
}

def get_weather(city):    
    url = f'http://api.openweathermap.org/data/2.5/weather'
    params = {'q': city, 'APPID': '2a4ff86f9aaa70041ec8e82db64abf56'}
    res = requests.get(url, params) # делаем GET запрос
    return res.json() # так как возвращают json, конвертируем его в словарь

def temp_c(temp_k):
    temp = temp_k-273.15
    return f"{temp:+.0f} °C"

def select_icon(data, res):
    if data["clouds"]["all"] < 25:
        res["icon"] = ICONS["clear"]
        res["icon_alt"] = "clear"
    elif data["clouds"]["all"] > 75:
        res["icon"] = ICONS["overcast"]
        res["icon_alt"] = "overcast"
    else:
        res["icon"] = ICONS["cloudy"]
        res["icon_alt"] = "cloudy"
    
    if "rain" in data:
        if data["rain"]["1h"] > 0.9:
            res["icon"] = ICONS["rain"]
            res["icon_alt"] = "rain"

    if "snow" in data:
        if data["snow"]["1h"] > 0.9:
            res["icon"] = ICONS["snow"]
            res["icon_alt"] = "snow"    

def prepare_data(data, res):
    if data["cod"] == 200:
        if data["name"].lower() == res["name"].lower():
            res["temp"] = temp_c(data["main"]["temp"])
            select_icon(data, res)
            return
    res["temp"] = f"City {res["name"]} not found"
    
            
def city(ct):
    data = get_weather(ct)
    # print(data)
    res = {"name": ct.title()}
    prepare_data(data, res)

    return res