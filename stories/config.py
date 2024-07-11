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
    aid_to_africa = scripts / "aid_to_africa"
    aid_to_africa_output = output / "aid_to_africa"
    eu27_oda_project = scripts / "eu27_targets"
    eu_project_data = eu27_oda_project / "EU ODA" / "docs" / "data"
