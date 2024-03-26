# Import necessary libraries
from PIL import Image, ImageDraw, ImageFont
from time import sleep
import ILI9488 as TFT
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI

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
disp.add_text("Beat_num", "100", ((320/2)-50, (160/2)-20), font=Beat_num_font, color=text_color)
disp.add_text("Beat_text", "Bpm", (230, 110), font=Beat_text_font, color=text_color)
disp.display()

# Load sprite images
sprite_image = disp.load_sprite_from_file("heart70.png")
sprite_image1 = disp.load_sprite_from_file("heart76.png")

# Animation loop
while True:
    # Display first sprite image
    disp.add_sprite("biele", sprite_image, (230, 50), transparent=True)
    disp.remove_sprite("idk")
    disp.display()
    sleep(0.1)

    # Display second sprite image
    disp.remove_sprite("biele")
    disp.add_sprite("idk", sprite_image1, (230, 50), transparent=True)
    disp.display()
