import os
import pickle
import pandas as pd
import numpy as np
import scipy.stats as stats
import libs.utils.utils as utils
import libs.handle.dataset as dataset
import libs.analysis.behavior_single_session as analyze_behavior_single_session



# Extract stimulus set code based on the trials data
def extract_stimset_code(trials):
    
    df = trials.copy()
    df = df[df['trial']>0]

    counts = pd.concat([df['cue_left'], df['cue_right']]).value_counts().sort_index()

    contrast_list = np.abs(df['contrast']).unique().shape[0] 
    contrast_add_val = np.sort((df['cue_left']+df['cue_right']).unique())


    import scipy.stats as stats
    if counts.std() > 1e-8:
        z_scores = stats.zscore(counts)
        TF = np.abs(z_scores) > 1.5
    else:
        TF = pd.Series([False]*len(counts), index=counts.index)
    outliers_counts = TF.sum()
    outliers_values = pd.DataFrame(counts[TF])


    if contrast_list <= 1:
        stimset = 'Easy1'

    elif contrast_list == 2:
        stimset = 'Easy2'

    elif contrast_list >= 3 and contrast_add_val.shape[0] == 1:
        stimset = 'Categorization'

    elif contrast_list >= 3 and contrast_add_val.shape[0] >= 2 and outliers_counts == 1:
        # Onside
        val = outliers_values.index[0]
        if val == 0:
            stimset = 'Identification'
        elif val == 0.125:
            stimset = 'OneSide0125'
        elif val == 1.0:
            stimset = 'OneSideFull'
        else:
            stimset = 'not defined'

    elif contrast_list>=3 and contrast_add_val.shape[0] >= 2 and outliers_counts == 2:
        # Mix
        if outliers_values.index.isin([0, 1.0]).any():
            stimset = 'Mix_OneSideFull_Identification'
        else:
            stimset = 'not defined'

    else:
        stimset = 'not defined'
    
    return stimset


def extract_metadata(meta_file):
    header       = meta_file["header"]
    subject      = header.loc[header["name"]=="subject", "value"].iloc[0]
    program_name = header.loc[header["name"] == "programName", "value"].iloc[0]
    descriptions = header.loc[header["name"]=="descriptions", "value"].iloc[0]
    time         = meta_file["time"]

    datetime     = time.loc[time["name"]=="datetime", "value"].iloc[0]
    start_time   = time.loc[time["name"]=="start", "value"].iloc[0]
    end_time     = time.loc[time["name"]=="end", "value"].iloc[0]
    start_time   = utils.parse_time(time_str=start_time, date_str=datetime)
    end_time     = utils.parse_time(time_str=end_time, date_str=datetime)
    
    return subject, program_name, descriptions, start_time, end_time



def generate_session_information_auto(root_dir, target_subjects):
    
    subject_folders = utils.get_subfolders(root_dir)
    subject_folders = subject_folders[subject_folders['folder_name'].isin(target_subjects)]
    subject_folders['sort_key'] = subject_folders['folder_name'].apply(lambda x: target_subjects.index(x))
    subject_folders = subject_folders.sort_values('sort_key').reset_index(drop=True)

    session_dirs = []
    for i_subject in range(0, len(subject_folders)):
        session_folders = utils.get_subfolders(subject_folders.iloc[i_subject] ['absolute_path'])

        for i_session in range(0, len(session_folders)):
            session_dir = session_folders.loc[i_session]['absolute_path']
            session_dirs.append(session_dir)
            
    for idx, session_dir in enumerate(session_dirs):
        utils.printlg(f"Processing {session_dir} ({idx+1}/{len(session_dirs)})")
        generate_session_information_session(session_dir, save_dir=None)


def generate_session_information_session(session_dir, save_dir=None):
    input_dir = os.path.join(session_dir, 'procTeensy')
    if save_dir is None:
        save_dir = input_dir
    
    files_to_check = ['metaFile.pkl', 'trials.pkl']
    existing_files = [file for file in files_to_check if os.path.exists(os.path.join(input_dir, file))]
    
    if len(existing_files) == len(files_to_check):
        
        # Loading
        session = dataset.Session(session_dir)
        session.add_meta_file()
        session.add_trials()
        
        session_dir = session.session_dir
        trials = session.trials
        meta_file = session.meta_file
        
        # Processing
        session_information = generate_session_information(session_dir, meta_file, trials)

        # Saving
        save_path = os.path.join(save_dir, "session_information.pkl")
        with open(save_path, 'wb') as f:
            pickle.dump(session_information, f)
        return session_information
    else:
        print("Error | Missing files")
        return None
    


