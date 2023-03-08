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

    all_data_ts_before_preproc = TimeSeries.from_dataframe(
        car_data[["week_end_date", "car"]], time_col= 'week_end_date')
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


def cal_existing_car(data_to_use: dict, constant_k: float) -> dict:
    """Calculating CAR for exisiting records

    Args:
        data_to_use (dict): data to be used
        constant_k (float): referenced "case_7d_avg"/"total_copies" ratio

    Returns:
        dict: CAR for existing records
    """
    proc_ww = data_to_use["ww"]
    proc_case = data_to_use["case"]
    merged_df = merge(proc_ww, proc_case, on=["week_end_date"])
    merged_df["car"] = merged_df["case_7d_avg"] / (merged_df["copies_per_day_per_person"] * constant_k)

    return merged_df


def obtain_ref_constant(ref_data: dict) -> dict:
    """Get the ratio: "case_7d_avg"/"total_copies" for the referenced date

    Args:
        ref_data (dict): reference data
    """
    constant_k = ref_data["case"]["case_7d_avg"].values[0] / ref_data["ww"]["copies_per_day_per_person"].values[0]
    
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
    ww["total_copies"] = ww["copies_per_day_per_person"] * ww["national_pop"]

    return ww