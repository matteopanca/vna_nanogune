import vna_package as vna
import numpy as np
import matplotlib.pyplot as plt
import sys

plt.close('all')

#----- INPUT ARGS. -----
input_file = sys.argv[1]
sweep_type = sys.argv[2]
ref_meas = bool(int(sys.argv[3]))
unit = sys.argv[4]
#-----------------------
if sweep_type == 'h':
	ref_meas = False
scan_type = (sweep_type, ref_meas)
input_file = vna.out_path + input_file

data = np.genfromtxt(input_file, skip_header=1)
s11 = vna.SParameter(data, type=(1, 1), scan_type=scan_type, unit=unit)
s12 = vna.SParameter(data, type=(1, 2), scan_type=scan_type, unit=unit)
s21 = vna.SParameter(data, type=(2, 1), scan_type=scan_type, unit=unit)
s22 = vna.SParameter(data, type=(2, 2), scan_type=scan_type, unit=unit)

#Kittel
Ms = 1.4e6 #A/m - Co
n = (1, 0, 0) #(X, Y, Z) - n[2] is the applied field direction
kittel_freq = vna.fmr_kittel(s11.field, Ms, n, s11.unit)

#Plots
to_plot = 'an'
xAxis_type = 'f'
ax1 = []
fig1 = plt.figure(figsize=(16,10))
ax1.append(fig1.add_subplot(2,2,1))
s11.plot(ax1[0], to_plot, xAxis_type)
ax1[0].plot(s11.field, kittel_freq, '-ok')
ax1.append(fig1.add_subplot(2,2,2))
s12.plot(ax1[1], to_plot, xAxis_type)
ax1[1].plot(s12.field, kittel_freq, '-ok')
ax1.append(fig1.add_subplot(2,2,3))
s21.plot(ax1[2], to_plot, xAxis_type)
ax1[2].plot(s21.field, kittel_freq, '-ok')
ax1.append(fig1.add_subplot(2,2,4))
s22.plot(ax1[3], to_plot, xAxis_type)
ax1[3].plot(s22.field, kittel_freq, '-ok')
fig1.tight_layout()

#to_plot = 'an'
slice_type = 'f'
plot_each = 2
ax2 = []
fig2 = plt.figure(figsize=(16,10))
ax2.append(fig2.add_subplot(2,2,1))
s11.plot_slice(ax2[0], to_plot, slice_type, plot_each)
ax2.append(fig2.add_subplot(2,2,2))
s12.plot_slice(ax2[1], to_plot, slice_type, plot_each)
ax2.append(fig2.add_subplot(2,2,3))
s21.plot_slice(ax2[2], to_plot, slice_type, plot_each)
ax2.append(fig2.add_subplot(2,2,4))
s22.plot_slice(ax2[3], to_plot, slice_type, plot_each)
#leg = ax2[3].legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.) #http://matplotlib.org/users/legend_guide.html
leg = ax2[3].legend(loc='lower left')
leg.draggable(True)
fig2.tight_layout()

plt.show()