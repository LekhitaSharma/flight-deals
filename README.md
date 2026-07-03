Flight Deals
A Django web app that tracks cheap flights and alerts you when prices drop below your budget, built and hosted on PythonAnywhere.

What it does :
- Stores user destinations, budgets, and IATA codes in google sheets which we access using SHEETY API(data_manager.py)
- Reads the lowests prices you have set using SHEETY API.
- Searches real-time flight prices via flight API (Serpapi in flight_search.py)
- Checks the price and compare with the lowest prices when you click on 'Refresh Data' on the web app, using caches to save API calls.
- Designed for PythonAnywhere scheduled tasks
  
Tech Stack :
- Backend: Python 3, Django
- APIs: Flight Search API, Sheety/Google Sheets (via data_manager.py)
- Database: SQLite (dev) / MySQL (PythonAnywhere)
- Hosting: PythonAnywhere
