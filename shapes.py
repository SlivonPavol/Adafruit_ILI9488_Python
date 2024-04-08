# Import necessary libraries
from PIL import Image, ImageDraw, ImageFont
from time import sleep
import ILI9488 as TFT
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
def display_data(bpm, oxygen):
    # Raspberry Pi configuration
    DC = 24
    RST = 25
    SPI_PORT = 0
    SPI_DEVICE = 0
    
    # Create TFT LCD display class
    disp = TFT.ILI9488(DC, rst=RST, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=64000000))
    
    # Initialize display
    disp.begin()
    
    # Clear display
    disp.clear()
    
    # Example of adding text
    text_name = "example_text"
    text_content = "Hello, World!"
    custom_font_path = "arial.ttf"
    Beat_num_font = ImageFont.truetype(custom_font_path, size=70)
    Beat_text_font = ImageFont.truetype(custom_font_path, size=30)
    text_position = (50, 50)  # Position where you want to place the text
    text_color = (255, 255, 255)  # Color of the text (default is white)
    
    # Add text to the display
    disp.add_text("Beat_num", bpm, ((320/2)-50, 60), font=Beat_num_font, color=text_color)
    disp.add_text("Beat_text", "Bpm", (230, 110), font=Beat_text_font, color=text_color)
    disp.add_text("oxygen_num", oxygen, ((320/2)-50, 190), font=Beat_num_font, color=text_color)
    disp.add_text("oxygen_text", "%", (240, 240), font=Beat_text_font, color=text_color)
    disp.display()
    
    # Load sprite images
    heart_image = disp.load_sprite_from_file("heart1.png", size=(70,70))
    heart_image1 = disp.load_sprite_from_file("heart1.png", size=(76,76))
    oxygen_image = disp.load_sprite_from_file("oxygen1.png", size=(70,70))
    oxygen_image1 = disp.load_sprite_from_file("oxygen1.png", size=(76,76))
    
    # Animation loop
    while True:
        # Display first sprite image
        disp.add_sprite("male_srdco", heart_image, (230, 50), transparent=True)
        disp.remove_sprite("velke_srdco")
        disp.add_sprite("male_oxygen", oxygen_image, (230, 175), transparent=True)
        disp.display()
        sleep(0.1)
    
        # Display second sprite image
        disp.remove_sprite("male_srdco")
        disp.add_sprite("velke_srdco", heart_image1, (230, 50), transparent=True)
        disp.display()
