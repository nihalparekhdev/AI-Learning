import requests

longitude = 48.85
latitude = 2.35 

url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m"

response = requests.get(url)
data = response.json()
print(data)

temperature = data ["current"]["temperature_2m"]
print(f"The current temperature at latitude {latitude} and longitude {longitude} is {temperature}°C")

#Function to take temprature for different locations
def get_temprature (latitude, longitude):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m"
    response = requests.get(url)
    data = response.json()
    temperature = data ["current"]["temperature_2m"]
    return temperature

paris_temp = get_temprature(48.85, 2.35)
newyork_temp = get_temprature(40.71, -74.01)

print(f"The current temperature in Paris is {paris_temp}°C")
print(f"The current temperature in New York is {newyork_temp}°C")



