#!/usr/bin/env python
# coding: utf-8

# # Mesogens with NP | Equilibriums

# ## Temperature: 8.4 | Cluster Run

# ### Date: 15/01/2019 | System P = 2.3, Expected value of $T_c$ : 8.03 

from __future__ import division
import hoomd
import hoomd.md

#-----Define relevant variables

p_max = 2.3;
t_max = 8.4;
copies = 1;
steps_run = 2e5;
init_file = "T_CM&NP_" + str(t_max) + "_P_" + str(p_max) + "_ramp.gsd"

#-----Define a simulation context

    #-----CPU run

#hoomd.context.initialize("--mode=cpu");
    
    #-----GPU run

hoomd.context.initialize("--mode=gpu");

#-----Extract the configuration of the system and expand the system

snap = hoomd.data.gsd_snapshot(init_file, frame = -1);
snap.replicate(copies,copies,copies);
system = hoomd.init.read_snapshot(snap);

#-----Define each mesogen in the local reference frame of each center of mass

rigid = hoomd.md.constrain.rigid();
rigid.set_param('M', 
               types = ['A']*8,
               positions = [(-4,0,0),(-3,0,0),(-2,0,0),(-1,0,0),
                            (1,0,0),(2,0,0),(3,0,0),(4,0,0)]);

#-----Declare molecules as rigid bodies

rigid.create_bodies();

#-----Define the potential energy

nl = hoomd.md.nlist.tree();
lj = hoomd.md.pair.lj(r_cut = 3.5, nlist = nl);
lj.set_params(mode = 'shift')

#------Define the interaction

lj.pair_coeff.set('NP','NP', epsilon = 1.0, sigma = 5.0);
lj.pair_coeff.set('M', 'M', epsilon = 1.0, sigma = 1.0);
lj.pair_coeff.set('A', 'A', epsilon = 1.0, sigma = 1.0);
lj.pair_coeff.set('M', 'A', epsilon = 1.0, sigma = 1.0);
lj.pair_coeff.set('NP', 'M', epsilon = 1.0, sigma = 3.0);
lj.pair_coeff.set('NP', 'A', epsilon = 1.0, sigma = 3.0);

#------Select an standar integrator

hoomd.md.integrate.mode_standard(dt = 0.005);

#-----Define some groups and make their union

nanoparticles = hoomd.group.type(name = 'NPs', type = 'NP');
mesogens = hoomd.group.rigid_center();
groupNP_mes = hoomd.group.union(name = 'NP_Mes', a = nanoparticles, b = mesogens);

#-----Integrate using NPT

npt = hoomd.md. integrate.npt(group = groupNP_mes, kT = t_max, tau = 12.0, tauP = 12.0, P = p_max);

#-----Save data

log_file = "T_" + str(t_max) + "_P_" + str(p_max) + "_equilibrium.log"
gsd_file = "T_" + str(t_max) + "_P_" + str(p_max) + "_equilibrium.gsd"
meso_gsd_file = "T_CM_" + str(t_max) + "_P_" + str(p_max) + "_equilibrium.log"

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
                       period = 1e2,
                       overwrite = True);
gsd = hoomd.dump.gsd(gsd_file, period = 1e2, group = hoomd.group.all(), overwrite = True);
meso_gsd = hoomd.dump.gsd(meso_gsd_file, period=1e2, group = mesogens, overwrite = True);

#-----Run part of the simulation(5e4 steps)

hoomd.run(steps_run / 4)

#-----Update coupling parameters

npt.set_params(tau = 12.1, tauP = 12.1)

#-----Continue the simulation(1e5 steps)

hoomd.run(steps_run / 4)

#-----Update coupling parameters

npt.set_params(tau = 12.2.0, tauP = 12.2)

#-----Continue the simulation(1.5e5 steps)

hoomd.run(steps_run / 4)

#-----Update coupling parameters

npt.set_params(tau = 12.3, tauP = 12.3)

#-----Finish the simulation(2e5 steps)

hoomd.run(steps_run / 4)

#-----Get volume and density information.

system.box.get_volume()
system.get_metadata()