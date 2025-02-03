from flask import Flask, render_template, request, send_file
import requests
import matplotlib.pyplot as plt
import io
import numpy as np
from sklearn.linear_model import LinearRegression

app = Flask(__name__)

def get_weather(city_name, api_key):
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}q={city_name}&appid={api_key}&units=metric"

    response = requests.get(complete_url)

    if response.status_code == 200:
        data = response.json()
        main = data['main']
        wind = data['wind']
        weather_description = data['weather'][0]['description']

        weather_info = {
            "temperature": main['temp'],
            "pressure": main['pressure'],
            "humidity": main['humidity'],
            "wind_speed": wind['speed'],
            "description": weather_description
        }
        return weather_info
    else:
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    weather_data = {}
    if request.method == 'POST':
        cities = request.form['cities'].split(',')
        api_key = "2b96a8439385796545930ee2c5ac5473"
        for city in cities:
            city = city.strip()
            weather_info = get_weather(city, api_key)
            if weather_info:
                weather_data[city] = weather_info
    return render_template('index.html', weather_data=weather_data)

@app.route('/plot.png')
def plot_png():
    cities = request.args.get('cities').split(',')
    api_key = "2b96a8439385796545930ee2c5ac5473"
    
    pressures = []
    temperatures = []
    labels = []

    for city in cities:
        city = city.strip()
        weather_data = get_weather(city, api_key)
        if weather_data:
            pressures.append(weather_data['pressure'])
            temperatures.append(weather_data['temperature'])
            labels.append(city)
    
    if pressures and temperatures:
        x = np.array(pressures).reshape(-1, 1)
        y = np.array(temperatures)
        
        model = LinearRegression()
        model.fit(x, y)
        y_pred = model.predict(x)

        plt.figure()
        plt.scatter(x, y, color='blue')
        plt.plot(x, y_pred, color='red')
        
        for i, txt in enumerate(labels):
            plt.annotate(txt, (x[i], y[i]))
        
        plt.xlabel('Pressão (hPa)')
        plt.ylabel('Temperatura (°C)')
        plt.title('Regressão Linear entre Pressão e Temperatura')

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        return send_file(buf, mimetype='image/png')
    else:
        return "No data available for these cities.", 404

if __name__ == '__main__':
    app.run(debug=True)
