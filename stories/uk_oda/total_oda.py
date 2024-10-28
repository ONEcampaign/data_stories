import pandas as pd
from oda_data import set_data_path, ODAData

from stories import config

set_data_path(config.Paths.raw_data)

g7_donors = [
    4,  # France
    5,  # Germany
    6,  # Italy
    12,  # United Kingdom
    301,  # Canada
    302,  # United States
    701,  # Japan
]


def get_official_oda(start_year: int, end_year: int, donors: list):
    """"""
    oda = ODAData(
        donors=donors,
        years=range(start_year, end_year + 1),
        currency="GBP",
        prices="constant",
        base_year=2023,
        include_names=True,
    )

    oda.load_indicator("total_oda_official_definition")

    return oda.get_data()


def get_oda_gni(start_year: int, end_year: int, donors: list):
    """"""
    oda = ODAData(
        donors=donors, years=range(start_year, end_year + 1), include_names=True
    )

    oda.load_indicator(["oda_gni_flow", "oda_gni_ge"])

    flow = oda.get_data("oda_gni_flow").loc[lambda d: d.year < 2018]
    ge = oda.get_data("oda_gni_ge").loc[lambda d: d.year >= 2018]

    data = pd.concat([flow, ge], ignore_index=False)

    return data


if __name__ == "__main__":
    amounts = get_official_oda(1992, 2023, g7_donors)
    ratios = get_oda_gni(1992, 2023, g7_donors)
    ratios = (
        ratios.filter(["year", "donor_name", "value"])
        .pivot(index="year", columns="donor_name", values="value")
        .reset_index()
    )
