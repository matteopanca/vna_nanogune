import numpy as np
import matplotlib.pyplot as plt

#-------------------- CLASS Definition --------------------

class SParameter:

	#CLASS VARIABLES
	n_params = 10
	corr_index = [[2, 4], [6, 8]]

	#CONSTRUCTOR
	#'f' is frequency, 'h' is field - the boolean field is for the Ref. Meas. (only 'f')
	def __init__(self, data, type=(1, 1), scan_type=('f', True), unit='Oe'):
		rows, cols = data.shape
		n_blocks = np.round(cols/self.n_params) #it should be a integer ('round' just to be sure)
		self.type = type
		self.scan_type = scan_type
		self.unit = unit
		
		if self.scan_type[0] == 'f':
			self.n_freq = int(rows)
			self.n_field = int(n_blocks)
			if self.scan_type[1]:
				self.n_field -=  1
				start_pos = self.n_params
			else:
				start_pos = 0
			self.freq = np.zeros(self.n_freq, dtype=np.float_)
			self.field = np.zeros(self.n_field, dtype=np.float_)
			for i in range(self.n_field):
				self.freq += data[:, start_pos+self.n_params*i]
				self.field[i] = data[0, start_pos+self.n_params*i+1]
			self.freq /= self.n_field
		elif self.scan_type[0] == 'h':
			self.n_freq = int(n_blocks)
			self.n_field = int(rows)
			if self.scan_type[1]:
				raise RuntimeError('Ref. Meas. not available in H mode')
				return None
			else:
				start_pos = 0
			self.freq = np.zeros(self.n_freq, dtype=np.float_)
			self.field = np.zeros(self.n_field, dtype=np.float_)
			for i in range(self.n_freq):
				self.freq[i] = data[0, start_pos+self.n_params*i]
				self.field += data[:, start_pos+self.n_params*i+1]
			self.field /= self.n_freq
		else:
			raise RuntimeError('Scan type not defined')
			return None
		self.freq /= 1.0e9 #Hz to GHz
		if self.unit == 'Oe':
			self.field *= 10 #mT to Oe
		
		self.re = np.zeros((self.n_freq, self.n_field), dtype=np.float_)
		self.im = np.zeros((self.n_freq, self.n_field), dtype=np.float_)
		if self.scan_type[0] == 'f':
			for i in range(self.n_field):
				self.re[:, i] = data[:, start_pos+self.corr_index[self.type[0]-1][self.type[1]-1]+self.n_params*i]
				self.im[:, i] = data[:, start_pos+1+self.corr_index[self.type[0]-1][self.type[1]-1]+self.n_params*i]
		else:
			for i in range(self.n_freq):
				self.re[i, :] = data[:, start_pos+self.corr_index[self.type[0]-1][self.type[1]-1]+self.n_params*i]
				self.im[i, :] = data[:, start_pos+1+self.corr_index[self.type[0]-1][self.type[1]-1]+self.n_params*i]
		self.amp = np.sqrt(self.re**2 + self.im**2)
		self.amp_dB = 20*np.log10(self.amp)
		self.phase = np.arctan2(self.im, self.re)
		self.names = {'r': self.re, 'i': self.im, 'a': self.amp, 'p': self.phase, 'ad': self.amp_dB}
		
		#Norm and Ref. Meas. (only 'f')
		self.re_norm = np.empty(0, dtype=np.float_)
		self.im_norm = np.empty(0, dtype=np.float_)
		self.amp_norm = np.empty(0, dtype=np.float_)
		self.amp_norm_dB = np.empty(0, dtype=np.float_)
		self.phase_norm = np.empty(0, dtype=np.float_)
		
		if self.scan_type[0] == 'h':
			self.re_norm = np.zeros((self.n_freq, self.n_field), dtype=np.float_)
			self.im_norm = np.zeros((self.n_freq, self.n_field), dtype=np.float_)
			self.amp_norm = np.zeros((self.n_freq, self.n_field), dtype=np.float_)
			self.phase_norm = np.zeros((self.n_freq, self.n_field), dtype=np.float_)
			for i in range(self.n_freq):
				self.re_norm[i, :] = self.re[i, :] - self.re[i, 0]
				self.im_norm[i, :] = self.im[i, :] - self.im[i, 0]
				self.amp_norm[i, :] = self.amp[i, :] - self.amp[i, 0]
				self.phase_norm[i, :] = self.phase[i, :] - self.phase[i, 0]
			self.amp_norm_dB = 20*np.log10(self.amp_norm)
		elif self.scan_type[1]:
			self.re_ref = data[:, self.corr_index[self.type[0]-1][self.type[1]-1]]
			self.im_ref = data[:, 1+self.corr_index[self.type[0]-1][self.type[1]-1]]
			self.amp_ref = np.sqrt(self.re_ref**2 + self.im_ref**2)
			self.amp_ref_dB = 20*np.log10(self.amp_ref)
			self.phase_ref = np.arctan2(self.im_ref, self.re_ref)
			self.amp_norm = np.zeros((self.n_freq, self.n_field), dtype=np.float_)
			self.phase_norm = np.zeros((self.n_freq, self.n_field), dtype=np.float_)
			for i in range(self.n_field):
				self.amp_norm[:, i] = self.amp[:, i]/self.amp_ref
				self.phase_norm[:, i] = self.phase[:, i] - self.phase_ref
			self.re_norm = self.amp_norm*np.cos(self.phase_norm)
			self.im_norm = self.amp_norm*np.sin(self.phase_norm)
			self.amp_norm_dB = 20*np.log10(self.amp_norm)
		
		self.names['rn'] = self.re_norm
		self.names['in'] = self.im_norm
		self.names['an'] = self.amp_norm
		self.names['pn'] = self.phase_norm
		self.names['and'] = self.amp_norm_dB
	
	#----- METHODS -----
	
	def plot(self, ax, plot_type='an', xAxis_type='h', N=128):
		myMap = plt.get_cmap('jet', N)
		
		if xAxis_type == 'h': #field
			xAxis_data = self.field
		elif xAxis_type == 'i': #index
			xAxis_data = np.arange(len(self.field))
		else:
			raise RuntimeError('X-Axis type not defined')
			return []
		#out_plot = ax.pcolormesh(xAxis_data, self.freq, self.names[plot_type], cmap=myMap, shading='flat')
		out_plot = ax.contourf(xAxis_data, self.freq, self.names[plot_type], N, cmap=myMap)
		ax.set_title('S({:d},{:d}) - {:s}'.format(self.type[0], self.type[1], plot_type))
		if xAxis_type == 'h': #field
			if self.unit == 'Oe':
				ax.set_xlabel('H (Oe)')
			elif self.unit == 'mT':
				ax.set_xlabel('$\mu_0$H (mT)')
			elif self.unit == 'A':
				ax.set_xlabel('I (A)')
		elif xAxis_type == 'i': #index
			ax.set_xlabel('Index')
		ax.set_ylabel('f (GHz)')
		plt.colorbar(out_plot, ax=ax)
		return out_plot
	
	def plot_slice(self, ax, plot_type='an', slice_type='f', plot_each=1, N=128):
		myMap = plt.get_cmap('jet', N)
		
		out_plots = []
		if slice_type == 'f':
			tot_curves = self.n_field
		elif slice_type == 'h':
			tot_curves = self.n_freq
		else:
			raise RuntimeError('Slice type not defined')
			return out_plots
		n_plots = int(np.ceil(tot_curves/plot_each))
		if n_plots == 0: #maybe it's never happening...
			return out_plots
		
		if slice_type == 'f':
			for i in range(n_plots):
				gen_color = myMap(i/(n_plots-1))
				out_plot = ax.plot(self.freq, self.names[plot_type][:, plot_each*i], '-', color=gen_color, label='{:.1f} {:s}'.format(self.field[plot_each*i], self.unit))
				out_plots.append(out_plot)
			ax.set_title('S({:d},{:d}) - {:s}'.format(self.type[0], self.type[1], plot_type))
			ax.set_xlabel('f (GHz)')
		else:
			for i in range(n_plots):
				gen_color = myMap(i/(n_plots-1))
				out_plot = ax.plot(self.field, self.names[plot_type][plot_each*i, :], '-', color=gen_color, label='{:.3f} GHz'.format(self.freq[plot_each*i]))
				out_plots.append(out_plot)
			ax.set_title('S({:d},{:d}) - {:s}'.format(self.type[0], self.type[1], plot_type))
			if self.unit == 'Oe':
				ax.set_xlabel('H (Oe)')
			elif self.unit == 'mT':
				ax.set_xlabel('$\mu_0$H (mT)')
			elif self.unit == 'A':
				ax.set_xlabel('I (A)')
		ax.grid(True)
		#leg = ax.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.) #http://matplotlib.org/users/legend_guide.html
		#leg.draggable(True)
		return out_plots

#-------------------- FUNCTIONS --------------------

def fmr_kittel(h, m, n, unit='Oe'):
	#m in A/m
	#n[2] is the applied field direction
	mu0 = np.pi*4.0e-7
	gamma = (2.0023*1.6021766e-19/(2*9.109383e-31))/(np.pi*2.0e9) #GHz/T
	if unit == 'Oe':
		h_conv = np.complex_(1e-4*h/mu0) #from Oe to A/m
	elif unit == 'mT':
		h_conv = np.complex_(1e-3*h/mu0) #from mT to A/m
	else:
		raise RuntimeError('Unit not yet supported')
		return []
	kittel_freq = mu0*gamma*np.real(np.sqrt((h_conv + (n[0] - n[2])*m)*(h_conv + (n[1] - n[2])*m)))
	return kittel_freq