# 1. Purpose:

This repository analyzes the relationship between wastewater (WW) samples and reported COVID-19 cases from early 2022 to present. The data is provided by [ESR](https://github.com/ESR-NZ/covid_in_wastewater), and funded by the [Ministry of Health](https://www.health.govt.nz).

# 2. Data source:

- COVID-19 cases:
    - National data: [link](https://github.com/ESR-NZ/covid_in_wastewater/blob/main/data/cases_national.csv)
    - Regional data: [link](https://github.com/ESR-NZ/covid_in_wastewater/blob/main/data/cases_regional.csv)

- Waste water samples:
    - National data: [link](https://github.com/ESR-NZ/covid_in_wastewater/blob/main/data/ww_national.csv)
    - Regional data: [link](https://github.com/ESR-NZ/covid_in_wastewater/blob/main/data/ww_regional.csv)


# 3. Installation:

The repository can be easily installed via the provided `make` command as:

```
export CONDA_BASE=<CONDA_BASE>
make all
```
where `CONDA_BASE` is the location where the base _CONDA_ environment is installed. The above command will install a working environment (including all dependant libraries) for this code repository. After the installation, the working environment can be triggered as `conda activate esr_task`

# 4. Usage:

## 4.1 COVID case comparisons:

In order to calculate the regional correlations for COVID cases, the following command can be used:
```
conda activate esr_task
ww --workdir <WORKDIR> [--cfg <CFG>]
```
where `--workdir` is the working directory for the data processing. `--cfg` is used to specify the configuration for `ww`.

In the configuration, we can specify:

- `method`: which method is used to compare the COVID cases:
    - `corr`: standard correlation coefficient (pearson)
    - `dtw`: dynamic time warping
    - `mse`: mean square error

- `preproc`: what preprocessing steps to be carried out
  - `norm`: applying min/max scaling on the data
  - `fft`: applying FFT smoothing

- `missing_fill_method`: the method used to fill the missing data in the WW dataset.

- `regions`: regions to be included in the study (if _null_ then all regions will be used)

- `start`/`end`: dates to be included in the study

- `vis`/`csv`: output controls (if producing _figure_ or _csv_).

An example of configuration file can be found at `etc/case_cfg.yml`.


For instance, we can produce the comparisons for the evolution of COVID cases as:
```
conda activate esr_task
ww --workdir /tmp/covid_corr --cfg etc/ww_cfg.yml
```
The outputs are saved in `/tmp/covid_corr`.

## 4.2 Case Ascertainment Rate (CAR):

**CAR** can be estimated and predicted using the following method:
```
conda activate esr_task
carr --workdir <WORKDIR> [--cfg <CFG>]
```
where `--workdir` is the working directory, and `--cfg` is the configuration.

In the configuration, we can specify:

- `ref_date`: which date is used to be the "truth" for estimating CAR

- `preproc`: what preprocessing steps to be carried out
    - `norm`: applying min/max scaling on the data

- `fcst_method`: which timeseries forecasting method to be used, currently the following methods are supported:
    - `linear`: Linear regression
    - `rf`: Random forest
    - `tcn`: Temporal Convolutional Network

- `regions`: regions to be included in the study (if _null_ then all regions will be used)

- `start`/`end`: dates to be included in the study


An example of configuration file can be found at `etc/car_cfg.yml`.


# Appendix:

A very simple CAR estimation method is employed here:

It is understood that:
```
CAR = (Reported cases / actual total cases) x 100%
```

Assuming that the `actual cases` can be extracted based on `copies_per_day_per_person`, as `actual cases = copies_per_day_per_person * k` where `k` is a constant that can be derived from a "ground truth" (e.g., the data obtained at _t0_). Therefore, `CAR` can be estimated using:

```
Reported cases(t0) = copies_per_day_per_person (t0) * k(t0)
CAR(t) = (Reported cases(t) / (copies_per_day_per_person (t) * k(t0)))
```
where `t0` represents the time that we obtain the "truth" (where `estimated cases == actual cases`)

Note that this is a very simple method to estimate `CAR`, a more detailed and comprehensive approach can be found [here](https://www.sciencedirect.com/science/article/pii/S0022519322003241)


