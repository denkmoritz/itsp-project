import os
import requests

# Function to get Street View images
def get_streetview_image(api_key, fov, pitch, size, heading, location, data_folder):
    base_url = "https://maps.googleapis.com/maps/api/streetview"

    params = {
        "key": api_key,
        "fov": fov,
        "heading": heading,
        "location": f"{location[0]},{location[1]}",
        "pitch": pitch,
        "size": size
    }

    os.makedirs(data_folder, exist_ok=True)

    filename = f"{location[0]}_{location[1]}_heading_{heading}.jpg"
    save_path = os.path.join(data_folder, filename)

    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        with open(save_path, "wb") as file:
            file.write(response.content)
        print(f"Image saved to {save_path}")
        return save_path
    else:
        print(f"Failed to get image: {response.status_code}, {response.text}")
        return None