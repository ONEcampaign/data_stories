import pandas as pd
from bblocks import add_short_names_column

from stories.config import Paths
from stories.eu27_targets.eui_share import eu_own_resources_constant_eur
from stories.eu27_targets.oda import add_target_column
from stories.eu27_targets.oda_projections import eu_spending_projections


def load_and_prepare_data(
    start_year: int, end_year: int, base_year: int
) -> pd.DataFrame:
    """Loads EU spending projections and prepares the data with targets and ODA/GNI ratio.

    Returns:
        pd.DataFrame: DataFrame containing prepared data.
    """
    df = eu_spending_projections(
        start_year=start_year,
        end_year=end_year,
        base_year=base_year,
        include_historical=True,
        exclude_idrc=False,
        exclude_ukraine=False,
    ).pipe(add_target_column)

    # Transform the target from percentage to absolute value
    df["target"] *= df["gni"]

    # Transform the ratio to percentage
    df["oda_gni_ratio"] *= 100
    return df


def add_member_state_names(df: pd.DataFrame) -> pd.DataFrame:
    """Adds member state short names to the DataFrame.

    Args:
        df (pd.DataFrame): DataFrame with donor codes.

    Returns:
        pd.DataFrame: DataFrame with member state names added.
    """
    return add_short_names_column(
        df=df, id_column="donor_code", id_type="DACCode", target_column="Member State"
    )


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Renames columns to human-readable names.

    Args:
        df (pd.DataFrame): DataFrame to rename columns for.

    Returns:
        pd.DataFrame: DataFrame with renamed columns.
    """
    return df.rename(
        columns={
            "year": "Year",
            "oda_gni_ratio": "ODA/GNI ratio",
            "oda": "ODA",
            "target": "Target",
        }
    )


def filter_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Filters columns to keep only the required ones.

    Args:
        df (pd.DataFrame): DataFrame to filter.

    Returns:
        pd.DataFrame: Filtered DataFrame.
    """
    return df.filter(["Year", "Member State", "ODA/GNI ratio", "ODA", "Target", "gni"])


def calculate_eu_totals(df: pd.DataFrame) -> pd.DataFrame:
    """Calculates EU27 totals for ODA and GNI and appends them to the DataFrame.

    Args:
        df (pd.DataFrame): Original DataFrame with individual country data.

    Returns:
        pd.DataFrame: DataFrame with EU27 totals appended.
    """
    eu_totals = df.groupby("Year")[["ODA", "Target", "gni"]].sum().reset_index()
    eu_totals["Member State"] = "EU27 Countries"
    eu_totals["ODA/GNI ratio"] = 100 * eu_totals["ODA"] / eu_totals["gni"]

    return pd.concat([eu_totals, df], ignore_index=True).drop(columns=["gni"])


def clean_data_for_viz(df: pd.DataFrame) -> pd.DataFrame:
    """Rounds and calculates the missing target column, finalizing the DataFrame.

    Args:
        df (pd.DataFrame): DataFrame to finalize.

    Returns:
        pd.DataFrame: Finalized DataFrame.
    """
    df["ODA/GNI ratio"] = df["ODA/GNI ratio"].round(2)
    df["ODA"] = df["ODA"].round(0)
    df["Missing to target"] = (df["Target"] - df["ODA"]).clip(0).round(0)

    return df.drop(columns=["Target"])


def main_column_chart_with_projections(
    start_year: int = 2014, end_year: int = 2023, base_year: int = 2025
) -> pd.DataFrame:
    """Main processing function for ODA data.

    Returns:
        pd.DataFrame: Final DataFrame ready for output.
    """
    data = (
        load_and_prepare_data(
            start_year=start_year, end_year=end_year, base_year=base_year
        )
        .pipe(add_member_state_names)
        .pipe(rename_columns)
        .pipe(filter_columns)
        .sort_values(["Member State", "Year"])
        .pipe(calculate_eu_totals)
        .pipe(clean_data_for_viz)
    )

    return data


def eui_spending_chart(members: pd.DataFrame) -> pd.DataFrame:

    members = members.query("`Member State` == 'EU27 Countries'")

    data = eu_own_resources_constant_eur().filter(
        [
            "year",
            "total_oda_official_definition",
            "own_resources",
            "value_eu",
        ]
    )

    data = data.merge(members, left_on="year", right_on="Year", how="left")
    data["Member States"] = data["ODA"] - data["value_eu"]

    data = data.filter(["year", "Member States", "own_resources", "value_eu"])

    data = data.rename(
        columns={
            "own_resources": "Non-imputable EU Institutions ODA",
            "value_eu": "Imputable EU Institutions ODA",
        }
    )

    return data


if __name__ == "__main__":
    df = main_column_chart_with_projections()
    df.to_csv(Paths.eu_project_data / "eu27_column_chart_2014_2034.csv", index=False)

    df.to_clipboard(index=False)

    eu = eui_spending_chart(df)
    eu.to_clipboard(index=False)
