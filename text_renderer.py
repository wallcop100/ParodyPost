from PIL import Image, ImageDraw, ImageFont
import textwrap

class TextRenderer:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.draw = None

    def init_image(self):
        self.image = Image.new('1', (self.width, self.height), 255)  # 255: clear the frame
        self.draw = ImageDraw.Draw(self.image)

    def load_font(self, font_path, font_size):
        return ImageFont.truetype(font_path, font_size)

    def render_text(self, text, font, max_width):
        wrapped_text = textwrap.fill(text, width=max_width)
        return wrapped_text.split('\n')

    def draw_text(self, text_lines, font, start_x, start_y):
        y = start_y
        for line in text_lines:
            line_width, line_height = self.draw.textsize(line, font=font)
            x = start_x + (self.width - line_width) // 2  # Center the text horizontally
            self.draw.text((x, y), line, font=font, fill=0)
            y += line_height  # Move to the next line

    def get_image(self):
        return self.image
