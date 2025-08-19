import os
import xarray as xr
import numpy as np
import h5py
from variables_config import (
    zarr_store_path, hdf5_store_path,
    start_train_year, end_train_year,
    test_years, out_of_sample_years
)

# Ensure output directories exist
os.makedirs(hdf5_store_path, exist_ok=True)
stats_dir = os.path.join(hdf5_store_path, "stats")
os.makedirs(stats_dir, exist_ok=True)
test_dir = os.path.join(hdf5_store_path, "test")
os.makedirs(test_dir, exist_ok=True)
train_dir = os.path.join(hdf5_store_path, "train")
os.makedirs(train_dir, exist_ok=True)
sample_dir = os.path.join(hdf5_store_path, "out_of_sample")
os.makedirs(sample_dir, exist_ok=True)
constant_mask_dir = os.path.join(hdf5_store_path, "constant_mask")
os.makedirs(constant_mask_dir, exist_ok=True)

def combine_data(surface_file, upper_file, static_file):
    ds_surface = xr.open_dataset(surface_file)
    ds_upper = xr.open_dataset(upper_file)
    ds_static = xr.open_dataset(static_file)

    # Combine into one data array
    surface_data = xr.concat([ds_surface[var] for var in ds_surface.data_vars], dim="channel")
    upper_data = xr.concat([ds_upper[var] for var in ds_upper.data_vars], dim="channel")
    static_data = xr.concat([ds_static[var] for var in ds_static.data_vars], dim="channel")

    # ---- move valid_time → time ----
    if "valid_time" in surface_data.dims:
        surface_data = surface_data.rename({"valid_time": "time"})
    if "valid_time" in upper_data.dims:
        upper_data = upper_data.rename({"valid_time": "time"})
    if "valid_time" in static_data.dims:
        static_data = static_data.rename({"valid_time": "time"})
        
    # ---- expand static_data with time to surface_data ----
    static_expanded = static_data.squeeze("time").expand_dims({"time": surface_data.time})

    # ---- flatten pressure_level with upper_data to channel ----
    if "pressure_level" in upper_data.dims:
        upper_reshaped = upper_data.stack(channel2=("channel", "pressure_level"))
        ## drop channel with conflict
        upper_reshaped = upper_reshaped.reset_index("channel2", drop=True)
        upper_reshaped = upper_reshaped.rename({"channel2": "channel"})
    else:
        upper_reshaped = upper_data

    # ---- concat along channel ----
    full_data = xr.concat([surface_data, upper_reshaped, static_expanded], dim="channel")
    return full_data.transpose("time", "channel", "latitude", "longitude").values

def save_h5(filename, data):
    with h5py.File(filename, "w") as f:
        f.create_dataset("fields", data=data.astype(np.float32))

if __name__ == "__main__":
    static_file = os.path.join(zarr_store_path, "static_masks.nc")
    all_datasets = []

    # Train years
    for year in range(start_train_year, end_train_year + 1):
        arr = combine_data(
            os.path.join(zarr_store_path, f"surface_{year}.nc"),
            os.path.join(zarr_store_path, f"upper_{year}.nc"),
            static_file
        )
        #save_h5(os.path.join(hdf5_store_path, f"{year}.h5"), arr)
        print(">>> Create Train data.")
        save_h5(os.path.join(train_dir, f"{year}.h5"), arr)
        all_datasets.append(arr)

    # Test years
    for year in test_years:
        arr = combine_data(
            os.path.join(zarr_store_path, f"surface_{year}.nc"),
            os.path.join(zarr_store_path, f"upper_{year}.nc"),
            static_file
        )
        print(">>> Create Test data.")
        save_h5(os.path.join(test_dir, f"{year}.h5"), arr)
        all_datasets.append(arr)

    # Out-of-sample years
    for year in out_of_sample_years:
        arr = combine_data(
            os.path.join(zarr_store_path, f"surface_{year}.nc"),
            os.path.join(zarr_store_path, f"upper_{year}.nc"),
            static_file
        )
        print(">>> Create Sample data.")
        save_h5(os.path.join(sample_dir, f"{year}.h5"), arr)
        all_datasets.append(arr)

    # Compute global stats
    all_data = np.concatenate(all_datasets, axis=1)
    means = np.mean(all_data, axis=(0, 2, 3))
    stds = np.std(all_data, axis=(0, 2, 3))

    # reshape to [1, C, 1, 1]
    means = means.reshape(1, -1, 1, 1)
    stds = stds.reshape(1, -1, 1, 1)

    np.save(os.path.join(stats_dir, "global_means.npy"), means)
    np.save(os.path.join(stats_dir, "global_stds.npy"), stds)

    #===================================================================================
    # create land_mask.npy, soil_type.npy, topography.npy
    ds = xr.open_dataset(static_file)

    # 1.Land-sea mask
    lsm = ds["lsm"].values  # shape [lat, lon]
    land_mask = (lsm > 0.5).astype(np.float32).squeeze()  # ocean=0, land=1
    np.save(os.path.join(constant_mask_dir, "land_mask.npy"), land_mask)

    # 2 Soil type
    slt = ds["slt"].values
    soil_type = slt.astype(np.int32).squeeze()
    np.save(os.path.join(constant_mask_dir, "soil_type.npy"), soil_type)

    # 3 Topography
    g = 9.80665  # m/s^2
    z = ds["z"].values
    topography = (z / g).astype(np.float32).squeeze()
    np.save(os.path.join(constant_mask_dir, "topography.npy"), topography)

    print(">>> Final process_era5...")
