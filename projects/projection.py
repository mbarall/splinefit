import sys
from splinefit import msh
import splinefit as sf
import numpy as np
import helper
import matplotlib.pyplot as plt
import pickle

inputfile = sys.argv[1]
outputfile = sys.argv[2]
if len(sys.argv) < 4:
    figfile = None
else:
    figfile = sys.argv[3]

coords, tris = sf.msh.read(inputfile)
pcl_xyz = coords[:,1:]
pcl_xyz, mu, std = sf.fitting.normalize(pcl_xyz)

edges = sf.msh.get_data(tris)

bnd_xyz = helper.close_boundary(pcl_xyz[edges[:,0],:])


basis = sf.fitting.pca(bnd_xyz, num_components=3)
proj_basis = sf.fitting.pca(bnd_xyz, num_components=2)
ax = helper.plot_points(bnd_xyz)
bnd_xy = sf.fitting.projection(bnd_xyz, proj_basis)
pcl_xy = sf.fitting.projection(pcl_xyz, proj_basis)
helper.plot_points(bnd_xyz, ax, 'k')
helper.plot_points(bnd_xy, ax, 'b-')
helper.plot_basis(basis, ax)
plt.savefig(figfile)
data = helper.Struct()
data.mu = mu
data.std = std
data.basis = basis
data.proj_basis = proj_basis
data.edges = edges
data.bnd_xyz = bnd_xyz
data.bnd_xy = bnd_xy
data.pcl_xyz = pcl_xyz
data.pcl_xy = pcl_xy
pickle.dump(data, open('.'.join(outputfile.split('.')[:-1]) + '.p', 'wb'))
