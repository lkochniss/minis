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

function formatDate(dateString) {
    const date = new Date(dateString); 
    const year = date.getFullYear(); 
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0'); 
    return `${day}.${month}.${year}`; 
}

const labels = data.map(d => formatDate(new Date(d.label)));
const values = data.map(d => d.value);

const chartData = ` \`\`\`chart

type: line 
title: Bewertungen der Miniaturen
labels: ${JSON.stringify(labels.values)} 
series:
	- title: Bewertung
	  data: ${JSON.stringify(values.values)} 
tension: 0.2
width: 80%
labelColors: false
fill: false
beginAtZero: true
bestFit: false
bestFitTitle: undefined
bestFitNumber: 0
  \`\`\` `;

dv.paragraph(chartData);
```
