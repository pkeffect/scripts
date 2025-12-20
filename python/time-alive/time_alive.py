# VERSION: 0.0.3
import datetime
import time
import os
import sys

# ANSI escape codes for colors
COLORS = {
    "reset": "\033[0m",
    "bold": "\033[01m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
}

def color_text(text, color_name):
    """Applies ANSI color to text."""
    if color_name in COLORS:
        return COLORS[color_name] + text + COLORS["reset"]
    else:
        return text

def clear_screen():
    """Clears the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def move_cursor_to_top():
    """Moves cursor to top of terminal without clearing."""
    sys.stdout.write("\033[H")
    sys.stdout.flush()

def get_datetime_input(prompt):
    """Gets date and time input from the user (without seconds) and returns a datetime object."""
    while True:
        date_str = input(f"{prompt} (YYYY-MM-DD HH:MM): ")
        try:
            return datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M')
        except ValueError:
            print(color_text("Invalid date and time format.", "red") + " Please use YYYY-MM-DD HH:MM format.")

def calculate_age_components(birth_datetime, current_datetime):
    """Calculates exact age components (years, months, days, hours, minutes, seconds)."""
    
    # Start with the current datetime components
    year = current_datetime.year
    month = current_datetime.month
    day = current_datetime.day
    hour = current_datetime.hour
    minute = current_datetime.minute
    second = current_datetime.second
    
    birth_year = birth_datetime.year
    birth_month = birth_datetime.month
    birth_day = birth_datetime.day
    birth_hour = birth_datetime.hour
    birth_minute = birth_datetime.minute
    birth_second = birth_datetime.second
    
    # Calculate seconds
    if second < birth_second:
        second += 60
        minute -= 1
    second -= birth_second
    
    # Calculate minutes
    if minute < birth_minute:
        minute += 60
        hour -= 1
    minute -= birth_minute
    
    # Calculate hours
    if hour < birth_hour:
        hour += 24
        day -= 1
    hour -= birth_hour
    
    # Calculate days
    if day < birth_day:
        month -= 1
        if month <= 0:
            month = 12
            year -= 1
        # Get days in the previous month
        if month == 2:
            # Check for leap year
            if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
                day += 29
            else:
                day += 28
        elif month in [4, 6, 9, 11]:
            day += 30
        else:
            day += 31
    day -= birth_day
    
    # Calculate months
    if month < birth_month:
        month += 12
        year -= 1
    month -= birth_month
    
    # Calculate years
    years = year - birth_year
    
    return years, month, day, hour, minute, second

if __name__ == "__main__":
    print(color_text("🎉 Welcome to the Amazing Age Timer! 🎉", "cyan"))

    birth_datetime = get_datetime_input(color_text("👶 Please enter your date and time of birth", "yellow"))
    current_datetime_input = get_datetime_input(color_text("📅 Please enter your current date and time", "yellow"))

    print(color_text("\n⏳ Age Timer starting... Press Ctrl+C to stop.", "green"))
    time.sleep(1)
    
    clear_screen()

    try:
        while True:
            current_datetime = datetime.datetime.now()
            years, months, days, hours, minutes, seconds = calculate_age_components(birth_datetime, current_datetime)

            move_cursor_to_top()
            print(color_text("✨ Time Alive! ✨", "magenta") + " 🎂")
            print("-" * 20)
            print(f"{color_text('Years:', 'blue'):<10} {color_text(str(years), 'bold')}")
            print(f"{color_text('Months:', 'blue'):<10} {color_text(str(months), 'bold')}")
            print(f"{color_text('Days:', 'blue'):<10} {color_text(str(days), 'bold')}")
            print(f"{color_text('Hours:', 'blue'):<10} {color_text(str(hours), 'bold')}")
            print(f"{color_text('Minutes:', 'blue'):<10} {color_text(str(minutes), 'bold')}")
            print(f"{color_text('Seconds:', 'blue'):<10} {color_text(str(seconds), 'bold')}")
            print("-" * 20)
            print(color_text("⏱️  Updating every second...", "cyan"))

            time.sleep(1)

    except KeyboardInterrupt:
        print(color_text("\n🛑 Age Timer stopped.", "red"))
        print(color_text("Thank you for using the Age Timer! 👋", "green"))