import pandas as pd
from bblocks import add_short_names_column, convert_id
from pydeflate import set_pydeflate_path

from stories.config import Paths
from stories.eu27_targets.growth import (
    get_current_deflators,
    extend_deflators_to_year,
    get_gdp_growth_factor,
)
from stories.eu27_targets.oda import (
    get_total_oda_and_gni,
    calculate_oda_gni_ratio,
    add_target_oda,
    add_target_column,
    get_total_oda_data,
)
from stories.eu27_targets.tools import to_constant

MAX_DATA_YEAR: int = 2023
set_pydeflate_path(Paths.raw_data)


def get_gni_projections(
    oda_df: pd.DataFrame | None = None,
    last_year: int = 2034,
    prices: str = "current",
    base_year: int | None = None,
    rolling_window: int = 3,
) -> pd.DataFrame:

    if oda_df is None:
        oda_df = (
            get_total_oda_and_gni([2023])
            .filter(["year", "donor_code", "gni"])
            .dropna(subset=["gni"])
        )

    if prices == "current":
        deflators = get_current_deflators(base=oda_df.year.max())

    else:
        deflators = get_gdp_growth_factor(from_year=oda_df.year.max())

    deflators = deflators.pipe(
        extend_deflators_to_year, last_year, rolling_window=rolling_window
    ).loc[lambda d: d.year > oda_df.year.max()]

    gni_projection = oda_df.drop(columns="year").merge(
        deflators, left_on="donor_code", right_on="dac_code", how="right"
    )

    gni_projection["gni"] = gni_projection["gni"].astype(float)
    gni_projection["value"] = gni_projection["value"].astype(float)

    gni_projection["gni"] = gni_projection["gni"] * gni_projection["value"]

    return gni_projection.filter(["year", "donor_code", "gni"])


def projected_gni_to_spending(
    gni: pd.DataFrame, individual_targets: bool = True
) -> pd.DataFrame:
    """"""
    if individual_targets:
        gni = add_target_oda(gni)

    return gni


def _interpolate_gni_projections(
    df: pd.DataFrame,
    start_year: int,
    projections_end_year: int,
):
    # for every donor, linearly interpolate any oda_gni_ratio that is missing
    years = pd.DataFrame({"year": range(start_year, projections_end_year + 1)})

    interpolated_data = []

    for donor in df.donor_code.unique():
        donor_data = df.loc[lambda d: d.donor_code == donor].copy()
        donor_data = donor_data.merge(years, on="year", how="right").fillna(
            {"donor_code": donor}
        )
        donor_data = donor_data.sort_values("year").interpolate(method="linear")

        donor_data = donor_data.astype({"donor_code": "Int32"})

        interpolated_data.append(donor_data)

    return pd.concat(interpolated_data, ignore_index=True)


def _get_gni_targets_from_target_year(
    oda_df: pd.DataFrame, target_year: int, projections_end_year: int
):
    # latest data
    latest = oda_df.loc[oda_df.year == MAX_DATA_YEAR].copy()

    at_target = latest.loc[lambda d: d.oda_gni_ratio >= d.target]
    below_target = latest.loc[lambda d: d.oda_gni_ratio < d.target]

    dfs = []

    dfs.append(at_target.assign(year=target_year))
    dfs.append(below_target.assign(year=target_year, oda_gni_ratio=lambda d: d.target))

    df = pd.concat([oda_df, *dfs], ignore_index=True).filter(
        ["year", "donor_code", "oda_gni_ratio"]
    )

    return df


def individual_gni_targets(
    start_year: int = 2018,
    target_year: int = 2030,
    projections_end_year: int = 2034,
    include_idrc: bool = True,
    include_ukraine: bool = True,
    use_2022_ukraine: bool | None = None,
):
    years = list(range(start_year, MAX_DATA_YEAR + 1))
    # Get spending data
    oda_df = get_total_oda_data(
        years=years,
        include_idrc=include_idrc,
        include_ukraine=include_ukraine,
        use_2022_ukraine=use_2022_ukraine,
    ).loc[lambda d: d.donor_code != 918]

    # Add ODA/GNI
    oda_df = calculate_oda_gni_ratio(oda_df)

    # Add targets
    oda_df = add_target_column(oda_df)

    # Get GNI targets
    df = _get_gni_targets_from_target_year(
        oda_df, target_year=target_year, projections_end_year=projections_end_year
    )

    return _interpolate_gni_projections(df, start_year, projections_end_year)


