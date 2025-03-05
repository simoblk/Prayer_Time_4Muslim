import requests
from datetime import datetime, timedelta
import json
import csv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from tkinter import font as tkfont
from tkcalendar import Calendar  # Requires tkcalendar library

# Constants
API_URL = "http://api.aladhan.com/v1/timingsByCity"
METHODS = {
    "Shia Ithna-Ansari": 0,
    "University of Islamic Sciences, Karachi": 1,
    "Islamic Society of North America (ISNA)": 2,
    "Muslim World League (MWL)": 3,
    "Umm Al-Qura, Makkah": 4,
    "Egyptian General Authority of Survey": 5,
    "Institute of Geophysics, University of Tehran": 7
}

# Function to fetch prayer times
def get_prayer_times(city, country, date, method):
    params = {
        "city": city,
        "country": country,
        "method": method,
        "date": date
    }
    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        return data["data"]["timings"]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching prayer times: {e}")
        return None

# Function to fetch monthly prayer times
def fetch_monthly_prayer_times(city, country, year, month, method):
    monthly_times = {}
    start_date = datetime(year, month, 1)
    next_month = start_date.replace(day=28) + timedelta(days=4)
    end_date = next_month - timedelta(days=next_month.day)
    
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%d-%m-%Y")
        prayer_times = get_prayer_times(city, country, date_str, method)
        if prayer_times:
            monthly_times[date_str] = prayer_times
        current_date += timedelta(days=1)
    return monthly_times

# Function to save data to a JSON file
def save_to_json(data, filename="prayer_times.json"):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)
    print(f"Data saved to {filename}")

# Function to save data to a CSV file
def save_to_csv(data, filename="prayer_times.csv"):
    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Date", "Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"])
        for date, timings in data.items():
            writer.writerow([date, timings["Fajr"], timings["Dhuhr"], timings["Asr"], timings["Maghrib"], timings["Isha"]])
    print(f"Data saved to {filename}")

# Function to save data to a PDF file
def save_to_pdf(data, filename="prayer_times.pdf"):
    c = canvas.Canvas(filename, pagesize=letter)
    c.setFont("Helvetica", 12)
    y = 750  # Starting y position
    for date, timings in data.items():
        c.drawString(50, y, f"📅 Date: {date}")
        y -= 20
        c.drawString(50, y, f"🕋 Fajr: {timings['Fajr']}")
        y -= 20
        c.drawString(50, y, f"🕋 Dhuhr: {timings['Dhuhr']}")
        y -= 20
        c.drawString(50, y, f"🕋 Asr: {timings['Asr']}")
        y -= 20
        c.drawString(50, y, f"🕋 Maghrib: {timings['Maghrib']}")
        y -= 20
        c.drawString(50, y, f"🕋 Isha: {timings['Isha']}")
        y -= 30  # Add extra space between dates
        if y < 50:  # Create a new page if running out of space
            c.showPage()
            y = 750
    c.save()
    print(f"Data saved to {filename}")

# Function to handle the "Fetch" button click
def gui_fetch_prayer_times():
    city = city_entry.get()
    country = country_entry.get()
    method = method_var.get()
    selected_date = cal.get_date()
    year, month = map(int, selected_date.split("-")[:2])
    
    if not city or not country or not method:
        messagebox.showerror("Error", "Please fill in all fields.")
        return
    
    monthly_times = fetch_monthly_prayer_times(city, country, year, month, METHODS[method])
    
    if not monthly_times:
        messagebox.showerror("Error", "Failed to fetch prayer times.")
        return
    
    # Clear previous results and display new ones
    result_text.delete(1.0, tk.END)
    for date, timings in monthly_times.items():
        result_text.insert(tk.END, f"\n📅 Date: {date}\n")
        result_text.insert(tk.END, "----------------------------\n")
        for name, time in timings.items():
            result_text.insert(tk.END, f"🕋 {name}: {time}\n")
        result_text.insert(tk.END, "\n")
    
    # Save to JSON by default
    save_to_json(monthly_times, f"prayer_times_{city}_{year}_{month}.json")
    messagebox.showinfo("Success", "Prayer times fetched and saved successfully!")

