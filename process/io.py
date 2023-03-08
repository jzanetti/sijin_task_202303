from pandas import DataFrame
from pandas import to_datetime
from process import DATA_SRC
from os.path import join, basename
from logging import getLogger
from pandas import read_csv
from urllib.error import HTTPError
from datetime import datetime

logger = getLogger()


def export_csv(workdir: str, data: DataFrame, filename: str = "top_locations.csv"):
    """Export data to CSV

    Args:
        data (DataFrame): data to be written
    """
    data.to_csv(join(workdir, filename), index=False)


def data_filter(
    data: DataFrame,
    args: dict) -> DataFrame:
    """Exclude unwanted data

    Args:
        data (DataFrame): data to be processed
        args (dict): contains the filters such as 
            regions, start and end

    Returns:
        list: filterd data
    """
    if args["regions"] is not None:
        data = data[data["Region"].isin(args["regions"])]
    
    if args["start"] is not None:
        data = data[data["week_end_date"] >= args["start"]]

    if args["end"] is not None:
        data = data[data["end"] <= args["end"]]

    return data


def obtain_latest_data(
        data_name: str = "cases", 
        data_type: str = "regional") -> DataFrame:
    """Download the latest data from a pre-defined data source

    Args:
        workdir (str): working directory
        data_name (str, optional): data to be downloaded. Defaults to "ww".
        data_type (str, optional): whether it's a regional or national data

    Returns:
        DataFrame: the decoded data
    """
    data_path_remote = DATA_SRC.format(data_name=data_name, data_type=data_type)
    try:
        data =  read_csv(data_path_remote)
        data['week_end_date'] = to_datetime(data['week_end_date'])
        return data
    except HTTPError:
        logger.error(f"Not able to get the requested data from {data_path_remote}: {err}")
    


