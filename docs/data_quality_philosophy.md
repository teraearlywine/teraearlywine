---
title: Data Quality Philosophy
status: new
---


# Data Quality Philosophy

Data quality is something that has been top of mind lately. With the rise of more ELT systems, as opposed to ETL, best practices for writing automated SQL data assertions has been overlooked by the data and business intelligence community. More and more businesses are implementing production transformation pipelines using SQL because of tools like DBT and Dataform — yet are realizing that “the data” may not be as accurate or optimized as possible & it’s costing  *a lot*  of money. When they ask their team of data professionals why it’s not accurate, MIA or why they’re hemorrhaging cash, they’re met with blank stares. The landscape for data has changed vastly from what it was when I was first starting out professionally.

So the overarching philosophy of the day:

**Prefer data to no data.**

Simple, no? Not the most controversial philosophy on the planet. However, I was recently enlightened to peoples tolerance for **NULL** values. No one will bat an eye so long as the numbers add up at the end of the day. To build the intuition for you a little more, just the other day I found a critical backend bug because there wasn’t data where there should have been. When you’re shipping a package and use a tracking number, you probably want the tracking number in a database to have *something as opposed to nothing.*

> If data is missing from a column no one looks at, then is it even missing?
>

One thing tools like DBT and dataform provide are assertions that are not dissimilar to writing assertions using python, so I thought I’d put together a list of my favorite ones to use.

Below is a compiled list of assertions (SQL to follow with examples) — that have saved me a lot of time spent trying to reverse engineer a query. It will make you, your backend engineers *and* your business stakeholders incredibly grateful (because you will start finding all the bugs and simultaneously will be enriching the data)

---

## SQL checks you can automate for ELT / ETL or any production transformation pipeline:

1. Data completeness (prefer data to no data)

2. Uniqueness check

3. Referential integrity check

4. Data type check

There are a handful more but are closer to a smoke and mirrors check than anything. These are the ones I’ve found particularly useful and believe these follow the pareto principle, 20/80 - 20% of the bugs account for 80% of the problems, or something.

---

# 1. Data completeness

When you prefer data to no data, a rule of thumb is to assume all keys, primary, foreign, composite and surrogate should be immutable. Meaning if the data’s *not* there, it likely exists due to a bug upstream.

So checking your keys for NULLS on any given table refresh is enormously succesful for bolstering the ongoing data integrity of your ELTs. This also applies even if you have to hand create another primary surrogate key.

## Different ways you can check a table for NULL values:

### COUNT(*)

This type of check is useful if you are trying to validate the primary key of an extremely large table. It is optimal because it only counts the null records for a given column, instead of trying to count every record in the table.

```sql
SELECT COUNT(*) AS missing_count
FROM   your_table
WHERE  your_column IS NULL
```

### SELECT *

This type of check is also useful, and can be applied if you want to see all the records that come with the NULL check. While the former COUNT(*) is good for comparing two, or running a daily job, this one helps with deducing the error source

```sql
SELECT *
FROM   your_table
WHERE  NOT (your_column IS NOT NULL)
```

---

# 2. Uniqueness check

This by and large is the most popular assertion to use because where there’s duplicated records there’s miscalculated revenue numbers, so people notice issues like this more. It’s also the most problematic for the same reasons. More on that later. Still. Uniqueness checks are clocked at second, because the completeness check has caught way more data integrity issues.

## HAVING count_records > 1

If no data is returned, you good.

```sql
SELECT  your_column
			, COUNT(*) AS count_records
FROM    your_table
GROUP BY
			 your_column
HAVING count_records > 1
```
