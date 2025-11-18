### Payout Intake & Finance Summary:
#### Design and implementation decisions

#### 1. Security and Environmental settings

* **Configuration:**
  
  Sensitive data (DB credentials, `SECRET_KEY`) is stored in a root **`.env`** file and accessed via the **`python-decouple`** library. This ensures secrets are never checked into version control, adhering to modern security standards.


* **Authentication & CSRF:**
  
  The service is designed to be a partner-facing API, relying on **header-based authentication**. This architecture is **immune to CSRF attacks** because authorisation doesn't rely on vulnerable browser session cookies.

---

#### 2. Idempotent Intake (Task 1)

* **Database Integrity:**
  
  Idempotency is primarily enforced at the PostgreSQL level using a **`unique_together`** constraint on `(external_ref, partner_code)`. This provides the strongest guarantee against accidental data duplication.


* **Application Logic:** 
  
  The `PayoutViewSet.create()` method uses **`Payout.objects.get_or_create()`**.
  * The DRF serializer's automatic unique validation is explicitly disabled (`validators = []`) to ensure the request reaches the `ViewSet`'s custom `get_or_create` logic.


* **Response:** 
  
  If a duplicate is detected, the API returns the existing record with an **`HTTP 200 OK`** status and a message confirming the existing record was used. This ensures stability and predictability for partner systems.


* **Data Type:**
  
  The `amount` field uses a `DecimalField` to maintain financial precision and prevent floating-point errors.

---

#### 3. Finance Summary (Task 2)

* **Performance:**

  The summary is highly performant because it leverages **Django ORM Aggregation (`.values()`, `.annotate()`, `Sum`)**. This translates the grouping and total calculation into a single, highly efficient SQL query (`GROUP BY`), minimising processing time.


* **Filtering:**

  The summary is exposed via a custom DRF `@action` that requires `start_date` and `end_date` query parameters for accurate time-series reporting.
