from crewai import Agent, Task, Crew
from crewai.tools import tool
import os
import requests
import datetime
from memory import save_memory, get_memory
from notifier import send_alert

# -------- TOOLS -------- #

@tool
def open_youtube():
    """Open YouTube in browser"""
    os.system("start https://youtube.com")
    return "YouTube opened"

@tool
def open_google():
    """Open Google"""
    os.system("start https://google.com")
    return "Google opened"

@tool
def tell_time():
    """Get current time"""
    return str(datetime.datetime.now())

@tool
def get_crypto_price():
    """Get current Bitcoin price"""
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    data = requests.get(url).json()
    return f"Bitcoin price is ${data['bitcoin']['usd']}"

@tool
def analyze_market():
    """Basic crypto analysis. Tells whether the market is bullish, bearish or sideways."""
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true"
    data = requests.get(url).json()
    
    price = data["bitcoin"]["usd"]
    change = data["bitcoin"]["usd_24h_change"]

    if change > 2:
        return f"Bullish trend 📈. Price: {price}"
    elif change < -2:
        return f"Bearish trend 📉. Price: {price}"
    else:
        return f"Sideways market ⚖️. Price: {price}"

@tool
def send_crypto_alert():
    """Analyze and send crypto alert"""
    result = analyze_market()
    send_alert(result)
    return "Alert sent to Telegram"

# -------- AGENTS -------- #

planner = Agent(
    role="Planner",
    goal="Break user request into steps",
    backstory="Expert in planning tasks",
    verbose=True,
    allow_delegation=True
)

executor = Agent(
    role="Executor",
    goal="Execute tasks using tools",
    backstory="Handles real-world actions",
    verbose=True,
    allow_delegation=False,
    tools=[open_youtube, open_google, tell_time, get_crypto_price, analyze_market, send_crypto_alert]
)

analyst = Agent(
    role="Analyst",
    goal="Analyze results and make decisions",
    verbose=True,
    allow_delegation=False,
    backstory="Expert in crypto and data analysis"
)

def run_multi_agent(user_input):
    memory = get_memory(user_input)
    context = f"Past memory: {memory}\nUser request: {user_input}"

    task = Task(
        description=context,
        expected_output="Final result of executing the user request",
        agent=planner
    )

    crew = Crew(
        agents=[planner, executor, analyst],
        tasks=[task],
        verbose=True
    )

    result = crew.kickoff()
    
    save_memory(user_input + " -> " + str(result))
    
    return result
