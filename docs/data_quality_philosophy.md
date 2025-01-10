---
title: Data Quality Philosophy

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

