const fetch = require('node-fetch');
const fs = require('fs');

const NOTION_SECRET = process.env.NOTION_SECRET;
const DATABASE_ID = process.env.DATABASE_ID;

async function fetchNotionData() {
    const response = await fetch(`https://api.notion.com/v1/databases/${DATABASE_ID}/query`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${NOTION_SECRET}`,
            'Notion-Version': '2022-06-28',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            filter: {
                property: "Calendar",
                rich_text: {
                    equals: "Fitness"
                }
            },
            sorts: [{ property: 'Date', direction: 'ascending' }]
        })
    });

    const data = await response.json();
    if (!response.ok) {
        throw new Error(`Notion API error: ${JSON.stringify(data)}`);
    }
    return data;
}

async function processAndSaveData() {
    try {
        const rawData = await fetchNotionData();
        const processedData = rawData.results.map(item => ({
            date: item.properties.Date.date.start,
            value: 1
        }));

        fs.writeFileSync('data/chart-data.json', JSON.stringify(processedData, null, 2));
        console.log('Data updated successfully');
    } catch (error) {
        console.error('Error processing Notion data:', error);
    }
}

processAndSaveData();