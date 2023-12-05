"""A command-line utility to download podcast episodes from an XML feed.

Functions:
    - main(xml, output_folder)

Usage:
    To use this module as a command-line tool, run the script with the
    following command:

    $ python podcast_downloader.py [XML_FILE] [OUTPUT_FOLDER]

Arguments:
---------
        - XML_FILE: The URL or local path to the XML feed containing podcast
              episodes.
        - OUTPUT_FOLDER: The local directory where downloaded podcast episodes
              will be saved.

"""
import pathlib
import time
import io

import click
import feedparser
import requests
from slugify import slugify
from tqdm import tqdm
import pydub


@click.command()
@click.argument("xml")
@click.argument(
    "output_folder",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
)
def main(xml: str, output_folder: str) -> None:
    """Parse the XML feed and save files to the output folder.

    Args:
    ----
        xml (str): The URL or local path to the XML feed containing podcast
              episodes.
        output_folder (str): The local directory where downloaded podcast
              episodes will be saved.

    Returns:
    -------
        - None

    Description:
        This is the main function that parses the podcast feed specified by the
        'xml' argument, downloads the audio files, and saves them to the
        specified 'output_folder'. It uses the click library for command-line
        interface handling and tqdm for progress bar display.

    """
    feed = feedparser.parse(xml)
    for entry in tqdm(feed.entries):
        title = entry["title"]
        datetime = entry["published_parsed"]
        slug = slugify(title)
        link = [x["href"] for x in entry["links"] if "audio" in x["type"]].pop()
        extension = pathlib.Path(link).suffix.lstrip(".")
        output_filename = (
            pathlib.Path(output_folder)
            / f"{time.strftime('%Y-%m-%d', datetime)}-{slug}.mp3"
        )
        if output_filename.exists():
            continue
        request = requests.get(link, timeout=30)
        audio_data = io.BytesIO(request.content)
        audio_data.seek(0)
        audio_segment = pydub.AudioSegment.from_file(audio_data, format=extension)
        audio_segment = audio_segment.set_channels(1)
        audio_segment.export(output_filename, format="mp3", bitrate="92k")


if __name__ == "__main__":
    main()
