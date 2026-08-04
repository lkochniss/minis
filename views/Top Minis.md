---
spielsystem:
einheit:
armee:
fraktion:
modelltyp:
hersteller:
limit: 10
---

```dataview
TABLE bewertung AS "Bewertung", fertigstellung AS "Fertigstellung" 
FROM "reviews" 
WHERE (spielsystem = this.spielsystem OR !this.spielsystem) 
  AND (einheit = this.einheit OR !this.einheit) 
  AND (armee = this.armee OR !this.armee)
  AND (fraktion = this.fraktion OR !this.fraktion)
  AND (modelltyp = this.modelltyp OR !this.modelltyp)
  AND (hersteller = this.hersteller OR !this.hersteller)
  AND bewertung > 0
SORT bewertung DESC, fertigstellung DESC LIMIT this.limit
```
