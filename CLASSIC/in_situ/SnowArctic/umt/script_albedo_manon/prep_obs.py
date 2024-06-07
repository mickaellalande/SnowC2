import pdb
import numpy as np
import pandas as pd

def prep_obs (ds, site_code) :

    # ds is an xarray dataset with the following characteristics :
    # - only variables : GLOB, REFL, snd_man (and if they exist snd, snw, or Tsurf)
    # - index "time" in datetime format
    # - flags on data have been used and removed
    # - snow depth values are in meters
    # - variable values are floats, not strings
    # - the appropriate time slice has been selected to correspond to simulation

    # Drop duplicate indexes in case, and bring all data back to hourly basis using mean

    ds = ds.drop_duplicates(dim='time', keep='first')
    ds = ds.resample(time='1H').mean()
    
    df = pd.read_fwf('/home/mag009/crocus/Simulation/run_all_new/met_forcing/basin_forcing_'+site_code+'_ext.met',header=None,infer_nrows=3000)
    df['hh'] = df[0].apply(lambda x: '{0:0>2}'.format(x))
    df['jjj'] = df[2].apply(lambda x: '{0:0>3}'.format(x))
    df['date_block'] = df[3].astype(str)+"/"+df['jjj'].astype(str)+"/"+df['hh'].astype(str)
    df['time'] = pd.to_datetime(df['date_block'], format='%Y/%j/%H')
    df.index = pd.DatetimeIndex(df.time)
    df = df.loc[ds.time.values[0]:ds.time.values[-1]]
    ds['snow'] = df[12].values == 0

    # Filter radiation data and compute albedo

    GLOBval=20
    REFLval=2
    mask = np.logical_and(ds.GLOB>=GLOBval, ds.REFL>=REFLval)
    mask = np.logical_and(mask, ds.GLOB>ds.REFL)
    mask = np.logical_and(mask, ds.snow.values)
    GLOB_resamp = ds.GLOB[mask].resample(time='1D')
    REFL_resamp = ds.REFL[mask].resample(time='1D')
    mask_resamp = GLOB_resamp.count()>=5
    GLOB_filt_day = GLOB_resamp.sum()[mask_resamp]
    REFL_filt_day = REFL_resamp.sum()[mask_resamp]
    albs_temp = REFL_filt_day / GLOB_filt_day
    ds['albs'] = albs_temp[albs_temp<0.9]
    ds['albs_raw'] = ds.REFL / ds.GLOB
    
    ds = ds.drop_vars(['REFL','GLOB','albs_raw','snow'])

    # Save netcdf file

    DEFAULT_ENCODING = {
        'zlib': True,
        'shuffle': True,
        'complevel': 4,
        'fletcher32': False,
        'contiguous': False,
    }
    def generate_encodings(data):
        encoding = {}
        for var in data.data_vars:
            encoding[var] = DEFAULT_ENCODING.copy()
        return encoding
    encoding = generate_encodings(ds)
    ds.to_netcdf('/home/mag009/crocus/Simulation/run_all_new/obs_eval/obs_insitu_'+site_code+'.nc')