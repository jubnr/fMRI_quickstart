import glob
import pandas as pd
import numpy as np
import spacy, os
from nilearn.image import load_img, mean_img
from nilearn.glm.first_level import compute_regressor
from nilearn.maskers import NiftiMasker
from sklearn.linear_model import RidgeCV
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import GroupKFold, cross_val_predict
from pathlib import Path
from nilearn.plotting import plot_stat_map, plot_img, view_img
from nilearn.datasets import load_mni152_template
from matplotlib import pyplot as plt
from tqdm import tqdm

BASE_PATH = Path("/neurospin/unicog/protocols/IRMf/LePetitPrince_Pallier_2018/MEG/workspace-LPP/data/MEG/LPP/LPP_IRMEG_visual/derivatives/preprocessed_data/")
TR = 2.0
SMOOTHING_FWHM = 6 # in mm | 8 mm is the optimal value for 3T
nlp = spacy.load("fr_core_news_lg")

OUTPUT_DIR_BASE = Path("/home_local/Bonnaire/scripts/source_reconstruction/irmeg/figures/")
OUTPUT_DIR_BASE.mkdir(parents=True, exist_ok=True) 

participant_folders = sorted(BASE_PATH.glob("sub-*"))
subjects = [folder.name for folder in participant_folders]

def correlate(y_true, y_pred, eps=1e-10):
    X_mean = y_true - y_true.mean(0)
    Y_mean = y_pred - y_pred.mean(0)
    SX2 = np.sqrt(np.sum(X_mean ** 2, axis=0))
    SY2 = np.sqrt(np.sum(Y_mean ** 2, axis=0))
    SXY = np.sum(X_mean * Y_mean, axis=0)
    return SXY / (SX2 * SY2 + eps)

if not subjects:
    print(f"Aucun participant trouvé dans {BASE_PATH}. Vérifiez le chemin et la structure des dossiers.")
    exit()

print(f"Participants trouvés : {subjects}")

all_words_in_data = []
for subject_folder in tqdm(participant_folders, desc="Collecte des mots uniques"):
    lpp_events_subject = sorted(glob.glob(str(BASE_PATH / subject_folder / 'fmri/func' / '*run-*_*events.tsv')))
    for event_path in lpp_events_subject:
        try:
            event_df = pd.read_csv(event_path, sep='\t')
            all_words_in_data.extend(event_df['stimulus'].tolist())
        except FileNotFoundError:
            print(f"Avertissement: Fichier d'événements non trouvé pour {event_path}. Ignoré.")
        except Exception as e:
            print(f"Erreur lors de la lecture de {event_path}: {e}. Ignoré.")

unique_words = sorted(list(set(all_words_in_data)))
print(f"Nombre total de mots uniques trouvés dans toutes les données : {len(unique_words)}")

if not unique_words:
    print("Erreur: Aucun mot unique n'a pu être extrait. Vérifiez les fichiers d'événements.")
    exit()

try:
    embedding_dim = nlp(unique_words[0]).vector.shape[0]
    print(f"Dimension des embeddings spaCy : {embedding_dim}")
except Exception as e:
    print(f"Erreur lors de la récupération de la dimensionnalité de l'embedding pour le mot '{unique_words[0]}': {e}")
    exit()

random_embeddings_dict = {}
rng = np.random.default_rng() 
print("Génération d'embeddings aléatoires pour chaque mot unique...")
for word in unique_words:
    random_vector = rng.standard_normal(embedding_dim)
    random_embeddings_dict[word] = random_vector
print("Préparation des embeddings aléatoires terminée.")

all_subjects_score_maps_true = [] 
all_subjects_score_maps_random = [] 

