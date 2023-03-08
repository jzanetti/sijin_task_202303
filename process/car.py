from pandas import DataFrame, merge, concat
from datetime import datetime
from process.pred_model import use_tcn, use_linear, use_randomforest
from darts import TimeSeries
from darts.dataprocessing.transformers import Scaler
from pandas import Timestamp
from darts.metrics.metrics import rmse

def validation_run(all_data_ts: dict, model) -> dict:
    """Create validation runs

    Args:
        all_data_ts (dict): all the data to be used
        model (_type_): model being set up

    Returns:
        dict: data from validation run
    """
    train, val = all_data_ts["data"].split_after(Timestamp("20230107"))

    model.fit(train)
    pred = model.predict(n=len(val))

    if all_data_ts["scaler"] is not None:
        train = all_data_ts["scaler"].inverse_transform(train)
        val = all_data_ts["scaler"].inverse_transform(val)
        pred = all_data_ts["scaler"].inverse_transform(pred)

    err = rmse(pred, val)

    return {
        "train": train,
        "val": val,
        "pred": pred,
        "err": err
    }


def predict_run(all_data_ts: dict, model, fwd_step: int = 5) -> dict:
    """Create prediction runs

    Args:
        all_data_ts (dict): all the data to be used
        model (_type_): model being set up

    Returns:
        dict: data from prediction run
    """
    model.fit(all_data_ts["data"])

    pred_series = model.predict(n=fwd_step)

    if all_data_ts["scaler"] is not None:
        train = all_data_ts["scaler"].inverse_transform(all_data_ts["data"])
        pred = all_data_ts["scaler"].inverse_transform(pred_series)

    return {
        "train": train,
        "pred": pred
    }

def car_prediction(car_data: dict, fcst_method: str, preproc_cfg: list or None) -> dict:
    """Time series prediction for CAR

    Args:
        car_data (dict): CAR data to be used
        fcst_method (str): forecasting method to be used
        preproc_cfg (listorNone): preprocessing configuration
    """
    def _preproc(data_in: DataFrame, preproc_cfg: list) -> dict:
        """Preprocessing

        Args:
            data (DataFrame): data to be applied
            preproc_cfg (list): preprocessing configuration

        Returns:
            dict: the updated data
        """
        if preproc_cfg is None:
            return {
                "scaler": None,
                "data": data_in
            }
        
        for proc_preproc_step in preproc_cfg:

            if proc_preproc_step == "norm":
                scaler = Scaler()
                data_out = scaler.fit_transform(data_in)
        
        return {
                "scaler": scaler,
                "data": data_out
        }


    all_data = []
    for proc_region in car_data:
        proc_car = car_data[proc_region]
        all_data.append(proc_car)
    all_data = concat(all_data, ignore_index=True)
    all_data = all_data.groupby(["week_end_date"]).agg({"car": 'mean'})["car"].reset_index()
    all_data_ts_before_preproc = TimeSeries.from_dataframe(all_data, time_col= 'week_end_date')
    all_data_ts = _preproc(all_data_ts_before_preproc, preproc_cfg)

    if fcst_method == "tcn":
        model = use_tcn()
    elif fcst_method == "linear":
        model = use_linear()
    elif fcst_method == "rf":
        model = use_randomforest()

    val_outs = validation_run(all_data_ts, model)
    prd_outs = predict_run(all_data_ts, model)

    return {"val": val_outs, "prd": prd_outs, "method": fcst_method}


def cal_existing_car(data_to_use: dict, constant_k: dict) -> dict:
    """Calculating CAR for exisiting records

    Args:
        data_to_use (dict): data to be used
        constant_k (float): referenced "case_7d_avg"/"total_copies" ratio

    Returns:
        dict: CAR for existing records
    """
    unique_regions = sorted(data_to_use["ww"]["Region"].unique())

    car_data = {}
    for proc_region in unique_regions:
        proc_ref_k = constant_k[proc_region]

        proc_ww = data_to_use["ww"][data_to_use["ww"]["Region"] == proc_region]
        proc_case = data_to_use["case"][data_to_use["case"]["Region"] == proc_region]
        merged_df = merge(proc_ww, proc_case, on=["week_end_date", "Region"])
        merged_df["factor"] = merged_df["copies_per_day_per_person"]/ merged_df["case_7d_avg"]

        merged_df["car"] = merged_df["factor"] * proc_ref_k
        car_data[proc_region] = merged_df

    return car_data


def obtain_ref_constant(ref_data: dict) -> dict:
    """Get the ratio: "case_7d_avg"/"total_copies" for the referenced date

    Args:
        ref_data (dict): reference data
    """
    unique_regions = sorted(ref_data["ww"]["Region"].unique())

    constant_k = {}
    for proc_region in unique_regions:
        proc_ww = ref_data["ww"][ref_data["ww"]["Region"] == proc_region]
        proc_case = ref_data["case"][ref_data["case"]["Region"] == proc_region]
        constant_k[proc_region] = proc_case["case_7d_avg"].values[0] / proc_ww["copies_per_day_per_person"].values[0]
    
    return constant_k


def split_ref_data(ww: DataFrame, case: DataFrame, ref_date: datetime, exclude_ref_data: bool = False) -> dict:
    """Split Referenced data from the entire dataset

    Args:
        ww (DataFrame): WW dataset
        case (DataFrame): CASE datasrt
        ref_date (datetime): referenced date

    Returns:
        dict: split dataset
    """
    ref_date = datetime.strptime(str(ref_date), "%Y%m%d")

    ww_ref = ww[ww["week_end_date"] == ref_date]
    case_ref = case[case["week_end_date"] == ref_date]

    if exclude_ref_data:
        ww_data = ww[ww["week_end_date"] != ref_date]
        case_data = case[case["week_end_date"] != ref_date]
    else:
        ww_data = ww
        case_data = case

    return {
        "ref": {
            "ww": ww_ref,
            "case": case_ref
        },
        "data": {
            "ww": ww_data,
            "case": case_data
        }
    }



def process_ww(ww: DataFrame) -> DataFrame:
    """Obtain total copies from WW data

    Args:
        ww (DataFrame): raw WW dataset

    Returns:
        DataFrame: _description_
    """
    ww["total_copies"] = ww["copies_per_day_per_person"] * ww["population_covered"]

    return ww