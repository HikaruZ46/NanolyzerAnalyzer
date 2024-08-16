import matplotlib.axes
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import tqdm
import os
from .Common import *
from .EventCommander import Event, plot_single_event

class EventGroup() :
    def __init__(self) -> None:
        self.event_list = []
        self.event_group_df = pd.DataFrame()

    def set_csv(self, path: str, sample: str, voltage) -> None :
        df = pd.read_csv(path)
        df.loc[:,H.file_name] = df[H.id].apply(lambda x: os.path.join(os.path.dirname(path), 'events', f'event_{int(x):08}.csv'))
        df.loc[:, H.sample_type] = sample
        df.loc[:, H.Voltage] = voltage
        self.set_df(df)
        pass

    
    def set_df(self, df: pd.DataFrame) -> None :
        self.event_group_df = df
        self.event_group_df.loc[:,H.effective_baseline_pA] = np.abs(self.event_group_df[H.effective_baseline_pA])
        self.event_group_df.loc[:, H.average_fractional_blockade] = self.event_group_df[H.average_blockage_pA] / self.event_group_df[H.effective_baseline_pA]
        self.event_group_df.loc[:, H.max_fractional_blockade] = self.event_group_df[H.max_blockage_pA] / self.event_group_df[H.effective_baseline_pA]
        self.event_group_df[H.average_delta_g] = self.event_group_df[H.average_blockage_pA]/self.event_group_df[H.Voltage]
        self.event_group_df[H.max_delta_g] = self.event_group_df[H.max_blockage_pA]/self.event_group_df[H.Voltage]
        self.event_group_df.loc[:,H.log_duration_us] = np.log10(self.event_group_df[H.duration_us])
        self.event_group_df[H.log_max_blockage_duration_us] = np.log10(self.event_group_df[H.max_blockage_duration_us])
        self.event_group_df[H.log_min_blockage_duration_us] = np.log10(self.event_group_df[H.min_blockage_duration_us])
        pass

    def summary(self, **kwargs) -> None :
        # print(self.event_group_df.describe())
        print(f'sample_type: {np.unique(self.event_group_df[H.sample_type].values)}')
        print(f'Voltage: {np.unique(self.event_group_df[H.Voltage].values)}')
        print(f'Number of events: {self.event_group_df.shape[0]}')
        print(f'Average duration: {self.event_group_df[H.duration_us].mean()}')
        print(f'Average blockage: {self.event_group_df[H.average_blockage_pA].mean()}')
        self.summary_plot(**kwargs)
        plt.show()
        pass

    def summary_plot(self, ax=None, hue = H.Voltage, **kwargs) :
        if ax == None :
            fig, ax = plt.subplots()
        sns.scatterplot(data=self.event_group_df, x=H.duration_us, y=H.average_blockage_pA, hue=hue, ax=ax, **kwargs)
        ax.set_xscale('log')
        return ax

def read_events_csv(path:str, sample:str, voltage) -> EventGroup :
    this_event_group = EventGroup()
    this_event_group.set_csv(path, sample, voltage)
    return this_event_group

def merge_event_groups(event_group_list : list) -> EventGroup :
    this_event_group = EventGroup()
    df = pd.concat([event_group.event_group_df for event_group in event_group_list], axis=0, ignore_index=True)
    this_event_group.set_df(df)
    return this_event_group

def split_event_group(event_group: EventGroup, N: int) -> list:
    """
    Split an EventGroup into multiple EventGroups, each containing at most N events.
    
    Args:
    event_group (EventGroup): The original EventGroup to be split.
    N (int): The maximum number of events each split EventGroup should contain.
    
    Returns:
    list: A list of EventGroups, each with at most N events.
    """
    split_event_groups = []
    
    # Split the DataFrame into chunks of size N
    df_chunks = [event_group.event_group_df.iloc[i:i + N] for i in range(0, len(event_group.event_group_df), N)]
    
    # Create a new EventGroup for each chunk and add it to the list
    for chunk in df_chunks:
        new_event_group = EventGroup()
        new_event_group.set_df(chunk)
        split_event_groups.append(new_event_group)
    
    return split_event_groups

'''
filter_event_group(event_group : EventGroup, filter_dict : dict) -> EventGroup :
この関数はEventGroupクラスのインスタンスとフィルター条件を受け取り，条件に合致するEventGroupを返す。
filter_dictは以下のようになる。
{
    'sample_type' : 'H2A',
    'Voltage' : 300,
    'id' : {
        'gt' : 100,
        'lt' : 200
    }
}
この場合はsample_typeがH2AでVoltageが300でidが100より大きく200より小さいものを返す。

'''


