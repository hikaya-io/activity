var doughnutFunction = function(componentID,dataSet, dataLabels, tolaDoughnutColors){
    var ctx = document.getElementById(componentID);
    var tolaDoughnutChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: dataLabels,
            datasets: [{
                label: "placeholder", // user input axis label
                data: dataSet,
                backgroundColor: tolaDoughnutColors,
                borderColor: tolaDoughnutColors,
                borderWidth: 1,
            }]
        },
        options: {
            legend: {
                display: true,
                labels: {
                    boxWidth: 10,
                }
            },
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero:true,
                    }
                }]
            },
            responsive: true,
            maintainAspectRatio: true
            //add options relating to legend generation
        }
    });
};