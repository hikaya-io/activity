var lineFunction = function(data, tolaLineColors){
    var ctx = document.getElementById(data.component_id);

    var tolaLineChart = new Chart(ctx, {
        type: 'line',
        data: {            
            labels: ['1','2'], //data.labels
            fill: false,
            lineTension: 0.1,
            backgroundColor: '#82BC00',
            borderColor: '#82BC00',
            borderCapStyle: 'butt',
            borderDashOffset: 0.0,
            borderJoinStyle: 'miter',
            pointBorderColor: '#82BC00',
            pointBackgroundColor: "#fff",
            pointBorderWidth: 1,
            pointHoverRadius: 5,
            pointHoverBackgroundColor: '#82BC00',
            pointHoverBorderColor: '#82BC00',
            pointHoverBorderWidth: 2,
            pointRadius: 1,
            pointHitRadius: 10,
            data: [65, 59, 80, 81],
        },          
        options: {            
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero:true,
                    }
                }]
            },
            height: 260,
            responsive: true,
            maintainAspectRatio: true}
    });
};
