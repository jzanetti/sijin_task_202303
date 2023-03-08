from datetime import datetime
from logging import INFO, Formatter, StreamHandler, basicConfig, getLogger
from os.path import join, exists
from os import makedirs
from yaml import safe_load as yaml_load


def construct_inputs(workdir: str, start: str or None, end: str or None, regions: list or None) -> dict:
    """Process the argument inputs

    Args:
        workdir (str): working directory
        start (str): start date for data processing
        end (str): end date for data processing
        regions (list): regions to be used

    Returns:
        dict: the dict contains required inputs for the data processing
    """
    if not exists(workdir):
        makedirs(workdir)
    
    args_to_use = {
        "start": start,
        "end": end,
        "regions": regions
    }

    for time_key in ["start", "end"]:
        if args_to_use[time_key] is not None:
            try:
                args_to_use[time_key] = datetime.strptime(str(args_to_use[time_key]), "%Y%m")
            except ValueError:
                args_to_use[time_key] = datetime.strptime(str(args_to_use[time_key]), "%Y%m%d")

    return args_to_use


def read_cfg(cfg: str) -> dict:
    """Read a configuration file

    Args:
        cfg (str): configuration path

    Returns:
        dict: configuration
    """
    with open(cfg, "r") as fid:
        return yaml_load(fid)



def setup_logging(workdir: str = "/tmp", logger_utc: datetime = datetime.utcnow()):
    """set up logging system for tasks

    Args:
        workdir (str): working directory
        logger_utc (datetime, optional): When the logger is recorded.
    """
    formatter = Formatter("%(asctime)s - %(name)s.%(lineno)d - %(levelname)s - %(message)s")
    ch = StreamHandler()
    ch.setLevel(INFO)
    ch.setFormatter(formatter)
    basicConfig(filename=join(workdir, f"esr_run.{logger_utc.strftime('%Y%m%d')}")),
    logger = getLogger()
    logger.setLevel(INFO)
    logger.addHandler(ch)

    return logger
