from pathlib import Path
import logging

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
logger = logging.getLogger("data_stories")


class Paths:
    """Class to store the paths to the data and output folders."""

    project = Path(__file__).resolve().parent.parent
    raw_data = project / "raw_data"
    output = project / "output"
    scripts = project / "stories"
