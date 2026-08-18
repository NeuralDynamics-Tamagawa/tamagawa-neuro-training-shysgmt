# Basic lilbraries
import os
import numpy as np
import pandas as pd
from requests import session
from scipy import stats
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import seaborn as sns
import pickle
#import cv2

# Local libraries
import libs.utils.utils as utils
import libs.prep_behavior.procTeensy_to_pkl as pt2pkl
import libs.prep_behavior.generate_trials as generate_trials
import libs.prep_behavior.generate_session_information as generate_session_information
import libs.prep_behavior.generate_push_peth as generate_push_peth
import libs.analysis.behavior_single_session as analysis_behavior_single_session
import libs.analysis.spikes as spikes

import spikeinterface as si

class Session:
    def __init__(self, session_dir):
        
        if not os.path.exists(session_dir):
            raise FileNotFoundError(f"Session directory {session_dir} does not exist.")
        
        self.session_dir = session_dir
        self.session_information = self.load_session_information()
    
    # Get file paths
    def get_file_path_list(self):
        file_path_list = utils.list_filepath_lib(self.session_dir)
        return file_path_list
    
    
    # Helper functions
    def _load_pickle(self, relative_path):
        path = os.path.join(self.session_dir, relative_path)
        if not os.path.exists(path):
            print(f"File not found: {path}")
            return None 
        with open(path, 'rb') as f:
            return pickle.load(f)


    # Load dataset
    def load_meta_file(self):
        return self._load_pickle(os.path.join('procTeensy', 'metaFile.pkl'))
    
    def load_procTeensy(self):
        return self._load_pickle(os.path.join('procTeensy', 'procTeensy.pkl'))
        
    def load_event(self):
        return self._load_pickle(os.path.join('procTeensy', 'event.pkl'))

    def load_trials(self):
        trials = self._load_pickle(os.path.join('procTeensy', 'trials.pkl'))
        if trials is None:
            return pd.DataFrame()
        return trials[trials['trial']>0]

    def load_push_peth(self):
        return self._load_pickle(os.path.join('procTeensy', 'push_peth.pkl'))

    def load_session_information(self):
        return self._load_pickle(os.path.join('procTeensy', 'session_information.pkl'))

    
    def load_sorting_analyzer(self, i_imec, folder_name='sorting_analyzer'):
        imec_folder = 'imec'+str(i_imec)
        base_dir = os.path.join(self.session_dir, 'spikeinterface', imec_folder, folder_name)
        path = os.path.join(base_dir)
        print(f'Loading sorting_analyzer from {path}')
        sorting_analyzer = si.load_sorting_analyzer(path)
        return sorting_analyzer, base_dir
    
    
    def load_procTeensy_to_imec(self, i_imec):
        imec_folder = 'imec'+str(i_imec)
        processed_data = os.path.join(self.session_dir, 'processed-data', imec_folder)
        file_name = 'procTeensy_to_'+imec_folder+'.npy'
        path = os.path.join(processed_data, file_name)
        procTeensy_to_imec = np.load(path)
        return procTeensy_to_imec


    # Load dataset and add to session
    def add_file_path_list(self):
        self.file_path_list = self.get_file_path_list()
        return self
    
    def add_meta_file(self):
        self.meta_file = self.load_meta_file()
        return self
    
    def add_procTeensy(self):
        self.procTeensy = self.load_procTeensy()
        return self

    def add_event(self):
        self.event = self.load_event()
        return self
    
    def add_trials(self):
        self.trials = self.load_trials()
        return self
    
    def add_push_peth(self):
        self.push_peth = self.load_push_peth()
        return self
    
    def add_session_information(self):
        self.session_information = self.load_session_information()
        return self
    
    def add_sorting_analyzer(self, i_imec=0, folder_name='sorting_analyzer_dredge'):
        sorting_analyzer, base_dir = self.load_sorting_analyzer(i_imec=i_imec, folder_name=folder_name)
        self.sorting_analyzer = sorting_analyzer
        self.sorting_analyzer_base_dir = base_dir
        return self
    
    
    def add_procTeensy_to_imec(self, i_imec):
        self.procTeensy_to_imec = self.load_procTeensy_to_imec(i_imec=i_imec)
        return self
    
    
    def add_frame_to_procTeensy(self, i_imec=None):

        if not hasattr(self, 'file_path_list'):
            self.add_file_path_list()

        rows = self.file_path_list[
            self.file_path_list['file_name']
            == 'frame_to_procTeensy.pkl'
        ]

        if len(rows) == 0:
            utils.printlg("No frame_to_procTeensy.pkl found")
            return self

        for _, row in rows.iterrows():

            abs_path = row["absolute_path"]

            cam_folder = [
                part for part in abs_path.split(os.sep)
                if part.startswith("cam")
            ]

            if len(cam_folder) == 0:
                continue

            cam_name = cam_folder[0]

            f2p = pd.read_pickle(abs_path)
            
            if i_imec is not None:
                self.add_procTeensy_to_imec(i_imec=i_imec)
                p2i = self.procTeensy_to_imec
                f2p['time'] = (
                    p2i[
                        f2p['procTeensy_row']
                    ]
                )

            setattr(
                self,
                f"frame_to_procTeensy_{cam_name}",
                f2p
            )

            utils.printlg(
                f'Loaded frame_to_procTeensy for {cam_name}'
            )

        return self
                    

    
    
    def add_dlc_csv(self):
        found = False  # 
        
        for _, row in self.file_path_list.iterrows():
            if "Basler" in row["file_name"] and row["extension"] == ".csv":
                abs_path = row["absolute_path"]
                
                cam_folder = [part for part in abs_path.split(os.sep) if part.startswith("cam")]
                cam_name = cam_folder[-1] if cam_folder else "unknown"

                dlc_data = self.load_dlc_csv(abs_path)
                
                utils.printlg(f'Loaded DLC data for {cam_name} from {abs_path}')
                setattr(self, f"dlc_csv_{cam_name}", dlc_data)
        
        if not found:
            utils.printlg("No DLC CSV files found in file_path_list")
        
        return self
    
    
    def add_arguments_trials(self):
        self.add_trials()
        trials = self.trials
        trials = analysis_behavior_single_session.augment_trials(trials=trials)
        self.trials = trials
        return self

    
    # Recalculate
    def recalc_metaFile(self):
        procTeensy_dir = os.path.join(self.session_dir, 'procTeensy')
        self.meta_file = pt2pkl.metafile(procTeensy_dir, procTeensy_dir, save=True)    
        utils.printlg('Recalculated metaFile.pkl')
        return self.meta_file
    
    def recalc_trials(self):
        trials = generate_trials.generate_trials(meta_file=self.meta_file, event=self.load_event())
        trials.to_pickle(path = os.path.join(self.session_dir, 'procTeensy', 'trials.pkl'))
        self.trials = trials
        utils.printlg('Recalculated trials.pkl')
        return self.trials
    
    def recalc_session_information(self):
        session_information = generate_session_information.generate_session_information(meta_file=self.meta_file, trials=self.trials)
        save_path = os.path.join(self.session_dir, "procTeensy", "session_information.pkl")
        with open(save_path, 'wb') as f:
            pickle.dump(session_information, f)
        self.session_information = session_information
        utils.printlg('Recalculated session_information.pkl')
        return self.session_information
    
    def recalc_push_peth(self):
        event = self.load_event()
        trials = self.load_trials()
        peth_dict = generate_push_peth.generate_push_peth(meta_file=self.meta_file, trials=trials, event=event)
        save_path = os.path.join(self.session_dir, "procTeensy", "push_peth.pkl")
        with open(save_path, 'wb') as f:
            pickle.dump(peth_dict, f)
        self.push_peth = peth_dict
        utils.printlg('Recalculated push_peth.pkl')
        return self.push_peth
    
    
    
    
    
    def compute_frame_to_procTeensy(self, video_path, col_name_cam='cam1', overwrite=False):
        
        utils.printlg(f'video_path = {video_path}')
        utils.printlg(f'col_name_cam = {col_name_cam}')
        
        # Check if frame_to_procTeensy.pkl already exists
        save_path = os.path.dirname(video_path)
        frame_to_procTeensy_path = os.path.join(save_path, 'frame_to_procTeensy.pkl')
        if os.path.exists(frame_to_procTeensy_path) and not overwrite:
            utils.printlg(f'frame_to_procTeensy.pkl already exists at {frame_to_procTeensy_path}. Loading it.')
            frame_to_procTeensy = pd.read_pickle(frame_to_procTeensy_path)
            setattr(self, f"frame_to_procTeensy_{col_name_cam}", frame_to_procTeensy)
            return
        

        # Load video and get frame count
        cap = cv2.VideoCapture(video_path)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Load procTeensy data and extract exposure signal
        procTeensy = self.load_procTeensy()
        exposure_signal = procTeensy[col_name_cam]
        
        # Cluster exposure signal to identify movement vs baseline
        utils.printlg('Compute K-means clustering')
        # Moving average
        window_size = 2
        # rolling
        cam1_smoothed = exposure_signal.rolling(window=window_size, center=True).mean()
        # k-means clustering
        from sklearn.cluster import KMeans
        kmeans = KMeans(n_clusters=2, random_state=0).fit(cam1_smoothed.dropna().values.reshape(-1, 1))
        labels = kmeans.labels_

        # Ensure that label 0 corresponds to the baseline (no movement)
        if labels[0] == 1:
            labels = np.abs(labels-1)  # Invert labels to make sure 0 is the baseline
            
        # Find switch points where label changes from 0 to 1
        s = pd.Series(labels)
        switch_points = s[(s.shift(1) == 0) & (s == 1)].index
        
        #
        reg_last_frame = round(len(switch_points) / frame_count)

        # Regulated frame points
        reg_frame_points = np.linspace(switch_points[0], switch_points[-1*reg_last_frame], num=frame_count, dtype=int)

        # Plot smoothed signal with switch points and regulated frame points
        edge = np.linspace(switch_points[0], switch_points[-1], num=9, dtype=int)
        window = 500

        plt.figure(figsize=(15, 5))
        for i in range(9):
            plt.subplot(3, 3, i+1)
            sns.lineplot(data=cam1_smoothed[edge[i]-window:edge[i]+window])
            sns.lineplot(x=cam1_smoothed.index[edge[i]-window:edge[i]+window], y=labels[edge[i]-window:edge[i]+window]*np.max(cam1_smoothed))
            sns.scatterplot(x=reg_frame_points, y=np.full_like(reg_frame_points, np.max(cam1_smoothed)), s=50)
            plt.xlim(edge[i]-window, edge[i]+window)
        plt.suptitle(f'frame counts: {frame_count},  switch points: {len(switch_points)},  reg points: {len(reg_frame_points)}')
        plt.tight_layout()
        plt.savefig(os.path.join(save_path, 'smoothed_with_reg_frame_points.png'))
        plt.close()

        # Create and save DataFrame mapping frame to procTeensy row
        frame = np.arange(len(reg_frame_points))
        row = reg_frame_points 
        frame_to_procTeensy = pd.DataFrame(row, index=frame, columns=['procTeensy_row'])
        frame_to_procTeensy.index.name = 'frame'
        utils.printlg(f'Saving frame_to_procTeensy.pkl to {save_path}')
        save_path = os.path.dirname(video_path)
        frame_to_procTeensy.to_pickle(os.path.join(save_path, 'frame_to_procTeensy.pkl'))
        
        setattr(self, f"frame_to_procTeensy_{col_name_cam}", frame_to_procTeensy)
        
        return self
        
    
    

    def compute_procTeensy_to_frame(self, frame_to_procTeensy, target_procTeensy_row):
        df = frame_to_procTeensy.copy()
        
        procTeensy_row = []
        frames = []
        
        for target_row in target_procTeensy_row:
            series = (df["procTeensy_row"] - target_row).abs()
            
            if series.notna().any():
                idx = series.idxmin()
            else:
                idx = None 
            
            procTeensy_row.append(target_row)
            frames.append(idx)
        
        p2f = pd.DataFrame({
            "procTeensy_row": procTeensy_row,
            "frame": frames
        })
        
        return p2f
    
    def compute_frame_to_imec(self, frame_to_procTeensy, procTeensy_to_imec):
        f2p = frame_to_procTeensy.copy()
        p2i = procTeensy_to_imec.copy()
        f2p['time'] = (
            p2i[
                f2p['procTeensy_row']
            ]
        )
        f2i = f2p[['time']].copy()
        return f2i
    
    
        
    def load_dlc_csv(self, dlc_output_path):
        
        df = pd.read_csv(dlc_output_path, header=[0,1,2])

        dlc = {}

        for bodypart in df.columns.levels[1]:
            subdf = df.xs(bodypart, level=1, axis=1)
            subdf.columns = subdf.columns.droplevel(0)
            dlc[bodypart] = subdf  

        del dlc["bodyparts"]

        dlc = {k.lower(): v for k, v in dlc.items()}

        return dlc
    
    
    
    

def fill_dlc_coords(df, threshold=0.999, method="ffill"):

    df_filled = df.copy()
    mask = df_filled["likelihood"] < threshold
    df_filled.loc[mask, ["x", "y"]] = pd.NA

    if method == "ffill":
        df_filled[["x", "y"]] = df_filled[["x", "y"]].ffill()
    elif method == "bfill":
        df_filled[["x", "y"]] = df_filled[["x", "y"]].bfill()
    elif method == "linear":
        df_filled[["x", "y"]] = df_filled[["x", "y"]].interpolate(method="linear")
    else:
        raise ValueError("method must be 'ffill', 'bfill', or 'linear'")

    return df_filled
