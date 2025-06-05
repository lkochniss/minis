```dataview
TABLE bewertung AS "Bewertung", fertigstellung AS "Fertigstellung" 
FROM "minis" 
WHERE bewertung SORT bewertung ASC, fertigstellung DESC LIMIT 10
```
