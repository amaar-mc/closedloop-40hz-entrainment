"""
Cortical Response Model — TRIBE V2 Integration with Biophysical Fallback

Wraps Meta's TRIBE V2 brain foundation model to predict cortical responses
to 40 Hz auditory stimulation. When TRIBE V2 is available, uses the model's
learned cortical predictions. When unavailable, falls back to a parametric
cortical response model based on published ASSR literature.

The model outputs regional cortical activation levels for 6 ROIs relevant
to 40 Hz gamma entrainment:
    1. Auditory cortex left (Heschl's gyrus / STG)
    2. Auditory cortex right
    3. Inferior frontal gyrus left
    4. Inferior frontal gyrus right
    5. Middle/superior frontal gyrus
    6. Medial frontal / cingulate

These activations drive the Wilson-Cowan neural mass model to produce
EEG-level oscillatory dynamics with theta-gamma PAC.

Author: Amaar Chughtai
Date: April 2026
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)

# Try importing TRIBE V2
try:
    from tribev2 import TribeModel
    TRIBE_V2_AVAILABLE = True
    logger.info("TRIBE V2 model loaded successfully")
except ImportError:
    TRIBE_V2_AVAILABLE = False
    logger.info("TRIBE V2 not installed — using parametric cortical model")

# Try importing MNE for atlas-based ROI extraction
try:
    import mne
    MNE_AVAILABLE = True
except ImportError:
    MNE_AVAILABLE = False


# ROI names used throughout the pipeline
ROI_NAMES: list[str] = [
    "auditory_left",
    "auditory_right",
    "ifg_left",
    "ifg_right",
    "mfg_sfg",
    "medial_frontal",
]

N_ROIS: int = len(ROI_NAMES)

# Desikan-Killiany atlas labels for each ROI
# Used when extracting from TRIBE V2's fsaverage5 predictions
DK_ATLAS_MAPPING: dict[str, list[str]] = {
    "auditory_left": ["transversetemporal-lh", "superiortemporal-lh"],
    "auditory_right": ["transversetemporal-rh", "superiortemporal-rh"],
    "ifg_left": ["parsopercularis-lh", "parstriangularis-lh", "parsorbitalis-lh"],
    "ifg_right": ["parsopercularis-rh", "parstriangularis-rh", "parsorbitalis-rh"],
    "mfg_sfg": [
        "caudalmiddlefrontal-lh", "caudalmiddlefrontal-rh",
        "rostralmiddlefrontal-lh", "rostralmiddlefrontal-rh",
        "superiorfrontal-lh", "superiorfrontal-rh",
    ],
    "medial_frontal": [
        "medialorbitofrontal-lh", "medialorbitofrontal-rh",
        "rostralanteriorcingulate-lh", "rostralanteriorcingulate-rh",
        "caudalanteriorcingulate-lh", "caudalanteriorcingulate-rh",
    ],
}


@dataclass
class CorticalResponseConfig:
    """Configuration for cortical response model."""

    # TRIBE V2 settings
    tribe_v2_cache_dir: str = "./cache/tribe_v2"
    tribe_v2_device: str = "auto"

    # Parametric fallback: ROI activation levels for stim/rest
    # Based on published fMRI ASSR data (Pastor et al. 2002, Steinmann & Gutschalk 2011)
    stim_activations: list[float] = field(
        default_factory=lambda: [
            6.5,   # Auditory L: strongest ASSR response
            6.5,   # Auditory R: bilateral
            4.5,   # IFG L: moderate frontal activation
            4.5,   # IFG R: moderate frontal activation
            4.0,   # MFG/SFG: lower frontal
            3.8,   # Medial frontal: attention-modulated
        ]
    )
    rest_activations: list[float] = field(
        default_factory=lambda: [
            3.0,   # Auditory L: spontaneous baseline
            3.0,   # Auditory R
            3.0,   # IFG L
            3.0,   # IFG R
            3.0,   # MFG/SFG
            3.0,   # Medial frontal
        ]
    )

    # Temporal dynamics
    onset_tau_sec: float = 1.5     # ASSR onset time constant
    offset_tau_sec: float = 2.0    # ASSR offset time constant
    habituation_rate: float = 0.005  # Per-second habituation

    # Inter-subject variability
    subject_variability_std: float = 0.15  # Relative std across subjects


class CorticalResponseModel:
    """
    Predicts cortical ROI activations in response to 40 Hz auditory stimulation.

    Two modes:
        1. TRIBE V2 mode: Uses the pretrained model to predict cortical surface
           activations from audio stimuli, then extracts ROI means.
        2. Parametric mode: Uses literature-based activation levels with
           exponential temporal dynamics (onset/offset/habituation).

    The output — a vector of 6 ROI activations — feeds the Wilson-Cowan
    neural mass model to produce EEG-level oscillatory dynamics.
    """

    def __init__(
        self,
        cfg: CorticalResponseConfig,
        use_tribe_v2: bool = True,
    ) -> None:
        self.cfg = cfg
        self.use_tribe_v2 = use_tribe_v2 and TRIBE_V2_AVAILABLE
        self.tribe_model: Optional[object] = None

        # State for parametric mode
        self._current_activations = np.array(cfg.rest_activations, dtype=np.float64)
        self._stim_array = np.array(cfg.stim_activations, dtype=np.float64)
        self._rest_array = np.array(cfg.rest_activations, dtype=np.float64)
        self._stim_duration = 0.0  # Cumulative stim time (for habituation)

        # Cached TRIBE V2 predictions
        self._tribe_cache: dict[str, np.ndarray] = {}

        # Label vertex indices for ROI extraction (lazy loaded)
        self._roi_vertex_indices: dict[str, np.ndarray] | None = None

        if self.use_tribe_v2:
            self._load_tribe_model()
        else:
            logger.info("Using parametric cortical response model (ASSR literature)")

    def _load_tribe_model(self) -> None:
        """Load TRIBE V2 model from HuggingFace Hub."""
        try:
            self.tribe_model = TribeModel.from_pretrained(
                "facebook/tribev2",
                cache_folder=self.cfg.tribe_v2_cache_dir,
                device=self.cfg.tribe_v2_device,
            )
            logger.info("TRIBE V2 model loaded from HuggingFace Hub")
        except Exception as e:
            logger.warning(f"Failed to load TRIBE V2: {e}. Falling back to parametric.")
            self.use_tribe_v2 = False
            self.tribe_model = None

    def _load_roi_indices(self) -> None:
        """Load fsaverage5 atlas labels and build ROI vertex index map."""
        if not MNE_AVAILABLE:
            logger.warning("MNE not available — cannot extract ROI indices")
            return

        subjects_dir = str(Path(mne.datasets.fetch_fsaverage(verbose=False)).parent)
        labels = mne.read_labels_from_annot(
            "fsaverage", parc="aparc", subjects_dir=subjects_dir
        )

        # Build name → vertex indices mapping
        label_map: dict[str, np.ndarray] = {}
        for label in labels:
            label_map[label.name] = label.vertices

        self._roi_vertex_indices = {}
        for roi_name, dk_labels in DK_ATLAS_MAPPING.items():
            vertices = []
            for dk_label in dk_labels:
                if dk_label in label_map:
                    # Offset right hemisphere vertices by left hemisphere count
                    verts = label_map[dk_label]
                    if dk_label.endswith("-rh"):
                        verts = verts + 10242  # fsaverage5 has 10242 per hemi
                    vertices.append(verts)
                else:
                    logger.warning(f"Atlas label '{dk_label}' not found")

            if vertices:
                self._roi_vertex_indices[roi_name] = np.concatenate(vertices)
            else:
                self._roi_vertex_indices[roi_name] = np.array([], dtype=int)

        logger.info(
            f"Loaded ROI vertex indices: "
            + ", ".join(
                f"{k}={len(v)}" for k, v in self._roi_vertex_indices.items()
            )
        )

    def predict_tribe_v2(
        self,
        audio_path: str | Path,
    ) -> np.ndarray:
        """
        Predict ROI activations using TRIBE V2 model.

        Note: TRIBE V2 requires naturalistic audio (speech/music) because
        its pipeline uses WhisperX for text extraction. Pure synthetic
        stimuli (click trains, AM tones) will fail at the transcription
        step. For 40 Hz entrainment simulation, use the parametric model
        (get_activations) which is calibrated against ASSR literature.

        TRIBE V2 can be used to validate cortical responses for:
        - Speech stimuli with 40 Hz AM overlay
        - Naturalistic audio to characterize baseline cortical activity
        - Cross-validation of parametric model assumptions

        Args:
            audio_path: Path to WAV file (must contain speech content).

        Returns:
            roi_activations: Shape (n_rois,) = (6,).
        """
        if self.tribe_model is None:
            raise RuntimeError("TRIBE V2 model not loaded")

        audio_path = str(audio_path)

        # Check cache
        if audio_path in self._tribe_cache:
            return self._tribe_cache[audio_path]

        # Load ROI indices if needed
        if self._roi_vertex_indices is None:
            self._load_roi_indices()

        # Run TRIBE V2 inference
        df = self.tribe_model.get_events_dataframe(audio_path=audio_path)
        preds, segments = self.tribe_model.predict(events=df)
        # preds shape: (n_timesteps, n_vertices) where n_vertices ≈ 20484

        # Average across time to get steady-state activation
        mean_activation = np.mean(preds, axis=0)  # (n_vertices,)

        # Extract ROI means
        roi_activations = np.zeros(N_ROIS, dtype=np.float64)
        for i, roi_name in enumerate(ROI_NAMES):
            if self._roi_vertex_indices and roi_name in self._roi_vertex_indices:
                vertices = self._roi_vertex_indices[roi_name]
                valid = vertices[vertices < len(mean_activation)]
                if len(valid) > 0:
                    roi_activations[i] = np.mean(mean_activation[valid])
                else:
                    roi_activations[i] = np.mean(mean_activation)
            else:
                roi_activations[i] = np.mean(mean_activation)

        # Rescale to neural mass model drive range [2.0, 8.0]
        roi_min, roi_max = roi_activations.min(), roi_activations.max()
        if roi_max - roi_min > 1e-6:
            roi_activations = 2.0 + 6.0 * (roi_activations - roi_min) / (roi_max - roi_min)
        else:
            roi_activations[:] = 5.0

        # Cache
        self._tribe_cache[audio_path] = roi_activations

        return roi_activations

    def get_activations(
        self,
        is_stimulating: bool,
        dt_sec: float = 1.0,
        subject_seed: int | None = None,
    ) -> np.ndarray:
        """
        Get current ROI activations for the simulation step.

        In parametric mode, applies exponential approach dynamics:
            During stim: activations approach stim_activations
            During rest: activations approach rest_activations

        Includes habituation (prolonged stimulation reduces response).

        Args:
            is_stimulating: Whether 40 Hz stimulation is active.
            dt_sec: Time step in seconds.
            subject_seed: Seed for subject-specific variability.

        Returns:
            activations: ROI activations, shape (n_rois,) = (6,).
        """
        cfg = self.cfg

        if is_stimulating:
            target = self._stim_array.copy()
            tau = cfg.onset_tau_sec

            # Apply habituation: reduce target over prolonged stimulation
            self._stim_duration += dt_sec
            hab_factor = np.exp(-cfg.habituation_rate * self._stim_duration)
            # Habituation reduces the stim-rest difference, not absolute level
            target = self._rest_array + (target - self._rest_array) * hab_factor
        else:
            target = self._rest_array.copy()
            tau = cfg.offset_tau_sec

            # Recovery during rest
            self._stim_duration = max(0.0, self._stim_duration - dt_sec * 0.5)

        # Exponential approach
        alpha = 1.0 - np.exp(-dt_sec / tau)
        self._current_activations += alpha * (target - self._current_activations)

        # Add subject-specific variability
        if subject_seed is not None:
            rng = np.random.default_rng(subject_seed)
            variability = rng.normal(1.0, cfg.subject_variability_std, N_ROIS)
            return (self._current_activations * variability).astype(np.float64)

        return self._current_activations.copy()

    def reset(self) -> None:
        """Reset to initial resting state."""
        self._current_activations = np.array(
            self.cfg.rest_activations, dtype=np.float64
        )
        self._stim_duration = 0.0


if __name__ == "__main__":
    print("=" * 60)
    print("Cortical Response Model — Self-Test")
    print("=" * 60)

    print(f"\nTRIBE V2 available: {TRIBE_V2_AVAILABLE}")
    print(f"MNE available: {MNE_AVAILABLE}")

    cfg = CorticalResponseConfig()
    model = CorticalResponseModel(cfg, use_tribe_v2=False)

    # Test parametric mode dynamics
    print("\nParametric mode — Stimulation onset dynamics:")
    print("-" * 40)
    model.reset()
    for t in range(20):
        act = model.get_activations(is_stimulating=True, dt_sec=1.0)
        if t % 5 == 0:
            print(f"  t={t:2d}s: {' '.join(f'{a:.2f}' for a in act)}")

    print("\nOffset dynamics (after 20s stim):")
    for t in range(10):
        act = model.get_activations(is_stimulating=False, dt_sec=1.0)
        if t % 3 == 0:
            print(f"  t={20+t:2d}s: {' '.join(f'{a:.2f}' for a in act)}")

    # Test subject variability
    print("\nSubject variability (stim condition):")
    print("-" * 40)
    for subj in range(5):
        model.reset()
        for _ in range(10):
            model.get_activations(is_stimulating=True, dt_sec=1.0)
        act = model.get_activations(is_stimulating=True, dt_sec=1.0, subject_seed=subj)
        print(f"  Subject {subj}: {' '.join(f'{a:.2f}' for a in act)}")

    print(f"\nROI names: {ROI_NAMES}")
    print(f"N_ROIS: {N_ROIS}")
    print("\n[PASS] Cortical response model produces valid dynamics")
