from django.shortcuts import render
import requests_cache
from pprint import pprint
from datetime import datetime, timedelta
from data_manager import DataManager
from flight_search import FlightSearch
from flight_data import find_cheapest_flight

# ==================== Conserve requests and preserve your free plan ====================
requests_cache.install_cache(
    "flight_cache",
    urls_expire_after={
        "*.sheety.co*": requests_cache.DO_NOT_CACHE,
        "*": 3600,
    }
)
# ==================== Setup ====================
data_manager = DataManager()
sheet_data = data_manager.get_destination_data()
flight_search = FlightSearch()

# ==================== Set the Dates and Origin Airport ====================
tomorrow = datetime.now() + timedelta(days=1)
six_month_from_today = datetime.now() + timedelta(days=(6 * 30))
ORIGIN_CITY_IATA = "BHO"  # Want to make it a text space for user to enter input

# ==================== Find Cheap Flights ====================
for destination in sheet_data:
    pprint(f"Getting flights for {destination['city']}...")
    flights = flight_search.check_flights(
        ORIGIN_CITY_IATA,
        destination["iataCode"],
        from_time=tomorrow,
        to_time=six_month_from_today
    )
    cheapest_flight = find_cheapest_flight(flights, return_date=six_month_from_today.strftime("%Y-%m-%d"))
    pprint(f"{destination['city']}: INR {cheapest_flight.price}")

    if cheapest_flight.price != "N/A" and cheapest_flight.price < destination["lowestPrice"]:
        pprint(f"Lower price flight found to {destination['city']}!")
        data_manager.update_lowest_price(destination["id"], cheapest_flight.price)

        print(f"Low price alert! Only INR {cheapest_flight.price} to fly",)
        print(f"\nfrom {cheapest_flight.origin_airport} to {cheapest_flight.destination_airport},")
        print(f"\non {cheapest_flight.out_date} until {cheapest_flight.return_date}.")

    else:
        print(f"Uh oh !! The flight prices aren't lesser than the cheapest price you entered. "
              f"Current price - INR {cheapest_flight.price} to fly. "
              f"The price or below you are looking for - INR {destination['lowestPrice']}")