for SUBJECT in tqdm(subjects, desc="Traitement des participants"):
    print(f"\n--- Traitement du participant : {SUBJECT} ---")

    subject_output_dir = OUTPUT_DIR_BASE / SUBJECT
    subject_output_dir.mkdir(parents=True, exist_ok=True)

    fmri_runs = sorted(glob.glob(str(BASE_PATH / f'{SUBJECT}/fmri/func' / '*task-lpp*MNI*preproc_bold.nii.gz')))
    lpp_events = sorted(glob.glob(str(BASE_PATH / f'{SUBJECT}/fmri/func' / '*run-*_*events.tsv')))

    if not fmri_runs or not lpp_events:
        print(f"Données fMRI ou events manquants pour {SUBJECT}. Passage au participant suivant.")
        continue

    masker = None 
    
    all_fmri_masked_runs_true = []
    all_regs_runs_true = []
    all_run_indices_runs_true = []

    all_fmri_masked_runs_random = []
    all_regs_runs_random = []
    all_run_indices_runs_random = [] 

    for i, (run_path, event_path) in enumerate(zip(fmri_runs, lpp_events)):
        try:
            if masker is None: 
                print(f"  Initialisation du masker pour {SUBJECT} en utilisant {os.path.basename(run_path)} comme référence.")
                reference_img_for_masker = load_img(run_path)
                masker = NiftiMasker(mask_strategy='epi', detrend=True, standardize=True, smoothing_fwhm=SMOOTHING_FWHM)
                masker.fit(reference_img_for_masker)
            
            event_df = pd.read_csv(event_path, sep='\t')
            words = event_df['stimulus'].tolist()
            
            run_img = load_img(run_path)
            n_volumes = run_img.shape[3]
            frame_times = TR * np.arange(n_volumes)
            onsets = event_df.onset.values
            durations = np.zeros(len(onsets))

            true_embeddings = np.array([nlp(word).vector for word in words])
            preds_true = []
            for j in range(true_embeddings.shape[1]):
                predictor = compute_regressor(
                    np.vstack([onsets, durations, true_embeddings[:, j]]),
                    hrf_model='spm',
                    frame_times=frame_times
                )
                preds_true.append(predictor[0])
            spacy_regressors_true = np.array(preds_true)
            regs_true = spacy_regressors_true[:, :, 0].T

            random_embeddings = np.array([random_embeddings_dict[word] for word in words])
            preds_random = []
            for j in range(random_embeddings.shape[1]):
                predictor = compute_regressor(
                    np.vstack([onsets, durations, random_embeddings[:, j]]),
                    hrf_model='spm',
                    frame_times=frame_times
                )
                preds_random.append(predictor[0])
            spacy_regressors_random = np.array(preds_random)
            regs_random = spacy_regressors_random[:, :, 0].T

            fmri_masked = masker.transform(run_img)

            all_fmri_masked_runs_true.append(fmri_masked)
            all_regs_runs_true.append(regs_true)
            
            all_fmri_masked_runs_random.append(fmri_masked) 
            all_regs_runs_random.append(regs_random)
            
            current_run_indices = [i] * fmri_masked.shape[0]
            all_run_indices_runs_true.extend(current_run_indices)
            all_run_indices_runs_random.extend(current_run_indices)

        except Exception as e:
            print(f"Erreur lors du traitement du run {run_path} pour {SUBJECT}: {e}")
            continue

    if not all_fmri_masked_runs_true: 
        print(f"Aucune donnée fMRI traitée pour {SUBJECT}. Passage au participant suivant.")
        continue

    all_fmri_masked_concat_true = np.vstack(all_fmri_masked_runs_true)
    all_regs_concat_true = np.vstack(all_regs_runs_true)
    all_run_indices_np_true = np.array(all_run_indices_runs_true)

    all_fmri_masked_concat_random = np.vstack(all_fmri_masked_runs_random) 
    all_regs_concat_random = np.vstack(all_regs_runs_random)
    all_run_indices_np_random = np.array(all_run_indices_runs_random) 

    print(f"\n--- Analyse pour {SUBJECT} avec VRAIS embeddings ---")
    n_runs = len(set(all_run_indices_np_true))
    if n_runs < 2: 
        print(f"Pas assez de runs ({n_runs}) pour la cross-validation pour {SUBJECT}. Passage au participant suivant.")
        continue

    cv = GroupKFold(n_splits=n_runs)

    model_pipeline_true = make_pipeline(
        StandardScaler(),
        RidgeCV(alphas=np.logspace(-2, 4, 10), alpha_per_target=True)
    )

    try:
        print(f"Calcul de cross_val_predict (VRAIS embeddings) pour {SUBJECT}...")
        Y_preds_true = cross_val_predict(model_pipeline_true, all_regs_concat_true, all_fmri_masked_concat_true, groups=all_run_indices_np_true, cv=cv)

        print(f"Calcul du score de corrélation (VRAIS embeddings) pour {SUBJECT}...")
        scores_true = correlate(all_fmri_masked_concat_true, Y_preds_true)
        subject_score_map_true = masker.inverse_transform(scores_true)
        all_subjects_score_maps_true.append(subject_score_map_true) 
        print(f"Carte de scores générée pour {SUBJECT} (VRAIS embeddings).")

    except Exception as e:
        print(f"Erreur lors de l'analyse des vrais embeddings pour {SUBJECT}: {e}")
        continue

    print(f"\n--- Analyse pour {SUBJECT} avec EMBEDDINGS ALÉATOIRES ---")
    cv_random = GroupKFold(n_splits=n_runs) 

    model_pipeline_random = make_pipeline(
        StandardScaler(),
        RidgeCV(alphas=np.logspace(-2, 4, 10), alpha_per_target=True)
    )

    try:
        print(f"Calcul de cross_val_predict (Embeddings Aléatoires) pour {SUBJECT}...")
        Y_preds_random = cross_val_predict(model_pipeline_random, all_regs_concat_random, all_fmri_masked_concat_random, groups=all_run_indices_np_random, cv=cv_random)

        print(f"Calcul du score de corrélation (Embeddings Aléatoires) pour {SUBJECT}...")
        scores_random = correlate(all_fmri_masked_concat_random, Y_preds_random)
        subject_score_map_random = masker.inverse_transform(scores_random)
        all_subjects_score_maps_random.append(subject_score_map_random) 
        print(f"Carte de scores générée pour {SUBJECT} (Embeddings Aléatoires).")

    except Exception as e:
        print(f"Erreur lors de l'analyse des embeddings aléatoires pour {SUBJECT}: {e}")
        continue


