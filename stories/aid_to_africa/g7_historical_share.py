import pandas as pd

from oda_data import ODAData, set_data_path
from stories.config import Paths, logger

# Set path to store the raw oda data
set_data_path(Paths.raw_data)


def get_total_flows(start_year: int = 1960, end_year: int = 2023) -> pd.DataFrame:
    """Get the total net ODA flows to Africa and Developing countries from the G7 countries."""

    # Oda object
    oda = ODAData(years=range(start_year, end_year), include_names=True)

    # Load the indicator
    oda.load_indicator("recipient_total_flow_net")

    # Get the data
    return oda.get_data()


def filter_africa_total(df: pd.DataFrame) -> pd.DataFrame:
    return df.query("recipient_code.isin([10100])")


def filter_dev_countries(df: pd.DataFrame) -> pd.DataFrame:
    return df.query("recipient_code.isin([10001])")


def filter_g7_countries(df: pd.DataFrame) -> pd.DataFrame:
    return df.query("donor_code == 20003")


def filter_dac_countries(df: pd.DataFrame) -> pd.DataFrame:
    return df.query("donor_code == 20001")


def share_to_africa(g7_only: bool = True) -> pd.DataFrame:
    """Get the share of ODA to Africa from the total ODA to developing countries."""

    # Get indicator data
    df = get_total_flows()

    if g7_only:
        df = df.pipe(filter_g7_countries)
    else:
        df = df.pipe(filter_dac_countries)

    africa = df.pipe(filter_africa_total)
    dev_countries = df.pipe(filter_dev_countries)

    df = pd.concat([africa, dev_countries], ignore_index=True).filter(
        ["year", "donor_name", "recipient_name", "value"]
    )

    df = df.pivot(
        index=["year", "donor_name"], columns="recipient_name", values="value"
    ).reset_index()

    df["share"] = round(100 * df["Africa"] / df["Developing countries"], 2)

    return df


if __name__ == "__main__":
    share = share_to_africa()
