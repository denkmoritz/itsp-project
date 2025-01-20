import numpy as np
from geopy.distance import geodesic
from road.getRoad import get_road_from_db

# Function to calculate segments
def calculate_segment_azimuth_and_midpoint(geometry, step=5):
    try:
        segment_data = []

        if geometry.geom_type == "LineString":
            coords = list(geometry.coords)
            segment_data.extend(process_linestring(coords, step))
        elif geometry.geom_type == "MultiLineString":
            for linestring in geometry.geoms:
                coords = list(linestring.coords)
                segment_data.extend(process_linestring(coords, step))

        return segment_data
    except Exception as e:
        print(f"Error calculating azimuth and midpoint: {e}")
        return []

# Function to process segments and calculate azimuth and midpoints
def process_linestring(coords, step):
    segment_data = []
    for i in range(0, len(coords) - 1, step):
        x1, y1 = coords[i]  # Longitude, Latitude
        x2, y2 = coords[min(i + 1, len(coords) - 1)]  # Longitude, Latitude

        # Calculate azimuth, round to 3 decimal places, and cast to float
        azimuth_radians = np.arctan2(x2 - x1, y2 - y1)
        azimuth_degrees = float(round(np.degrees(azimuth_radians) % 360, 3))

        # Calculate midpoint, rounding to 6 decimal places for simplicity
        midpoint = (round((x1 + x2) / 2, 6), round((y1 + y2) / 2, 6))

        segment_data.append((azimuth_degrees, midpoint))
    return segment_data

# Function to assure that midpoints keep a certain distance from each other
def filter_by_distance(segment_data, min_distance_km=2):
    filtered_data = []

    for azimuth, midpoint in segment_data:
        # Check distance against all previously accepted points
        if all(
            geodesic((prev_midpoint[1], prev_midpoint[0]), (midpoint[1], midpoint[0])).km >= min_distance_km
            for _, prev_midpoint in filtered_data
        ):
            filtered_data.append((azimuth, midpoint))

    return filtered_data

# Main function of this file, returns the processed data to main.py
def get_segment_data(ref=None, iso_1=None, step=5, min_distance_km=2):
    try:
        edges = get_road_from_db(ref, iso_1)
        if edges.empty:
            print(f"No data available for the reference: {ref} in state: {iso_1}")
            return []

        # Drop invalid geometries
        edges = edges.dropna(subset=['geometry'])

        # Extract all segment data into flat list
        all_segment_data = []
        for geom in edges['geometry']:
            segment_data = calculate_segment_azimuth_and_midpoint(geom, step=step)
            all_segment_data.extend(segment_data)  # Flatten the list of tuples

        # Filter segments based on minimum distance
        filtered_segment_data = filter_by_distance(all_segment_data, min_distance_km=min_distance_km)

        return filtered_segment_data
    except Exception as e:
        print(f"Error retrieving segment data: {e}")
        return []