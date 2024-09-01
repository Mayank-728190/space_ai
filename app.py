from flask import Flask, request, render_template, jsonify, send_file, abort
import cv2
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import requests
from io import BytesIO
import os

app = Flask(__name__)

# Path to save the processed image
PROCESSED_IMAGE_PATH = 'static/processed_image.png'

# Ensure the static directory exists
os.makedirs(os.path.dirname(PROCESSED_IMAGE_PATH), exist_ok=True)

# Load and preprocess the image from file
def load_image_from_file(file):
    if file.content_length == 0:
        raise ValueError("Uploaded file is empty.")
    
    file_content = file.read()
    if not file_content:
        raise ValueError("Failed to read the uploaded file.")
    
    image = cv2.imdecode(np.frombuffer(file_content, np.uint8), cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError("Failed to decode the image. The file might not be a valid image.")
    
    image = cv2.resize(image, (512, 512))  # Resize for consistency
    return image

# Load and preprocess the image from URL
def load_image_from_url(url):
    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError("Failed to download the image from the URL.")
    
    image = cv2.imdecode(np.frombuffer(response.content, np.uint8), cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError("Failed to decode the image from the URL content.")
    
    image = cv2.resize(image, (512, 512))  # Resize for consistency
    return image

# Estimate altitude from image
def estimate_altitude(image):
    mean_intensity = np.mean(image)
    altitude = mean_intensity * 100  # Simple linear mapping; adjust as needed
    return altitude

# Calculate required thrust based on altitude
def calculate_required_thrust(altitude, lander_mass=1000):  # Default mass is 1000kg
    gravity = 1.62  # Lunar gravity in m/s^2
    required_thrust = lander_mass * gravity * (1 + altitude / 1000)
    return required_thrust

# Determine which thrusters should be on
def determine_active_thrusters(required_thrust):
    thrusters = {
        "front": required_thrust / 4,
        "back": required_thrust / 4,
        "left": required_thrust / 4,
        "right": required_thrust / 4,
    }
    return thrusters

# Preprocess the image (normalize)
def preprocess_image(image):
    scaler = MinMaxScaler()
    image_flattened = image.reshape(-1, 1)
    image_normalized = scaler.fit_transform(image_flattened).reshape(image.shape)
    return image_normalized

# Find the best landing spots
def find_best_spots(image, altitude):
    heatmap = np.zeros_like(image)
    spots = []

    step_size = 64
    window_size = 128
    
    for y in range(0, image.shape[0] - window_size + 1, step_size):
        for x in range(0, image.shape[1] - window_size + 1, step_size):
            window = image[y:y + window_size, x:x + window_size]
            mean_brightness = np.mean(window)
            std_dev = np.std(window)
            
            score = 1 / (std_dev + 1) * (1 - abs(mean_brightness - altitude / 100))
            heatmap[y:y + window_size, x:x + window_size] = score
            spots.append((score, (x, y)))

    spots.sort(reverse=True, key=lambda s: s[0])
    best_spots = spots[:3]
    
    return heatmap, best_spots

# Mark the best spots on the image
def mark_spots_on_image(image, best_spots, altitude):
    marked_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    labels = ["Spot 1", "Spot 2", "Spot 3"]
    colors = [(0, 255, 0), (255, 255, 0), (0, 0, 255)]  # Green, Yellow, Red

    for i, (score, (x, y)) in enumerate(best_spots):
        cv2.rectangle(marked_image, (x, y), (x + 128, y + 128), colors[i], 2)
        cv2.putText(marked_image, f"{labels[i]} (Alt: {altitude:.2f}m)", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors[i], 2, cv2.LINE_AA)

    return marked_image

# Save the processed image
def save_processed_image(marked_image):
    cv2.imwrite(PROCESSED_IMAGE_PATH, marked_image)

# Define the main route
@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        if request.method == 'POST':
            if 'file' in request.files and request.files['file'].filename != '':
                file = request.files['file']
                image = load_image_from_file(file)
            elif 'url' in request.form and request.form['url'] != '':
                url = request.form['url']
                image = load_image_from_url(url)
            else:
                return "Please upload an image file or provide a URL.", 400

            altitude = estimate_altitude(image)
            required_thrust = calculate_required_thrust(altitude)
            active_thrusters = determine_active_thrusters(required_thrust)
            
            preprocessed_image = preprocess_image(image)
            heatmap, best_spots = find_best_spots(preprocessed_image, altitude)
            marked_image = mark_spots_on_image(image, best_spots, altitude)
            save_processed_image(marked_image)
            
            result = {
                "altitude": altitude,
                "required_thrust": required_thrust,
                "active_thrusters": active_thrusters,
                "best_spots": best_spots
            }

            return render_template('result.html', result=result)
        
    except Exception as e:
        return f"An error occurred: {str(e)}", 400

    return render_template('index.html')

# Serve the processed image
@app.route('/processed_image')
def serve_image():
    if not os.path.isfile(PROCESSED_IMAGE_PATH):
        abort(404, description="Processed image not found.")
    return send_file(PROCESSED_IMAGE_PATH, mimetype='image/png')

# Define a result route to display the altitude, thrust information, and image
@app.route('/result')
def result_page():
    return render_template('result.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)  # Use port 80 for Render
