✈️ Flight Deals
A Django web app that tracks cheap flights and alerts you when prices drop below your budget, built and hosted on PythonAnywhere.

What it does :
- Searches real-time flight prices via flight API (Amadeus/Skyscanner-style in flight_search.py)
- Stores user destinations, budgets, and IATA codes in Django models (models.py)
- Checks the price when you click on 'Refresh Data' on the web app, using caches to save API calls.
- Designed for PythonAnywhere scheduled tasks
  
Tech Stack :
- Backend: Python 3, Django
- APIs: Flight Search API, Sheety/Google Sheets (via data_manager.py)
- Database: SQLite (dev) / MySQL (PythonAnywhere)
- Hosting: PythonAnywhere
