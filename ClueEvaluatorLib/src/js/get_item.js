document.getElementById('getitemform').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent default form submission

    const startTime = performance.now(); // Start time
    // Collect user input from the form fields
    const itemname = document.getElementById('itemname').value;
    // Send the JSON data to the server via an HTTP POST request
    fetch(`http://127.0.0.1:8000/items/?item_name=${encodeURIComponent(itemname)}`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json"
        },
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
        const endTime = performance.now(); // End time
        const timeTaken = endTime - startTime; // Calculate duration
        document.getElementById('timeTaken').textContent = `Time taken: ${timeTaken.toFixed(2)} ms`; // Display time taken
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('response').textContent = 'Error: ' + error.message;
    });

    // Clear the form after submission
    document.getElementById('initform').reset();
});
