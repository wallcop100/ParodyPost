# pages.py
from text_renderer import TextRenderer


def calculate_max_body_width(renderer, font_path, font_size, display_width, margin=0):
    font = renderer.load_font(font_path, font_size)
    sample_char = 'W'
    char_width = renderer.draw.textsize(sample_char, font=font)[0]
    max_body_width = (display_width + 100 - margin * 2) // char_width
    return max_body_width
def render_title_page(epd, header_text, body_text):
        # Text rendering parameters
        header_font_path = 'fonts/OldLondon.ttf'
        body_font_path = 'fonts/PixelifySans.ttf'
        header_size = 57
        body_size = 25
        max_body_width = 20




        # Initialize TextRenderer
        renderer = TextRenderer(epd.height, epd.width)
        renderer.init_image()

        # Load fonts
        header_font = renderer.load_font(header_font_path, header_size)
        body_font = renderer.load_font(body_font_path, body_size)

        # Render and draw header text
        header_lines = renderer.render_text(header_text, header_font, max_body_width)
        header_height = sum(renderer.draw.textsize(line, font=header_font)[1] for line in header_lines)
        header_y = (epd.width - header_height) // 8  # Adjust vertical positioning
        renderer.draw_text(header_lines, header_font, 0, header_y)

        # Render and draw body text
        body_lines = renderer.render_text(body_text, body_font, max_body_width)
        body_height = sum(renderer.draw.textsize(line, font=body_font)[1] for line in body_lines)
        body_y = header_y + header_height + 10  # Add some padding between header and body
        renderer.draw_text(body_lines, body_font, 0, body_y)

        # Display the image on the e-Paper display
        epd.display(epd.getbuffer(renderer.get_image()))

def render_headline_page(epd, body_text):
    # Text rendering parameters
    body_font_path = 'fonts/PerfectDOS.ttf'


    # Count words
    word_list = body_text.split()
    word_count = len(word_list)
    if word_count < 20:
        body_size = 22
        max_body_width = 18
    else:
        body_size = 18
        max_body_width = 20

    # Initialize TextRenderer
    renderer = TextRenderer(epd.height, epd.width)
    renderer.init_image()
    # Load font
    body_font = renderer.load_font(body_font_path, body_size)

    # Render and draw body text
    body_lines = renderer.render_text(body_text, body_font, max_body_width)
    body_height = sum(renderer.draw.textsize(line, font=body_font)[1] for line in body_lines)
    body_y = (epd.height - body_height) // 8  # Center vertically
    renderer.draw_text(body_lines, body_font, 0, body_y)

    # Display the image on the e-Paper display
    epd.display(epd.getbuffer(renderer.get_image()))


def render_body_page(epd, body_text):
    # Text rendering parameters
    body_font_path = 'fonts/PerfectDOS.ttf'
    body_size = 17


    # Initialize TextRenderer
    renderer = TextRenderer(epd.height, epd.width)
    renderer.init_image()
    max_body_width = calculate_max_body_width(renderer, body_font_path, body_size, epd.width)
    # Load font
    body_font = renderer.load_font(body_font_path, body_size)

    # Render and draw body text
    body_lines = renderer.render_text(body_text, body_font, max_body_width)
    y = 0  # Start rendering from the top-left corner
    for line in body_lines:
        renderer.draw.text((0, y), line, font=body_font, fill=0)
        y += renderer.draw.textsize(line, font=body_font)[1]  # Move to the next line

    # Display the image on the e-Paper display
    epd.display(epd.getbuffer(renderer.get_image()))