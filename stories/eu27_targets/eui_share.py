import pandas as pd
from oda_data import set_data_path, ODAData
from oda_reader import download_dac1
from pydeflate import set_pydeflate_path

from stories import config
from stories.eu27_targets.common import EU27, EU28

CURRENCY = "USD"

set_data_path(config.Paths.raw_data)
set_pydeflate_path(config.Paths.raw_data)


def get_total_oda(start_year: int = 2022, end_year: int = 2023) -> pd.DataFrame:

    oda = ODAData(
        years=range(start_year, end_year + 1),
        donors=EU27 + [20918, 918],
        currency=CURRENCY,
    )

    oda.load_indicator(["total_oda_official_definition"])

    df = (
        oda.get_data()
        .pivot(index=["year", "donor_code"], columns="indicator", values="value")
        .reset_index()
    )

    return df


def download_eu_x_eui(x: list = EU27, start_year: int = 2022) -> pd.DataFrame:
    filters = {
        "flow_type": "1120",
        "measure": "2102",
        "price_base": "V",
        "unit_measure": "USD",
    }
    df = download_dac1(start_year=start_year, filters=filters)

    df = df.loc[lambda d: d.donor_code.isin(x)]

    return df


if __name__ == "__main__":
    # data27 = download_eu_x_eui(EU27, start_year=2020)
    # data28 = download_eu_x_eui(EU28, start_year=2014).loc[lambda d: d.year <= 2019]
    total = get_total_oda(start_year=2022)
