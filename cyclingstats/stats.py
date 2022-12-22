import pandas as pd
import numpy as np

def calc_hr_zones(LTHR:float) -> list:
    """
    Calculate boundaries for Coggan heart rate (HR) zones from the lactate threshold heart rate (LTHR)

    https://www.trainingpeaks.com/blog/power-training-levels/
    https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.111.3820&rep=rep1&type=pdf
    1 - Active Recovery
    2 - Endurance
    3 - Tempo
    4 - Lactate Threshold
    5 - VO2Max
    """
    return [0.69*LTHR, 0.84*LTHR, 0.95*LTHR, 1.06*LTHR]

def calc_power_zones(FTP:float) -> list:
    """
    Calculate boundaries for Coggan power zones from the functional threshold power (FTP)

    https://www.trainingpeaks.com/blog/power-training-levels/
    https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.111.3820&rep=rep1&type=pdf
    1 - Active Recovery
    2 - Endurance
    3 - Tempo
    4 - Lactate Threshold
    5 - VO2Max
    6 - Anaerobic Capacity
    Note: the numbers below define the start of the zones
    """
    return [0.56*FTP, 0.76*FTP, 0.91*FTP, 1.06*FTP, 1.21*FTP]

def time_in_zone(X:pd.Series, zones:list) -> list:
    """
    Calculate time spent in power/heart rate zones for a training session
    Arguments
        X               - (pd.Series) time series of heart rates/power recorded
        zones           - (list) boundaries for heart rate/power zones 
                          (output of functions calc_power_zones or calc_hr_zones)
    Returns
        time_in_zone    - (np.array) time spent in heart rate/power zones
    """
    time_in_zone = np.zeros(len(zones)+1)
    for n, (z_min, z_max) in enumerate(zip([0]+zones, zones+[1e6])):
        time_in_zone[n] = ((X >= z_min) & (X < z_max)).sum()
    return time_in_zone

def combine_pedal_smoothness(left, right, balance):
    return left*(balance.clip(0,100)/100) + right*(1-balance.clip(0,100)/100)

def elevation_gain(altitude: pd.Series):
    # calculate the total elevation gain during a workout
    return altitude.diff()[altitude.diff() > 0].sum()

def elevation_loss(altitude: pd.Series):
    # calculate the total elevation loss during a workout
    return altitude.diff()[altitude.diff() < 0].sum()

def normalised_power(power: pd.Series) -> float:
    # calculate normalised power (NP) for each training individually
    # make sure power is a pandas series with a monotonic datetimeindex
    return power.rolling('30s', min_periods=30).mean().pow(4).mean()**(1/4)

def intensity_factor(NP, FTP) -> float:
    # calculate intensity factor (IF) as ratio between normalised power (NP) and functional threshold power (FTP)
    return NP/FTP

def training_stress_score(T, IF) -> float:
    # calculate training stress score (TSS) using duration of workout in seconds (T) and intensity factor (IF)
    return 100 * (T/3600) * IF**2 

def variability_index(NP:float, power: pd.Series) -> float:
    # calculate variability index (VI) using normalised power (NP) and power
    # for each training individually
    return NP / power.mean()

def efficiency_factor(NP:float, heart_rate: pd.Series) -> float:
    # calculate efficiency factor (EF) using normalised power (NP) and heart rate
    # for each training individually
    return NP / heart_rate.mean()

def chronic_training_load(TSS: pd.Series):
    # calculate chronic training load (CTL) (fitness)
    return TSS.ewm(span=42).mean()

def acute_training_load(TSS: pd.Series):
    # calculate acute training load (ATL) (fatigue)
    return TSS.ewm(span=7).mean()

def training_stress_balance(CTL, ATL):
    # calculate the training stress balance (TSB) (form) from chronic training load (CTL) and acute training load (ATL)
    return CTL - ATL

def agg_power(X:pd.DataFrame, FTP, col_hr='heart_rate', col_power='power'):
    """
    Calculate statistics related to power for a training session
    Arguments
        X           - (pd.DataFrame) time series including columns 'power' and 'heart_rate' with the timestamp as index
        FTP         - (float) functional threshold power [W]
        col_hr      - (string) name of the heart rate column
        col_power   - (string) name of the power column
    Returns
                      (pd.Series) power statistics
    """
    T = len(X)
    NP = normalised_power(X[col_power])
    IF = intensity_factor(NP, FTP)
    TSS = training_stress_score(T, IF)
    VI = variability_index(NP, X[col_power])
    EF = efficiency_factor(NP, X[col_hr])

    return pd.Series({'normalised_power'        : NP,
                      'intensity_factor'        : IF,
                      'training_stress_score'   : TSS,
                      'variability_index'       : VI,
                      'efficiency_factor'       : EF})

def agg_zones(X:pd.DataFrame, hr_zones:list, power_zones:list, col_hr='heart_rate', col_power='power'):
    """
    Calculate statistics related to time in zones for a training session
    Arguments
        X           - (pd.DataFrame) time series including columns 'power' and 'heart_rate' with the timestamp as index
        hr_zones    - (list) list of boundaries for heart rate zones
        power_zones - (list) list of boundaries for power zones
    Returns
                      (pd.Series) power statistics
    """
    time_in_hr_zone = {'time_in_hr_zone%s'%(n+1):t for n, t in enumerate(time_in_zone(X[col_hr], hr_zones))}
    time_in_power_zone = {'time_in_power_zone%s'%(n+1):t for n, t in enumerate(time_in_zone(X[col_power], power_zones))}
    return pd.Series({**time_in_hr_zone, **time_in_power_zone})
