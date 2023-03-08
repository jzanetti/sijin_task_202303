from pandas import DataFrame
from numpy import zeros, fft, copy, abs
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime

from logging import getLogger
from sklearn.metrics import mean_squared_error
from tslearn.metrics import dtw

logger = getLogger()

def data_preproc(data: DataFrame, preproc_steps: list or None, preproc_method: str = "MinMaxScaler") -> DataFrame:
    """Apply different perprocessing approaches to the data

    Args:
        data (list): data to be used
        method (str, optional): preprocessing method. Defaults to "MinMaxScaler".

    Raises:
        Exception: method has not been implemented yet

    Returns:
        list: preprocessed data
    """
    def _fft_smooth(data: DataFrame, cutoff_freq: float = 0.5) -> list:
        """Apply FFT smoothing for the data series

        Args:
            data (DataFrame): data to be applied
            cutoff_freq (float, optional): FFT cutoff frequency. Defaults to 0.25.

        Returns:
            list: the list of new data
        """
        fft_data = fft.fft(data)
        freqs = fft.fftfreq(len(data))

        filtered_fft = copy(fft_data)
        filtered_fft[abs(freqs) > cutoff_freq] = 0

        smoothed_data = fft.ifft(filtered_fft).real

        return smoothed_data

    data["data"] = data[["case_7d_avg"]]
    if preproc_steps is None:
        return data

    for proc_step in preproc_steps:
        if proc_step == "norm":
            logger.info("applying the min/max scalling to the data ...")
            if preproc_method == "MinMaxScaler":
                scaler = MinMaxScaler()
                data["data"] = scaler.fit_transform(data[["data"]])
            else:
                raise Exception(f"The preproc method {preproc_method} has not been implemented yet ...")
        elif proc_step == "fft":
            logger.info("applying FFT to the data ...")
            data["data"]  = _fft_smooth(data["data"])

    return data


def rank_comp(comp_results: dict, top_num: int = 5) -> dict:
    """Extract the regions with the highest correlations

    Args:
        calculated_corr (dict): calculated cross-region correlations
        top_num (int, optional): export the five regions with the highest correlations. Defaults to 5.
    """
    if comp_results["method"] == "corr":
        data_to_use = comp_results["index"][comp_results["index"] < 0.99]
        top_values = sorted(data_to_use, reverse=True)[:top_num*3]
    elif comp_results["method"] in ["mse", "dtw"]:
        data_to_use = comp_results["index"][comp_results["index"] > 0.0]
        top_values = sorted(data_to_use, reverse=False)[:len(comp_results["regions"]) + top_num*3]

    top_locations_tmp = [
        (i, j) for i in range(comp_results["index"].shape[0]) for j in range(
        comp_results["index"].shape[1]) if comp_results["index"][i,j] in top_values
        ]

    top_locations = []
    for proc_loc in top_locations_tmp:
        if proc_loc[0] == proc_loc[1]:
            continue

        if proc_loc not in top_locations:
            top_locations.append(proc_loc)
    
        if len(top_locations) >= top_num:
            break
    
    highest_corr_locations = {comp_results["method"]: [], "region1": [], "region2": []}
    for proc_loc in top_locations:
        highest_corr_locations[comp_results["method"]].append(
            comp_results["index"][proc_loc[0], proc_loc[1]])
        highest_corr_locations["region1"].append(
            comp_results["regions"][proc_loc[0]])
        highest_corr_locations["region2"].append(
            comp_results["regions"][proc_loc[1]])
    
    highest_corr_locations = DataFrame.from_dict(highest_corr_locations)

    ascending = True
    if comp_results["method"] == "corr":
        ascending = False

    highest_corr_locations = highest_corr_locations.sort_values(
        comp_results["method"], ascending=ascending)

    return highest_corr_locations


def get_regional_ts_comparison(data: DataFrame, method: str, preproc: list or None):
    """Get the region timeseries correlation

    Args:
        data (DataFrame): data to be processed
        preproc_flag (bool, optional): whether apply preprocessing on the data. Defaults to True.
    """


    def _check_missing_data(data_to_check: DataFrame, expected_data_length: int or None) -> bool:
        """Check if there are any missing data depending on the data length

        Args:
            data_to_check (DataFrame): data to be checked
            expected_data_length (intorNone): the reference data length

        Returns:
            bool: If True, then there is missing data
        """
        if expected_data_length is None:
            expected_data_length = len(data_to_check)
            return False

        if expected_data_length == len(data_to_check):
            return False
        
        return True


    unique_regions = sorted([x for x in data["Region"].unique().tolist() if str(x) != 'nan'])

    proc_ts = {}
    expected_data_length = None
    for proc_region in unique_regions:

        proc_data = data[data["Region"] == proc_region]
        proc_ts[proc_region] = data_preproc(
            proc_data.sort_values("week_end_date")[["week_end_date", "case_7d_avg"]].reset_index(
            drop=True), preproc)

        if expected_data_length is None:
            expected_data_length = len(proc_ts[proc_region])
        
        if _check_missing_data(proc_ts[proc_region], expected_data_length):
            raise Exception(f"{proc_region} has an unexpected data length !")


    output = {
        "index": zeros((len(unique_regions), len(unique_regions))),
        "xy": [],
        "regions": unique_regions,
        "dates": [datetime.utcfromtimestamp(
            dt.astype('O')/1e9) for dt in sorted(data["week_end_date"].unique())],
        "proc_ts": proc_ts,
        "method": method
    }

    for i, proc_region1 in enumerate(unique_regions):
        selected_data = proc_ts[proc_region1]
        output["xy"].append(proc_region1)
        for j, proc_region2 in enumerate(unique_regions):
            data_to_be_compared = proc_ts[proc_region2]

            if method == "corr":
                proc_index = selected_data["data"].corr(
                    data_to_be_compared["data"])
            elif method == "mse":
                proc_index = mean_squared_error(
                    selected_data["data"], 
                    data_to_be_compared["data"]
                )
            elif method == "dtw":
                proc_index = dtw(
                    selected_data["data"].values.tolist(), 
                    data_to_be_compared["data"].values.tolist())


            output["index"][i, j] = proc_index

    return output


