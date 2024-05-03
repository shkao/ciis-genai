import os
import csv
from scrapegraphai.graphs import SmartScraperGraph

# Configuration for the scraper graph
graph_config = {
    "llm": {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "model": "gpt-3.5-turbo",
    },
}

# Creating an instance of SmartScraperGraph
smart_scraper_graph = SmartScraperGraph(
    prompt="請抓取頁面中全部發明展的資訊，包含以下欄位: event_name, event_type, date, location, registration_deadline",
    source="https://www.innosociety.org/m/404-1649-53197.php?Lang=zh-tw",
    config=graph_config,
)

# Running the scraper graph
result = smart_scraper_graph.run()

# The 'events' key contains the list of events
events = result["events"]
csv_file_path = "exhibition_data.csv"

# Writing data to a CSV file
with open(csv_file_path, "w", newline="", encoding="utf-8") as file:
    csv_writer = csv.writer(file)
    csv_writer.writerow(
        ["Event Name", "Event Type", "Date", "Location", "Registration Deadline"]
    )  # header

    # Iterate through each event and write to the CSV
    for event in events:
        csv_writer.writerow(
            [
                event["event_name"],
                event.get("event_type", "N/A"),  # Using .get() for optional fields
                event["date"],
                event["location"],
                event["registration_deadline"],
            ]
        )

print(f"Data has been successfully saved to {csv_file_path}.")
