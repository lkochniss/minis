---
spielsystem: 
einheit: 
armee: 
fraktion: 
modelltyp: 
hersteller:
---

```dataview
TABLE fertigstellung AS "Fertigstellung", bewertung AS "Bewertung"
FROM "minis" 
WHERE fertigstellung 
  AND (spielsystem = this.spielsystem OR !this.spielsystem) 
  AND (bewertung >= this.bewertung OR !this.bewertung) 
  AND (einheit = this.einheit OR !this.einheit) 
  AND (armee = this.armee OR !this.armee)
  AND (fraktion = this.fraktion OR !this.fraktion)
  AND (modelltyp = this.modelltyp OR !this.modelltyp)
  AND (hersteller = this.hersteller OR !this.hersteller)
SORT fertigstellung DESC 
LIMIT 10
```
