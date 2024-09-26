import os
import emoji
import yfinance as yf
import logging
from utility import update_svg, configure_logging
import requests
from decimal import Decimal, ROUND_DOWN

configure_logging()


def main():
    output_svg_filename = 'screen-custom.svg'

    # If you make changes to this file be sure to make a backup in case you ever update!

    # Add custom code here like getting PiHole Status, car charger status, API calls.
    # Assign the value you want to display to custom_value_1, and it will replace CUSTOM_DATA_1 in screen-custom.svg.
    # You can edit the screen-custom.svg to change appearance, position, font size, add more custom data.
    data, week_percent = fetch_data()

    vti_cur_price = fetch_vti_data()

    sold_price = 238
    stocks_owned = 773
    vti_lost = (vti_cur_price - sold_price) * stocks_owned
    vti_lost = vti_lost.quantize(Decimal('0'), rounding=ROUND_DOWN)


    logging.info("Updating SVG")
    output_dict = {
        'YEAR_VAR': str(data["miles"]),
        'YEAR_GOAL': str(data["yearGoal"]),
        'MONTH_VAR': str(data["month"]),
        'MONTH_GOAL': str(data["monthGoal"]),
        'WEEK_VAR': str(data["week"]),
        'WEEK_GOAL': str(data["weekGoal"]),
        'WEEK_LEFT': str(data["weekLeft"]),
        'WEEK_PERCENT': str(week_percent),
        # 'VOO_PRICE': str(fetch_voo_data()),
        'VTI_PRICE': str(vti_cur_price),
        'VTI_LOST': str(vti_lost),
        # 'VOO_PRICE': "999",
    }

    logging.info(output_dict)
    update_svg(output_svg_filename, 'screen-output-custom-temp.svg', output_dict)


def fetch_data():
    url = os.getenv("CYCLE_URL")

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        data = response.json()

        # Extract miles value as Decimal
        miles = Decimal(data["miles"])

        # Extract week value
        week = Decimal(data["week"])

        # Round down the miles value to 2 decimal points
        # rounded_miles = miles.quantize(Decimal('0.0'), rounding=ROUND_DOWN)
        # rounded_week = week.quantize(Decimal('0.0'), rounding=ROUND_DOWN)

        weekPercent = week / 60 * 100
        rounded_weekPercent = weekPercent.quantize(Decimal('0'), rounding=ROUND_DOWN)

        return data, rounded_weekPercent

    except requests.RequestException as e:
        print("Error fetching data:", e)
        return None, None


# Function to fetch historical price data for VOO
def fetch_voo_data():
    voo_ticker = yf.Ticker("VOO")
    current_price = voo_ticker.history(period="1d")['Close'].iloc[-1]  # Fetch the latest closing price
    # Extract week value
    current_price = Decimal(current_price)

    # Round down the miles value to 2 decimal points
    current_price = current_price.quantize(Decimal('0.00'), rounding=ROUND_DOWN)
    logging.info(current_price)
    return current_price


def fetch_vti_data():
    voo_ticker = yf.Ticker("VTI")
    current_price = voo_ticker.history(period="1d")['Close'].iloc[-1]  # Fetch the latest closing price
    # Extract week value
    current_price = Decimal(current_price)

    # Round down the miles value to 2 decimal points
    current_price = current_price.quantize(Decimal('0.00'), rounding=ROUND_DOWN)
    logging.info(current_price)
    return current_price


if __name__ == "__main__":
    main()
