from django.shortcuts import render
from django.http import JsonResponse
from django.core.cache import cache
from datetime import datetime, timedelta
import requests_cache
from .data_manager import DataManager
from .flight_search import FlightSearch
from .flight_data import find_cheapest_flight

def flight_deals_home(request):
    # FAST - only reads cache, no API calls
    deals = cache.get('flight_deals_data', [])
    last_updated = cache.get('flight_deals_updated', 'Never')

    context = {
        'deals': deals,
        'last_updated': last_updated
    }
    return render(request, 'flight_deals/flights_home.html', context)


def refresh_deals_api(request):
    """
    SLOW - hits SerpAPI + Sheety for each city
    Call this via /flight-deals/api/refresh/ or scheduled task
    """
    try:
        # 1. Cache API responses for 1 hour so testing doesn't burn credits
        requests_cache.install_cache("flight_cache", expire_after=3600)

        # 2. Get all destination cities from Sheety
        data_manager = DataManager()
        sheet_data = data_manager.get_destination_data()

        # 3. Init SerpAPI wrapper
        flight_search = FlightSearch()

        # 4. Set search window: tomorrow → 6 months from now
        tomorrow = datetime.now() + timedelta(days=1)
        six_month_from_today = datetime.now() + timedelta(days=180)
        ORIGIN_CITY_IATA = "BHO"

        all_deals = []

        # 5. Loop each city from your sheet
        for destination in sheet_data:
            # 5a. Call SerpAPI - this is the slow part
            flights = flight_search.check_flights(
                origin_city_code=ORIGIN_CITY_IATA,
                destination_city_code=destination["iataCode"],
                from_time=tomorrow,
                to_time=six_month_from_today
            )

            # 5b. Parse cheapest flight - no return_date param needed now
            cheapest_flight = find_cheapest_flight(flights)

            # 5c. Build dict for template
            deal_info = {
                'city': destination['city'],
                'iata': destination['iataCode'],
                'price': cheapest_flight.price,
                'lowest_price': destination['lowestPrice'],
                'is_deal': False,
                'origin': cheapest_flight.origin_airport,
                'destination': cheapest_flight.destination_airport,
                'out_date': cheapest_flight.out_date,
                'return_date': cheapest_flight.return_date,
            }

            # 5d. If we found a new low, flag it + update Sheety
            if cheapest_flight.price != "N/A" and float(cheapest_flight.price) < float(destination['lowestPrice']):
                deal_info['is_deal'] = True
                data_manager.update_lowest_price(destination["id"], cheapest_flight.price)

            all_deals.append(deal_info)

        # 6. Save results to cache for 24 hours
        cache.set('flight_deals_data', all_deals, 86400)
        cache.set('flight_deals_updated', datetime.now().strftime("%Y-%m-%d %H:%M"))

        # 7. Return success JSON
        return JsonResponse({
            'status': 'success',
            'deals_updated': len(all_deals),
            'last_updated': cache.get('flight_deals_updated')
        })

    except Exception as e:
        # If anything breaks, return the error
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)