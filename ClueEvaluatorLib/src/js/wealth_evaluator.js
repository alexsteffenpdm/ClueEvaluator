var intervalId = window.setInterval(function(){
    if (AllowUpdates == false) {
        return;
    }

    fetch(`http://127.0.0.1:8000/update/wealthevaluator`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json"
        },
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        // Parse the response body to JSON
        return response.json();
    })
    .then(content => {
        // Display server response


        document.getElementById("num_caskets").textContent = content.stats.opened;
        document.getElementById("num_uniques").textContent = content.stats.uniques;
        document.getElementById("num_broadcasts").textContent = content.stats.broadcasts;

        document.getElementById("unique_rate").textContent = content.item_rates.unique_rate;
        document.getElementById("broadcast_rate").textContent = content.item_rates.broadcast_rate;

        document.getElementById("we_money_total").textContent = content.money_rates.total;
        document.getElementById("we_money_hourly").textContent = content.money_rates.hourly;
        document.getElementById("we_money_avg").textContent = content.money_rates.average;
    })
    .catch(error => {
        console.error('Error fetching or processing data:', error);
    });

}, UpdateInterval);


// {
//     "item_rates": {
//       "unique_rate": "0.00%",
//       "broadcast_rate": "0.00%"
//     },
//     "money_rates": {
//       "hourly": "0",
//       "total": "0",
//       "average": "0"
//     },
//         "stats": {
//             "opened": 0,
//             "uniques": 0,
//             "broadcasts": 0,
//         }
//   }
