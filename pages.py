# pages.py
from text_renderer import TextRenderer

def render_title_page(epd, header_text, body_text):
    # Text rendering parameters
    header_font_path = 'fonts/OldLondon.ttf'
    body_font_path = 'fonts/PixelifySans.ttf'
    header_size = 50
    body_size = 20
    max_body_width = 25

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

def render_body_page(epd, body_text):
    # Text rendering parameters
    body_font_path = 'fonts/PixelifySans.ttf'
    body_size = 16
    max_body_width = 34

    # Initialize TextRenderer
    renderer = TextRenderer(epd.height, epd.width)
    renderer.init_image()

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