---
körnung: 5
---


```dataviewjs 
const data = dv.pages('"minis"')
	.where(p => p.fertigstellung && p.bewertung) 
	.sort(k => k.fertigstellung, 'asc')
	.map(p => ({ 
		label: p.fertigstellung, 
		value: p.bewertung, 
		fileName: p.file.name
	}))
	.sort((a, b) => new Date(a.label) - new Date(b.label));

// Funktion zum Formatieren des Datums
function formatDate(dateString) {
    const date = new Date(dateString); 
    const year = date.getFullYear(); 
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0'); 
    return `${day}.${month}.${year}`; 
}

// Gruppierung der Daten in Gruppen von 5
const groupedData = [];
const currentPage = dv.current();
const dataSlice = parseInt(currentPage.körnung);

for (let i = 0; i < data.length; i += dataSlice) {
    const group = Array.from(data.slice(i, i + dataSlice));
   const avgValue = group.reduce((sum, d) => sum + d.value, 0) / group.length; 
    const groupLabel = group[0].label; // Das Label der ersten Miniatur in der Gruppe
    groupedData.push({ label: groupLabel, value: avgValue });
}

// Formatieren der Labels und Werte für das Diagramm
const labels = groupedData.map(d => formatDate(new Date(d.label)));
const values = groupedData.map(d => d.value);

// Erstellen des Chart-Datenstrings
const chartData = ` \`\`\`chart

type: line 
title: Durchschnittsbewertungen der Miniaturen (je ${dataSlice})
labels: ${JSON.stringify(labels)} 
series:
	- title: Durchschnittliche Bewertung (je ${dataSlice})
	  data: ${JSON.stringify(values)} 
tension: 0.2
width: 80%
labelColors: false
fill: false
beginAtZero: true
bestFit: false
bestFitTitle: undefined
bestFitNumber: 0
  \`\`\` `;

// Ausgabe des Diagramms
dv.paragraph(chartData);
```

