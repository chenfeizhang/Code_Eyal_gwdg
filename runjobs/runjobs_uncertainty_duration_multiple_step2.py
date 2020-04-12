'''

Collect data and estimate the distribution of spike detection delay.

'''

hostname = 'chenfei'
model = 'GE_diam_0' 
codedirectory = '..'
datafolder = '/scratch/%s/%s/'%(hostname, model)
electrode_place = 'soma'
import numpy as np
import scipy.io as sio
import os
import matplotlib.pyplot as plt
runs = 400
for tau in (5,): 
  for posNa in (47,): 
    for fr in (519, ):
      sdd_list = []
      appendix = 'tau%dfr%dposNa%s'%(tau, fr, posNa)
      foldername = datafolder + 'Uncertainty/' + appendix + '/' # appendix with subthreshold
      data = sio.loadmat('../runjobs/%s_tau%s_mean_std_cv_%s.mat'%(model, tau, electrode_place))
      mean_list = data['mean'][0]
      std_list = data['std'][0]
      k_id_begin = 40
      k_id_end = 50
      for k_id in range(k_id_begin, k_id_end, 10):
          if os.path.isfile(foldername + 'Series%s'%(k_id)+'/delay.mat') == True:
            data = sio.loadmat(foldername + 'Series%s'%(k_id)+'/delay.mat')
            delay = data['delay'][0]
            len_delay_all = len(delay)
            delay = np.array(delay)
            delay = delay[delay<20]
            bin_num = 200
            bins = np.arange(bin_num+1)*20.0/bin_num
            hist, bin_edges= np.histogram(delay, bins)
            sio.savemat(foldername + 'Series%s'%(k_id)+'/hist.mat', {'bin':bin_edges[1:], 'p':hist/len_delay_all/(20/bin_num)})
            plt.plot(bin_edges[1:], hist/len_delay_all/(20.0/bin_num), label='std = %fnA'%(std_list[k_id]))
          else:
            delay = []
            for i in range(1, runs+1):
              if os.path.isfile(foldername + 'Series%s'%(k_id) + '/spike_detection_duration_%s.npy'%(i)) == True:
                data = np.load(foldername + 'Series%s'%(k_id) + '/spike_detection_duration_%s.npy'%(i),allow_pickle=True)
                delay += list(data)
              else: continue
            data = {'delay':delay}
            sio.savemat(foldername + 'Series%s'%(k_id)+'/delay.mat', data)
            len_delay_all = len(delay)
            delay = np.array(delay)
            delay = delay[delay<20]
            bins = np.arange(101)/100.0*20
            hist, bin_edges= np.histogram(delay, bins)
            sio.savemat(foldername + 'Series%s'%(k_id)+'/hist.mat', {'bin':bin_edges[1:], 'p':hist/len_delay_all/(20/100)})
