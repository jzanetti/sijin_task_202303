from os.path import join
from matplotlib.pyplot import pcolor, title, savefig, xticks, yticks, figure, close, subplots, colorbar, plot
from process import REGIONAL_COLORS
from pandas import concat
import matplotlib.ticker as mtick


def car_ts_prd(workdir: str, car_data: dict, figsize: tuple = (15, 10), filename: str = "car_{type}.png", fontsize: int = 25):
    """Plot CAR TS

    Args:
        workdir (str): working directory
        car_data (dict): CAR data
        figsize (tuple, optional): figure size. Defaults to (15, 10).
        filename (str, optional): filename to be used. Defaults to "cas.png".
    """
    _, ax1 = subplots(figsize=figsize)
    for type in ["val", "prd"]:
        _, ax1 = subplots(figsize=figsize)
        if type == "val":
            car_data[type]["train"].plot(color="k", label="training dataset", ax=ax1)
            car_data[type]["val"].plot(color="r", label="validation dataset", ax=ax1)
            car_data[type]["pred"].plot(color="b", label="prediction", ax=ax1)
            ax1.set_title(f"Validation using the prediction method {car_data['method']} \n RMSE: {round(car_data[type]['err'], 3)}", fontsize=fontsize)
        elif type == "prd":
            car_data[type]["train"].plot(color="k", label="training dataset", ax=ax1)
            car_data[type]["pred"].plot(color="r", label="prediction", ax=ax1)
            ax1.set_title(f"Prediction using {car_data['method']}", fontsize=fontsize)
        
        ax1.set_xlabel('Date', fontsize=fontsize)
        ax1.set_ylabel('CAR', fontsize=fontsize)
        ax1.tick_params(axis='both', which='major', labelsize=fontsize)

        legend = ax1.legend()
        for i in range(len(legend.texts)):
            legend.texts[i].set_fontsize(fontsize)

        ax1.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1, decimals=0))
        savefig(join(workdir, filename.format(type=type)), bbox_inches="tight")
        close()



def car_ts(workdir: str, car_data: dict, figsize: tuple = (15, 10), filename: str = "car.png", fontsize: int = 25):
    """Plot CAR TS

    Args:
        workdir (str): working directory
        car_data (dict): CAR data
        figsize (tuple, optional): figure size. Defaults to (15, 10).
        filename (str, optional): filename to be used. Defaults to "cas.png".
    """
    all_data = []
    _, ax1 = subplots(figsize=figsize)
    for proc_region in car_data:
        proc_car = car_data[proc_region]
        all_data.append(proc_car)
        proc_car.plot(x="week_end_date", y="car", ax=ax1, label=proc_region)
    all_data = concat(all_data, ignore_index=True)
    mean_car = all_data.groupby("week_end_date")["car"].mean()
    mean_car.plot(x="week_end_date", ax=ax1, linewidth=10, label="Nationwide")
    ax1.set_xlabel('Date', fontsize=fontsize)
    ax1.set_ylabel('CAR', fontsize=fontsize)
    ax1.tick_params(axis='both', which='major', labelsize=fontsize)
    ax1.plot([0, len(mean_car)], [1.0, 1.0], linewidth=5, color="k")
    ax1.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1, decimals=0))
    title(f"Regional and national wide CAR estimation \n "
          f"between {min(all_data['week_end_date'])} and {max(all_data['week_end_date'])}", fontsize=fontsize)
    savefig(join(workdir, filename), bbox_inches="tight")
    close()



def comp_map(workdir: str, corr_output: dict, figsize: tuple = (12, 12), filename: str = "comparison.png", cmap: str = "jet"):
    """Produce the correlation maps across different regions

    Args:
        workdir (str): working directory
        corr_output (dict): produced correlations
        args (dict): arguments to be used
        figsize (tuple, optional): Figure size. Defaults to (12, 12).
        filename (str, optional): Output file name. Defaults to "cross_corr.png".
    """
    figure(figsize=figsize)
    pcolor(corr_output["index"], cmap=cmap)
    xticks(range(len(corr_output["index"])), corr_output["xy"], rotation=45)
    yticks(range(len(corr_output["index"])), corr_output["xy"])
    title(f"{corr_output['method'].upper()} (preprocessed) between regions in COVID cases\n "
        f"between {min(corr_output['dates']).strftime('%Y%m%d')} and "
        f"{max(corr_output['dates']).strftime('%Y%m%d')}")
    colorbar()
    savefig(join(workdir, filename), bbox_inches="tight")
    close()


def case_ts(workdir: str, corr_output: dict, figsize: tuple = (15, 10), filename: str = "ts.png"):
    """Produce the cas timeseries

    Args:
        workdir (str): working directory
        corr_output (dict): produced correlations
        figsize (tuple, optional): Figure size. Defaults to (15, 10).
        filename (str, optional): Filename to be used. Defaults to "ts_corr.png".
    """
    _, ax1 = subplots(figsize=figsize)
    ax2 = ax1.twinx()

    for i, proc_region in enumerate(corr_output["regions"]):
        proc_cases = corr_output["proc_ts"][proc_region]["case_7d_avg"]
        proc_cases_norm = corr_output["proc_ts"][proc_region]["data"]

        ax1.plot(proc_cases, color=REGIONAL_COLORS[i], linestyle = "-", label=proc_region, linewidth=3.0)
        ax2.plot(proc_cases_norm, color=REGIONAL_COLORS[i], linestyle = "--", alpha=1.0, linewidth=1.0)

    ax1.set_ylabel("Number of cases: solid line")
    ax2.set_ylabel("Number of cases (after preprocessing): dashed line")
    ax1.set_xlabel("Date")

    ax1.set_xticks(range(0, len(proc_cases), 5))
    ax1.set_xticklabels([dt.strftime("%Y%m") for dt in corr_output['dates']][::5], rotation=45.0)

    ax1.legend()
    ax1.set_title(f"COVID cases in New Zealand \n "
        f"between {corr_output['dates'][0].strftime('%Y%m%d')} and "
        f"{corr_output['dates'][1].strftime('%Y%m%d')}")
    savefig(join(workdir, filename), bbox_inches="tight")
    close()

