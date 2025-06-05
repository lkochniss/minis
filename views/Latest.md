```dataview
TABLE fertigstellung AS "Fertigstellung", bewertung AS "Bewertung"
FROM "minis" 
WHERE fertigstellung SORT fertigstellung DESC LIMIT 10
```