if not all_subjects_score_maps_true or not all_subjects_score_maps_random:
    print("Aucune carte de scores de participant n'a pu être générée pour l'une ou l'autre condition. Fin du script.")
    exit()

print(f"\nCalcul de la carte de scores moyenne pour {len(all_subjects_score_maps_true)} participants (VRAIS embeddings)...")
mean_score_map_group_true = mean_img(all_subjects_score_maps_true)

print(f"Calcul de la carte de scores moyenne pour {len(all_subjects_score_maps_random)} participants (EMBEDDINGS ALÉATOIRES)...")
mean_score_map_group_random = mean_img(all_subjects_score_maps_random)

if mean_score_map_group_true.shape == mean_score_map_group_random.shape:
    contrast_map_group = mean_score_map_group_true - mean_score_map_group_random
    
    print("Affichage de la carte de contraste de groupe (Vrais - Aléatoires)...")
    contrast_fig = plot_stat_map(
        contrast_map_group,
        threshold=0.05, # Seuil pour la visualisation (peut être ajusté)
        title='Group Contrast Map (True Embeddings - Random Embeddings)',
        cut_coords=(-50, -47, 8),
        cmap='cold_hot' # Carte de couleurs symétrique pour montrer positif/négatif
    )
    contrast_fig.savefig(f"{OUTPUT_DIR_BASE}/group_contrast_true_minus_random_map.png", dpi=300)

    background_img = load_mni152_template()
    interactive_contrast_view = view_img(
        contrast_map_group,
        bg_img=background_img,
        cmap='cold_hot',
        threshold=0.05,
        title='Contrast Map (Group Level)'
    )
    interactive_contrast_view.save_as_html(f"{OUTPUT_DIR_BASE}/interactive_view_contrast_group-level.html")
else:
    print("Erreur: Les cartes moyennes de groupe n'ont pas les mêmes dimensions. Impossible de calculer le contraste.")

print("\nAffichage de la carte de scores moyenne de groupe (VRAIS embeddings).")
group_fig_true_display = plot_stat_map(
    mean_score_map_group_true,
    threshold=0.1,
    title=f'Group Mean Correlation Map (True spaCy Embeddings)',
    cut_coords=(-50, -47, 8)
)

group_fig_true_display.savefig(f"{OUTPUT_DIR_BASE}/group_fig_true_group-level.png", dpi='300') # Sauvegarde déjà faite plus haut


background_img = load_mni152_template()
interactive_true_view = view_img(
    group_fig_true_display,
    bg_img=background_img,
    cmap='cold_hot',
    threshold=0.1,
    title='True SpaCy embeddings (Group Level)'
)
interactive_true_view.save_as_html(f"{OUTPUT_DIR_BASE}/interactive_true_view.html")

print("\nAffichage de la carte de scores moyenne de groupe (EMBEDDINGS ALÉATOIRES).")
group_fig_random_display = plot_stat_map(
    mean_score_map_group_random,
    threshold=0.1,
    title=f'Group Mean Correlation Map (Random Embeddings)',
    cut_coords=(-50, -47, 8)
)

group_fig_random_display.savefig(f"{OUTPUT_DIR_BASE}/group_fig_random_group-level.png", dpi='300') # Sauvegarde déjà faite plus haut


interactive_random_view = view_img(
    group_fig_random_display,
    bg_img=background_img,
    cmap='cold_hot',
    threshold=0.1,
    title=f'Group Mean Correlation Map (True Embeddings)',
)
interactive_random_view.save_as_html(f"{OUTPUT_DIR_BASE}/interactive_random_view.html")

print("\n--- Script finito ! ---")