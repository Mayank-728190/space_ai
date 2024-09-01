# Space AI
Overview
Space AI is a web application that analyzes images to identify optimal landing spots on lunar surfaces. By leveraging image processing techniques, the application estimates altitude, calculates required thrust, and identifies the best landing spots. Users can upload an image or provide a URL to an image, and the application will process it to provide detailed analysis results.

Features
Image Upload and URL Input: Upload an image file or provide a URL to analyze lunar landing spots.
Altitude Estimation: Estimate the altitude based on image pixel intensity.
Thrust Calculation: Calculate the required thrust for a lunar lander based on the estimated altitude.
Landing Spot Identification: Identify and mark the top three landing spots based on image analysis.
Processed Image Display: Display the processed image with marked landing spots.
Technologies Used
Flask: Web framework for building the application.
OpenCV: Image processing library for handling image operations.
NumPy: Numerical operations library for image manipulation.
Scikit-learn: For normalization of image data.
Requests: For handling image downloads from URLs.
Setup and Installation
Prerequisites
Python 3.x
Flask
OpenCV
NumPy
Scikit-learn
Requests


File Structure
app.py: Main Flask application file.
templates/: Contains HTML templates for the application.
index.html: Form for image upload and URL input.
result.html: Page displaying analysis results.
static/: Contains static files such as CSS and images.
requirements.txt: Python dependencies for the project.

Troubleshooting
Image Not Found: Ensure that the image path in the PROCESSED_IMAGE_PATH is correct and accessible.
Dependencies: Ensure all required packages are installed correctly.
Server Errors: Check the Flask server logs for detailed error messages.

License
This project is licensed under the MIT License. See the LICENSE file for details.
