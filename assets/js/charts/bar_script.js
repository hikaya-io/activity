var barFunction = function(componentID,dataSet, dataLabels, tolaBarColors){
    var ctx = document.getElementById(componentID);
    var tolaBarChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: dataLabels,
            datasets: [{
                label: "# of people", // user input axis label
                data: dataSet,
                backgroundColor: tolaBarColors,
                borderColor: tolaBarColors,
                borderWidth: 1,
            }]
        },
        options: {
            legend: {
                display: false,
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
        }
    });
};