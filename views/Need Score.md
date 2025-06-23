---
spielsystem: Warhammer 40k
---
Letzte Bilder um den 28.01.25
```dataview
TABLE einheit AS "Einheit", fertigstellung AS "Fertigstellung" 
FROM "minis" 
WHERE fertigstellung != "" AND bewertung = NULL AND this.spielsystem != null AND spielsystem = this.spielsystem OR this.spielsystem = null AND bewertung = NULL AND fertigstellung != ""
SORT fertigstellung DESC
```
