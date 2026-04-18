# Muse 2 Channel Mapping to ds005048

## Mapping

| Muse 2 Position | 10-10 System | ds005048 Proxy | 10-20 System | Rationale |
|-----------------|-------------|----------------|-------------|-----------|
| AF7 | Anterior-frontal L | **F7** | Inferior frontal L | AF7 is midpoint between Fp1 and F7 on the left circumferential arc. F7 (BA45, IFG pars triangularis) is functionally closer than Fp1 (BA10, frontal pole). Both are lateral prefrontal. |
| AF8 | Anterior-frontal R | **F8** | Inferior frontal R | Mirror of AF7/F7. Both project to lateral prefrontal cortex. |
| TP9 | Temporal-parietal L | **T7** | Temporal L | TP9 is below/behind T7, near the mastoid. T7 (BA21/42, posterior STG) is the nearest 10-20 electrode. T7 overlies auditory cortex, relevant for 40 Hz ASSR. |
| TP10 | Temporal-parietal R | **T8** | Temporal R | Mirror of TP9/T7. T8 (BA22, posterior STG) covers auditory cortex. |

## 4-Channel Subset from ds005048

**Channels: F7, F8, T7, T8** (indices 2, 6, 7, 11 in the 19-channel montage)

## Scientific Justification

1. **F7/F8 capture frontal theta** which drives the phase component of PAC. They are the closest 10-20 positions to the Muse 2's frontal electrodes.
2. **T7/T8 overlie auditory cortex** (superior temporal gyrus), the primary generator of the 40 Hz Auditory Steady-State Response (ASSR). This is directly relevant for auditory entrainment.
3. The 4 channels preserve **bilateral symmetry** (left/right) and **regional diversity** (frontal/temporal).
4. Lahijanian et al. (2024) found 40 Hz entrainment strongest at frontal and temporal source locations — our channel selection captures both.

## Known Limitations

1. **Spatial approximation**: AF7 is ~2-3 cm anterior to F7; TP9 is ~3-4 cm inferior/posterior to T7. Cortical tissue beneath differs.
2. **Lost channels**: Fp1, Fp2, F3, Fz, F4 are dropped. Fz (midline frontal) is a strong theta source; its loss may degrade theta-phase estimation.
3. **CAR with 4 channels** is a coarser spatial filter than with 7. The channel mean is less stable.
4. **PAC labels will change**: Mean MI across 4 channels (F7/F8/T7/T8) differs from mean MI across 7 frontal channels. Direct R² comparison with 7-channel model is not meaningful — evaluate against own baselines.
5. **Domain gap at deployment**: Muse 2 uses dry electrodes (high impedance, more EMG) vs ds005048's gel electrodes with ICA cleaning. Model trained on research-quality proxies will face degraded input quality at demo time.
6. **Reference mismatch**: ds005048 uses average reference; Muse 2 uses FPz reference. Systematic amplitude differences expected.
7. **Sample rate**: ds005048 is 250 Hz, Muse 2 is 256 Hz. Requires resampling at inference time.

## Feature Dimensions

| Component | 7-channel | 4-channel | Formula |
|-----------|-----------|-----------|---------|
| Band powers (4 bands) | 28 | 16 | 4 * n_channels |
| Theta/gamma ratios | 7 | 4 | n_channels |
| PAC-structure features | 21 | 12 | 3 * n_channels |
| Cross-channel stats | 5 | 5 | Fixed |
| **Spectral total** | **61** | **37** | 8 * n_ch + 5 |
| PAC-derived (causal) | 7 | 7 | Fixed |
| Stim context | 5 | 5 | Fixed |
| **TCN input total** | **73** | **49** | spectral + 12 |
