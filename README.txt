Smartport
=========

DESCRIPTION
-----------

Smartport analyzes Uber movement data to find the most congested routes in a city for a given time of the day. It algorithmically routes a given set of buses to cover these congested nodes and cater to as many people as possible. The stops for these bus routes are found by looking for the most popular place nearest to the center. This is obtained by looking at the ratings and open/close timings for establishments in the vicinity given by the Google Places API.

Finally, the results are rendered on a map for visualization. Different routes are colored differently. The user interact with the app to change parameters, pan in, pan out and view statistics based on the options chosen.

Smartport does this by using Flask server and Javascript front end. When a request is received, the Flask server reads the Uber movement data and adjacency matrix. This data is then processed. Finally, the stops are obtained by making calls to the Google API.

This response is received by the Javascript front-end and rendered for viewing as a HTML page.


INSTALLATION
------------

1. Install python 2.7
	Python 2.7.6 or newer.

2. Install python libraries/dependencies
	Navigate to the project root folder.
	pip install -r requirements.txt

3. Unpack the toy data
	Navigate to the project root folder.
	Run tar -xvzf adjacency.tar.gz

4. Preprocessing
	To run the app for another city's data, download the Uber movement data from https://movement.uber.com/?lang=en-US
	sqlite3	movement.db < preprocess_commands.txt

EXECUTION
---------
1. Run the flask server
	From the terminal, execute python __init__.py

2. Open the app in your browser
	Navigate to http://localhost:5000/

3. Click on dashboard on the top right corner. Select the configuration you want to test.

The optimized routes will be displayed on the map.