def filter_event_group(event_group: EventGroup, filter_dict: dict) -> EventGroup:
    df = event_group.event_group_df
    for key, value in filter_dict.items():
        if isinstance(value, dict):
            for op, val in value.items():
                if op == "gt":
                    df = df.loc[df[key] > val]
                elif op == "lt":
                    df = df.loc[df[key] < val]
                elif op == "gte":
                    df = df.loc[df[key] >= val]
                elif op == "lte":
                    df = df.loc[df[key] <= val]
                elif op == "eq":
                    df = df.loc[df[key] == val]
                elif op == "neq":
                    df = df.loc[df[key] != val]
                elif op == "in":
                    # シーケンス型に対応
                    if isinstance(val, (list, tuple, np.ndarray, pd.Series)):
                        df = df[df[key].isin(val)]
                    else:
                        raise ValueError(f"'in' operator requires a list, tuple, ndarray, or Series, got {type(val).__name__}")
                else:
                    raise ValueError(f"Unsupported operator: {op}")
        else:
            df = df.loc[df[key] == value]
    
    df = df.reset_index(drop=True)
    this_event_group = EventGroup()
    this_event_group.set_df(df)
    return this_event_group


'''
overlay_event_group(event_group : EventGroup, data_type = datatype.zeroed, ax = None, alpha = 0.05, lw = 0.05, color = 'C0', **kwargs) -> matplotlib.axes._axes.Axes :
この関数はEventGroupクラスのインスタンスを受け取り，そのインスタンスの全てのイベントを重ねてプロットする。（いわゆる重ね合わせ）
    data_typeにrawを指定すると生データ（baselineの補正なし）
    zeroedを指定するとベースラインを引いたデータ
    delta_gを指定するとコンダクタンス値の変化を求めたデータ
をプロットする。colorを指定しないとプロットごとに色が変わる可能性があるため，デフォルトではC0を指定している。
'''

def overlay_event_group(event_group : EventGroup,
                        data_type = datatype.zeroed,
                        ax = None,
                        alpha = 0.05,
                        lw = 0.05,
                        color = 'C0',
                        seps = 2000,
                        **kwargs) -> matplotlib.axes._axes.Axes :
    if ax == None :
        fig, ax = plt.subplots()
    for i in tqdm.tqdm(range(event_group.event_group_df.shape[0]), desc='Overlaying events') :
        event = get_single_event(event_group,
                                 event_group.event_group_df.loc[i, H.sample_type],
                                 event_group.event_group_df.loc[i, H.Voltage],
                                 event_group.event_group_df.loc[i, H.id])
        plot_single_event(event,data_type=data_type, ax=ax, alpha=alpha, lw=lw, color = color, seps = seps, **kwargs)
    ax.set_title(f'{event_group.event_group_df[H.sample_type].values[0]} {event_group.event_group_df[H.Voltage].values[0]} mV')
    return ax

'''
get_single_event(EventGroup : EventGroup, sampletype, voltage, id) -> Event :
この関数はEventGroupクラスのインスタンスとsampletype, voltage, idを受け取り，その条件に合致するEventクラスのインスタンスを返す。
特定のイベントに関する情報を得たい場合に使用する。
'''

def get_single_event(EventGroup : EventGroup, sampletype, voltage, id) -> Event :
    df = EventGroup.event_group_df.loc[(EventGroup.event_group_df[H.sample_type] == sampletype)
                                        & (EventGroup.event_group_df[H.Voltage] == voltage) 
                                        & (EventGroup.event_group_df[H.id] == id),:].copy()
    if df.shape[0] == 0 :
        raise ValueError("No such event")
    event = Event()
    event.set_summary_df(df)
    event.set_current_csv(df[H.file_name].values[0])
    return event

'''
get_total_trace(EventGroup: EventGroup, data_type = datatype.zeroed) -> np.ndarray :
この関数はEventGroupクラスのインスタンスを受け取り，そのインスタンスの全てのイベントのデータを結合して一つの配列にまとめて返す。
    data_typeにrawを指定すると生データ
    zeroedを指定するとベースラインを引いたデータ
    delta_gを指定するとコンダクタンス値の変化を求めたデータ
を返す。
'''

def get_total_trace(EventGroup: EventGroup, data_type = datatype.zeroed) -> np.ndarray :
    total_trace = []
    for i in tqdm.tqdm(range(EventGroup.event_group_df.shape[0]), desc='Getting total trace') :
        event = get_single_event(EventGroup,
                                 EventGroup.event_group_df.loc[i, H.sample_type],
                                 EventGroup.event_group_df.loc[i, H.Voltage],
                                 EventGroup.event_group_df.loc[i, H.id])
        if data_type == datatype.raw :
            data = event.current_data
        elif data_type == datatype.zeroed :
            data = event.zeroed_current_data
        elif data_type == datatype.delta_g :
            data = event.delta_g_data
        elif data_type == datatype.normalized :
            data = event.normalized_current
        else :
            raise ValueError("Unsupported data type: " + data_type)
        total_trace.extend(data.tolist())
    total_trace = np.array(total_trace)
    return total_trace