def generate_session_information(session_dir, meta_file, trials):
    
    subject, program_name, descriptions, start_time, end_time = extract_metadata(meta_file)

    trials = trials[trials['trial']>0]
    program_name = meta_file['header'].value[1]
    rec = "rec" in descriptions.strip()
    num_diff_contrast = np.abs(trials['contrast']).unique().shape[0]

    time_info = analyze_behavior_single_session.time_info(trials)
    
    correct_rate = analyze_behavior_single_session.correct_rate(trials)
    

    if num_diff_contrast >= 2:

        # Fit psychometric function 1 gamma
        params = {
            'parstart': np.array([0., 20., 0.1]),
            'parmin':   np.array([-20., 0.1, 0.0]),
            'parmax':   np.array([20., 10., 0.3]),
            'nfits': 100
        }
        psyfun_fitted_1gamma = analyze_behavior_single_session.fitting_psyfun(trials, P_model='erf_psycho', params=params)
        
        # Fit psychometric function 2 gammas
        params = {
            'parstart': np.array([0., 20., 0.1, 0.1]),
            'parmin':   np.array([-20., 0.1, 0.0, 0.0]),
            'parmax':   np.array([20., 10., 0.3, 0.3]),
            'nfits': 100
        }
        psyfun_fitted_2gamma = analyze_behavior_single_session.fitting_psyfun(trials, P_model='erf_psycho_2gammas', params=params)
        
        # Fit psychometric function erf
        psyfun_erf_fitted = analyze_behavior_single_session.fitting_psyfun_erf(trials)
        
    else:
        psyfun_fitted_1gamma = None
        psyfun_fitted_2gamma = None
        psyfun_erf_fitted = None

    # Reaction time
    reaction_time = analyze_behavior_single_session.reaction_time(trials)
    
    # Conditional probabilities pre-stimulus
    conditional_probabilities_prestim = analyze_behavior_single_session.conditional_probabilities_prestim(
        trials,
        alter_index_border=0.8
        )
    
    stim_set = extract_stimset_code(trials)

    status_list = list(trials['status'].unique())

    contrast_list = sorted(trials['contrast'].dropna().unique(), reverse=False)

    num_trials = trials.shape[0]
    
    
    if program_name == 'dm2afc_illusion_of_control_v001':
        df, chronometric_function_correlation = analyze_behavior_single_session.chronometric_function_correlation(
            trials=trials, stat="spearman",
            sig_boarder=0.05,
            outliner_cut_method=("percentile", 97.5)
            )

        correlation_TI_ST = analyze_behavior_single_session.correlation_TI_ST(
            trials=trials,
            outliner_cut_method=("percentile", 97.5),
            sig_border = 0.05
            )

        test_TI = analyze_behavior_single_session.test_TI(
            trials,
            ti_min=0,
            outliner_cut_method=("percentile", 97.5),
            sig_border=0.05
            )
        
        probe = trials.loc[trials['status']=='probe', 'time_investment']
        error = trials.loc[trials['status']=='error', 'time_investment']
        boundaries_TI = analyze_behavior_single_session.find_distribution_boundary(data1=probe, data2=error, gridsize=1000, normalize=True, plot=False)
        
    else:
        chronometric_function_correlation = None
        correlation_TI_ST = None              
        test_TI = None
        boundaries_TI = None
    
    

    session_information = {
        "session_dir":session_dir,
        "subject":subject,
        "program_name":program_name,
        "start_datetime":start_time,
        "end_datetime":end_time,
        "descriptions":descriptions,
        "recording":int(rec),
        "num_diff_contrast":num_diff_contrast,
        "contrast_list":contrast_list,
        "stimulus_set":stim_set,
        "time_info":time_info,
        "status_list":status_list,
        "num_trials": num_trials,
        "correct_rate":correct_rate,
        "psyfun_fitted_1gamma":psyfun_fitted_1gamma,
        "psyfun_fitted_2gamma":psyfun_fitted_2gamma,
        "psyfun_erf_fitted":psyfun_erf_fitted,
        "reaction_time":reaction_time,
        "conditional_probabilities_prestim":conditional_probabilities_prestim,
        "chronometric_function_correlation":chronometric_function_correlation,
        "correlation_TI_ST":correlation_TI_ST,
        "test_TI":test_TI,
        "boundaries_TI": boundaries_TI,
    }
    
    return session_information



