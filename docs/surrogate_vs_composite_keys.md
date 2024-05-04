---
title: Surrogate vs. Composite Keys
status: new
---


# Surrogate vs. Composite Keys


### Challenges with SQL Development using Cloud Tools

The problem today with cloud tools is that they’re all oriented towards data manipulation SQL. But, if you want to create a robust production SQL transformation, that becomes challenging.  Lets say you have a generic table with app data or user histories, and you’re trying to create a new table derived from it in DBT. How to ensure uniqueness with any new table or dimension you create, given that you can’t auto-increment a newer primary key?

You are now required to create one.

---

### So what are they?

A primary surrogate key is completely artificial and has no business meaning (wow, copy that from wikipedia, you robot?). Hah. No really — it’s almost refreshing how little use these keys have as far as context goes (there’s a pun in there, let me know if you see it.) Surrogate keys can be considered primary keys, as they typically serve to protect the granularity of the table and improve the integrity of a data system.

A composite key on the otherhand has business meaning. In the case of our following example, `composite tracking number` changes if the tracking number is recycled, either if it’s assigned to a different order or return. Composite keys do not have to be unique. In the event we ever need to differentiate between a tracking number and the order, this key can handle it. Particularly useful for data enrichment.

---

# Creating a surrogate key

What worked today to create a useful surrogate key was merging a few techniques together. GENERATE_UUID() would’ve been the most ideal because of how simple it is, except for the fact that it’s genuinely random, so if a table rebuilds in a day, your key will change and any downstream joins go kaput.

I suppose this can have it’s benefits (conversation for another time). For my case; we needed the surrogate key data to remain the same.

The challenge with this table is the underlying data is not normalized / nor posesses a true primary key. It’s a massive union of many different tables. So we have to assume that any table created downstream is missing some fundamental things. To protect the data / table integrity, creating a surrogate key is the best way without over-doing it on compute or dealing with data loss.

Given the SQL logic, I used the two keys most relevant to the entity (in this case a shipping label tracking number and the label scan date along the supply chain) in combination with a ROW_COUNT() window function. Sudo code to follow.

<aside>
Disclaimer: The following SQL is sudo code and meant for illustrative purposes only

</aside>

```sql
WITH pre_processing_fields_cte AS (
SELECT  columns
		  , ROW_COUNT() OVER (PARTITION BY tracking_number ORDER BY created_ts ASC) AS surrogate_key
FROM    some_table
)

, create_artificial_keys AS (
  SELECT * EXCEPT (composite_tracking_transaction_evidence_key, composite_tracking_order_key)
       , COALESCE(composite_tracking_order_key, composite_tracking_transaction_evidence_key) AS composite_tracking_number_key
  FROM (
    SELECT  *
		      , TO_HEX(MD5(CONCAT(tracking_number, created_ts, surrogate_key))) AS pk_surrogate_key
          , TO_HEX(MD5(CONCAT(tracking_number, transaction_id))) AS composite_tracking_transaction_key
          , TO_HEX(MD5(CONCAT(tracking_number, order_id))) AS composite_tracking_order_key
    FROM    pre_processing_fields_cte
  )
)

SELECT *
FROM   create_artificial_keys
```
