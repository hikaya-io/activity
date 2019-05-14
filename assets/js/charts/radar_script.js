var radarFunction = function(componentID,dataSet, dataLabels,tolaRadarColors){
    var ctx = document.getElementById(componentID);

    var tolaRadarChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: dataLabels,
            datasets: [{
                label: '# of Things', // user input axis label
                data: dataSet,
                backgroundColor: tolaRadarColors[0],
                borderColor: tolaRadarColors[0],
                borderWidth: 1,
            }]
        },
        options: {
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero:true,
                    }
                }]
            }
            //add options relating to legend generation
        }
    });
};