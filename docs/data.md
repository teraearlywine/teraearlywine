---
title: Data
status: new
---

# Data


## The SQL Data Quality Checklist 
A useful list with different data quality checks you can perform on a table. (Assuming you can use SQL)

1. Completeness check 
2. Uniqueness check
3. Consistency check
4. Range check
5. Referential integrity check
6. Pattern check
7. Data type check
8. Logical consistency check
9. Sum check


I prefer the first two (completeness and uniqueness check) because they're the most useful when working 
with raw data. This is because NULL values (completeness) typically signify a bug in the upstream processes and 
data integrity issues. This either means the process of writing data to the table is screwed
or something relating to the app or code is screwed. 

Philosophically speaking, prefer to _have_ data as opposed to _no_ data. 




<details>

<summary> How to Anchor Data Quality Analysis</summary>

<h3><b>Approach:</b></h3>

<b>The lowest most atomic level: </b> Comparing one to five primary key id's<br>
<b>At the day-granularity:       </b> Comparing one day's worth of data using EXCEPT DISTINCT distinct<br>
<b>Aggregated table-stats:       </b> Comparing categorical and numerical columnar data <br>


</details>