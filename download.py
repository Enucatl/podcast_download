import xml.etree.ElementTree as ET
import click
import pathlib
import re
import requests
from tqdm import tqdm


def get_valid_filename(s):
    # https://stackoverflow.com/a/46801075
    s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)


@click.command()
@click.argument("filename", type=click.Path(exists=True))
@click.argument(
    "output_folder", type=click.Path(exists=True, file_okay=False, dir_okay=True)
)
def main(filename, output_folder):
    tree = ET.parse(filename)
    items = tree.findall(".//item")
    for item in tqdm(items):
        title = get_valid_filename(item.find("title").text)
        url = item.find("enclosure").attrib["url"]
        output_path = pathlib.Path(output_folder) / f"{title}.mp3"
        if output_path.exists():
            continue
        else:
            request = requests.get(url)
            with open(output_path, "wb") as output_file:
                output_file.write(request.content)


if __name__ == "__main__":
    main()