# Function to handle export options
def export_data():
    if not result_text.get(1.0, tk.END).strip():
        messagebox.showerror("Error", "No data to export.")
        return
    
    export_format = export_var.get()
    city = city_entry.get()
    selected_date = cal.get_date()
    year, month = map(int, selected_date.split("-")[:2])
    
    if export_format == "CSV":
        save_to_csv(monthly_times, f"prayer_times_{city}_{year}_{month}.csv")
    elif export_format == "PDF":
        save_to_pdf(monthly_times, f"prayer_times_{city}_{year}_{month}.pdf")
    messagebox.showinfo("Success", f"Data exported to {export_format} successfully!")

# GUI Setup
app = tk.Tk()
app.title("Prayer Times Fetcher")
app.geometry("700x600")  # Set window size
app.configure(bg="#f0f0f0")  # Light gray background

# Custom Fonts
title_font = tkfont.Font(family="Helvetica", size=16, weight="bold")
label_font = tkfont.Font(family="Helvetica", size=12)
button_font = tkfont.Font(family="Helvetica", size=12, weight="bold")

# Title Label
title_label = ttk.Label(app, text="🌙 Monthly Prayer Times Fetcher", font=title_font, background="#f0f0f0")
title_label.grid(row=0, column=0, columnspan=2, pady=(10, 20))

# Input Fields
ttk.Label(app, text="City:", font=label_font, background="#f0f0f0").grid(row=1, column=0, padx=10, pady=5, sticky="e")
city_entry = ttk.Entry(app, font=label_font, width=25)
city_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")

ttk.Label(app, text="Country:", font=label_font, background="#f0f0f0").grid(row=2, column=0, padx=10, pady=5, sticky="e")
country_entry = ttk.Entry(app, font=label_font, width=25)
country_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")

ttk.Label(app, text="Calculation Method:", font=label_font, background="#f0f0f0").grid(row=3, column=0, padx=10, pady=5, sticky="e")
method_var = tk.StringVar(value="Islamic Society of North America (ISNA)")
method_dropdown = ttk.Combobox(app, textvariable=method_var, values=list(METHODS.keys()), font=label_font, width=25)
method_dropdown.grid(row=3, column=1, padx=10, pady=5, sticky="w")

# Calendar Widget
ttk.Label(app, text="Select Month and Year:", font=label_font, background="#f0f0f0").grid(row=4, column=0, padx=10, pady=5, sticky="e")
cal = Calendar(app, selectmode="day", year=datetime.now().year, month=datetime.now().month, date_pattern="yyyy-mm-dd")
cal.grid(row=4, column=1, padx=10, pady=5, sticky="w")

# Fetch Button
fetch_button = ttk.Button(app, text="Fetch Prayer Times", command=gui_fetch_prayer_times, style="Accent.TButton")
fetch_button.grid(row=5, column=0, columnspan=2, pady=20)

# Export Options
export_var = tk.StringVar(value="CSV")
export_frame = ttk.LabelFrame(app, text="Export Options", padding=10)
export_frame.grid(row=6, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

ttk.Radiobutton(export_frame, text="CSV", variable=export_var, value="CSV").pack(side="left", padx=10)
ttk.Radiobutton(export_frame, text="PDF", variable=export_var, value="PDF").pack(side="left", padx=10)
export_button = ttk.Button(export_frame, text="Export Data", command=export_data, style="Accent.TButton")
export_button.pack(side="right", padx=10)

# Result Text Box
result_text = scrolledtext.ScrolledText(app, wrap=tk.WORD, font=label_font, width=70, height=15, bg="#ffffff", fg="#333333")
result_text.grid(row=7, column=0, columnspan=2, padx=10, pady=10)

# Custom Style for Button
style = ttk.Style()
style.configure("Accent.TButton", font=button_font, background="#4CAF50", foreground="white", padding=10)

# Run the GUI
app.mainloop()