"""
My first attempt to make a python routine for analysing XGC data.

This routine plots the ion density (iden) over the mesh of the XGC simulation.
"""
import os
import adios2
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
import numpy as np

# File paths
mesh_file = '/global/homes/q/qt4627/XGC_projects/neoclassical/run_xgca_gpu_batch/xgc.mesh.bp'
data_file_pattern = '/global/homes/q/qt4627/XGC_projects/neoclassical/run_xgca_gpu_batch/xgc.f2d.{:05d}.bp'
data_files = [data_file_pattern.format(i) for i in range(10, 5001, 10)]
repo_dir = os.path.dirname(os.path.abspath(__file__))
plot_dir = os.path.join(repo_dir, 'plots')
os.makedirs(plot_dir, exist_ok=True)

# Read the mesh data
with adios2.Stream(mesh_file, 'r') as mesh_stream:
    for _ in mesh_stream.steps():
        rz_data = mesh_stream.read('rz')
        connect_list = mesh_stream.read('nd_connect_list')

        # track current step
        print(f"Current step is {mesh_stream.current_step()}")

        # inspect variables in current step
        for name, info in mesh_stream.available_variables().items():
            print("variable_name: " + name, end=" ")
            for key, value in info.items():
                print("\t" + key + ": " + value, end=" ")
            print()


# Extract the R (radius) and Z (height) coordinates
R = rz_data[:, 0]
Z = rz_data[:, 1]

# Create a list of triangles for the mesh
triangles = []
for triangle in connect_list:
    triangles.append([(R[triangle[0]], Z[triangle[0]]), 
                      (R[triangle[1]], Z[triangle[1]]), 
                      (R[triangle[2]], Z[triangle[2]])])
    
with adios2.Stream(data_files[0], 'r') as data_stream:
    for _ in data_stream.steps():
        # track current step
        print(f"Current step is {data_stream.current_step()}")

        # inspect variables in current step
        for name, info in data_stream.available_variables().items():
            print("variable_name: " + name, end=" ")
            for key, value in info.items():
                print("\t" + key + ": " + value, end=" ")
            print()

        ion_density = data_stream.read('i_den')
        max_density = np.max(ion_density)
        min_density = np.min(ion_density)

# Loop to get max and min density
for i, data_file in enumerate(data_files):
    print(f'Processing frame {i+1} of {len(data_files)}')
    with adios2.Stream(data_file, 'r') as data_stream:
        for _ in data_stream.steps():
            ion_density = data_stream.read('i_den')
    if np.max(ion_density) > max_density:
        max_density = np.max(ion_density)
    if np.min(ion_density) < min_density:
        min_density = np.min(ion_density)

# Loop to plot the mesh with ion density
for i, data_file in enumerate(data_files):
    print(f'Processing frame {i+1} of {len(data_files)}')
    if i % 100 != 0 and i != 499:
        continue
    with adios2.Stream(data_file, 'r') as data_stream:
        for _ in data_stream.steps():
            ion_density = data_stream.read('i_den')
    ion_density_avg = (ion_density[connect_list[:, 0]] +
                       ion_density[connect_list[:, 1]] +
                       ion_density[connect_list[:, 2]]) / 3
    fig, ax = plt.subplots(figsize=(10, 10))
    mesh = PolyCollection(triangles, array=ion_density_avg, edgecolor='k')
    # Set max and min for colorbar
    mesh.set_clim(vmin=min_density, vmax=max_density)
    ax.add_collection(mesh)
    ax.set_xlabel('R (m)')
    ax.set_ylabel('Z (m)')
    ax.set_title(f'Ion Density (i_den) over XGC Mesh - Frame {i+1}')
    ax.grid(True)
    ax.axis('equal')
    ax.set_xlim([R.min(), R.max()])
    ax.set_ylim([Z.min(), Z.max()])
    cbar = plt.colorbar(mesh, ax=ax, orientation='vertical')
    cbar.set_label('Ion Density (i_den)')
    fig.savefig(f'{plot_dir}/frame_{i+1}.png')
    plt.close()
