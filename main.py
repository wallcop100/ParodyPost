# main.py
import logging
import pages
from waveshare_epd import epd2in7_V2
import time

# Set up logging
logging.basicConfig(level=logging.DEBUG)

def main():
    try:
        logging.info("epd2in7 Demo")
        epd = epd2in7_V2.EPD()

        # Initialize and clear the display
        logging.info("init and Clear")
        epd.init()
        epd.Clear()

        # Text for title and body
        title_text = 'Parody Post'
        headline_1_text = 'Lib Dems Guarantee Free Unicorn Rides and Magic Healthcare in Election Manifesto'
        article_1_text = "In a shocking turn of events, the Liberal Democrats have promised voters the impossible in their latest manifesto. Alongside pledges on NHS and social care, the party has promised free unicorn rides and healthcare powered by magic. Critics call it a 'fairytale' of an election promise."

        # Render and display the page
        #pages.render_body_page(epd, article_1_text)
        pages.render_title_page(epd, title_text, headline_1_text)

        # Keep the display on for a while before clearing and going to sleep
        time.sleep(5)

        # Put the display to sleep
        logging.info("Goto Sleep...")
        epd.sleep()

    except IOError as e:
        logging.info(e)

    except KeyboardInterrupt:
        logging.info("ctrl + c:")
        epd2in7_V2.epdconfig.module_exit(cleanup=True)
        exit()

if __name__ == "__main__":
    main()
