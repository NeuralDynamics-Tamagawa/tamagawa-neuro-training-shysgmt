import os
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import libs.utils.utils as utils
import libs.prep_behavior.generate_trials as generate_trials
import libs.handle.dataset as handle_dataset
import libs.analysis.spikes as spikes







def generate_push_peth(meta_file, trials, event):
    
    sampling_rate = 5000
    
    
    # Event times
    row_idx = trials['row_idx_ready']
    row_idx.dropna(inplace=True)
    quiescence_time = row_idx / sampling_rate
    
    row_idx = trials['row_idx_stim']
    row_idx.dropna(inplace=True)
    stim_time = row_idx / sampling_rate

    row_idx = trials['row_idx_select']
    row_idx.dropna(inplace=True)
    select_time = row_idx / sampling_rate

    row_idx = trials['row_idx_dispenser']
    row_idx.dropna(inplace=True)
    dispenser_time = row_idx / sampling_rate

    # Push onset times
    TF = (event['column_name_changed']=='left_button')&(event['left_button']==1)
    left_button_time = event[TF]['row_index'].values/sampling_rate

    TF = (event['column_name_changed']=='right_button')&(event['right_button']==1)
    right_button_time = event[TF]['row_index'].values/sampling_rate

    
    bin_size = 0.05
    time_window = [0, 5]    


    ppl_quiescence = spikes.PETH(
        metadata={'session': meta_file, 'description': 'PETH for left button presses during quiescence'},
        spike_times=left_button_time,
        event_times=quiescence_time,
        bin_size=bin_size,
        time_window=time_window
    )

    ppr_quiescence = spikes.PETH(
        metadata={'session': meta_file, 'description': 'PETH for right button presses during quiescence'},
        spike_times=right_button_time,
        event_times=quiescence_time,
        bin_size=bin_size,
        time_window=time_window
    )
    
    ppl_stim = spikes.PETH(
        metadata={'session': meta_file, 'description': 'PETH for left button presses during stimulation'},
        spike_times=left_button_time,
        event_times=stim_time,
        bin_size=bin_size,
        time_window=time_window
    )
    
    ppr_stim = spikes.PETH(
        metadata={'session': meta_file, 'description': 'PETH for right button presses during stimulation'},
        spike_times=right_button_time,
        event_times=stim_time,
        bin_size=bin_size,
        time_window=time_window
    )
    
    ppl_select = spikes.PETH(
        metadata={'session': meta_file, 'description': 'PETH for left presses during selection'},
        spike_times=left_button_time,
        event_times=select_time,
        bin_size=bin_size,
        time_window=time_window
    )
    
    ppr_select = spikes.PETH(
        metadata={'session': meta_file, 'description': 'PETH for right button presses during selection'},
        spike_times=right_button_time,
        event_times=select_time,
        bin_size=bin_size,
        time_window=time_window
    )
    
    ppl_dispenser = spikes.PETH(
        metadata={'session': meta_file, 'description': 'PETH for left presses during dispenser'},
        spike_times=left_button_time,
        event_times=dispenser_time,
        bin_size=bin_size,
        time_window=time_window
    )
    
    ppr_dispenser = spikes.PETH(
        metadata={'session': meta_file, 'description': 'PETH for right presses during dispenser'},
        spike_times=right_button_time,
        event_times=dispenser_time,
        bin_size=bin_size,
        time_window=time_window
    )
    
    peth_dict = {
            'quiescence': {
                'left': ppl_quiescence,
                'right': ppr_quiescence,
            },
            'stim': {
                'left': ppl_stim,
                'right': ppr_stim,
            },
            'select': {
                'left': ppl_select,
                'right': ppr_select,
            },
            'dispenser': {
                'left': ppl_dispenser,
                'right': ppr_dispenser,
            }
        }

    return peth_dict



def generate_push_peth_session(session_dir, save_dir=None):
    input_dir = os.path.join(session_dir, 'procTeensy')
    if save_dir is None:
        save_dir = input_dir
    
    files_to_check = ['event.pkl']
    existing_files = [file for file in files_to_check if os.path.exists(os.path.join(input_dir, file))]
    
    if len(existing_files) == len(files_to_check):
        
        # Loading
        session   = handle_dataset.Session(session_dir)
        event     = handle_dataset.Session.load_event(session)
        meta_file = session.meta_file
        trials   = session.trials
            
        # Processing
        # delete old pkl push_peth_df
        files = [
            "PP_L_quiescence.pkl",
            "PP_R_quiescence.pkl",
            "PP_L_stim.pkl",
            "PP_R_stim.pkl",
            "PP_L_select.pkl",
            "PP_R_select.pkl",
            "PP_L_dispenser.pkl",
            "PP_R_dispenser.pkl",
            "push_peth_left_quiescence.pkl",
            "push_peth_right_quiescence.pkl",
        ]

        for filename in files:
            path = os.path.join(save_dir, filename)
            if os.path.exists(path):
                os.remove(path)

        peth_dict = generate_push_peth(meta_file=meta_file, trials=trials, event=event)

        save_path = os.path.join(save_dir, "push_peth.pkl")
        with open(save_path, 'wb') as f:
            pickle.dump(peth_dict, f)

        utils.printlg("Push PETH generated and saved to: " + save_dir)
    else:
        print("Error | Missing files")
        return None
    
    
    
def generate_push_peth_auto(root_dir, target_subjects):
    
    subject_folders = utils.get_subfolders(root_dir)
    subject_folders = subject_folders[subject_folders['folder_name'].isin(target_subjects)]
    subject_folders['sort_key'] = subject_folders['folder_name'].apply(lambda x: target_subjects.index(x))
    subject_folders = subject_folders.sort_values('sort_key').reset_index(drop=True)

    for i_subject in range(0, len(subject_folders)):
        session_folders = utils.get_subfolders(subject_folders.iloc[i_subject] ['absolute_path'])

        for i_session in range(0, len(session_folders)):
            #print("[" + str(i_subject) + "]" + subject_folders.iloc[i_subject]["folder_name"] + " | [" + str(i_session) + "]" + session_folders.iloc[i_session]["folder_name"])
            session_dir = session_folders.loc[i_session]['absolute_path']
            generate_push_peth_session(session_dir, save_dir=None)
            

if __name__ == "__main__":
    root_folder = 'Z:/Data'
    target_subjects = ['RSS023', 'RSS025', 'RSS026', 'RSS027', 'RSS030', 'RSS033', 'RSS036', 'RSS038', 'RSS039', 'RSS040', 'RSS041', 'RSS044', 'RSS045', 'RSS046']
    #target_subjects = ['RSS044']
    generate_push_peth_auto(root_folder, target_subjects)