def individual_spending(
    start_year: int = 2018,
    include_idrc: bool = True,
    include_ukraine: bool = True,
    use_2022_ukraine: bool = None,
    currency: str = "EUR",
) -> pd.DataFrame:
    years = list(range(start_year, MAX_DATA_YEAR + 1))
    # Get spending data
    oda_df = get_total_oda_data(
        years=years,
        currency=currency,
        include_idrc=include_idrc,
        include_ukraine=include_ukraine,
        use_2022_ukraine=use_2022_ukraine,
    ).loc[lambda d: d.donor_code != 918]

    # Add ODA/GNI
    oda_df = calculate_oda_gni_ratio(oda_df)

    return oda_df


def spending_versions(
    start_year: int = 2018,
    prices: str = "current",
    base_year: int | None = None,
) -> pd.DataFrame:
    full = individual_spending(
        start_year=start_year,
    ).assign(indicator="Using latest official data")

    no_ukr = individual_spending(
        start_year=start_year,
        include_ukraine=False,
    ).assign(indicator="Excluding Ukraine")

    no_idrc = individual_spending(
        start_year=start_year,
        include_idrc=False,
    ).assign(indicator="Excluding IDRC")

    no_ukr_no_idrc = individual_spending(
        start_year=start_year,
        include_idrc=False,
        include_ukraine=False,
    ).assign(indicator="Excluding Ukraine and IDRC")

    df = pd.concat([full, no_ukr, no_idrc, no_ukr_no_idrc], ignore_index=True)

    if prices == "constant":
        return to_constant(df, base_year=base_year)
    else:
        df = df.assign(prices="current")

    return df


def target_versions(
    start_year: int = 2018,
    target_year: int = 2030,
    projections_end_year: int = 2034,
    use_2022_ukraine: bool = False,
    to_flourish: bool = True,
):
    full = individual_gni_targets(
        start_year=start_year,
        target_year=target_year,
        projections_end_year=projections_end_year,
    ).assign(indicator="Using latest official data")

    no_ukr = individual_gni_targets(
        start_year=start_year,
        target_year=target_year,
        projections_end_year=projections_end_year,
        include_ukraine=False,
        use_2022_ukraine=use_2022_ukraine,
    ).assign(indicator="Excluding Ukraine")

    no_idrc = individual_gni_targets(
        start_year=start_year,
        target_year=target_year,
        projections_end_year=projections_end_year,
        include_idrc=False,
    ).assign(indicator="Excluding IDRC")

    no_ukr_no_idrc = individual_gni_targets(
        start_year=start_year,
        target_year=target_year,
        projections_end_year=projections_end_year,
        use_2022_ukraine=use_2022_ukraine,
        include_idrc=False,
        include_ukraine=False,
    ).assign(indicator="Excluding Ukraine and IDRC")

    df = pd.concat([full, no_ukr, no_idrc, no_ukr_no_idrc], ignore_index=True)

    df = add_short_names_column(df=df, id_column="donor_code", id_type="DACCode").drop(
        columns=["donor_code"]
    )

    file_name = f"individual_gni_targets_{start_year}_{projections_end_year}_target_{target_year}"

    if to_flourish:
        file_name = file_name + "_flourish"
        df = df.pivot(
            index=[c for c in df.columns if c not in ["name_short", "oda_gni_ratio"]],
            columns="name_short",
            values="oda_gni_ratio",
        ).reset_index()
        df["order"] = df.indicator.map(
            {
                "Using latest official data": 1,
                "Excluding Ukraine": 2,
                "Excluding IDRC": 3,
                "Excluding Ukraine and IDRC": 4,
            }
        )
        df = df.sort_values(["year", "order"]).drop(columns="order")

    df.to_csv(Paths.eu_project_data / f"{file_name}.csv", index=False)

    return df


