import pandas as pd
from oda_data import set_data_path, ODAData
from oda_reader import download_dac1
from pydeflate import set_pydeflate_path, deflate

from stories import config
from stories.eu27_targets.common import EU27, EU28

CURRENCY = "USD"

set_data_path(config.Paths.raw_data)
set_pydeflate_path(config.Paths.raw_data)


def to_constant_eur(data: pd.DataFrame, year: int, column: str) -> pd.DataFrame:
    return deflate(
        df=data,
        base_year=year,
        source_currency="USA" if CURRENCY == "USD" else "EUI",
        target_currency="EUI",
        date_column="year",
        deflator_source="oecd_dac",
        deflator_method="dac_deflator",
        exchange_source="oecd_dac",
        exchange_method="implied",
        source_column=column,
        target_column=column,
        id_column="donor_code",
        id_type="DAC",
    )


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


def total_eux(x: list = EU27, start_year: int = 2022) -> pd.DataFrame:
    total = (
        get_total_oda(start_year=start_year)
        .rename(columns={"total_oda_official_definition": "value"})
        .groupby(["year"], observed=True, dropna=False)[["value"]]
        .sum(numeric_only=True)
        .reset_index()
    )

    to_eu = (
        download_eu_x_eui(x, start_year=start_year)
        .groupby(["year"], observed=True, dropna=False)[["value"]]
        .sum(numeric_only=True)
        .reset_index()
    )

    data = pd.merge(total, to_eu, on="year", how="left", suffixes=("", "_eu"))

    data["total"] = data["value"] - data["value_eu"]

    return data.filter(["year", "total"])


def eui_period_share(period: str = "previous") -> float:

    if period == "previous":
        years = range(2014, 2020)
        donors = EU28
    else:
        years = range(2020, 2023)
        donors = EU27

    spending = total_eux(donors, start_year=min(years)).loc[
        lambda d: d.year.isin(years)
    ]
    spending_eui = get_total_oda(start_year=min(years), end_year=max(years)).loc[
        lambda d: d.donor_code.isin([20918, 918])
    ]

    share = pd.merge(spending, spending_eui, on="year", how="left")

    share = (
        share.assign(donor="EU28").groupby("donor").sum(numeric_only=True).reset_index()
    )

    share["share"] = 100 * share["total_oda_official_definition"] / share["total"]

    return round(share.share.sum(), 1)


def eu_own_resources_constant_eur() -> pd.DataFrame:
    spending_eui = (
        get_total_oda(start_year=2014, end_year=2022)
        .loc[lambda d: d.donor_code.isin([20918, 918])]
        .pipe(to_constant_eur, 2022, "total_oda_official_definition")
    )

    contributions_to_eui = download_eu_x_eui(EU27, start_year=2014).pipe(
        to_constant_eur, 2022, "value"
    )

    contributions_to_eui = (
        contributions_to_eui.groupby("year")["value"].sum().reset_index()
    )

    data = pd.merge(spending_eui, contributions_to_eui, on="year", how="left")

    data["own_resources"] = data["total_oda_official_definition"] - data["value"]

    data["own_resources_share"] = (
        100 * data["own_resources"] / data["total_oda_official_definition"]
    )

    print(data.query("year.between(2020,2023)").own_resources.mean())

    return data


def eui_mff_shares() -> tuple[float, float]:

    previous = eui_period_share("previous")
    current = eui_period_share("current")

    return previous, current


if __name__ == "__main__":
    ...
    # data27 = download_eu_x_eui(EU27, start_year=2020)
    # data28 = download_eu_x_eui(EU28, start_year=2014).loc[lambda d: d.year <= 2019]
    # total_eu = total_eux(start_year=2022)

    own = eu_own_resources_constant_eur()
