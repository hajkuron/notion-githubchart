const fitnessCalendar = new CalHeatmap();
const projectsCalendar = new CalHeatmap();

async function fetchChartData(calendarName) {
    try {
        const response = await fetch(`data/chart-data-${calendarName}.json`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log(`Fetched data for ${calendarName}:`, data);
        return data;
    } catch (error) {
        console.error(`Error fetching data for ${calendarName}:`, error);
        return [];
    }
}

async function initializeCalendar(cal, data, containerId, legendId, colorScheme) {
    console.log(`Initializing calendar for ${containerId} with data:`, data);
    try {
        cal.paint(
            {
                data: {
                    source: data,
                    x: 'date',
                    y: 'value',
                },
                date: { start: new Date('2024-01-01') },
                range: 12,
                scale: {
                    color: {
                        type: 'linear',
                        domain: [0.25, 0.5, 0.75, 1],
                        range: colorScheme
                    },
                },
                domain: {
                    type: 'month',
                    gutter: 4,
                    label: { text: 'MMM', textAlign: 'start', position: 'top' },
                },
                subDomain: { 
                    type: 'ghDay', 
                    radius: 2, 
                    width: 11, 
                    height: 11, 
                    gutter: 4,
                    emptyColor: '#2d333b',
                },
                itemSelector: `#${containerId}`,
            },
            [
                [
                    Tooltip,
                    {
                        text: function (date, value, dayjsDate) {
                            return (
                                (value !== null ? value : 'No') +
                                ' contributions on ' +
                                dayjs(dayjsDate).format('dddd, MMMM D, YYYY')
                            );
                        },
                    },
                ],
                [
                    LegendLite,
                    {
                        includeBlank: true,
                        itemSelector: `#${legendId}`,
                        radius: 2,
                        width: 11,
                        height: 11,
                        gutter: 4,
                    },
                ],
                [
                    CalendarLabel,
                    {
                        width: 30,
                        textAlign: 'start',
                        text: () => ['', 'M', '', 'W', '', 'F', ''],
                        padding: [25, 0, 0, 0],
                    },
                ],
            ]
        );
        console.log(`Calendar for ${containerId} painted successfully`);
    } catch (error) {
        console.error(`Error painting calendar for ${containerId}:`, error);
    }
}

async function initializeCalendars() {
    try {
        const fitnessData = await fetchChartData('Fitness');
        const projectsData = await fetchChartData('Projects');
        
        const greenColorScheme = ['#0e4429', '#006d32', '#26a641', '#39d353'];
        const blueColorScheme = ['#0a3069', '#0d4a6e', '#0969da', '#54aeff'];
        
        if (fitnessData.length === 0) {
            console.error('No data available for Fitness calendar');
        } else {
            await initializeCalendar(fitnessCalendar, fitnessData, 'fitness-calendar', 'fitness-legend', greenColorScheme);
        }
        
        if (projectsData.length === 0) {
            console.error('No data available for Projects calendar');
        } else {
            await initializeCalendar(projectsCalendar, projectsData, 'projects-calendar', 'projects-legend', blueColorScheme);
        }
    } catch (error) {
        console.error('Error initializing calendars:', error);
    }
}

// Initialize the calendars when the page loads
document.addEventListener('DOMContentLoaded', () => {
    if (!document.getElementById('fitness-calendar')) {
        console.error('Fitness calendar container not found');
    }
    if (!document.getElementById('projects-calendar')) {
        console.error('Projects calendar container not found');
    }
    initializeCalendars();
});

// Log any errors that occur during calendar creation
fitnessCalendar.on('error', (error) => {
    console.error('Fitness Calendar error:', error);
});

projectsCalendar.on('error', (error) => {
    console.error('Projects Calendar error:', error);
});

document.getElementById('fitness-prev-button').addEventListener('click', (e) => {
    e.preventDefault();
    fitnessCalendar.previous();
});

document.getElementById('fitness-next-button').addEventListener('click', (e) => {
    e.preventDefault();
    fitnessCalendar.next();
});

document.getElementById('projects-prev-button').addEventListener('click', (e) => {
    e.preventDefault();
    projectsCalendar.previous();
});

document.getElementById('projects-next-button').addEventListener('click', (e) => {
    e.preventDefault();
    projectsCalendar.next();
});
