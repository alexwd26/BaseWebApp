<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fetch API Data</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Inter', sans-serif;
        }
    </style>
</head>
<body class="bg-gray-100 p-6">
    <div class="container max-w-2xl mx-auto bg-white shadow-md rounded-lg p-8">
        <h1 class="text-2xl font-semibold text-gray-800 mb-6 text-center">Fetch Data from API</h1>
        <div id="loading" class="text-center mb-4">
            <p class="text-gray-600">Loading data...</p>
        </div>
        <div id="error" class="text-center text-red-500 mb-4" style="display:none;">
            <p>Error: Unable to fetch data.</p>
        </div>
        <ul id="data-list" class="space-y-3">
            </ul>
    </div>

    <script>
        const dataList = document.getElementById('data-list');
        const loadingIndicator = document.getElementById('loading');
        const errorDisplay = document.getElementById('error');
        const apiUrl = 'http://15.228.148.198:8000/api/menus/';

        fetch(apiUrl)
            .then(response => {
                console.log("Fetch response:", response); // Added console log
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                loadingIndicator.style.display = 'none';
                if (!data || !Array.isArray(data) || data.length === 0) {
                    dataList.innerHTML = '<li class="text-gray-500 text-center">No data available.</li>';
                    return;
                }
                // Assuming the API returns an array of menu items
                data.forEach(item => {
                    const listItem = document.createElement('li');
                    listItem.className = "bg-gray-50 rounded-md p-4 flex items-center justify-between shadow-sm";
                    listItem.innerHTML = `<span class="text-gray-700 font-semibold">${item.name || 'Unknown'}</span>
                                          <span class="text-blue-600 font-semibold text-sm">Price: $${item.price || 'N/A'}</span>`;
                    dataList.appendChild(listItem);
                });
            })
            .catch(error => {
                loadingIndicator.style.display = 'none';
                errorDisplay.style.display = 'block';
                console.error('Error fetching data:', error);
                errorDisplay.innerHTML = `<p class="text-red-500 text-center">Failed to load data: ${error.message}</p>`; // Display the error message
            });
    </script>
</body>
</html>
