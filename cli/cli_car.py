"""
Usage: car --workdir <WORK DIR> --cfg <CFG>

Author: Sijin Zhang

Description: 
    This is a wrapper to calculate different statistical properties from regional covid data

Debug:
    export PYTHONPATH=~/Github/esr_task/env.yml:$PYTHONPATH
"""

import argparse
from process.io import obtain_latest_data, data_filter
from process.utils import setup_logging, construct_inputs, read_cfg
from process.car import process_ww, split_ref_data, obtain_ref_constant, cal_existing_car, car_prediction
from process.vis import car_ts, car_ts_prd

def get_example_usage():
    example_text = """example:
        *  car --workdir /tmp/covid_corr --cfg etc/case_cfg.yml
        """
    return example_text


def setup_parser():
    parser = argparse.ArgumentParser(
        description="This is a wrapper to compare COVID cases for different regions",
        epilog=get_example_usage(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--workdir",
        required=True,
        help=f"Working directory")

    parser.add_argument(
        "--cfg",
        required=True,
        help=f"Configuration to be applied")

    return parser.parse_args(
        # ["--workdir", "/tmp/esr_task5", "--cfg", "etc/car_cfg.yml"]
    )


def run(workdir: str, cfg: str):
    """Run CAR estimation and prediction

    Args:
        workdir (str): working directory
        cfg (str): configuration file
    """
    logger = setup_logging()

    logger.info("reading configuration ...")
    cfg = read_cfg(cfg)

    logger.info("reformating inputs ...")
    args = construct_inputs(workdir, cfg["start"], cfg["end"], cfg["regions"])

    logger.info("getting required ww and case data ...")
    ww = process_ww(data_filter(obtain_latest_data(data_name="ww") , args))
    case = data_filter(obtain_latest_data() , args)

    logger.info("Split ww and case data into reference and others ...")
    data = split_ref_data(ww, case, cfg["ref_date"], exclude_ref_data=False)

    logger.info("Obtaining the constant k for estimating CAR ...")
    constant_k = obtain_ref_constant(data["ref"])

    logger.info("Estimating CAR ...")
    car = cal_existing_car(data["data"], constant_k)

    logger.info("Predicting CAR ...")
    car_from_prd = car_prediction(car, cfg["fcst_method"], cfg["preproc"])

    logger.info("Plotting CAR ...")
    car_ts(workdir, car)

    logger.info("Plotting CAR prediction...")
    car_ts_prd(workdir, car_from_prd)


def main():
    args = setup_parser()

    run(args.workdir, args.cfg)

if __name__ == "__main__":
    main()

