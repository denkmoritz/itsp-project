import cv2
import numpy as np
import matplotlib.pyplot as plt

# Function to detect the color of the google car
def detect_color(image, box_width, box_height, vertical_offset=0, plot_path = None):
    # Get image dimensions
    height, width, _ = image.shape

    # Calculate center of image
    center_x, center_y = width // 2, height // 2

    # Vertical offset to move box up or down
    center_y += vertical_offset

    # Calculate half box dimensions
    half_width, half_height = box_width // 2, box_height // 2

    # Define top-left and bottom-right points of box
    top_left = (center_x - half_width, center_y - half_height)
    bottom_right = (center_x + half_width, center_y + half_height)

    # Crop region inside box
    cropped_region = image[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]

    # Handle empty cropped region if something went wrong
    if cropped_region.size == 0:
        print("Cropped region is empty. Check box dimensions or image size.")
        return

    # Convert cropped region to HSV color space
    hsv_cropped = cv2.cvtColor(cropped_region, cv2.COLOR_BGR2HSV)

    # Default blue color in BGR
    blue = [255, 0, 0]

    # Get HSV limits for blue
    lower_blue, upper_blue = get_limits(color=blue, range_width=30, sat_low=40, val_low=40)
    print(f"HSV lower limit: {lower_blue}, HSV upper limit: {upper_blue}")

    # Create mask for blue
    blue_mask = cv2.inRange(hsv_cropped, lower_blue, upper_blue)

    # Calculate proportions of blue pixels
    blue_pixels = cv2.countNonZero(blue_mask)
    total_pixels = cropped_region.shape[0] * cropped_region.shape[1]
    blue_percentage = (blue_pixels / total_pixels) * 100

    # Determine predominant color
    if blue_percentage > 10:  # Threshold for determining "predominant"
        predominant_color = "blue"
        print(f"Blue is the predominant color and the percentage is: {blue_percentage:.2f} %")
    else:
        predominant_color = "unknown"
        print("The predominant color is unknown.")

    # Visualize cropped region and mask
    if plot_path:
        plt.figure(figsize=(8, 4))
        plt.subplot(1, 2, 1)
        plt.imshow(cv2.cvtColor(cropped_region, cv2.COLOR_BGR2RGB))
        plt.title("Cropped Region")
        plt.axis("off")

        plt.subplot(1, 2, 2)
        plt.imshow(blue_mask, cmap="gray")
        plt.title("Blue Mask")
        plt.axis("off")

        plt.savefig(plot_path)
        plt.close()

    return predominant_color, plot_path

# Function to calculate limits for colors (range)
def get_limits(color=None, range_width=30, sat_low=40, val_low=40):
    if color is not None:
        # Convert BGR to HSV
        c = np.uint8([[color]])
        hsvC = cv2.cvtColor(c, cv2.COLOR_BGR2HSV)
        hue = hsvC[0][0][0]  # Get hue value
    else:
        hue = 120  # Default to typical blue hue

    # Adjust range for hue, saturation, and value
    lowerLimit = np.array([max(hue - range_width, 0), sat_low, val_low], dtype=np.uint8)
    upperLimit = np.array([min(hue + range_width, 180), 255, 255], dtype=np.uint8)

    return lowerLimit, upperLimit