```dataview
TABLE bewertung AS "Bewertung", fertigstellung AS "Fertigstellung" 
FROM "minis" 
WHERE bewertung SORT bewertung DESC, fertigstellung DESC LIMIT 20
```
