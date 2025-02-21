from flask import Flask, render_template, request, session, redirect, url_for
import google.generativeai as genai
import requests
import os

# Configure API Keys
genai.configure(api_key="AIzaSyCV3bvXOXo8V-OMwTj2YrW3ITrYQm0ySiw")  # Replace with your actual Gemini API key
NEWS_API_KEY = "165b0f00fdd94fa49e20d86483d5fd46"  # Replace with your actual News API key
WEATHER_API_KEY = "5e63ffd3ab59119a8c93b2a1975d44fd"  # Replace with your actual OpenWeather API key

# Initialize Flask App
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secure random key for session management

# Function to fetch news
def get_news():
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        articles = response.json().get("articles", [])
        return [article["title"] for article in articles[:10]]  # Return top 5 headlines
    return ["Could not fetch news. Try again later."]

# Function to fetch weather
def get_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return f"Weather in {city}: {data['weather'][0]['description']}, Temp: {data['main']['temp']}°C"
    return "Could not fetch weather data. Check the city name."

# Function to chat with Gemini
def chat_with_gemini(prompt):
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {e}"

# Define Flask Routes
@app.route("/", methods=["GET", "POST"])
def home():
    if "chat_history" not in session:
        session["chat_history"] = []

    if request.method == "POST":
        user_input = request.form.get("user_input").strip().lower()
        bot_reply = ""

        # Keyword detection for API calls
        if "news" in user_input:
            bot_reply = "\n".join(get_news())
        elif "weather in" in user_input:
            city = user_input.split("weather in")[-1].strip()
            bot_reply = get_weather(city)
        else:
            bot_reply = chat_with_gemini(user_input)

        session["chat_history"].append({"user": user_input, "bot": bot_reply})
        session.modified = True  

    return render_template("index.html", chat_history=session["chat_history"])

# Fix: Redirect to home after clearing chat
@app.route("/clear", methods=["POST"])
def clear_chat():
    session["chat_history"] = []
    session.modified = True
    return redirect(url_for("home"))  # Redirect back to `/`

if __name__ == "__main__":
    app.run(debug=True)
