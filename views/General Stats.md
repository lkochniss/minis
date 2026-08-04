
```dataview
TABLE WITHOUT ID Einheit, Anzahl, Min, Max, Avg
FROM "reviews" 
WHERE einheit != null
GROUP BY einheit as "Einheit" 
FLATTEN length(rows) as "Anzahl"
FLATTEN min(nonnull(rows.bewertung)) as Min
FLATTEN max(nonnull(rows.bewertung)) as Max
FLATTEN round(average(nonnull(rows.bewertung)), 1) as Avg
```
```dataview
TABLE WITHOUT ID Armee, Anzahl, Min, Max, Avg
FROM "reviews" 
WHERE armee != null
GROUP BY armee as Armee 
FLATTEN length(rows) as "Anzahl"
FLATTEN min(nonnull(rows.bewertung)) as Min
FLATTEN max(nonnull(rows.bewertung)) as Max
FLATTEN round(average(nonnull(rows.bewertung)), 1) as Avg
```
```dataview
TABLE WITHOUT ID Spielsystem, Anzahl, Min, Max, Avg
FROM "reviews" 
WHERE spielsystem != null
GROUP BY spielsystem as "Spielsystem" 
FLATTEN length(rows) as "Anzahl"
FLATTEN min(nonnull(rows.bewertung)) as Min
FLATTEN max(nonnull(rows.bewertung)) as Max
FLATTEN round(average(nonnull(rows.bewertung)), 1) as Avg

```
