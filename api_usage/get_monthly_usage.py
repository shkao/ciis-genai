import os
from datetime import datetime, timedelta
import time
import csv
import requests
import pandas as pd


def fetch_usage_data(token, org_id, date):
    url = f"https://api.openai.com/v1/usage?date={date}"
    headers = {
        "Authorization": f"Bearer {token}",
        "OpenAI-Organization": org_id,
    }
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else None


def summarize_daily_usage(data, cost_per_input_token, cost_per_output_token):
    if not data or "data" not in data:
        return (0, 0, 0, 0.0)
    total_requests = sum(item["n_requests"] for item in data["data"])
    total_context_tokens = sum(item["n_context_tokens_total"] for item in data["data"])
    total_generated_tokens = sum(
        item["n_generated_tokens_total"] for item in data["data"]
    )
    input_token_cost = total_context_tokens * cost_per_input_token
    output_token_cost = total_generated_tokens * cost_per_output_token
    total_cost = input_token_cost + output_token_cost
    return (
        total_requests,
        total_context_tokens,
        total_generated_tokens,
        total_cost,
    )


def write_to_csv(
    filename,
    date,
    total_requests,
    total_context_tokens,
    total_generated_tokens,
    total_cost,
):
    header = [
        "Date",
        "Total Requests",
        "Total Context Tokens",
        "Total Generated Tokens",
        "Total Cost",
    ]
    data_row = [
        date,
        total_requests,
        total_context_tokens,
        total_generated_tokens,
        f"{total_cost:.2f}",
    ]
    file_exists = os.path.exists(filename)
    with open(filename, "a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(header)
        writer.writerow(data_row)


def process_month_usage(
    token, org_id, year, month, cost_per_input_token, cost_per_output_token
):
    filename = f"{year:04d}{month:02d}.csv"
    start_date = datetime(year, month, 1).date()  # Convert to date for comparison
    end_date = datetime.now().date()
    if (
        end_date.month != month or end_date.year != year
    ):  # If current date is not within the month
        end_date = (
            datetime(year, month + 1, 1) - timedelta(days=1)
            if month != 12
            else datetime(year + 1, 1, 1) - timedelta(days=1)
        ).date()  # Convert to date for comparison

    existing_dates = set()
    if os.path.exists(filename):
        with open(filename, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                existing_dates.add(row["Date"])

    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        if date_str not in existing_dates:
            data = fetch_usage_data(token, org_id, date_str)
            usage_summary = summarize_daily_usage(
                data, cost_per_input_token, cost_per_output_token
            )

            write_to_csv(filename, date_str, *usage_summary)
            time.sleep(1)  # Rest for 1 second to avoid rate limits
        current_date += timedelta(days=1)


def summarize_total_cost(year, month):
    filename = f"{year:04d}{month:02d}.csv"
    try:
        df = pd.read_csv(filename)
        total_cost_sum = df["Total Cost"].sum()
        print(f"Total Cost for {year}-{month}: {total_cost_sum:.2f}")
    except FileNotFoundError:
        print(f"No data file found for {year}-{month}.")


def main():
    TOKEN = os.environ.get("OPENAI_CIIS_API_KEY")
    ORG_ID = os.environ.get("OPENAI_ORGANIZATION")
    YEAR = datetime.now().year
    MONTH = datetime.now().month
    USD_TO_TWD_RATE = 33.0
    COST_PER_INPUT_TOKEN = 10.0 / 1000000
    COST_PER_OUTPUT_TOKEN = 30.0 / 1000000

    cost_per_input_token = COST_PER_INPUT_TOKEN * USD_TO_TWD_RATE
    cost_per_output_token = COST_PER_OUTPUT_TOKEN * USD_TO_TWD_RATE

    filename = f"{YEAR:04d}{MONTH:02d}.csv"
    process_month_usage(
        TOKEN, ORG_ID, YEAR, MONTH, cost_per_input_token, cost_per_output_token
    )
    summarize_total_cost(YEAR, MONTH)


if __name__ == "__main__":
    main()
