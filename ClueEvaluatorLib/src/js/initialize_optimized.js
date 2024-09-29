document.getElementById('initform').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent default form submission
    const startTime = performance.now(); // Start time

    // Collect user input from the form fields
    const jsonData = {
        player_name: document.getElementById('username').value,
        tier_4_luck: document.getElementById('tier_4_luck').checked,
        orlando: document.getElementById('has_orlando').checked,
        rebuild_db: document.getElementById('should_rebuild_db').checked,
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
            // Wait for the JSON body and extract the 'detail' field before throwing an error
            return response.json().then(errorData => {
                throw new Error(errorData.detail || 'An unknown error occurred');
            });
        }
        return response.json();
    })
    .then(data => {
        // Display server response
        document.getElementById('response').textContent = JSON.stringify(data, null, 2);
        const endTime = performance.now(); // End time
        const timeTaken = endTime - startTime; // Calculate duration
        document.getElementById('timeTaken').textContent = `Time taken: ${timeTaken.toFixed(2)} ms`; // Display time taken
        AllowUpdates = true;
    })
    .catch(error => {
        console.error('Error:', error);
        // Display the error detail in the response div
        document.getElementById('response').textContent = `Error: ${error.message}`;
    });

    // Clear the form after submission
    document.getElementById('initform').reset();
});
