from django.core.management.base import BaseCommand
from django.core.cache import cache
from datetime import datetime, timedelta
from flight_deals.data_manager import DataManager
from flight_deals.flight_search import FlightSearch
from flight_deals.flight_data import find_cheapest_flight
import requests_cache

class Command(BaseCommand):
    help = 'Fetch latest flight deals'

    def handle(self, *args, **kwargs):
        requests_cache.install_cache("flight_cache", expire_after=3600)
        
        data_manager = DataManager()
        sheet_data = data_manager.get_destination_data()
        flight_search = FlightSearch()
        
        tomorrow = datetime.now() + timedelta(days=1)
        six_month_from_today = datetime.now() + timedelta(days=180)
        ORIGIN_CITY_IATA = "BHO"
        
        all_deals = []
        
        for destination in sheet_data:
            print(f"Getting flights for {destination['city']}...")
            flights = flight_search.check_flights(
                ORIGIN_CITY_IATA,
                destination["iataCode"],
                from_time=tomorrow,
                to_time=six_month_from_today
            )
            # return_date = six_month_from_today.strftime("%Y-%m-%d")
            cheapest_flight = find_cheapest_flight(flights)
            
            deal_info = {
                'city': destination['city'],
                'iata': destination['iataCode'],
                'price': cheapest_flight.price,
                'lowest_price': destination["lowestPrice"],
                'is_deal': False,
                'origin': cheapest_flight.origin_airport,
                'destination': cheapest_flight.destination_airport,
                'out_date': cheapest_flight.out_date,
                'return_date': cheapest_flight.return_date,
            }
            
            if cheapest_flight.price != "N/A" and float(cheapest_flight.price) < float(destination["lowestPrice"]):
                deal_info['is_deal'] = True
                data_manager.update_lowest_price(destination["id"], cheapest_flight.price)
            
            all_deals.append(deal_info)
        
        cache.set('flight_deals_data', all_deals, 86400)
        cache.set('flight_deals_updated', datetime.now().strftime("%Y-%m-%d %H:%M"))
        self.stdout.write(self.style.SUCCESS(f"Updated {len(all_deals)} deals"))