def eu_spending_projections(
    start_year: int = 2014,
    end_year: int = 2030,
    base_year: int = 2025,
    include_historical: bool = True,
    exclude_ukraine: bool = False,
    exclude_idrc: bool = False,
) -> pd.DataFrame:
    """"""

    suffix = "_excl_ukr" if exclude_ukraine else ""
    suffix += "_excl_idrc" if exclude_idrc else ""

    targets = individual_gni_targets(
        start_year=start_year,
        projections_end_year=2034,
        use_2022_ukraine=True,
        include_idrc=not exclude_idrc,
        include_ukraine=not exclude_ukraine,
    ).assign(indicator=f"2023{suffix}")

    if include_historical:
        historical_constant = individual_spending(
            start_year=start_year,
            include_idrc=not exclude_idrc,
            include_ukraine=not exclude_ukraine,
            use_2022_ukraine=None if exclude_ukraine else True,
        ).pipe(to_constant, base_year=base_year)

    else:
        historical_constant = pd.DataFrame()
        targets = targets.loc[lambda d: d.year >= 2024]

    constant_projections = get_gni_projections(
        oda_df=historical_constant.loc[lambda d: d.year == d.year.max()]
        .filter(["year", "donor_code", "gni"])
        .dropna(subset=["gni"]),
        last_year=2034,
        prices="constant",
        base_year=base_year,
        rolling_window=3,
    ).assign(prices="constant", base_year=base_year)

    constant_spending = pd.concat(
        [historical_constant, constant_projections], ignore_index=True
    )

    constant_data = targets.merge(
        constant_spending,
        on=["year", "donor_code"],
        how="left",
        suffixes=("", "_h"),
    )
    constant_data = constant_data.assign(oda=lambda d: d.oda_gni_ratio * d.gni)

    return constant_data.filter(
        [
            "year",
            "donor_code",
            "name_short",
            "oda_gni_ratio",
            "gni",
            "indicator",
            "oda",
            "prices",
        ]
    )


def spending_targets_by_country(
    start_year: int = 2018,
    target_year: int = 2030,
    projections_end_year: int = 2034,
    exclude_2022_ukraine: bool = True,
) -> pd.DataFrame:

    target_versions(
        start_year=start_year,
        target_year=target_year,
        projections_end_year=projections_end_year,
        use_2022_ukraine=exclude_2022_ukraine,
        to_flourish=True,
    )

    df = target_versions(
        start_year=start_year,
        target_year=target_year,
        projections_end_year=projections_end_year,
        use_2022_ukraine=exclude_2022_ukraine,
        to_flourish=False,
    ).assign(
        donor_code=lambda d: convert_id(
            d["name_short"], from_type="regex", to_type="DACCode"
        )
    )

    historical_current = spending_versions(start_year=start_year, prices="current")

    historical_constant = spending_versions(
        start_year=start_year, prices="constant", base_year=2025
    )

    current_projections = get_gni_projections(
        last_year=projections_end_year, prices="current", rolling_window=3
    ).assign(prices="current")

    constant_projections = get_gni_projections(
        last_year=projections_end_year,
        prices="constant",
        base_year=2025,
        rolling_window=3,
    ).assign(prices="constant", base_year=2025)

    currentp = []
    constantp = []

    for indicator in historical_current.indicator.unique():
        currentp.append(current_projections.assign(indicator=indicator))

    current_projections = pd.concat(currentp, ignore_index=True)

    for indicator in historical_constant.indicator.unique():
        constantp.append(constant_projections.assign(indicator=indicator))

    constant_projections = pd.concat(constantp, ignore_index=True)

    current_df = pd.concat(
        [historical_current, current_projections], ignore_index=True
    ).drop(columns="oda_gni_ratio")

    constant_df = pd.concat(
        [historical_constant, constant_projections], ignore_index=True
    ).drop(columns="oda_gni_ratio")

    current_data = (
        df.merge(current_df, on=["year", "indicator", "donor_code"], how="left")
        .assign(oda=lambda d: d.oda_gni_ratio * d.gni)
        .filter(
            [
                "year",
                "donor_code",
                "name_short",
                "oda_gni_ratio",
                "gni",
                "indicator",
                "oda",
                "prices",
            ]
        )
    )
    constant_data = (
        df.merge(
            constant_df,
            on=["year", "indicator", "donor_code"],
            how="left",
            suffixes=("", "_h"),
        )
        .assign(oda=lambda d: d.oda_gni_ratio * d.gni)
        .filter(
            [
                "year",
                "donor_code",
                "name_short",
                "oda_gni_ratio",
                "gni",
                "indicator",
                "oda",
                "prices",
            ]
        )
    )

    data = pd.concat([current_data, constant_data], ignore_index=True)

    total = (
        data.groupby(["year", "indicator", "prices"])[["oda", "gni"]]
        .sum()
        .reset_index()
        .assign(
            oda_gni_ratio=lambda d: d.oda / d.gni,
            name_short="EU27 countries",
            donor_code="91827",
        )
    )

    data = pd.concat([total, data], ignore_index=True)

    flourish_data = (
        data.drop(columns=["gni"])
        .pivot(
            index=[
                c
                for c in data.drop(columns=["gni"]).columns
                if c not in ["oda", "prices"]
            ],
            columns="prices",
            values="oda",
        )
        .reset_index()
    )

    flourish_data.to_csv(
        Paths.eu_project_data / "spending_amounts_by_country_flourish.csv", index=False
    )

    return data


