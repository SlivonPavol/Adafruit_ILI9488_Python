import numbers
import time
import numpy as np
from PIL import ImageFont, Image, ImageDraw
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI

# Constants for ILI9488 TFT LCD
# If in portrait mode, switch width and height
ILI9488_TFTWIDTH = 480
ILI9488_TFTHEIGHT = 320


ILI9488_SWRESET = 0x01
ILI9488_SLPIN = 0x10
ILI9488_SLPOUT = 0x11
ILI9488_INVOFF = 0x20
ILI9488_INVON = 0x21
ILI9488_RAMWR = 0x2C
ILI9488_DISPOFF = 0x28
ILI9488_DISPON = 0x29
ILI9488_CASET = 0x2A
ILI9488_PASET = 0x2B
ILI9488_MADCTL = 0x36
ILI9488_PIXFMT = 0x3A
ILI9488_FRMCTR1 = 0xB1
ILI9488_INVCTR = 0xB4
ILI9488_DFUNCTR = 0xB6
ILI9488_PWCTR1 = 0xC0
ILI9488_PWCTR2 = 0xC1
ILI9488_VMCTR1 = 0xC5
ILI9488_GMCTRP1 = 0xE0
ILI9488_GMCTRN1 = 0xE1

# Constants for MADCTL
MADCTL_MY = 0x80
MADCTL_MX = 0x40
MADCTL_MV = 0x20
MADCTL_ML = 0x10
MADCTL_RGB = 0x00
MADCTL_BGR = 0x08
MADCTL_MH = 0x04


def color565(r, g, b):
    """Convert red, green, blue components to an 8-bit 888 RGB value."""
    return (r << 16) | (g << 8) | b


def image_to_data(image):
    """Convert a PIL image to 8-bit 888 RGB bytes."""
    pb = np.array(image.convert('RGB')).astype('uint32')
    color = (pb[:, :, 0] << 16) | (pb[:, :, 1] << 8) | pb[:, :, 2]
    return np.dstack(((color >> 16) & 0xFF, (color >> 8) & 0xFF, color & 0xFF)).flatten().tolist()


