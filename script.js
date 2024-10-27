const fitnessCalendar = new CalHeatmap();
const projectsCalendar = new CalHeatmap();
const morningRoutineCalendar = new CalHeatmap();
const shortWorkoutCalendar = new CalHeatmap();

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

function processRoutinesData(data, eventType) {
    return data.filter(item => {
        const summary = item.summary.toLowerCase();
        return eventType === 'read' ? 
            summary === "read" : 
            summary.includes("daily 60*60*3");
    }).map(item => ({
        date: item.date.split('T')[0], // Extract just the date part
        value: 1 // Assuming all events are completed
    }));
}

async function initializeCalendar(cal, data, containerId, legendId, colorScheme, routineType) {
    console.log(`Initializing calendar for ${containerId} with data:`, data);
    try {
        cal.paint(
            {
                data: {
                    source: data,
                    x: 'date',
                    y: 'value',
                },
                date: { start: new Date('2024-09-15') },
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
                // Add highlight configuration for today
                highlights: [
                    {
                        fill: 'red',
                        radius: 2,
                        dates: [new Date()]
                    }
                ],
            },
            [
                [
                    Tooltip,
                    {
                        text: function (date, value, dayjsDate) {
                            return value !== null ?
                                `${value} ${routineType} on ${dayjs(dayjsDate).format('dddd, MMMM D, YYYY')}` :
                                `No ${routineType} data on ${dayjs(dayjsDate).format('dddd, MMMM D, YYYY')}`;
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
        const routinesData = await fetchChartData('jonkuhar11_gmail.com');
        
        const greenColorScheme = ['#0e4429', '#006d32', '#26a641', '#39d353'];
        const blueColorScheme = ['#0a3069', '#0d4a6e', '#0969da', '#54aeff'];
        const orangeColorScheme = ['#3d1e00', '#7a2e00', '#bd4b00', '#fb8f44'];
        const purpleColorScheme = ['#3c1e79', '#5e35b1', '#7e57c2', '#b39ddb'];
        
        if (fitnessData.length === 0) {
            console.error('No data available for Fitness calendar');
        } else {
            await initializeCalendar(fitnessCalendar, fitnessData, 'fitness-calendar', 'fitness-legend', greenColorScheme, 'Fitness');
        }
        
        if (projectsData.length === 0) {
            console.error('No data available for Projects calendar');
        } else {
            await initializeCalendar(projectsCalendar, projectsData, 'projects-calendar', 'projects-legend', blueColorScheme, 'Projects');
        }

        if (routinesData.length === 0) {
            console.error('No data available for Routines calendar');
        } else {
            const readData = processRoutinesData(routinesData, 'read');
            const gymData = processRoutinesData(routinesData, 'Daily 60*60*3');
            
            await initializeCalendar(morningRoutineCalendar, readData, 'morning-routine-calendar', 'morning-routine-legend', orangeColorScheme, 'Read');
            await initializeCalendar(shortWorkoutCalendar, gymData, 'short-workout-calendar', 'short-workout-legend', purpleColorScheme, 'Daily 60*60*3');
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

morningRoutineCalendar.on('error', (error) => {
    console.error('Morning Routine Calendar error:', error);
});

shortWorkoutCalendar.on('error', (error) => {
    console.error('Short Workout Calendar error:', error);
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

document.getElementById('morning-routine-prev-button').addEventListener('click', (e) => {
    e.preventDefault();
    morningRoutineCalendar.previous();
});

document.getElementById('morning-routine-next-button').addEventListener('click', (e) => {
    e.preventDefault();
    morningRoutineCalendar.next();
});

document.getElementById('short-workout-prev-button').addEventListener('click', (e) => {
    e.preventDefault();
    shortWorkoutCalendar.previous();
});

document.getElementById('short-workout-next-button').addEventListener('click', (e) => {
    e.preventDefault();
    shortWorkoutCalendar.next();
});
