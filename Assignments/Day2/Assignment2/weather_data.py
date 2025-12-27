import requests
city = input("Enter city name: ")
import os
api_key = os.getenv("WEATHER_API")
try:
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    print("status code:", response.status_code)
    # print("response text:", response.text)
    data = response.json()
    print("resp data: ", data)

    with open("weather_report.txt", "w") as file:
        file.write(f"City: {data['name']}\n")
        file.write(f"Temperature: {data['main']['temp']} °C\n")
        file.write(f"Humidity: {data['main']['humidity']} %\n")
        file.write(f"Wind Speed: {data['wind']['speed']} m/s\n")
except:
    print("Some error occured.")