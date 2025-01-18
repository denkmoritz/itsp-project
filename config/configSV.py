import os

class ConfigSV:
    api_key = os.getenv("api_key", "****")
    fov = os.getenv("fov", 50)
    pitch = os.getenv("pitch", -40)
    size = os.getenv("size", "640x640")