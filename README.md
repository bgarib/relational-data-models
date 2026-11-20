# Relational Data Models (MySQL)

**Two operational database designs built in MySQL Workbench: a 22-table grocery point-of-sale system and a 4-table marina berth-rental system.**

Each model ships as the original `.mwb` file, forward-engineered MySQL DDL and an ER diagram that renders on GitHub.

| Model | Tables | Foreign keys | Focus |
|---|---|---|---|
| [Grocery POS](#1-grocery-point-of-sale) | 22 | 28 | Normalised master data, tickets, card payments, multi-currency pricing |
| [Marina](#2-marina-berth-rental) | 4 | 4 | Business rules enforced by the schema itself |

## 1. Grocery point of sale

Covers the full path from a product on the shelf to a paid ticket: products with brand, supplier, colour and unit measures; stores and locations with typed addresses; tickets and ticket lines; card payments with state, type and entry method; prices with cost, promotion and tax in separate currencies.

Design choices:
- **Lookup tables for every code** (address type, location type, card state, card type, entry method, currency, unit measure) so codes are validated, not free text.
- **Composite keys where the business has them:** `zipcode (ZIPCODE, COUNTRY)` because postcodes repeat across countries; `ticket_item (TICKET_ID, NUMSEQ)` and `phones (LOCATION_ID, NUMSEQ)` for ordered child rows.
- **Ticket totals stored on the header** (product, tax, order) for fast reporting, with line-level amounts kept for audit.

```mermaid
erDiagram
    address {
        int ADDRESS_ID PK
        char TYPE_ID FK
        varchar NAME
        smallint NUMBER
        int ZIPCODE FK
        varchar COUNTRY FK
    }
    address_type {
        char TYPE_ID PK
        varchar DESCRIPTION
    }
    brand {
        int BRAND_ID PK
        varchar NAME
        varchar DESCRIPTION
        int CONTACT_ID FK
    }
    ccentry_methd {
        char CCMETHD PK
        varchar DESCRIPTION
    }
    ccpayment {
        bigint CCPAYMENT_ID PK
        bigint CCPAYTRAN_ID
        char CURRENCY_ID FK
        decimal EXPECTED_AMOUNT
        decimal APPROVING_AMOUNT
        decimal APPROVED_AMOUNT
        char CCPAYMENT_STATE FK
        timestamp_f TIMECREATED
        timestamp_f TIMEUPDATED
        timestamp_f TIMEEXPIRED
    }
    ccpayment_card {
        bigint CCPAYMENT_ID PK,FK
        char PAYMENT_TYPE FK
        char IS_ENCRYPT
        varchar CARD_NUMBER
        varchar BANKNAME
        char CCEXPDATE
        char CCENTRY_METHD FK
    }
    ccpayment_state {
        char CCSTATE PK
        varchar DESCRIPTION
    }
    ccpayment_type {
        char CCTYPE PK
        varchar DESCRIPTION
    }
    color {
        bigint COLOR_ID PK
        smallint RGB_RED
        smallint RGB_GREEN
        smallint RGB_BLUE
        char HEX_CODE
        varchar COLOR_NAME
    }
    contact {
        int CONTACT_ID PK
        varchar NAME
        int ADDRESS_ID FK
    }
    currency {
        char CURRENCY_ID PK
        smallint CURRENCY_CODE
        varchar DESCRIPTION
    }
    location {
        bigint LOCATION_ID PK
        char TYPE_ID FK
        int ADDRESS_ID FK
    }
    location_type {
        char TYPE_ID PK
        varchar DESCRIPTION
    }
    phones {
        bigint LOCATION_ID PK,FK
        smallint NUMSEQ PK
        varchar EXTERNAL
        varchar INTERNAL
        varchar DESCRIPTION
    }
    price {
        bigint PRODUCT_ID PK,FK
        char COST_CURRENCY FK
        decimal COST
        char PRICE_CURRENCY FK
        decimal PRICE
        decimal PRICE_PROMOTION
        decimal TAXES
    }
    product {
        bigint PRODUCT_ID PK
        bigint CATEGORY_ID
        char SIZE_CODE FK
        decimal SIZE
        char WEIGHT_CODE FK
        decimal WEIGHT
        char PACK_CODE FK
        bigint COLOR_ID FK
        varchar NAME
        int BRAND_ID FK
        int SUPPLIER_ID FK
        varchar SHORT_DESCRIPTION
        varchar LONG_DESCRIPTION
        varchar THUMBNAIL
        varchar FULLIMAGE
    }
    store {
        smallint STORE_ID PK
        bigint LOCATION_ID FK
    }
    supplier {
        int SUPPLIER_ID PK
        varchar NAME
        int CONTACT_ID FK
        varchar PAYMENT_TERMS
    }
    ticket {
        bigint TICKET_ID PK
        timestamp_f TIMEPLACED
        smallint STORE_ID FK
        int CASHIER_ID
        decimal TOTAL_PRODUCT
        decimal TOTAL_TAX
        decimal TOTAL_ORDER
        char CURRENCY_ID FK
        bigint PAYMENT_ID FK
    }
    ticket_item {
        bigint TICKET_ID PK,FK
        smallint NUMSEQ PK
        bigint PRODUCT_ID FK
        varchar DESCRIPTION
        smallint QUANTITY
        decimal PRICE
        decimal TAX_AMOUNT
        decimal PRODUCT_AMOUNT
    }
    unit_measure {
        char METRIC_CODE PK
        varchar NAME
        varchar DESCRIPTION
    }
    zipcode {
        int ZIPCODE PK
        varchar COUNTRY PK
        varchar CITY
        varchar STATE
    }
    address_type ||--o{ address : "TYPE_ID"
    zipcode ||--o{ address : "ZIPCODE, COUNTRY"
    contact ||--o{ brand : "CONTACT_ID"
    currency ||--o{ ccpayment : "CURRENCY_ID"
    ccpayment_state ||--o{ ccpayment : "CCPAYMENT_STATE"
    ccentry_methd ||--o{ ccpayment_card : "CCENTRY_METHD"
    ccpayment ||--o{ ccpayment_card : "CCPAYMENT_ID"
    ccpayment_type ||--o{ ccpayment_card : "PAYMENT_TYPE"
    address ||--o{ contact : "ADDRESS_ID"
    address ||--o{ location : "ADDRESS_ID"
    location_type ||--o{ location : "TYPE_ID"
    location ||--o{ phones : "LOCATION_ID"
    currency ||--o{ price : "COST_CURRENCY"
    currency ||--o{ price : "PRICE_CURRENCY"
    product ||--o{ price : "PRODUCT_ID"
    brand ||--o{ product : "BRAND_ID"
    color ||--o{ product : "COLOR_ID"
    unit_measure ||--o{ product : "PACK_CODE"
    unit_measure ||--o{ product : "SIZE_CODE"
    supplier ||--o{ product : "SUPPLIER_ID"
    unit_measure ||--o{ product : "WEIGHT_CODE"
    location ||--o{ store : "LOCATION_ID"
    contact ||--o{ supplier : "CONTACT_ID"
    currency ||--o{ ticket : "CURRENCY_ID"
    ccpayment ||--o{ ticket : "PAYMENT_ID"
    store ||--o{ ticket : "STORE_ID"
    product ||--o{ ticket_item : "PRODUCT_ID"
    ticket ||--o{ ticket_item : "TICKET_ID"
```

## 2. Marina berth rental

A marina rents berths to people; people own vessels; a vessel can be docked at a berth.

The rule that makes this model interesting: **a vessel can only be docked at a berth rented by its own owner.** It is enforced with a composite foreign key, not application code:

```sql
UNIQUE KEY uq_berth_renter (BERTH_ID, RENTER_PERSON_ID)            -- on berth
FOREIGN KEY (BERTH_ID, OWNER_PERSON_ID)
  REFERENCES berth (BERTH_ID, RENTER_PERSON_ID)                     -- on vessel
```

Other constraints: berth codes are unique per marina, not globally; registration numbers, document IDs and emails are unique; vessel type is an `ENUM`; a vessel with no berth (`BERTH_ID` NULL) sits on the waiting list.

```mermaid
erDiagram
    berth {
        int BERTH_ID PK
        int MARINA_ID FK
        varchar BERTH_CODE
        decimal MAX_LENGTH_M
        decimal MAX_BEAM_M
        decimal DEPTH_M
        tinyint HAS_ELECTRICITY
        decimal MONTHLY_FEE
        int RENTER_PERSON_ID FK
        date RENTAL_START_DATE
        date RENTAL_END_DATE
    }
    marina {
        int MARINA_ID PK
        varchar NAME
        varchar CITY
        varchar COUNTRY
        smallint TOTAL_BERTHS
        varchar PHONE
        varchar EMAIL
    }
    person {
        int PERSON_ID PK
        varchar FIRST_NAME
        varchar LAST_NAME
        varchar DOCUMENT_ID
        varchar EMAIL
        varchar PHONE
        varchar NATIONALITY
        date BIRTH_DATE
    }
    vessel {
        int VESSEL_ID PK
        int OWNER_PERSON_ID FK
        int BERTH_ID FK
        varchar NAME
        varchar REGISTRATION_NUMBER
        enum VESSEL_TYPE
        decimal LENGTH_M
        decimal BEAM_M
        smallint BUILD_YEAR
    }
    marina ||--o{ berth : "MARINA_ID"
    person ||--o{ berth : "RENTER_PERSON_ID"
    person ||--o{ vessel : "OWNER_PERSON_ID"
    berth ||--o{ vessel : "BERTH_ID, OWNER_PERSON_ID"
```

`sql/marina_seed.sql` loads sample data (fictional people) and `sql/marina_queries.sql` answers occupancy, monthly income and waiting-list questions. Trying to dock a vessel at someone else's berth fails with a foreign key error, as designed.

## Files

```
models/       original MySQL Workbench files (.mwb)
sql/          DDL per model, seed data and example queries for the marina
tools/        mwb_to_sql.py: reads a .mwb file and writes the DDL and Mermaid diagram
```

Regenerate the DDL and diagrams:

```bash
python3 tools/mwb_to_sql.py models/marina_db.mwb sql/marina_db.sql marina_db.mmd
```

---
SQL Based Data Architectures II, Master in Business Analytics and Data Science, IE School of Science & Technology, November 2026.

Tools: MySQL Workbench · MySQL · Python
