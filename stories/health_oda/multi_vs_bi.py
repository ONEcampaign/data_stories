import pandas as pd

from stories import config
from stories.health_oda.get_oda import get_bilateral_health_oda
from stories.health_oda.trends import group_by_grouper
from oda_data import donor_groupings


def map_donor_type(df: pd.DataFrame) -> pd.DataFrame:
    bilateral = donor_groupings()["all_bilateral"] | {26: "Monaco"}
    multilateral = donor_groupings()["multilateral"] | {
        910: "Central American Bank for Economic Integration",
        1047: "COVID-19 Response and Recovery Multi-Partner Trust Fund",
        1048: "Joint Sustainable Development Goals Fund",
        1050: "WHO-Strategic Preparedness and Response Plan",
        1052: "International Centre for Genetic Engineering and Biotechnology",
    }

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


if __name__ == "__main__":
    split = health_split(1990, 2022, prices="current", base_year=None)
    split.to_csv(config.Paths.health_oda / "bilat_vs_multilat.csv", index=False)
