import sys
import os
import threading
import http.server
import socketserver
import logging

import folium
import cv2

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QTextEdit, QWidget, QPushButton,
    QProgressBar, QSizePolicy
)
from PyQt6.QtWebEngineWidgets import QWebEngineView

from data.getRef import get_ref_list
from road.getAzimuth import get_segment_data
from config.configSV import ConfigSV
from streetview.getStreetView import get_streetview_image
from image.colorDetection import detect_color

# ConfigSV instance for credentials
configSV = ConfigSV()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

def log_message(message: str):
    logging.info(message)

class MainUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Road Analysis Tool")
        self.setGeometry(100, 100, 1200, 800)   # Set window position with size

        self.state_to_roads = get_ref_list()

        # Initialize the HTTP server reference
        self.http_server = None

        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Control layout
        control_layout = QVBoxLayout()
        control_widget = QWidget()
        control_widget.setLayout(control_layout)
        control_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)

        # State selector
        state_layout = QHBoxLayout()
        self.state_selector = QComboBox()
        self.state_selector.addItems(self.state_to_roads.keys())
        self.state_selector.currentIndexChanged.connect(self.update_road_selector)
        state_layout.addWidget(QLabel("Select a State:"))
        state_layout.addWidget(self.state_selector)
        control_layout.addLayout(state_layout)

        # Road selector
        road_layout = QHBoxLayout()
        self.road_selector = QComboBox()
        self.update_road_selector()
        road_layout.addWidget(QLabel("Select a Road:"))
        road_layout.addWidget(self.road_selector)
        control_layout.addLayout(road_layout)

        # Analyze button
        self.analyze_button = QPushButton("Analyze")
        self.analyze_button.clicked.connect(self.trigger_workflow)
        control_layout.addWidget(self.analyze_button)

        # Add control widget to the main layout
        main_layout.addWidget(control_widget)

        # Map view
        self.map_view = QWebEngineView()
        self.map_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.set_placeholder()
        main_layout.addWidget(self.map_view, stretch=1)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setVisible(False)
        self.progress_bar.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        main_layout.addWidget(self.progress_bar)

        # Log output
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setFixedHeight(150)
        self.log_output.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        main_layout.addWidget(self.log_output)

    def update_road_selector(self):
        selected_state = self.state_selector.currentText()
        self.road_selector.clear()
        roads = self.state_to_roads.get(selected_state, [])
        self.road_selector.addItems(roads)

    def set_placeholder(self):
        placeholder_html = """
        <!DOCTYPE html>
        <html>
            <body style="background-color: #1e1e1e; color: white; text-align: center; font-family: Arial;">
                <h2>Welcome to the Road Analysis Tool</h2>
                <p>Select a state and a road, then click 'Analyze' to display the output on a map.</p>
            </body>
        </html>
        """
        self.map_view.setHtml(placeholder_html)

    def trigger_workflow(self):
        selected_state = self.state_selector.currentText()
        selected_ref = self.road_selector.currentText()
        if selected_state and selected_ref:
            self.generate_map(selected_state, selected_ref)

    # Function that assures that both sides of the car ('front and rear') are tested if first images has no result (color unknown)
    def process_segment(self, heading, lat, lon, index, selected_ref, selected_state):
        predominant = "unknown"
        plot_path = None

        # Folder to save images and plots
        image_folder = os.path.join("data/images", f"{selected_ref}_{selected_state}")
        if not os.path.exists(image_folder):
            os.makedirs(image_folder)

        for attempt in range(2):
            adjusted_heading = heading if attempt == 0 else (heading + 180) % 360
            log_message(f"Attempt {attempt + 1} for segment {index + 1}: Heading={adjusted_heading}")

            save_path = get_streetview_image(
                api_key=configSV.api_key,
                fov=configSV.fov,
                pitch=configSV.pitch,
                size=configSV.size,
                heading=adjusted_heading,
                location=(lat, lon),
                data_folder=image_folder
            )

            image = cv2.imread(save_path)
            if image is None:
                log_message(f"Failed to load image for segment {index + 1}, attempt {attempt + 1}")
                continue

            # Save the plot inside the same folder
            plot_path = os.path.join(image_folder, f"plot_{index}.png")
            predominant, plot_path = detect_color(
                image, box_width=200, box_height=200, vertical_offset=-30, plot_path=plot_path
            )

            log_message(f"Plot saved at: {plot_path}")

            if predominant != "unknown":
                break

        return predominant, plot_path

    # Function to start server and store the plots because otherwise the html file of map becomes too big
    def start_http_server(self, folder_path, port=8055):
        class CustomHandler(http.server.SimpleHTTPRequestHandler):
            def translate_path(self, path):
                # Force the server to serve files relative to `folder_path`
                relative_path = path.lstrip("/")
                full_path = os.path.join(folder_path, relative_path)
                print(f"Looking for file: {full_path}")
                return full_path

        # Start the server
        handler = CustomHandler
        httpd = socketserver.TCPServer(("", port), handler)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        print(f"Serving files from {folder_path} at http://localhost:{port}")
        return httpd

    def closeEvent(self, event):
        if self.http_server:
            log_message("Shutting down HTTP server...")
            self.http_server.shutdown()
            self.http_server.server_close()
        super().closeEvent(event)

    # Function that generates the map
    def generate_map(self, selected_state, selected_ref):
        try:
            # Prepare the image folder for storing plots
            image_folder = os.path.join("data/images", f"{selected_ref}_{selected_state}")
            if not os.path.exists(image_folder):
                os.makedirs(image_folder)

            road_data = get_segment_data(ref=selected_ref, iso_1=selected_state, min_distance_km=2)

            if not road_data:
                log_message("No valid data available for the selected road.")
                self.set_placeholder()
                return

            self.progress_bar.setMaximum(len(road_data))
            self.progress_bar.setValue(0)
            self.progress_bar.setVisible(True)

            results = []
            for i, (heading, (lon, lat)) in enumerate(road_data):
                log_message(f"Processing segment {i + 1}/{len(road_data)}: Heading={heading}, Location=({lat}, {lon})")
                predominant, plot_path = self.process_segment(heading, lat, lon, i, selected_ref, selected_state)
                print(f"Plot saved at: {plot_path}")  # Debugging
                results.append((lat, lon, predominant, plot_path))
                self.progress_bar.setValue(i + 1)
                self.progress_bar.setFormat(f"{i + 1}/{len(road_data)} segments processed")

            # Start the HTTP server AFTER plots are created
            self.http_server = self.start_http_server("data/images", port=8055)

            # Calculate center of the map using min/max lat/lon
            min_lat = min(result[0] for result in results)
            max_lat = max(result[0] for result in results)
            min_lon = min(result[1] for result in results)
            max_lon = max(result[1] for result in results)

            center_lat = (min_lat + max_lat) / 2
            center_lon = (min_lon + max_lon) / 2

            # Generate map with calculated center
            map_obj = folium.Map(location=[center_lat, center_lon])

            # Create markers on the map with information such as the plots
            for i, (lat, lon, color, plot_path) in enumerate(results):
                if plot_path and os.path.exists(plot_path):
                    # Compute the relative path
                    relative_path = os.path.relpath(plot_path, "data/images")
                    plot_url = f"http://localhost:8055/{relative_path.replace(os.path.sep, '/')}"
                else:
                    plot_url = None

                # Create a popup for each marker with the plot image
                popup_html = f"""
                <div style="text-align: center;">
                    <h4>Segment {i + 1}</h4>
                    <p>Latitude: {lat}<br>Longitude: {lon}<br>Color: {color}</p>
                    {"<img src='" + plot_url + "' alt='Segment Plot' style='width: 400px; height: auto;'>" if plot_url else ""}
                </div>
                """
                popup = folium.Popup(popup_html, max_width=800)
                marker_icon = folium.Icon(color="blue" if color == "blue" else "gray", icon="info-sign")
                folium.Marker(location=(lat, lon), popup=popup, icon=marker_icon).add_to(map_obj)

            # Render the map
            map_html = map_obj.get_root().render()
            self.map_view.setHtml(map_html)

            log_message("Map successfully loaded into QWebEngineView.")
        except Exception as e:
            log_message(f"An error occurred: {e}")
            self.set_placeholder()
        finally:
            self.progress_bar.setVisible(False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainUI()
    main_window.show()
    sys.exit(app.exec())