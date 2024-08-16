import matplotlib.axes
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from .Common import H, datatype

class Event() :
    def __init__(self) -> None:
        self.current_df = pd.DataFrame()
        self.event_path = str()
        self.summary_df = pd.DataFrame()
        self.baseline = np.float64()
        self.sample_type = str()
        self.voltage = np.float64()
        self.id = np.int64()
        self.duration_time = np.int64()
        self.eventstart_time = np.int64()

        self.if_current_set_flag = False
        self.if_summary_set_flag = False
        pass

    def set_current_csv(self, path:str) -> None :
        self.event_path = path
        self.current_df = pd.read_csv(path, header=None)
        if self.current_df.shape[1] == 3 :
            self.current_df.columns = [H.time_us, H.current_pA, H.fitted_current_pA]
        elif self.current_df.shape[1] == 4 :
            self.current_df.columns = [H.time_us, H.current_pA, H.fitted_current_pA, H.curve_fitted_current_pA]
        else :
            raise ValueError("Unsupported number of columns: " + str(self.current_df.columns))
        self.if_current_set_flag = True
        if self.if_summary_set_flag :
            self.current_data = np.abs(self.current_df.loc[:,H.current_pA].values)
            self.zeroed_current_data = self.current_data - self.baseline
            self.delta_g_data = self.zeroed_current_data / self.voltage
            self.normalized_current = self.current_data / self.baseline
            self.normalized_time = (self.current_df[H.time_us]-self.eventstart_time)/self.duration_time
            self.normalized_time = self.normalized_time.values
        pass

    def set_summary_df(self, df) -> None :
        self.summary_df = df
        self.baseline = self.summary_df.loc[:,H.effective_baseline_pA].values[0]
        self.sample_type = self.summary_df.loc[:,H.sample_type].values[0]
        self.voltage = self.summary_df.loc[:,H.Voltage].values[0]
        self.id = self.summary_df.loc[:,H.id].values[0]
        self.duration_time = self.summary_df.loc[:,H.duration_us].values[0]
        self.eventstart_time = int(self.summary_df.loc[:,H.intra_crossing_times_us].values[0].split(';')[0])
        self.if_summary_set_flag = True
        pass

'''
plot_single_event(event: Event, data_type=datatype.raw, ax=None) -> None : 
この関数はEventクラスのインスタンスを受け取り，そのインスタンスのcurrent_dfをプロットする。
    data_typeにrawを指定すると生データ
    zeroedを指定するとベースラインを引いたデータ
    delta_gを指定するとコンダクタンス値の変化を求めたデータ
をプロットする。
ax = axで指定のaxにplotする。Noneの場合は新しいfig, axを作成する。
'''

def plot_single_event(event: Event, data_type=datatype.raw, ax=None, seps = 2000, extract=False, **kwargs) -> matplotlib.axes.Axes :
    if ax == None :
        fig, ax = plt.subplots()

    if data_type == datatype.raw :
        xs = event.current_df[H.time_us]
        ys = event.current_df[H.current_pA]
        y_label = 'Current (pA)'
        normalized = False

    elif data_type == datatype.zeroed :
        xs = event.normalized_time
        ys = event.zeroed_current_data
        y_label = 'Zeroed Current (pA)'
        normalized = True

    elif data_type == datatype.delta_g :
        xs = event.normalized_time
        ys = event.delta_g_data
        y_label = 'delta_g (nS)'
        normalized = True
    
    elif data_type == datatype.normalized :
        xs = event.normalized_time
        ys = event.normalized_current
        y_label = 'Normalized Current'
        normalized = True
    else :
        raise ValueError("Unsupported data type: " + data_type)
    
    if extract :
        xs, ys = extract_seps(xs, ys, seps)
    
    ax.plot(xs, ys, **kwargs)
    if normalized :
        ax.set_xlabel('Normalized Time')
    else :
        ax.set_xlabel('Time (us)')
    ax.set_ylabel(y_label)
    ax.set_title(f'{event.sample_type} {event.voltage} mV {event.id}')
    return ax

def extract_seps(xs, ys, seps) :
    sep = 1/seps
    ind = np.where(xs[1:]%sep < xs[:-1]%sep)[0]
    xs = xs[ind]
    ys = ys[ind]
    return xs, ys
