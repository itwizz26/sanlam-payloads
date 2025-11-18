## Financial Payouts Service

This API/service handles the idempotent intake of partner payouts and generates aggregated finance summaries.
![root.png](screens/root.png)
---

### Setup and Run

#### Prerequisites

* Python 3.11+
* PostgreSQL 13+
* Postman (Optional for testing endpoints)

#### 1. Environment Setup

Clone and navigate to the project root

```
git clone https://github.com/itwizz26/sanlam-payloads.git
cd sanlam_payloads/payout_service
```

Create and activate virtual environment
```
python -m venv venv
source venv/bin/activate  # macOS/Linux
.\venv\Scripts\activate # Windows  
```

Install dependencies (including djangorestframework, python-decouple, and pytest-django)
```
pip install -r requirements.txt
```

#### 2. Configuration (.env File)

Create a file named .env in the project root. There is an example.env file included
with the solution to aid with the creation. Copy this file and rename to `.env`

#### 3. Apply database migrations
```
python manage.py migrate
```

#### 4. Run the development server

```
python manage.py runserver
```

The API will be available at http://127.0.0.1:8000/api/v1/.

### Running Tests
All core requirements are covered by the pytest suite. The pytest.ini file handles the necessary Django environment configuration.

From the root of the project (where the tests folder is), run the below command to test the solution.
```
pytest
```

#### Available API Endpoints
```
Endpoint                Method  Description
/api/v1/payouts/        POST	Accepts a new payout. Returns 200 OK        
                                for duplicates (idempotent).
/api/v1/payouts/        GET     Shows all payouts created.
/api/payouts/summary/	GET     Finance Summary. Returns totals grouped
                                by status for a specified date range. E.g.
                                /api/payouts/summary/?start_date=2025-11-17T00:00Z&end_date=2025-11-20T00:00Z
```
#### Payouts created
![payouts.png](screens/payouts.png)

#### Summary payouts
![summary.png](screens/summary.png)

Copyright &copy; 2025 [Itwizz26](https://github.com/itwizz26)