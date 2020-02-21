#!/usr/bin/env python
# coding: utf-8

# # Equilibrium

# In[1]:


#-----Import some essential packages

from __future__ import division
import hoomd
import hoomd.md

#-----Some important variables

p_max = 1.4;
t_max = 6.4;
copies = 4;
steps = 1e5;
#-----Crea un contexto de simulación

hoomd.context.initialize("--mode=gpu");

#-----Extrae la configuración del centro de masa de las partículas

snap = hoomd.data.gsd_snapshot("T_CM&NP_6.4_P_1.4_ramp.gsd",frame = -1)
snap.replicate(copies,copies,copies)
system = hoomd.init.read_snapshot(snap)

#-----Define cada mesógeno en el marco de referencia local de cada centro de masa.

rigid = hoomd.md.constrain.rigid();
rigid.set_param('M', 
                types=['A']*8,
                positions=[(-4,0,0),(-3,0,0),(-2,0,0),(-1,0,0),
                           (1,0,0),(2,0,0),(3,0,0),(4,0,0)]);

#-----Declara que las moléculas creadas son cuerpos rígidos

rigid.create_bodies();

#-----Define la energía potencial

nl = hoomd.md.nlist.tree();

lj = hoomd.md.pair.lj(r_cut = 3.5, nlist = nl)
lj.set_params(mode = 'shift')

#-----Define la interacción entre las especies de la simulación

lj.pair_coeff.set('NP','NP', epsilon = 1.0, sigma = 5.0);
lj.pair_coeff.set('M' ,'M' , epsilon = 1.0, sigma = 1.0);
lj.pair_coeff.set('A' ,'A' , epsilon = 1.0, sigma = 1.0);
lj.pair_coeff.set('M' ,'A' , epsilon = 1.0, sigma = 1.0);
lj.pair_coeff.set('NP','M' , epsilon = 1.0, sigma = 3.0);
lj.pair_coeff.set('NP','A' , epsilon = 1.0, sigma = 3.0);

#-----Select an standard integrator

hoomd.md.integrate.mode_standard(dt = 0.005);

#------Define some groups and make their union.

nanoparticles = hoomd.group.type(name = 'Nano_Particles', type = 'NP');
mesogens = hoomd.group.rigid_center();
groupNP_mes = hoomd.group.union(name = 'NP_Mes', a = nanoparticles, b = mesogens);

# In[2]:

#----Integrate using NPT

npt = hoomd.md.integrate.npt(group = groupNP_mes, kT = t_max, tau = 15.0, tauP = 15.0, P = p_max);

#-----Write output and Run the Simulation

log_file = "T_" + str(t_max) + "_P_" + str(p_max) + "_equilibrium.log"
gsd_file = "T_" + str(t_max) + "_P_" + str(p_max) + "_equilibrium.gsd" 
meso_gsd_file = "T_CM_" + str(t_max) + "_P_" + str(p_max) + "_equilibrium.gsd"

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
               group = mesogens,
               overwrite = True); 


# In[3]:


hoomd.run(steps)


# In[4]:


system.get_metadata()
