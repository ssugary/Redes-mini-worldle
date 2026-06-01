import math
import random
import sys
import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt

console = Console()


# Math function that calculates the haversine distance between two locations

def haversine(phi1, lambda1, phi2, lambda2):
    r = 6371.0
    phi1, lambda1, phi2, lambda2 = map(math.radians, [phi1, lambda1, phi2, lambda2]) # Convert degrees to radians
    dphi = phi2 - phi1          # Delta phi
    dlambda = lambda2 - lambda1 # Delta lambda
    
    a = math.sin(dphi/ 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return round(r * c) # Distance in kilometers


# Auxiliar function that calculates the arrow direction

def get_direction(lat_guess, lon_guess, lat_target, lon_target):
    direction = ""
    if lat_target > lat_guess:
        direction += "⬆️ N"
    elif lat_target < lat_guess:
        direction += "⬇️ S"
    
    if lon_target > lon_guess:
        direction += "➡️ E"
    elif lon_target < lon_guess:
        direction += "⬅️ W"
        
    return direction if direction else "📍"

# API Getter
def data_get():
    url = "https://countriesnow.space/api/v0.1/countries/positions"
    try:
        console.print("[yellow]Connecting in API RestCountries...[/yellow]")
        answer = requests.get(url, timeout=15)
        answer.raise_for_status()
        return answer.json()
    
    except requests.exceptions.RequestException as e:
        console.print(Panel(
            f"[bold red]Network Error![/bold red]\n{e}",
            title="⚠️ Critical Failure"
        ))
        
    return None

# API Process
def data_process(data):
    if not data or data.get('error') is True:
        return None
    
    countries = {}      # Countries dictionary
    
    for item in data['data']: 
        name = item['name']
        
        countries[name.lower().strip()] = {
            "name": name,
            "lat": item['lat'],
            "lon": item['long'],
        }
    return countries


# Game Loop Interface

def game(country_list):
    
    # Randomly choose a country
    country, data = random.choice(list(country_list.items()))
    
    
    console.clear()
    
    # Print the game rules
    console.print(Panel.fit(
        "[bold cyan]🌍 WORLDLE - GUESS THE COUNTRY 🌍[/bold cyan]\n"
        "You have 6 attempts to guess the secret country.\n"
        "With each attempt, we will show the distance and direction to the destination!",
        title="Game Rules"
    ))
        
    max_attempt = 6 #< Max attempts
    past_guess = [] #< Guess memory

    for attempt in range(1, max_attempt + 1):
        while True:
            # User input
            user_guess = Prompt.ask(f"\n[bold white]Attempt {attempt}/{max_attempt}[/bold white] - Enter a country").lower().strip()       
                     
            if user_guess in country_list:
                break
            
            # If user input is not a country, ask again
            console.print("[red]Invalid country or not found. Try again (e.g., Brazil, Japan, France).[/red]")   
                 
        guess = country_list[user_guess]
        
        # If user input is correct
        if user_guess == country:
            console.print(Panel(
                f"[bold green]🎉 CONGRATULATIONS! You got it right! 🎉[/bold green]\n"
                f"The secret country was indeed [bold gold1]{data['name']}[/bold gold1].",
                title="🏆 Victory!"
            ))
            return

        # Else
        dist = haversine(           # Get distance between the user guess and the answer
            guess['lat'], guess['lon'],
            data['lat'], data['lon']
        )
        direction = get_direction(  # Get direction between the user guess and the answer
            guess['lat'], guess['lon'],
            data['lat'], data['lon']
        )
        
        # Save the guess in memory
        past_guess.append({
            "country": guess['name'],
            "distance": f"{dist} km",
            "direction": direction
        })
        
        # Print the guesses
        table = Table(title="🗺️ Your Guesses")
        table.add_column("Guessed Country", style="cyan")
        table.add_column("Distance to Target", style="magenta")
        table.add_column("Direction to Follow", style="yellow")
        
        for p in past_guess:
            table.add_row(p['country'], p['distance'], p['direction'])
            
        console.clear()
        console.print(table)

    # If the uses up all you attempts, end the game
    console.print(Panel(
        f"[bold red]💥 Game over! You've run out of attempts. 💥[/bold red]\n"
        f"The secret country was: [bold cyan]{data['name']}[/bold cyan]",
        title="❌ Game Over"
    ))



def main():
    data = data_get()                   # Get the countries data
    if data:                            
        world_map = data_process(data)  # Process the data
        if world_map:
            game(world_map)             # Start the game loop

if __name__ == "__main__":
    main()