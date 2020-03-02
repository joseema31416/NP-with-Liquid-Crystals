#!/usr/bin/env python
# coding: utf-8

# # Temperature Ramp

# ## Mesogens with Nanoparticles, T: 5.0 -> 5.2

# In[1]:


#-----Import essential packages.

from __future__ import division
import hoomd
import hoomd.md

#-----Define important variables.

p_max = 2.8;
t_0   = 5.0; 
t_1   = 5.2;
steps_ramp = 5e4;

#-----Declare a simulation context.

hoomd.context.initialize("--mode=gpu");

#-----Initialize from a .gsd file.

system = hoomd.init.read_gsd("T_CM&NP_5.0_P_2.8_ramp.gsd", frame = -1);

#-----Define each mesogen in the local frame of reference of each rigid body.

rigid = hoomd.md.constrain.rigid();
rigid.set_param('M', 
                types = ['A']*8,
                positions = [(-4,0,0),(-3,0,0),(-2,0,0),(-1,0,0),
                           (1,0,0),(2,0,0),(3,0,0),(4,0,0)]);

#-----Create the mesogens.

rigid.create_bodies();

#-----Define the potential energy.

nl = hoomd.md.nlist.tree();

lj = hoomd.md.pair.lj(r_cut = 3.5, nlist = nl)
lj.set_params(mode = 'shift')

#-----Declare interactions.

lj.pair_coeff.set('NP','NP', epsilon = 1.0, sigma = 5.0);
lj.pair_coeff.set('M' ,'M' , epsilon = 1.0, sigma = 1.0);
lj.pair_coeff.set('A' ,'A' , epsilon = 1.0, sigma = 1.0);
lj.pair_coeff.set('M' ,'A' , epsilon = 1.0, sigma = 1.0);
lj.pair_coeff.set('NP','M' , epsilon = 1.0, sigma = 3.0);
lj.pair_coeff.set('NP','A' , epsilon = 1.0, sigma = 3.0);

#-----Select an standard integrator.

hoomd.md.integrate.mode_standard(dt = 0.005);

#------Define some groups and make their union.

nanoparticles = hoomd.group.type(name = 'Nano_Particles', type = 'NP');
mesogens = hoomd.group.rigid_center();
groupNP_mes = hoomd.group.union(name = "NP_Mes", a = nanoparticles, b = mesogens);

#----Integrate using an NPT integrator.

temp = hoomd.variant.linear_interp(points = [(0,t_0), (steps_ramp, t_1)]);

npt = hoomd.md.integrate.npt(group = groupNP_mes, kT = temp, tau = 2.0, tauP = 3.0, P = p_max);
npt.randomize_velocities(seed=42)

#-----Save .log y .gsd data.

log_file = "T_" + str(t_1) + "_P_" + str(p_max) + "_ramp.log"
gsd_file = "T_" + str(t_1) + "_P_" + str(p_max) + "_ramp.gsd" 
meso_gsd_file = "T_CM&NP_" + str(t_1) + "_P_" + str(p_max) + "_ramp.gsd"

log = hoomd.analyze.log(filename = log_file,
                         quantities = ['num_particles',
                                     'ndof',
                                     'translational_ndof',
                                     'rotational_ndof',
                                     'potential_energy',
                                     'kinetic_energy',
                                     'translational_kinetic_energy',
                                     'rotational_kinetic_energy',
                                     'temperature',
                                     'pressure',
                                      'volume'],
                         period = 1e3,
                         overwrite = True);
gsd = hoomd.dump.gsd(gsd_file,
               period = 1e3,
               group = hoomd.group.all(),
               overwrite = True); 
meso_gsd = hoomd.dump.gsd(meso_gsd_file,
               period = 1e3,
               group = groupNP_mes,
               overwrite = True); 


# In[2]:


#-----Run the simulation.

hoomd.run(steps_ramp)


# In[3]:


#-----Get density.

system.get_metadata()


# In[4]:


#-----Get volume.

system.box.get_volume()
