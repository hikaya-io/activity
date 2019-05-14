var pieFunction = function(componentID,dataSet, dataLabels, tolaPieColors){
    var ctx = document.getElementById(componentID);
    var tolaPieChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: dataLabels,
            datasets: [{
                label: '# of Things', // user input axis label
                data: dataSet,
                backgroundColor: tolaPieColors,
                borderColor: tolaPieColors,
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