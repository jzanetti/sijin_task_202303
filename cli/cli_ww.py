"""
Usage: covid_comp --workdir <WORK DIR> --cfg <CFG>

Author: Sijin Zhang

Description: 
    This is a wrapper to calculate different statistical properties from regional covid data

Debug:
    export PYTHONPATH=~/Github/sijin_task_202303:$PYTHONPATH
"""

import argparse
from process.io import obtain_latest_data, data_filter, export_csv
from process.utils import setup_logging, construct_inputs, read_cfg
from process.corr import get_regional_ts_comparison, rank_comp
from process.vis import comp_map, case_ts

def get_example_usage():
    example_text = """example:
        *  covid_comp --workdir /tmp/covid_corr --cfg etc/case_cfg.yml
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
       # [ "--workdir", "/tmp/esr_task_case3", "--cfg", "etc/ww_cfg.yml"]
    )


def run(workdir: str, cfg: str):
    """Producing regional comparisons

    Args:
        workdir (str): working directory
        cfg (str): configuration
    """
    logger = setup_logging()

    logger.info("Reading configuration ...")
    cfg = read_cfg(cfg)

    logger.info("Formating inputs ...")
    args = construct_inputs(workdir, cfg["start"], cfg["end"], cfg["regions"])

    logger.info("Data preprocessing ...")
    data = data_filter(obtain_latest_data(data_name="ww") , args)

    logger.info("Get regional comparison ...")
    comp_results = get_regional_ts_comparison(
        data, cfg["method"], cfg["preproc"], cfg["missing_fill_method"])

    if cfg["vis"]:
        logger.info("Creating plots ...")
        comp_map(workdir, comp_results)
        case_ts(workdir, comp_results)

    if cfg["csv"]:
        logger.info("Creating CSV ...")
        export_csv(workdir, rank_comp(comp_results))

    logger.info(f"job done ...")



def main():
    args = setup_parser()

    run(args.workdir, args.cfg)

if __name__ == "__main__":
    main()

