document.getElementById('initform').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent default form submission

    // Collect user input from the form fields
    const username = document.getElementById('username').value;
    const tier_4_luck = document.getElementById('tier_4_luck').checked;
    const orlando = document.getElementById('has_orlando').checked;
    const rebuild_db = document.getElementById('should_rebuild_db').checked;

    // Create JSON data from the input
    const jsonData = {
        player_name: username,
        tier_4_luck: tier_4_luck,
        orlando: orlando,
        rebuild_db: rebuild_db,
    };

    // Send the JSON data to the server via an HTTP POST request
    fetch("http://127.0.0.1:8000/initialize/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(jsonData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Display server response
        document.getElementById('response').textContent = JSON.stringify(data, null, 2);
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('response').textContent = 'Error: ' + error.message;
    });

    // Clear the form after submission
    document.getElementById('initform').reset();
});