def calculate_spending_period(
    df: pd.DataFrame, method: str, start: int = 2028, end: int = 2034
) -> dict:
    return (
        df.assign(method=method)
        .loc[lambda d: d.year.between(start, end)]
        .groupby(["method"])[["oda"]]
        .sum()
        .round(0)["oda"]
        .astype("Int64")
        .to_dict()
    )


def calculate_eu_spending_period(
    df: pd.DataFrame, method: str, start: int = 2028, end: int = 2034
) -> dict:
    share = 0.231
    return (
        df.assign(method=method)
        .loc[lambda d: d.year.between(start, end)]
        .assign(oda=lambda d: d.oda * share)
        .groupby(["method"])[["oda"]]
        .sum()
        .round(0)["oda"]
        .astype("Int64")
        .to_dict()
    )


def scenarios_eu_totals() -> None:

    key_numbers = {}

    full = eu_spending_projections(include_historical=True).assign(indicator="full")

    full_data = pd.concat(
        [
            full,
            # no_idrc,
            # no_ukr,
            # no_ukr_no_idrc,
        ],
        ignore_index=True,
    )
    latest = full_data.loc[full_data.year == 2023].filter(
        ["donor_code", "indicator", "oda"]
    )

    additional_spending_yearly = (
        full_data.query("year > 2023")
        .merge(
            latest,
            on=["donor_code", "indicator"],
            how="left",
            suffixes=("", "_baseline"),
        )
        .assign(additional_oda=lambda d: d.oda - d.oda_baseline)
        .assign(
            indicator=lambda d: d.indicator.map(
                {
                    "full": "Full",
                    "no_idrc": "Excluding IDRC",
                    "no_ukr": "Excluding Ukraine",
                    "no_ukr_no_idrc": "Excluding Ukraine and IDRC",
                }
            )
        )
        .drop(columns=["oda_baseline", "gni", "prices"])
    )

    additional_spending_yearly = add_short_names_column(
        df=additional_spending_yearly, id_column="donor_code", id_type="DACCode"
    ).drop(columns=["donor_code"])

    additional_spending_yearly["additional_oda"] = additional_spending_yearly[
        "additional_oda"
    ]
    additional_spending_yearly.to_csv(
        Paths.eu_project_data / "additional_spending_yearly.csv", index=False
    )


if __name__ == "__main__":
    scenarios_eu_totals()
