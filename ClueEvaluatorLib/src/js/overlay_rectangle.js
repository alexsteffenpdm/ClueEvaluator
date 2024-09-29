document.getElementById('create-rectangle-btn').addEventListener('click', function() {
    const container = document.body; // Use the whole document as the container

    // Create a rectangle and add it to the container
    const rectangle = document.createElement('div');
    rectangle.id = 'rectangle';
    const resizeHandle = document.createElement('div');
    resizeHandle.id = 'resize-handle';
    rectangle.appendChild(resizeHandle);
    container.appendChild(rectangle);

    // Show the rectangle
    rectangle.style.display = 'block';
    rectangle.style.top = '100px';   // Set initial position
    rectangle.style.left = '100px';
    rectangle.style.position = 'fixed';  // Allow moving freely on the screen

    let isDragging = false;
    let isResizing = false;

    let startX, startY, startWidth, startHeight;

    // Prevent text selection while dragging
    rectangle.addEventListener('mousedown', function(e) {
        if (e.target === resizeHandle) return; // Ignore when resize handle is clicked
        isDragging = true;
        startX = e.clientX; // Use clientX for dragging
        startY = e.clientY;
        e.preventDefault(); // Prevent text selection
    });

    // Mouse move event
    document.addEventListener('mousemove', function(e) {
        if (isDragging) {
            const newTop = e.clientY - rectangle.offsetHeight / 2;
            const newLeft = e.clientX - rectangle.offsetWidth / 2;
            rectangle.style.top = `${newTop}px`;
            rectangle.style.left = `${newLeft}px`;
        }
        if (isResizing) {
            rectangle.style.width = `${startWidth + (e.clientX - startX)}px`;
            rectangle.style.height = `${startHeight + (e.clientY - startY)}px`;
        }
    });

    // Mouse up event
    document.addEventListener('mouseup', function() {
        isDragging = false;
        isResizing = false;
    });

    // Resizing functionality
    resizeHandle.addEventListener('mousedown', function(e) {
        isResizing = true;
        startX = e.clientX;
        startY = e.clientY;
        startWidth = parseInt(window.getComputedStyle(rectangle).width, 10);
        startHeight = parseInt(window.getComputedStyle(rectangle).height, 10);
        e.stopPropagation(); // Prevent triggering the drag event
    });

    // Capture the rectangle's position and size when pressing the Enter key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            const rectData = {
                position: {
                    top: parseInt(rectangle.style.top, 10),
                    left: parseInt(rectangle.style.left, 10)
                },
                size: {
                    width: parseInt(rectangle.style.width, 10),
                    height: parseInt(rectangle.style.height, 10)
                }
            };

            console.log(rectData);

            // Send data to the server
            // fetch('http://127.0.0.1:8000/image/data', {
            //     method: 'POST',
            //     headers: {
            //         'Content-Type': 'application/json',
            //     },
            //     body: JSON.stringify(rectData),
            // })
            // .then(response => {
            //     if (!response.ok) {
            //         throw new Error('Network response was not ok');
            //     }
            //     return response.json();
            // })
            // .then(data => {
            //     console.log('Success:', data);
            // })
            // .catch(error => {
            //     console.error('Error:', error);
            // });
        }
    });

    // Prevent text selection when dragging the rectangle
    document.body.style.userSelect = 'none'; // Disable text selection for the body while dragging
    rectangle.addEventListener('mouseup', function() {
        document.body.style.userSelect = ''; // Re-enable text selection after dragging
    });

    delete rectangle;
});
