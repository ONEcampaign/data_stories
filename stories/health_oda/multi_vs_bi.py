import pandas as pd

from stories import config
from stories.health_oda.get_oda import get_bilateral_health_oda
from stories.health_oda.trends import group_by_grouper
from oda_data import donor_groupings


def multi_donors() -> dict:
    return donor_groupings()["multilateral"] | {
        910: "Central American Bank for Economic Integration",
        1047: "COVID-19 Response and Recovery Multi-Partner Trust Fund",
        1048: "Joint Sustainable Development Goals Fund",
        1050: "WHO-Strategic Preparedness and Response Plan",
        1052: "International Centre for Genetic Engineering and Biotechnology",
    }


def bilat_donors() -> dict:
    return donor_groupings()["all_bilateral"] | {26: "Monaco"}


def map_donor_type(df: pd.DataFrame) -> pd.DataFrame:
    bilateral = bilat_donors()
    multilateral = multi_donors()

    bilateral = {k: "Bilateral donors" for k in bilateral}
    multilateral = {k: "Multilateral donors" for k in multilateral}

    all_donors = bilateral | multilateral

    df["donor_type"] = df.donor_code.map(all_donors)

    return df


def health_split(
    start_year: int = 1990,
    end_year: int = 2023,
    prices: str = "constant",
    base_year: int | None = 2022,
) -> pd.DataFrame:

    # Define the grouper
    grouper = ["year", "donor_type"]

    # Get the data for health
    health = get_bilateral_health_oda(
        start_year=start_year, end_year=end_year, prices=prices, base_year=base_year
    )

    health = health.pipe(map_donor_type).pipe(group_by_grouper, grouper=grouper)

    # calculate share by donor type
    health["value"] = health.groupby("year")["value"].transform(
        lambda x: round(100 * x / x.sum(), 1)
    )

    health = health.pivot(
        index=["year"], columns="donor_type", values="value"
    ).reset_index()

    return health


def top_x_providers(
    start_year: int = 1990,
    end_year: int = 2023,
    donor_type: str = "Bilateral donors",
    top_x: int = 5,
    rolling_years: int = 3,
    prices: str = "constant",
    base_year: int | None = 2022,
) -> pd.DataFrame:

    # Define the grouper
    grouper = ["year", "donor_code", "donor_type"]

    # Get the data for health
    health = (
        get_bilateral_health_oda(
            start_year=start_year, end_year=end_year, prices=prices, base_year=base_year
        )
        .pipe(map_donor_type)
        .pipe(group_by_grouper, grouper=grouper)
        .loc[lambda d: d.donor_type == donor_type]
    )

    # calculate the rolling average
    health["value"] = health.groupby("donor_code", dropna=False, observed=True)[
        "value"
    ].transform(
        lambda x: x.rolling(rolling_years, min_periods=rolling_years - 1).mean()
    )

    # add donor share of total
    health["share"] = health.groupby("year")["value"].transform(
        lambda x: round(100 * x / x.sum(), 1)
    )

    health["donor_name"] = health.donor_code.map(multi_donors() | bilat_donors())

    # get the top x donors for each year
    health_top = (
        health.sort_values(["year", "value"], ascending=[True, False])
        .groupby("year")
        .head(top_x)
        .filter(["year", "donor_name", "value", "share"])
    )

    values = (
        health_top.pivot(
            index=["year"],
            columns="donor_name",
            values="value",
        )
        .reset_index()
        .assign(indicator="value")
    )

    shares = (
        health_top.pivot(
            index=["year"],
            columns="donor_name",
            values="share",
        )
        .reset_index()
        .assign(indicator="share")
    )

    data = pd.concat([values, shares], ignore_index=True)

    return data


if __name__ == "__main__":
    split = health_split(1990, 2022, prices="current", base_year=None)
    split.to_csv(config.Paths.health_oda / "bilat_vs_multilat.csv", index=False)

    top5_multi = top_x_providers(
        2008,
        2022,
        donor_type="Multilateral donors",
        top_x=5,
        rolling_years=3,
        prices="constant",
        base_year=2022,
    ).loc[lambda d: d.year >= 2010]

    top5_multi.to_csv(config.Paths.health_oda / "top5_multi.csv", index=False)
