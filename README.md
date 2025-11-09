# Multi-Currency Invoice Analytics API

## Introduction
This is a high-level design document for the Multi-Currency Invoice Analytics API. It explains the design approaches considered, the trade-offs made, and the architecture of the implemented solution. It also outlines the system's strengths, limitations, and potential future improvements.

---

## Overview
The system provides an API that allows users to:  
- Perform CRUD operations on invoices  
- Retrieve the total revenue for their account  
- Calculate the average invoice size  

### Key Concepts
- A **company** has an **account**, and employees of the company are **users**.  
- Users are associated with a specific company account and can perform operations on invoices related to that account.  
- **Total revenue**:
  - Users can specify whether to use **historic exchange rates** or **current exchange rates**.
  - Output is always in **USD**.  
- **Invoice average size**:
  - Conversion fees are applied.
  - Users can specify the output currency.
  - Exchange rate is always the **current rate**.

---

## Investigation

### Approach 1: Postgres Only
- Store invoices in a relational database (PostgreSQL).
- Advantages:
  - Fast CRUD operations via indexes and materialized views.
  - Batch inserts reduce overhead.
- Limitations:
  - Aggregation queries (SUM, AVG) are slow for millions of rows because full rows must be read from disk even if only one column is needed.

### Approach 2: Columnar Database (ClickHouse)
- Store invoices in a columnar database for fast aggregation queries.
- Advantages:
  - Very fast for analytical queries (aggregations).
- Limitations:
  - Slow for point queries, updates, and deletes.
  - Poor support for CRUD operations.

### Approach 3: Combined Postgres + ClickHouse (Best but Complex)
- Use **Postgres** for CRUD operations and point queries.
- Use **ClickHouse** for aggregation queries.
- Operations:
  - **Insertion:** Insert into both Postgres and ClickHouse.
  - **Selection:** Retrieve by ID from Postgres.
  - **Deletion:** Delete from Postgres, mark deleted in ClickHouse in a separate `invoices_deleted` table.
  - **Updating:** Update Postgres, insert new row in ClickHouse, mark old row in `deleted_invoices`.
- Trade-offs:
  - Higher disk usage.
  - More complex code.
  - Operational overhead (ClickHouse not fully managed in the cloud).

**Decision:** Approach 1 was implemented for simplicity and to avoid premature optimization.

---

## Component Diagram
The main components of the system:

- **API Layer:** Handles CRUD operations and analytics requests.
- **Exchange Rate Service:** Provides current and historical exchange rates.
- **Currency Converter Service:** Converts invoice amounts using exchange rates.
- **Integration Service:** Interfaces with third-party exchange rate APIs, with **Redis caching** to reduce API calls.
- **Database:** PostgreSQL stores all users, accounts, and invoices.

All APIs mainly interact with PostgreSQL.  
Exchange rate API calls the exchange rate service, while analytics API calls the currency converter service, which in turn uses the exchange rate service.

---

## Database Design

### Tables
1. **Users:** Represents system users who send requests.
2. **Accounts:** Represents companies; a single account has many users.
3. **Invoices:** Represents submitted invoices; each invoice belongs to one account.  

**Relationships:**
- One account → Many users  
- One account → Many invoices  

---

## Conclusion
### Strengths
- Modular design
- Easy to extend
- Cost-efficient due to caching

### Limitations
- Historic exchange rates only supported in USD
- Scaling is limited by PostgreSQL for large datasets

### Future Improvements
- Add multi-currency support for historic exchange rates via third-party APIs.
- Use batch insertion to reduce contention.
- Utilize materialized views to improve read performance.
- Prototype the combined Postgres + ClickHouse approach to accelerate aggregation queries.

---