def load_pooled_session_information(root_dir=None, target_subjects=None, save_path=None, check=True):

    if root_dir == None:
            root_dir = 'Z:/Data'

    subject_folders = utils.get_subfolders(root_dir)
    subject_folders = subject_folders[subject_folders['folder_name'].isin(target_subjects)]
    subject_folders['sort_key'] = subject_folders['folder_name'].apply(lambda x: target_subjects.index(x))
    subject_folders = subject_folders.sort_values('sort_key').reset_index(drop=True)


    df = pd.DataFrame(columns=['subject'])
    
    i = 0
    for i_subject in range(0, len(subject_folders)):
        session_folders = utils.get_subfolders(subject_folders.iloc[i_subject]['absolute_path'])
        utils.printlg(subject_folders.iloc[i_subject]["folder_name"])
        
        before_rec = 1
        
        for i_session in range(0, len(session_folders)):
            session_dir = session_folders.loc[i_session]['absolute_path'] 
            
            if check:
                utils.printlg("Processing session: " + session_dir)

            session = dataset.Session(session_dir)
            session.add_meta_file()
            meta_file = session.meta_file
            body_weight = meta_file['body_weight']
            
            si = session.load_session_information()
            
            df.loc[i, 'session_dir'] = si['session_dir']
            df.loc[i, 'subject'] = si['subject']
            df.loc[i, 'session_no'] = i_session+1
            df.loc[i, 'program_name'] = si['program_name']
            df.loc[i, 'start_datetime'] = si['start_datetime']
            df.loc[i, 'recording'] = si['recording']
            df.loc[i, 'num_diff_contrast'] = si['num_diff_contrast']
            df.loc[i, 'body_weight_pre'] = body_weight['pre'].values
            df.loc[i, 'body_weight_post'] = body_weight['post'].values
            df.loc[i, 'stimulus_set'] = si['stimulus_set']
            df.loc[i, 'probe'] = 'probe' in si['status_list']
            df.loc[i, 'num_trials'] = si['num_trials']
            df.loc[i, 'training_time_hour'] = si['time_info']['hour']
            df.loc[i, 'trials_per_min'] = si['time_info']['trials_per_min']
            df.loc[i, 'max_abs_stim'] = np.max(np.abs(np.array(si['contrast_list'])))
            df.loc[i, 'min_abs_stim'] = np.min(np.abs(np.array(si['contrast_list'])))

            correct_rate = si['correct_rate']
            df.loc[i, 'correct_rate'] = correct_rate['both']
            df.loc[i, 'correct_rate_left'] = correct_rate['left']
            df.loc[i, 'correct_rate_right'] = correct_rate['right']
            df.loc[i, 'lapse_rate_left'] = correct_rate['lapse_left']
            df.loc[i, 'lapse_rate_right'] = correct_rate['lapse_right']

            cnd_prob_prestim = si['conditional_probabilities_prestim']
            df.loc[i, 'alter_rate'] = cnd_prob_prestim ['alter_rate']
            df.loc[i, 'debias'] = cnd_prob_prestim ['alter_counts_index']
            
            
            # psyfun_fitted_1gamma if exists, extract it
            psyfit = si.get('psyfun_fitted_1gamma')
            if psyfit is not None:
                params = psyfit.get('model', {}).get('params', {})
                fitq  = psyfit.get('fit_quality', {})

                df.loc[i, 'pf_1gamma_bias']  = params.get('bias')
                df.loc[i, 'pf_1gamma_slope'] = params.get('slope')
                df.loc[i, 'pf_1gamma_gamma'] = params.get('gamma')
                df.loc[i, 'pf_1gamma_ll']    = fitq.get('log_likelihood')
                df.loc[i, 'pf_1gamma_pll']   = fitq.get('pseudo_log_likelihood')
                df.loc[i, 'pf_1gamma_aic']   = fitq.get('AIC')
                df.loc[i, 'pf_1gamma_bic']   = fitq.get('BIC')
            else:
                df.loc[i, ['pf_1gamma_bias','pf_1gamma_slope','pf_1gamma_gamma', 'pf_1gamma_ll','pf_1gamma_pll','pf_1gamma_aic', 'pf_1gamma_bic']] = np.nan

            
            # psyfun_fitted_2gamma if exists, extract it
            psyfit = si.get('psyfun_fitted_2gamma')
            if psyfit is not None:
                params = psyfit.get('model', {}).get('params', {})
                fitq  = psyfit.get('fit_quality', {})

                df.loc[i, 'pf_2gamma_bias']   = params.get('bias')
                df.loc[i, 'pf_2gamma_slope']  = params.get('slope')
                df.loc[i, 'pf_2gamma_gamma1'] = params.get('gamma1')
                df.loc[i, 'pf_2gamma_gamma2'] = params.get('gamma2')
                df.loc[i, 'pf_2gamma_ll']     = fitq.get('log_likelihood')
                df.loc[i, 'pf_2gamma_pll']    = fitq.get('pseudo_log_likelihood')
                df.loc[i, 'pf_2gamma_aic']    = fitq.get('AIC')
                df.loc[i, 'pf_2gamma_bic']    = fitq.get('BIC')
            else:
                df.loc[i, ['pf_2gamma_bias','pf_2gamma_slope','pf_2gamma_gamma1','pf_2gamma_gamma2','pf_2gamma_ll','pf_2gamma_pll','pf_2gamma_aic', 'pf_2gamma_bic']] = np.nan

            # psyfun_erf_fitted if exists, extract it
            psyfit_erf = si.get('psyfun_erf_fitted')
            if psyfit_erf is not None:
                params = psyfit_erf.get('model', {}).get('params', {})
                fitq  = psyfit_erf.get('fit_quality', {})

                df.loc[i, 'pf_erf_mu']    = params.get('mu')
                df.loc[i, 'pf_erf_sigma'] = params.get('sigma')
                df.loc[i, 'pf_erf_ll']    = fitq.get('log_likelihood')
                df.loc[i, 'pf_erf_pll']   = fitq.get('pseudo_log_likelihood')
                df.loc[i, 'pf_erf_aic']   = fitq.get('AIC')
                df.loc[i, 'pf_erf_bic']   = fitq.get('BIC')
            else:
                df.loc[i, ['pf_erf_mu','pf_erf_sigma','pf_erf_ll','pf_erf_pll','pf_erf_aic','pf_erf_bic']] = np.nan

            if si['program_name'] == 'dm2afc_illusion_of_control_v001':
                chrn_corr = si['chronometric_function_correlation']
                df.loc[i, 'chrn_rho'] = chrn_corr['rho']['all']
                df.loc[i, 'chrn_rho_left'] = chrn_corr['rho']['left']
                df.loc[i, 'chrn_rho_right'] = chrn_corr['rho']['right']
                df.loc[i, 'chrn_p'] = chrn_corr['p_value']['all']
                df.loc[i, 'chrn_p_left'] = chrn_corr['p_value']['left']
                df.loc[i, 'chrn_p_right'] = chrn_corr['p_value']['right']
                
                corr_TI_ST = si['correlation_TI_ST']
                df.loc[i, 'corrTIST_rho_probe'] = corr_TI_ST.loc['probe']['rho']
                df.loc[i, 'corrTIST_rho_error'] = corr_TI_ST.loc['error']['rho']
                df.loc[i, 'corrTIST_p_probe'] = corr_TI_ST.loc['probe']['p_value']
                df.loc[i, 'corrTIST_p_error'] = corr_TI_ST.loc['error']['p_value']

                test_TI = si['test_TI']
                df.loc[i, 'ks2samp_stat'] = test_TI['ks_2samp']['stat']
                df.loc[i, 'mannwhitneyu_U'] = test_TI['mannwhitneyu']['stat']
                df.loc[i, 'ks2samp_p'] = test_TI['ks_2samp']['p_value']
                df.loc[i, 'mannwhitneyu_p'] = test_TI['mannwhitneyu']['p_value']
                df.loc[i, 'A12'] = test_TI['mannwhitneyu']['A12']
                df.loc[i, 'delta'] = test_TI['mannwhitneyu']['delta']

                boundaries_TI = si['boundaries_TI']
                
                if boundaries_TI is not None:
                    df.loc[i, 'boundary_TI'] = boundaries_TI[0]
                else:
                    df.loc[i, 'boundary_TI'] = np.nan

            if (si['recording']==1)&(si['program_name'] == 'dm2afc_illusion_of_control_v001'):
                before_rec = 0

            df.loc[i, 'before_rec'] = before_rec

            i = i + 1

    session_information = df.copy()
    
    if save_path is not None:
        session_information.to_pickle(save_path)
    
    return session_information




if __name__ == "__main__":
    root_folder = 'Z:/Data'
    target_subjects = ['RSS023', 'RSS025', 'RSS026', 'RSS027', 'RSS030', 'RSS033', 'RSS036', 'RSS038', 'RSS039', 'RSS040', 'RSS041', 'RSS044', 'RSS045', 'RSS046', 'RSS048', 'RSS049', 'RSS050']
    #target_subjects = ['RSS041']
    generate_session_information_auto(root_folder, target_subjects)