"""
This python file aims to reproduce the plots seen at the bottom of:
https://github.com/PrincetonUniversity/XGC-Examples/wiki/neoclassical_benchmark
"""
import os
import adios2
import matplotlib.pyplot as plt
import numpy as np

class Flux:
    """
    Class for holding ion flux data
    """
    def __init__(self):
        self.e_radial_en_flux_3db_df_1d = None
        self.i_radial_en_flux_3db_df_1d = None
        self.e_radial_en_flux_3db_1d = None
        self.i_radial_en_flux_3db_1d = None
        self.e_radial_en_flux_ExB_df_1d = None
        self.i_radial_en_flux_ExB_df_1d = None
        self.e_radial_en_flux_ExB_1d = None
        self.i_radial_en_flux_ExB_1d = None
        self.e_radial_en_flux_df_1d = None
        self.i_radial_en_flux_df_1d = None
        self.e_radial_en_flux_1d = None
        self.i_radial_en_flux_1d = None

        self.e_radial_flux_3db_df_1d = None
        self.i_radial_flux_3db_df_1d = None
        self.e_radial_flux_3db_1d = None
        self.i_radial_flux_3db_1d = None
        self.e_radial_flux_ExB_df_1d = None
        self.i_radial_flux_ExB_df_1d = None
        self.e_radial_flux_ExB_1d = None
        self.i_radial_flux_ExB_1d = None
        self.e_radial_flux_df_1d = None
        self.i_radial_flux_df_1d = None
        self.e_radial_flux_1d = None
        self.i_radial_flux_1d = None

DATA_FILE = ('/pscratch/sd/q/qt4627/XGC_projects/neoclassical/'
             'run_xgca_gpu_batch/xgc.oneddiag.bp')
repo_dir = os.path.dirname(os.path.abspath(__file__))
plot_dir = os.path.join(repo_dir, 'plots_energy_flux_1d')
os.makedirs(plot_dir, exist_ok=True)

flux_strings = ["e_radial_en_flux_3db_df_1d",
                "i_radial_en_flux_3db_df_1d",
                "e_radial_en_flux_3db_1d",
                "i_radial_en_flux_3db_1d",
                "e_radial_en_flux_ExB_df_1d",
                "i_radial_en_flux_ExB_df_1d",
                "e_radial_en_flux_ExB_1d",
                "i_radial_en_flux_ExB_1d",
                "e_radial_en_flux_df_1d",
                "i_radial_en_flux_df_1d",
                "e_radial_en_flux_1d",
                "i_radial_en_flux_1d",
                "e_radial_flux_3db_df_1d",
                "i_radial_flux_3db_df_1d",
                "e_radial_flux_3db_1d",
                "i_radial_flux_3db_1d",
                "e_radial_flux_ExB_df_1d",
                "i_radial_flux_ExB_df_1d",
                "e_radial_flux_ExB_1d",
                "i_radial_flux_ExB_1d",
                "e_radial_flux_df_1d",
                "i_radial_flux_df_1d",
                "e_radial_flux_1d",
                "i_radial_flux_1d"]

flux = Flux()
with adios2.Stream(DATA_FILE, 'r') as data_stream:
    for i, _ in enumerate(data_stream.steps()):
        if i != 499:
            continue
        print(f"Current step is {i+1}")
        for flux_string in flux_strings:
            print(f"Reading {flux_string}")
            flux.__dict__[flux_string] = data_stream.read(flux_string)
    psi = data_stream.read('psi')
    i_grad_psi_sqr_1d = data_stream.read('i_grad_psi_sqr_1d')
    i_gc_density_df_1d = data_stream.read('i_gc_density_df_1d')
    e_grad_psi_sqr_1d = data_stream.read('e_grad_psi_sqr_1d')
    e_gc_density_df_1d = data_stream.read('e_gc_density_df_1d')

i_radial_en_flux_ExB_1d_over_time = np.zeros((500, len(psi)))
with adios2.Stream(DATA_FILE, 'r') as data_stream:
    for i, _ in enumerate(data_stream.steps()):
        print(f"Current step is {i+1}")
        i_radial_en_flux_ExB_1d_over_time[i, :] = data_stream.read('i_radial_en_flux_ExB_1d')


video_dir = os.path.join(plot_dir, 'i_radial_en_flux_ExB_1d_over_time')
os.makedirs(video_dir, exist_ok=True)
for i in range(500):
    if i % 100 != 0 and i != 499:
        continue
    fig, ax = plt.subplots()
    ax.plot(psi, i_radial_en_flux_ExB_1d_over_time[i, :])
    ax.plot(psi, i_radial_en_flux_ExB_1d_over_time[-1, :])
    fig.savefig(f'{video_dir}/i_radial_en_flux_ExB_1d_over_time_{i}.png',
                bbox_inches='tight', dpi=300)
    plt.close()

flux_avg = Flux()
for flux_string in flux_strings:
    flux_avg.__dict__[flux_string] = np.zeros(len(psi))
with adios2.Stream(DATA_FILE, 'r') as data_stream:
    for i, _ in enumerate(data_stream.steps()):
        if i < 399:
            continue
        for flux_string in flux_strings:
            flux_avg.__dict__[flux_string] += data_stream.read(flux_string)

for flux_string in flux_strings:
    flux_avg.__dict__[flux_string] /= 100

avg_dir = os.path.join(plot_dir, 'time_average')
os.makedirs(avg_dir, exist_ok=True)
for flux_string in flux_strings:
    fig, ax = plt.subplots()
    ax.plot(psi, flux_avg.__dict__[flux_string]/ np.sqrt(e_grad_psi_sqr_1d) * e_gc_density_df_1d,
            label=flux_string)
    fig.savefig(f'{avg_dir}/time_average_{flux_string}.png',
                bbox_inches='tight', dpi=300)
    plt.close()

fig, ax = plt.subplots()
ax.plot(psi, i_grad_psi_sqr_1d)
fig.savefig(f'{plot_dir}/e_grad_psi_sqr_1d.png',
            bbox_inches='tight', dpi=300)
plt.close()

fig, ax = plt.subplots()
ax.plot(psi, i_gc_density_df_1d)
fig.savefig(f'{plot_dir}/e_gc_density_df_1d.png',
            bbox_inches='tight', dpi=300)
plt.close()

# Plot the 