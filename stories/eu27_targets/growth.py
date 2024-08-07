import pandas as pd
from bblocks import set_bblocks_data_path, WorldEconomicOutlook, convert_id

from oda_data import donor_groupings

from stories import config

eu27 = list(donor_groupings()["eu27_countries"].keys())

set_bblocks_data_path(config.Paths.raw_data)


def filter_eu27(data: pd.DataFrame) -> pd.DataFrame:
    return data.loc[lambda d: d.dac_code.isin(eu27)]


def add_dac_codes(data: pd.DataFrame) -> pd.DataFrame:
    data["dac_code"] = convert_id(
        data["iso_code"],
        "ISO3",
        "DACCode",
        not_found=pd.NA,
    ).astype("Int32")
    return data


def calculate_growth_rate(data: pd.DataFrame) -> pd.DataFrame:
    return data.assign(
        value=lambda d: d.groupby("dac_code")["value"].pct_change()
    ).dropna(subset=["value"])


def rebase_value(data: pd.DataFrame, year: int) -> pd.DataFrame:
    return data.assign(
        value=lambda d: d.groupby("dac_code")["value"].transform(
            lambda x: x / x.loc[d.year.dt.year == year].sum()
        )
    )


def calculate_deflator(data: pd.DataFrame) -> pd.DataFrame:
    return data.assign(
        value=lambda d: d.groupby("dac_code", dropna=False, observed=True)[
            "value"
        ].transform(lambda x: (1 + x).cumprod())
    )


def get_constant_deflators(base: int = 2022):

    weo = WorldEconomicOutlook()

    weo.load_data("NGDP_D")

    df = (
        weo.get_data()
        .pipe(add_dac_codes)
        .pipe(filter_eu27)
        .pipe(rebase_value, year=base)
    )

    return df.filter(["dac_code", "iso_code", "year", "value"])


def get_current_deflators(base: int = 2023):

    weo = WorldEconomicOutlook()

    weo.load_data("NGDP")

    df = (
        weo.get_data()
        .pipe(add_dac_codes)
        .pipe(filter_eu27)
        .pipe(calculate_growth_rate)
        .pipe(calculate_deflator)
        .pipe(rebase_value, year=base)
    )

    return df.filter(["dac_code", "iso_code", "year", "value"])


def extend_deflators_to_year(
    data: pd.DataFrame, last_year: int, rolling_window: int
) -> pd.DataFrame:
    """This function creates rows for each donor for the missing years between the
    max year in the data and the last year specified in the arguments. The value is
    rolling average of the previous 3 years"""

    def fill_with_rolling_average(
        idx, group: pd.DataFrame, rolling_window: int = 3
    ) -> pd.DataFrame:

        # calculate yearly diff
        group["yearly_diff"] = group["value"].diff()

        new_index = pd.Index(
            range(group.year.max() - rolling_window, last_year + 1), name="year"
        )

        new_df = group.set_index("year").reindex(new_index)
        new_df["yearly_diff"] = (
            new_df["yearly_diff"].rolling(window=rolling_window).mean()
        )
        new_df["yearly_diff"] = new_df["yearly_diff"].ffill()
        new_df["value"] = new_df.value.fillna(
            (new_df["value"].shift(1).ffill() + new_df["yearly_diff"].shift(1).cumsum())
        )

        new_df = new_df.drop(columns=["yearly_diff"])
        group = group.drop(columns=["yearly_diff"])

        new_df[["dac_code", "iso_code"]] = idx

        new_df = new_df.loc[lambda d: d.index > group.year.max()]

        group = group
        new_df = new_df.reset_index()

        group = pd.concat([group, new_df], ignore_index=False)
        return group

    data = data.assign(year=lambda d: d.year.dt.year)

    dfs = []

    for group_idx, group_data in data.groupby(
        ["dac_code", "iso_code"], dropna=False, observed=True
    ):
        dfs.append(
            fill_with_rolling_average(
                idx=group_idx, group=group_data, rolling_window=rolling_window
            )
        )

    return pd.concat(dfs, ignore_index=True)


if __name__ == "__main__":

    # current = get_current_deflators(base=2023)
    # current_ext = extend_deflators_to_year(current, 2034, rolling_window=1)
    constant = get_constant_deflators(base=2025)