class ILI9488(object):
    """Representation of an ILI9488 TFT LCD."""

    def __init__(self, dc, spi, rst=None, gpio=None, width=ILI9488_TFTWIDTH, height=ILI9488_TFTHEIGHT):
        """Initialize the display."""
        self._dc = dc
        self._rst = rst
        self._spi = spi
        self._gpio = gpio if gpio else GPIO.get_platform_gpio()
        self.width = width
        self.height = height
        self._gpio.setup(dc, GPIO.OUT)
        if rst is not None:
            self._gpio.setup(rst, GPIO.OUT)
        self._spi.set_mode(0)
        self._spi.set_bit_order(SPI.MSBFIRST)
        self._spi.set_clock_hz(64000000)
        self.original_buffer = Image.new('RGB', (width, height))
        self.buffer = self.original_buffer.copy()
        self.sprites = {}
        self.texts = {}

    def create_sprite(self, size, color=(255, 255, 255)):
        """Create a sprite image with the specified size and color."""
        return Image.new('RGB', size, color)

    def add_sprite(self, name, sprite, position, transparent=False):
        """Add a sprite to the buffer."""
        if transparent:
            sprite = sprite.convert('RGBA')
            mask = Image.new('L', sprite.size, 0)
            mask_data = mask.load()
            sprite_data = sprite.load()
            tolerance = 20
            for x in range(sprite.width):
                for y in range(sprite.height):
                    if all(0 <= sprite_data[x, y][i] <= tolerance for i in range(3)):
                        mask_data[x, y] = 0
                    else:
                        mask_data[x, y] = 255
            self.buffer.paste(sprite, position, mask)
        else:
            self.buffer.paste(sprite, position)
        self.sprites[name] = (sprite, position)

    def remove_sprite(self, name):
        """Remove a sprite from the buffer."""
        if name in self.sprites:
            sprite, position = self.sprites.pop(name)
            region = (position[0], position[1], position[0] + sprite.width, position[1] + sprite.height)
            self.buffer.paste(self.original_buffer.crop(region), region)
        for sprite_name, (sprite, position) in self.sprites.items():
            self.buffer.paste(sprite, position)
        for text_name, (text, position, font, font_size, color) in self.texts.items():
            draw = ImageDraw.Draw(self.buffer)
            draw.text(position, text, font=font, fill=color)
            del draw

    def add_text(self, name, text, position, font=None, font_size=None, color=(255, 255, 255)):
        """Add text to the buffer."""
        if font is None:
            font = ImageFont.load_default()
        if font_size is None:
            font_size = font.getsize(text)[1]
        else:
            font = ImageFont.truetype(font.path, font_size)
        draw = ImageDraw.Draw(self.buffer)
        draw.text(position, text, font=font, fill=color)
        self.texts[name] = (text, position, font, font_size, color)

    def remove_text(self, name):
        """Remove text from the buffer."""
        if name in self.texts:
            del self.texts[name]
            self.buffer = self.original_buffer.copy()
            for sprite_name, (sprite, position) in self.sprites.items():
                self.buffer.paste(sprite, position)
            for text_name, (text, position, font, font_size, color) in self.texts.items():
                if text_name != name:
                    draw = ImageDraw.Draw(self.buffer)
                    draw.text(position, text, font=font, fill=color)
                    del draw

    def load_sprite_from_file(self, file_path, size=None):
        """Load an image file and convert it to a sprite."""
        image = Image.open(file_path).convert('RGB')
        if size is not None:
            image = image.resize(size)
        return image

    def send(self, data, is_data=True, chunk_size=4096):
        """Write data to the display."""
        self._gpio.output(self._dc, is_data)
        if isinstance(data, numbers.Number):
            data = [data & 0xFF]
        for start in range(0, len(data), chunk_size):
            end = min(start + chunk_size, len(data))
            self._spi.write(data[start:end])

    def command(self, data):
        """Write a command to the display."""
        self.send(data,False)

    def data(self, data):
        """Write display data to the display."""
        self.send(data, True)

    def reset(self):
        """Reset the display."""
        if self._rst is not None:
            self._gpio.set_high(self._rst)
            time.sleep(0.005)
            self._gpio.set_low(self._rst)
            time.sleep(0.02)
            self._gpio.set_high(self._rst)
            time.sleep(0.150)

    def _init(self):
        """Initialize the display."""
        self.command(ILI9488_SWRESET)
        time.sleep(0.010)
        self.command(ILI9488_INVOFF)
        self.command(ILI9488_PWCTR1)
        self.data([0x17, 0x15])
        self.command(ILI9488_PWCTR2)
        self.data([0x41])
        self.command(ILI9488_VMCTR1)
        self.data([0x00, 0x12, 0x80])
        self.command(ILI9488_MADCTL)
        self.data([0xE8])
        self.command(ILI9488_PIXFMT)
        self.data([0x66])
        self.command(0xB0)
        self.data([0x00])
        self.command(ILI9488_FRMCTR1)
        self.data([0xA0])
        self.command(ILI9488_INVCTR)
        self.data([0x02])
        self.command(ILI9488_DFUNCTR)
        self.data([0x02, 0x02, 0x3B])
        self.command(0xB7)
        self.data([0xC6])
        self.command(0xF7)
        self.data([0xA9, 0x51, 0x2C, 0x82])
        self.command(ILI9488_GMCTRP1)
        self.data([0x00, 0x03, 0x09, 0x08, 0x16, 0x0A, 0x3F, 0x78, 0x4C, 0x09, 0x0A, 0x08, 0x16, 0x1A, 0x0F])
        self.command(ILI9488_GMCTRN1)
        self.data([0x00, 0x16, 0x19, 0x03, 0x0F, 0x05, 0x32, 0x45, 0x46, 0x04, 0x0E, 0x0D, 0x35, 0x37, 0x0F])
        self.command(ILI9488_SLPOUT)
        time.sleep(0.150)
        self.command(ILI9488_DISPON)
        time.sleep(0.050)

    def begin(self):
        """Initialize the display."""
        self.reset()
        self._init()

    def set_window(self, x0=0, y0=0, x1=None, y1=None):
        """Set the pixel address window."""
        if x1 is None:
            x1 = self.width - 1
        if y1 is None:
            y1 = self.height - 1
        self.command(ILI9488_CASET)
        self.data(x0 >> 8)
        self.data(x0)
        self.data(x1 >> 8)
        self.data(x1)
        self.command(ILI9488_PASET)
        self.data(y0 >> 8)
        self.data(y0)
        self.data(y1 >> 8)
        self.data(y1)
        self.command(ILI9488_RAMWR)

    def display(self, image=None):
        """Write the display buffer to the hardware."""
        if image is None:
            image = self.buffer
        self.set_window()
        pixelbytes = list(image_to_data(image))
        self.data(pixelbytes)

    def clear(self, color=(0, 0, 0)):
        """Clear the image buffer."""
        self.original_buffer = Image.new('RGB', (self.width, self.height), color)
        self.buffer = self.original_buffer.copy()

    def draw(self):
        """Return a PIL ImageDraw instance."""
        return ImageDraw.Draw(self.buffer)

    def clear_section(self, x0, y0, x1, y1, color=(0, 0, 0)):
        """Clear a section of the image buffer."""
        draw = self.draw()
        draw.rectangle((x0, y0, x1, y1), fill=color)
