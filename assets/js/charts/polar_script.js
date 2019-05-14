var polarFunction = function(data, tolaPolarColors){
    var ctx = document.getElementById(data.component_id);
    var tolaPolarChart = new Chart(ctx, {
        type: 'polar',
        data: {
            datasets: [{
	        data: data,
	        backgroundColor: tolaPolarColors,
	        label: 'My dataset' // for legend
		    }],
		    labels: [
		        "Red",
		        "Green",
		        "Yellow",
		        "Grey",
		        "Blue"
		    ]},
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