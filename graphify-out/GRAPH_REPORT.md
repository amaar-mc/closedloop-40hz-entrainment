# Graph Report - .  (2026-04-11)

## Corpus Check
- Large corpus: 420 files · ~1,608,866 words. Semantic extraction will be expensive (many Claude tokens). Consider running on a subfolder, or use --no-semantic to run AST-only.

## Summary
- 4217 nodes · 7753 edges · 141 communities detected
- Extraction: 72% EXTRACTED · 28% INFERRED · 0% AMBIGUOUS · INFERRED: 2142 edges (avg confidence: 0.55)
- Token cost: 0 input · 0 output

## God Nodes (most connected - your core abstractions)
1. `StimAction` - 197 edges
2. `EntrainmentSimulator` - 142 edges
3. `FatigueAwareSimulator` - 142 edges
4. `MultiscaleCausalTCN` - 132 edges
5. `ModelConfig` - 127 edges
6. `RealtimePACForecaster` - 118 edges
7. `EEGNet` - 97 edges
8. `SpectralFeatureExtractor` - 59 edges
9. `ClosedLoopController` - 50 edges
10. `StreamingFeatureExtractor` - 47 edges

## Surprising Connections (you probably didn't know these)
- `Closed-Loop Adaptive Controller (z-score +/-0.5)` --references--> `src/controller.py (ClosedLoopController)`  [INFERRED]
  CSEF/Presentation/CSEF_2026_Presentation.pdf → src/controller.py
- `Research Paper: Personalized Deep Learning for Closed-Loop 40 Hz Entrainment` --semantically_similar_to--> `Research Paper v3 (MS: Personalized Closed-Loop 40 Hz Entrainment)`  [INFERRED] [semantically similar]
  docs/paper/RESEARCH_PAPER.md → CSEF/Research Paper/RESEARCH_PAPER_v3.md
- `Feature Leakage Story (R2 0.999 inflation, audit removed)` --semantically_similar_to--> `Dec 22 2025 Architecture Exploration V2-V8 (leakage detection)`  [INFERRED] [semantically similar]
  docs/CSEF_JUDGING_STRATEGY.md → archive/notebooks/v2_daily_log_draft.md
- `Research Paper v4 (PDF)` --semantically_similar_to--> `Research Paper v4 (Main Manuscript)`  [INFERRED] [semantically similar]
  docs/paper/RESEARCH_PAPER_v4.pdf → docs/paper/RESEARCH_PAPER_v4.md
- `EEGNet (Static PAC Estimator, 1457 params)` --references--> `src/eegnet.py`  [INFERRED]
  docs/paper/sections/04-methods.md → src/eegnet.py

## Hyperedges (group relationships)
- **Two-Stage Predictive Pipeline (EEGNet -> features -> TCN -> controller)** — findings_eegnet_architecture, findings_multiscale_tcn_architecture, concept_personalization_zscore, claudemd_closed_loop_control, concept_12_pac_stim_features [EXTRACTED 0.95]
- **Feature Ablation Breakthrough (73 -> 12 features)** — notebook_feb17_temporal_pivot, notebook_mar3_5_ablation_design, notebook_mar6_8_ablation_result, notebook_mar10_12_multiseed, concept_feature_ablation_discovery, concept_12_pac_stim_features, poster_v6_feature_discovery_narrative [EXTRACTED 0.95]
- **CSEF Submission Artifact Set** — abstract_csef, poster_v6, notebook_p10_lab_notebook, interview_qa_guide, facility_flyer_neurocare, csef_rules_comparison [INFERRED 0.88]
- **CSEF 2026 Presentation Materials Suite** — main_script_doc, short_version_doc, memorization_guide_doc, qa_bank_doc, qa_complete_doc, elevator_pitch_doc, judge_interview_prep_doc [EXTRACTED 0.95]
- **Closed-Loop 40 Hz Entrainment System Pipeline** — dataset_openneuro_ds005048, concept_eegnet_static, concept_12_pac_stim_features, concept_causal_tcn, concept_closed_loop_controller, concept_alignment_metric [EXTRACTED 0.95]
- **Clinical Translation Phases A/B/C and FDA Pathway** — clinical_phase_a_observational, clinical_phase_b_feasibility, clinical_phase_c_comparative, clinical_fda_de_novo, clinical_tier1_muse, clinical_tier2_openbci, clinical_tier3_hospital [EXTRACTED 0.90]
- **Eight-model convergence at R-squared = 0.287 static ceiling** — model_eegnet_static, model_spec_temp_net_v3, model_vit_tcnet_v4, model_ridge_regression_v5, model_atcnet_v8, concept_static_ceiling_r2_287, concept_architecture_search_8 [EXTRACTED 0.95]
- **Six-controller comparison on 35-subject real EEG replay** — controller_fixed_schedule, controller_reactive_threshold, controller_tcn_predictive, controller_hybrid_tcn_reactive, controller_pi, controller_alignment_oracle [EXTRACTED 0.95]
- **Primary TCN predictive result (alignment, targeting, PAC gap, universality)** — result_tcn_alignment_72_1, result_low_pac_targeting_82_6, result_pac_gap_30_5, result_35_of_35_benefit, controller_tcn_predictive [EXTRACTED 0.90]
- **Architecture Marathon: V1-V8 All Plateau at R2~0.287** — final_assessment_honest_baseline, v3_clean_mi_removal, v3_impl_spectempnet, v4_vit_tcnet_design, v4_failure_test_r2_0_252, ridge_regression_winner, eegnet_large_ceiling_confirmation, lab_notebook_architecture_marathon [EXTRACTED 0.90]
- **Honest Science Audit Arc (leakage discovery + errata)** — final_assessment_mi_leakage, v3_clean_mi_removal, leakage_free_shuffled_label_test, lab_notebook_errata_controller_table, lab_notebook_errata_date_correction, lab_notebook_errata_units_pac_gap [EXTRACTED 0.85]
- **Temporal Pivot -> MultiscaleTCN -> Real-Data Validation Flow** — lab_notebook_temporal_pivot, multiscale_causal_tcn_design, temporal_73_features, horizon_sweep_table, tcn_final_controller_table, lab_notebook_tcn_validation_locked [EXTRACTED 0.90]
- **Abstract Drafting Pipeline (Round1 -> Round2 -> Round3 Final)** — abstract_round1_draft1, abstract_round1_draft2, abstract_round1_draft3, abstract_round1_draft4, abstract_round1_draft5, abstract_round2_draft_a, abstract_round2_draft_b, abstract_round2_draft_c, abstract_round3_final, abstract_final_p10 [EXTRACTED 0.95]
- **Clinical Trial Phase Sequence (Observational -> Feasibility -> Comparative)** — clinical_roadmap_phase_a_observational, clinical_roadmap_phase_b_feasibility, clinical_roadmap_phase_c_comparative, clinical_roadmap_regulatory [EXTRACTED 0.90]
- **Project Timeline Dec 2025 -> March 2026 Daily-Log Arc** — v2_daily_log_project_kickoff, v2_daily_log_custom_loader, v2_daily_log_pac_computation_entry, v2_daily_log_eegnet_v1, v2_daily_log_v2_v8_exploration, v2_daily_log_temporal_pivot, v2_daily_log_tcn_development, v2_daily_log_horizon_sweep, v2_daily_log_controller_integration, v2_daily_log_real_data_validation, v2_daily_log_habituation_analysis, v2_daily_log_fatigue_sensitivity, v2_daily_log_final_validation, v2_daily_log_final_results_summary [EXTRACTED 0.95]
- **V1-V8 static PAC architecture search converging at R²≈0.287** — comp_analysis_v1_mi_leakage, comp_analysis_v2_clean_baseline, comp_analysis_v4_vit_tcnet_overfit, comp_analysis_v5_ridge_best, comp_analysis_v5_enh_leakage, comp_analysis_v7_raw_eeg_fail, comp_analysis_v8_specialized_fail, comp_analysis_r2_ceiling [EXTRACTED 0.95]
- **Seven-phase closed-loop implementation pipeline** — comp_method_phase1_env, comp_method_phase2_data, comp_method_phase3_pac, comp_method_phase4_eegnet, comp_method_phase5_personalization, comp_method_phase6_controller, comp_method_phase7_simulation [EXTRACTED 1.00]
- **Multi-audit framework (submission, pipeline, multiscale, deployment)** — submission_audit_leakage_pass, submission_audit_pac_oracle_dependency, submission_audit_smoothing_inflation, pipeline_audit_persistence_beats_tcn, pipeline_audit_ridge_beats_tcn, pipeline_audit_no_seeds_reproducibility, pipeline_audit_deployment_risk [EXTRACTED 0.90]
- **Eight-architecture search converging on R^2=0.287 ceiling** — concept_eegnet, concept_spectempnet, concept_vit_tcnet, concept_ridge_baseline, concept_atcnet, concept_r2_287_ceiling [EXTRACTED 0.95]
- **Six-controller closed-loop comparison on 35 subjects** — concept_fixed_schedule, concept_reactive_threshold, concept_tcn_predictive, concept_hybrid_controller, concept_pi_controller, concept_alignment_oracle, result_721_alignment [EXTRACTED 0.95]
- **Horizon sweep: Persistence vs Ridge vs TCN across 1-10s** — concept_persistence_baseline, concept_ridge_baseline, concept_multiscale_tcn, concept_horizon_inflection, concept_horizon_sweep [EXTRACTED 0.95]
- **Horizon Sweep Central Finding** — model_causal_tcn, result_horizon_sweep, fig3_horizon_sweep_chart, rationale_predict_further_not_better, rationale_data_ceiling [EXTRACTED 0.95]
- **Real EEG Controller Validation Flow** — dataset_ds005048, model_causal_tcn, concept_closed_loop_controller, result_controller_comparison, result_low_pac_targeting, result_all_35_benefit, result_oracle_bound_91 [EXTRACTED 0.95]
- **Poster Version Evolution V1 -> V5 -> Final PDFs** — poster_board_v1_main, poster_board_v2, poster_board_v3, poster_board_v4, poster_board_v5_pdf, poster_synopsys_final_pdf [EXTRACTED 0.90]
- **Multi-Version Presentation Script Suite** — v0_poster_script_main, v1_deep_technical, v1_simplified, v2_full_technical, v2_memorization_guide, presentation_script_md [INFERRED 0.90]
- **Research Background Documentation Package** — foundational_concepts_paper, literature_review_paper, technical_methods_paper, methodology_proposed_paper, annotated_bibliography, ad_ieee_paper, comprehensive_methodology_doc [EXTRACTED 1.00]
- **Phase 1 Ceiling to Phase 2 TCN Pivot Decision** — cpm_architecture_marathon, cpm_ceiling_discovery, cpm_spectempnet_leakage, pdd_snr_calculation, cpm_the_pivot, cpm_multiscale_tcn_arch [EXTRACTED 1.00]
- **Synopsys Submission Documentation Suite** — code_audit_report, judge_interview_prep, achievement_report, synopsys_winning_analysis, aiclub_email_draft [INFERRED 0.90]
- **TCN Architecture Design Rationale Cluster** — code_audit_rationale_tcn, code_audit_rationale_73_features, code_audit_rationale_lookback_20, code_audit_rationale_horizon_5s, code_audit_rationale_groupnorm, code_audit_rationale_huber_loss, code_audit_rationale_zscore_targets [EXTRACTED 1.00]
- **Research Documentation Progression (Concepts -> Lit Review -> Tech -> Methodology -> Biblio -> Paper)** — foundational_concepts_doc, literature_review_doc, technical_methods_doc, research_methodology_doc, annotated_bibliography, ieee_paper_draft [INFERRED 0.85]
- **Three-phase rigor audit (compliance + content + model)** — audit01_compliance, audit02_font, audit03_figure, audit04_content, audit05_defensibility, audit06_cross_doc, audit07_leakage, audit08_reproducibility, audit09_feature_validation, audit10_arch_exploration, audit11_hyperparam, audit_synthesis [EXTRACTED 1.00]
- **P10 two-stage controller data flow (EEG → EEGNet → features → TCN → personalization)** — p10_eegnet_baseline, p10_feature_73d, p10_multiscale_causal_tcn, p10_personalization_module, p10_two_stage_pipeline [EXTRACTED 1.00]
- **TCN architecture variants experimental sweep** — exp_deep_dilation, exp_multitask, exp_wider, exp_transformer, exp_design [EXTRACTED 1.00]
- **Closed-loop controller comparison (Fixed / PI / Reactive / TCN / Hybrid / Oracle) on PAC targeting gap** — pac_targeting_gap_controller_fixed, pac_targeting_gap_controller_pi, pac_targeting_gap_controller_reactive, pac_targeting_gap_controller_tcn, pac_targeting_gap_controller_hybrid, pac_targeting_gap_controller_oracle [EXTRACTED 0.95]
- **All six controllers compared in Figure 8** — controller_comparison_v2_fixed_schedule, controller_comparison_v2_reactive_threshold, controller_comparison_v2_pi_controller, controller_comparison_v2_tcn_predictive, controller_comparison_v2_hybrid_tcn_reactive, controller_comparison_v2_oracle [EXTRACTED 1.00]
- **Three evaluation metrics reported per controller** — controller_comparison_v2_alignment_metric, controller_comparison_v2_low_pac_stim_rate_metric, controller_comparison_v2_high_pac_rest_rate_metric [EXTRACTED 1.00]
- **Closed-Loop Control Strategies Compared on Stim-Alignment Plane** — stim_vs_alignment_pi_strategy, stim_vs_alignment_reactive_strategy, stim_vs_alignment_oracle_strategy, stim_vs_alignment_tcn_strategy, stim_vs_alignment_hybrid_strategy, stim_vs_alignment_fixed_strategy [EXTRACTED 0.95]
- **Threshold robustness claim: dual-axis sweep demonstrates TCN advantage over delta-z range** — threshold_sensitivity_tcn_alignment_curve, threshold_sensitivity_stim_rate_curve, threshold_sensitivity_reactive_baseline, threshold_sensitivity_tcn_advantage_zone, threshold_sensitivity_plateau_finding [INFERRED 0.85]
- **Train/Val/Test splits all land above identity line** — per_subject_utility_train_split, per_subject_utility_val_split, per_subject_utility_test_split, per_subject_utility_claim_universal_benefit [INFERRED 0.90]
- **Three-method PAC forecasting comparison across horizons** — horizon_sweep_persistence_baseline, horizon_sweep_ridge_baseline, horizon_sweep_causal_tcn, horizon_sweep_metric_r2, horizon_sweep_xaxis_horizon [EXTRACTED 0.95]
- **Argument structure: baseline collapse plus TCN stability within operational band justifies proactive control claim** — horizon_sweep_finding_baseline_collapse, horizon_sweep_finding_tcn_advantage, horizon_sweep_operational_band, horizon_sweep_claim_proactive_control [INFERRED 0.90]
- **End-to-end 7-stage closed-loop 40 Hz entrainment pipeline** — system_block_diagram_patient_eeg, system_block_diagram_preprocessing, system_block_diagram_eegnet, system_block_diagram_feature_extraction, system_block_diagram_causal_tcn, system_block_diagram_closed_loop_controller, system_block_diagram_audio_stim [EXTRACTED 0.95]
- **ML model stack: static PAC predictor, feature extractor, and temporal forecaster** — system_block_diagram_eegnet, system_block_diagram_feature_extraction, system_block_diagram_causal_tcn [EXTRACTED 0.90]
- **PAC trace + Reactive lane + TCN lane form head-to-head controller comparison** — timeline_example_pac_trace, timeline_example_reactive_lane, timeline_example_tcn_lane, timeline_example_low_pac_epochs [INFERRED 0.90]
- **Scientific method sections forming the poster narrative** — slide1_print_introduction, slide1_print_background, slide1_print_hypothesis, slide1_print_procedure, slide1_print_results, slide1_print_conclusions [INFERRED 0.85]
- **Results evidence group (findings + supporting figures)** — slide1_print_results, slide1_print_fig_horizon_sweep, slide1_print_fig_bar_comparison [INFERRED 0.80]
- **Full poster section structure (IMRaD layout)** — slide1_introduction, slide1_background, slide1_hypothesis, slide1_model_approach, slide1_materials, slide1_procedures, slide1_results_findings, slide1_conclusions [EXTRACTED 0.90]
- **Core quantitative findings of TCN predictive vs reactive closed-loop** — slide1_result_alignment, slide1_result_low_pac_targeting, slide1_result_pac_gap, slide1_result_per_subject [EXTRACTED 0.90]
- **Four-strategy closed-loop validation benchmark** — validation_comparison_strategy_fixed_schedule, validation_comparison_strategy_reactive_threshold, validation_comparison_strategy_predictive_lookahead, validation_comparison_strategy_oracle [EXTRACTED 0.95]
- **Three metrics evaluated: PAC improvement %, efficiency ratio, and stimulation time %** — validation_comparison_metric_pac_improvement_pct, validation_comparison_metric_efficiency_ratio, validation_comparison_metric_stimulation_time_pct [EXTRACTED 0.90]
- **Four controller strategies compared across both simulation backends** — tribe_v2_backend_strategy_fixed_schedule, tribe_v2_backend_strategy_reactive, tribe_v2_backend_strategy_predictive, tribe_v2_backend_strategy_oracle, tribe_v2_backend_original_exponential, tribe_v2_backend_tribe_v2_enhanced [EXTRACTED 0.95]
- **Three-metric evaluation framework: mean PAC, efficiency ratio, stimulation time** — tribe_v2_backend_metric_mean_pac, tribe_v2_backend_metric_efficiency_ratio, tribe_v2_backend_metric_stim_time_pct, tribe_v2_backend_comparison_figure [INFERRED 0.85]
- **Disease severity gradient (healthy to severe) swept in TRIBE V2 simulation** — tribe_v2_disease_severity_healthy, tribe_v2_disease_severity_preclinical, tribe_v2_disease_severity_mild, tribe_v2_disease_severity_moderate, tribe_v2_disease_severity_severe [EXTRACTED 0.95]
- **Three-panel figure: PAC response, PAC dynamics, stimulation efficiency** — tribe_v2_alzheimer_sweep_panel_pac_response, tribe_v2_alzheimer_sweep_panel_pac_dynamics, tribe_v2_alzheimer_sweep_panel_stim_efficiency [EXTRACTED 0.90]
- **Three closed-loop stimulation strategies compared across AD severity** — alzheimer_simulation_fixed_strategy, alzheimer_simulation_reactive_strategy, alzheimer_simulation_predictive_strategy [EXTRACTED 1.00]
- **Six-panel figure telling one story: severity-dependent controller comparison** — alzheimer_simulation_panel_a, alzheimer_simulation_panel_b, alzheimer_simulation_panel_c, alzheimer_simulation_panel_d, alzheimer_simulation_panel_e, alzheimer_simulation_panel_f [EXTRACTED 1.00]
- **Two-stage training pipeline: EEGNet static PAC -> TCN temporal PAC forecast** — figure9_raw_eeg_input_7ch, figure9_eegnet_1457_params, figure9_current_pac_estimate, figure9_tcn_features_input, figure9_causal_tcn_5154_params, figure9_future_pac_output [EXTRACTED 0.90]
- **Real-EEG replay validation flow** — figure9_primary_real_eeg_replay, figure9_tcn_controller, figure9_compare_vs_actual_pac, figure9_alignment_score, figure9_ground_truth_pac_input [EXTRACTED 0.90]
- **Three-panel dataset overview (channels, protocol, splits)** — figure8_panel_a_frontal_channels, figure8_panel_b_stim_rest_protocol, figure8_panel_c_subject_level_split [EXTRACTED 0.90]
- **Adaptive scheduling mechanism (TCN lookahead + hysteresis + PAC-gated proactive stim)** — figure3_adaptive_schedule, figure3_tcn_lookahead, figure3_hysteresis_3s, figure3_proactive_stimulation, figure3_pac_signal [EXTRACTED 0.90]
- **Fixed-schedule failure modes (no adaptation, wasted high-PAC stim, missed low-PAC rest)** — figure3_fixed_schedule, figure3_no_adaptation_claim, figure3_wasted_stim_claim, figure3_missed_low_pac_claim [EXTRACTED 0.90]
- **Alignment Composite Metric Construction** — figure12_alignment_metric, figure12_low_pac_stim_rate, figure12_high_pac_rest_rate, figure12_subject_median_threshold [EXTRACTED 0.90]
- **Four Controller Strategies Compared in Figure 13** — figure13_fixed_schedule_controller, figure13_reactive_controller, figure13_tcn_predictive_controller, figure13_oracle_controller [EXTRACTED 0.95]
- **Three Performance Metrics Reported per Controller** — figure13_alignment_metric, figure13_low_pac_stim_rate_metric, figure13_high_pac_rest_rate_metric [EXTRACTED 0.95]
- **PAC Mechanism: Theta Phase + Gamma Amplitude + MI Quantification** — figure2_theta_rhythm, figure2_gamma_oscillations, figure2_theta_modulates_gamma, figure2_tort_modulation_index [EXTRACTED 0.90]
- **Closed-Loop Alzheimer's Therapy Deployment Vision** — figure11_muse2_headband, figure11_closed_loop_therapy_claim, figure11_clinical_deployment, figure11_alzheimers_application, figure11_auditory_stimulation [INFERRED 0.80]
- **Three-Stage Translation Roadmap (Current -> Next -> Clinical)** — figure10_this_project, figure10_next_steps, figure10_clinical_vision [EXTRACTED 0.95]
- **Alignment comparison: fixed 45% vs adaptive 72%** — figure1_panel_a_fixed_schedule, figure1_panel_b_adaptive_schedule, figure1_fixed_alignment_45, figure1_adaptive_alignment_72 [EXTRACTED 0.95]
- **Complete Closed-Loop PAC Entrainment Pipeline** — figure5_raw_eeg_input, figure5_eegnet_model, figure5_feature_extraction, figure5_causal_tcn, figure5_closed_loop_controller, figure5_audio_signal_generator, figure5_audio_speaker_40hz [EXTRACTED 0.95]
- **Three-State Controller Decision Set** — figure5_decision_stimulate, figure5_decision_rest, figure5_decision_maintain [EXTRACTED 0.90]
- **TCN 12-Feature Input Vector** — figure5_spectral_features, figure5_pac_features, figure5_stim_context, figure5_causal_tcn [EXTRACTED 0.90]
- **Subject-level splits (35 total) from ds005048** — figure14_train_split, figure14_validation_split, figure14_test_split, figure14_openneuro_ds005048 [EXTRACTED 0.90]
- **Evidence chain supporting universal TCN advantage** — figure14_tcn_advantage_region, figure14_identity_line, figure14_binomial_test, figure14_claim_universal_benefit [EXTRACTED 0.90]
- **Three-condition feature ablation comparison** — figure4_all_73_features_condition, figure4_spectral_only_condition, figure4_pac_stim_12_features_condition [EXTRACTED 0.90]
- **73-feature composition: spectral + PAC + stim context** — figure4_spectral_feature_group, figure4_pac_feature_group, figure4_stim_context_feature_group [EXTRACTED 0.90]
- **Three-model horizon sweep comparison (Persistence vs TCN 7ch vs TCN 4ch)** — figure6_persistence_baseline, figure6_pac_stim_tcn_7ch, figure6_pac_stim_tcn_4ch [INFERRED 0.90]
- **TCN 7-channel performance across all horizons** — figure6_horizon1_tcn7, figure6_horizon3_tcn7, figure6_horizon5_tcn7, figure6_horizon7_tcn7, figure6_horizon10_tcn7 [EXTRACTED 1.00]
- **Three-panel controller timeline comparison** — figure7_actual_pac_signal, figure7_reactive_controller_decisions, figure7_tcn_predictive_controller_decisions [EXTRACTED 0.95]
- **Matched conditions across reactive vs TCN comparison** — figure7_matched_conditions_caption, figure7_only_difference_pac_source, figure7_reactive_controller_decisions, figure7_tcn_predictive_controller_decisions [EXTRACTED 0.90]

## Communities

### Community 0 - "Closed-Loop Controller"
Cohesion: 0.01
Nodes (273): ClosedLoopController, StimState, test_controller(), AudioEngine, _build_figure(), FixedScheduleControl, load_subject_data(), load_test_subjects() (+265 more)

### Community 1 - "Multiscale TCN Training"
Cohesion: 0.01
Nodes (265): CausalDSConvBlock, Checkpoint deployment realism audit.  Evaluates a trained checkpoint under multi, SeqDataset, _eval_denorm(), _eval_r2_norm(), Baseline and comparison model architectures for the architecture comparison stud, Causal Transformer encoder for sequence-to-scalar PAC prediction.      A causal, Train any nn.Module that takes (B, T, F) and outputs (B,) scalar predictions. (+257 more)

### Community 2 - "CSEF Presentation Prep"
Cohesion: 0.01
Nodes (331): Fixed Schedule Goes Wrong Direction (PAC gap = -6.6), Per-subject fine-tuning provides minimal +0.01 R2, Project Achievement Report, Architecture V3 Design: SpecTempNet, Archive 03 Memorization Guide, FINAL 01 Main Script (archive), FINAL 02 Short Version (archive), FINAL 04 Q&A + Danger Zones (archive) (+323 more)

### Community 3 - "Live EEG Streaming & UI"
Cohesion: 0.02
Nodes (203): Sleep 2 seconds and return one (n_channels, 500) float32 EEG window.          Sl, Stop stream and release BrainFlow session., Simulated EEG source using BrainFlow SYNTHETIC_BOARD.      Creates a BrainFlow b, SimulatedEEGAdapter, _get_patient_by_id(), _init_session_state(), label(), load_models() (+195 more)

### Community 4 - "Experimental Audits (Archive)"
Cohesion: 0.02
Nodes (95): Critical audit: Check if spectral features include target PAC, AddGaussianNoise, ChannelDropout, Compose, EEGAugmentation, MagnitudeWarp, Time-Series Data Augmentation for EEG  Implements augmentation techniques specif, Shift the signal in time (circular shift).      This makes the model robust to t (+87 more)

### Community 5 - "BIDS Data Loading"
Cohesion: 0.03
Nodes (87): BIDSDataProcessor, EEGWindowDataset, main(), BIDS Data Loader for Closed-Loop 40Hz Entrainment Research  Loads OpenNeuro ds, Get subject ID for a sample., Get session ID for a sample., Processes BIDS-compliant EEG dataset into training windows.      Pipeline:, Initialize BIDS data processor.          Args:             bids_root: Path to (+79 more)

### Community 6 - "Research Background & Literature"
Cohesion: 0.02
Nodes (134): Alzheimer's disease: 55M worldwide, tripling by 2050, OpenNeuro ds005048 dataset (v1.0.1), EEGNet regression (~2000 params) for PAC prediction, PING: Pyramidal-Interneuron Network Gamma mechanism, GENUS: Gamma Entrainment Using Sensory Stimulation, Model Predictive Control framework with MIQP, 30% non-responder fraction (Fortunato 10/33), Theta-gamma PAC as entrainment biomarker (beta=0.693 predictor) (+126 more)

### Community 7 - "Alzheimer Disease Model"
Cohesion: 0.04
Nodes (84): AlzheimerProfile, get_profile(), interpolate_profile(), Alzheimer's Disease Modeling Layer for TRIBE V2 Integration  Models the effects, Apply region-specific disease modification to ROI activations.          Differen, Modify neural mass model external drive for AD simulation.          Args:, Modify exponential simulator parameters for AD simulation.          Compatible w, Get Alzheimer's profile by severity name.      Args:         severity: One of "h (+76 more)

### Community 8 - "CSEF Abstract & References"
Cohesion: 0.03
Nodes (101): CSEF Abstract, Feature Ablation Headline Finding (73 -> 12 features), P10 Abstract PDF, P10 Synopsys Abstract, Backus et al. (2018) - Theta-Gamma Coupling & WM [5], Brian Intensify (ElSayed et al. 2025) [24], Cabral et al. (2025) Front Digital Health - Personalized digital therapeutics [16], Chan et al. 2025 (long-term 40Hz safety) (+93 more)

### Community 9 - "Experimental Ensembles"
Cohesion: 0.05
Nodes (72): ensemble_evaluate(), main(), Best combination experiments: 1. Target smoothing (ts=5) + deep TCN architecture, Evaluate ensemble of models by averaging predictions., Train model and evaluate., train_and_eval(), CausalConvBlock, compute_metrics() (+64 more)

### Community 10 - "Abstract Drafting Rounds"
Cohesion: 0.03
Nodes (85): P10 Final Abstract (247 words), Archived P10.Abstract (1).pdf (earlier draft), Archived P10.Abstract.pdf (earlier PDF), P10.Abstract.pdf (final submission), Round1 Draft1 Clinical Hook, Round1 Draft3 Problem-Solution, Round1 Draft4 Judges' Perspective, Round2 Draft A: Best Narrative (Draft 3 + 4 merge) (+77 more)

### Community 11 - "Methodology Plan Phases"
Cohesion: 0.03
Nodes (83): Annotated Bibliography Sources, MNE-BIDS Data Loader Example, Seven-Phase Methodology Plan, Phase 1: Environment Setup, Phase 2: Data Acquisition & Preprocessing, Phase 3: PAC Label Computation (Tort MI), Phase 4: EEGNet Architecture & Training, Phase 5: Personalization Module (30s rolling baseline) (+75 more)

### Community 12 - "Project Results Summary"
Cohesion: 0.03
Nodes (79): 91% of Oracle Performance, Core Innovation: Temporal PAC Prediction at 5-10s, Fixed Schedule goes WRONG direction (PAC gap -6.6), 6 Limitations: real-time, single dataset, short sessions, R2 ceiling, ts=5 in sweep, no clinical outcome, Real-Data Closed-Loop Validation (35 subjects), Project Achievement Report (Feb 27 2026), TCN Beats Baselines at 5-10s (+0.5 R2 margin), 35/35 Subjects Benefit (100%) (+71 more)

### Community 13 - "Replay & CUSUM Analysis"
Cohesion: 0.04
Nodes (39): CUSUMControl, evaluate_decisions(), _extract_biomarkers_single(), FixedScheduleControl, load_subjects(), main(), MultiBiomarkerReactiveControl, OracleControl (+31 more)

### Community 14 - "PDF Generation Scripts"
Cohesion: 0.05
Nodes (27): FPDF, clean_markdown(), generate_pdf(), parse_table(), Write a major section header (## level)., Write a subsection header (### level)., Write a sub-subsection header (#### level)., Write body paragraph text. (+19 more)

### Community 15 - "Mentor Feedback & Meetings"
Cohesion: 0.04
Nodes (59): Clark Maxwell Scaffolding Quote, Rationale for 5-Second Horizon, Horizon Sweep 1-10s, Feedback: Record EEG Demo Video, Kushal Khare Meeting Transcript (Mar 4), Feedback: Print Notebook Put in Folder, Feedback: Poster Has Too Much Text, Feedback: Prepare Two Script Versions (+51 more)

### Community 16 - "PPTX Presentation Builder"
Cohesion: 0.1
Nodes (43): _add_paragraph(), _add_textbox(), _first_paragraph(), main(), p01_title(), p02_intro1(), p03_intro2(), p04_methods1() (+35 more)

### Community 17 - "CSEF PPTX Generator"
Cohesion: 0.11
Nodes (55): add_body(), add_body_mixed(), add_bullet(), add_caption(), add_figure(), add_heading(), add_spacer(), add_subheading() (+47 more)

### Community 18 - "TVB Alignment Validation"
Cohesion: 0.06
Nodes (28): evaluate_alignment(), FixedScheduleCtrl, hedges_g(), main(), TVB Jansen-Rit Alignment Evaluation: Closed-Loop Controller Comparison  Runs Fix, ReactiveCtrl, run_oracle_trial(), run_trial() (+20 more)

### Community 19 - "LSTM/GRU Temporal Models (Legacy)"
Cohesion: 0.06
Nodes (36): MultiHorizonPredictor, Temporal PAC Prediction Models  LSTM and GRU architectures for predicting futu, Args:             n_channels: Number of EEG channels             n_samples: Sa, Args:             batch: Dictionary with keys:                 'eeg':, Count total trainable parameters., Count parameters per component., Extension: Predict PAC at multiple future horizons simultaneously.      Shares, Lightweight spatial encoder for individual EEG windows.      Reduces (7, 500) (+28 more)

### Community 20 - "TCN Variants Ablation"
Cohesion: 0.06
Nodes (30): AttentionPool1D, build_variant(), CausalDSConvBlock, CausalSinusoidalPE, _count_parameters(), DeepDilationTCN, LastStepPool, _make_regression_head() (+22 more)

### Community 21 - "Improved TCN Architecture"
Cohesion: 0.07
Nodes (28): AttentionPool1D, CausalDSConvBlock, ImprovedModelConfig, ImprovedTCN, LastStepPool, ImprovedTCN: Causal TCN with temporal multi-head self-attention and three-head o, Causal TCN with temporal multi-head self-attention and three regression heads., Upper-triangular boolean mask: True = masked (no attending to future). (+20 more)

### Community 22 - "Data Loader v2 (Archive)"
Cohesion: 0.07
Nodes (25): EEGDatasetV2, load_processed_data_v2(), Enhanced Data Loader for ΔPAC Prediction (Version 2)  Key improvements over v1, Load preprocessed data and compute ΔPAC labels.      Args:         data_dir:, PyTorch Dataset for EEG windows with ΔPAC labels.      Changes from v1:     -, Test the v2 data loader., Args:             X: EEG windows (n_samples, n_channels, n_timepoints), Apply data augmentation to EEG window.          Techniques:         1. Time j (+17 more)

### Community 23 - "TRIBE TCN Validation"
Cohesion: 0.08
Nodes (24): build_features_from_sequence(), CausalConv1dBlock, evaluate_alignment(), FixedScheduleCtrl, generate_pac_sequences(), hedges_g(), main(), TRIBE V2 + TCN-TRIBE: Train a TCN on TRIBE simulator data, then evaluate.  Pipel (+16 more)

### Community 24 - "Training v3 (Archive)"
Cohesion: 0.07
Nodes (26): compute_r2(), EEGDatasetV3, evaluate(), load_and_preprocess_data(), main(), Evaluate on validation/test set., Dataset with both raw EEG and pre-computed spectral features., Load processed data and extract spectral features. (+18 more)

### Community 25 - "CSEF Presentation Builder"
Cohesion: 0.13
Nodes (27): CSEF, main(), p01_title(), p02_intro1(), p03_intro2(), p04_methods1(), p05_methods2(), p06_methods3() (+19 more)

### Community 26 - "Lab Notebook PDF Generator"
Cohesion: 0.09
Nodes (33): add_figure(), build_styles(), build_table_flowable(), build_title_page(), build_toc(), clean_md(), escape_xml(), extract_metadata() (+25 more)

### Community 27 - "Data Source Adapters"
Cohesion: 0.08
Nodes (23): _NumpySimulatedAdapter, Hardware-agnostic EEG adapters for closed-loop inference.  Provides two adapters, Pure-numpy fallback when brainflow is not installed (e.g. cloud deploy).      Ge, Muse 2 BLE adapter — NOT VIABLE on macOS Darwin 25.4.0.      Attempted: 2026-03-, Attempt to open a Muse 2 BLE session.          Args:             mac_address: Bl, Sleep 2 seconds and return one (n_channels, 500) float32 EEG window.          Re, Stop stream and release BrainFlow session., RealEEGAdapter (+15 more)

### Community 28 - "Static PAC Prediction Findings"
Cohesion: 0.06
Nodes (35): Finding: R²=0.287 is a data ceiling (8 architectures converge), EEGNet baseline (1,457 params, R²=0.287), Fatigue model robustness across 4 formulations, Fatigue sensitivity: +9-11% adaptive advantage across severities, Rationale: custom .fdt/HDF5 loader with Fortran order, 73-dimensional causal feature vector design, Rationale: GroupNorm for cross-subject PAC baseline variability, Habituator/Facilitator patient split (48.6% / 51.4%) (+27 more)

### Community 29 - "Notebook Audit Phases"
Cohesion: 0.08
Nodes (34): Phase 1A: CSEF Compliance Checklist (18/18 PASS), Phase 1B: Font Audit (19/20 PASS, Times New Roman WARN), Phase 1C: Figure Audit (outdated 73-feat/31K-param spec WARN), Phase 2A: Content Accuracy (66/67 values verified), Hysteresis discrepancy: 5s code vs 3s research paper, Phase 2B: Defensibility STRONG rating, Four disclosed limitations (offline, EEGNet not in loop, site, channels), Phase 2C: Cross-document Consistency (12/12 core values) (+26 more)

### Community 30 - "Shared Utilities"
Cohesion: 0.07
Nodes (29): compute_regression_metrics(), count_parameters(), ensure_dir(), get_device(), load_config(), plot_comparison_bars(), plot_pac_timeseries(), plot_prediction_scatter() (+21 more)

### Community 31 - "TRIBE Alignment Validation"
Cohesion: 0.1
Nodes (12): evaluate_alignment(), FixedScheduleCtrl, hedges_g(), main(), OracleCtrl, PredictiveCtrl, TRIBE V2-Enhanced Simulation: Alignment & Clinical Utility Evaluation  Computes, Compute alignment metrics — exact same definitions as original study. (+4 more)

### Community 32 - "v8 Specialized EEG Models"
Cohesion: 0.08
Nodes (14): ATCNet, AugmentedDataset, EEGNet, evaluate_model(), PhaseSwapAugmentation, V8: Specialized EEG Architectures from Research  Based on recent literature (202, EEGNet: Compact CNN for EEG-based BCIs.      Original paper: Lawhern et al. (201, ATCNet: Attention Temporal Convolutional Network.      Combines multi-head self- (+6 more)

### Community 33 - "4ch Channel Comparison Figures"
Cohesion: 0.1
Nodes (27): Delta annotation (Delta = -0.473 at 5s between TCN7 and TCN4), Finding: Reducing to 4 Muse-compatible channels collapses predictive power beyond 3s, Finding: Persistence ties TCN at 1s horizon (0.726 vs 0.725), competitive only at 1-2s, Finding: TCN 7ch maintains R^2>=0.42 across 3-10s while persistence collapses and 4ch TCN goes negative, Persistence R^2=0.387 at 10s, TCN 4ch R^2=-0.081 at 10s, TCN 7ch R^2=0.669 at 10s, Persistence R^2=0.726 at 1s (+19 more)

### Community 34 - "System Block Diagram"
Cohesion: 0.09
Nodes (26): Alignment Score, Band 1: EEGNet Static PAC Predictor, Band 2: Causal TCN Temporal PAC Forecaster, Causal TCN (5,154 params), Compare vs Actual PAC, Current PAC Estimate (scalar output), Delta PAC Output (change prediction), EEGNet (1,457 params) (+18 more)

### Community 35 - "PAC Feature Extractors (Archive)"
Cohesion: 0.12
Nodes (22): butter_bandpass_filter(), compute_cross_channel_plv(), compute_direct_pac(), compute_instantaneous_phase_amplitude(), compute_phase_amplitude_correlation(), compute_phase_locking_value(), compute_preferred_phase(), extract_pac_features() (+14 more)

### Community 36 - "Excalidraw Diagram Generator"
Cohesion: 0.3
Nodes (21): _arrow(), box_with_text(), build_section_11(), build_section_15(), build_section_19(), build_section_2(), build_section_3(), build_section_6() (+13 more)

### Community 37 - "LaTeX Paper Generator"
Cohesion: 0.15
Nodes (21): apply_unicode_replacements(), convert_citations(), convert_inline_formatting(), escape_latex(), fix_common_issues(), generate_latex(), main(), make_label() (+13 more)

### Community 38 - "Paper Section Structure"
Cohesion: 0.13
Nodes (22): Acknowledgements Section, Background Section (40 Hz entrainment, gamma oscillations, prior literature), Conclusions Section (predictive closed-loop outperforms reactive, approaches oracle), Data, Charts & Models Section (Figure panels showing metrics), Dataset: OpenNeuro ds005048 (35 subjects, frontal EEG), Static EEGNet Stage (~1,457 params, 7 frontal channels, 2s windows), Further Research Section (next steps, clinical translation), Horizon Sweep Figure (TCN vs persistence/Ridge baselines at 1-10s) (+14 more)

### Community 39 - "System Architecture Figure"
Cohesion: 0.12
Nodes (22): Adaptive 40 Hz Stimulation, Audio Signal Generator (Adaptive), Audio Speaker (40 Hz Audio Output), Causal TCN (5,154 params, dilated d=1,2,4,8), Closed-Loop Controller, Control Parameters (30s roll. baseline, z-thr ±0.5, 3-sec hyst), Current PAC Estimate, MAINTAIN Decision (+14 more)

### Community 40 - "Leakage & V2 Findings (Archive)"
Cohesion: 0.1
Nodes (20): PAC_MI Circular Feature Leakage, Habituation Response Split (17/18 of 35), Horizon Sweep Table (1s/5s/10s), V2 Data Augmentation Suite, V2 Delta-PAC Prediction Target, EEGNetV2 (F1=12, F2=24, ~3.2K params), Huber Loss (delta=1.0), Architecture Marathon Day (Feb 16) (+12 more)

### Community 41 - "Sliding PAC Computation"
Cohesion: 0.15
Nodes (18): _bandpass_filter(), compute_multichannel_pac(), compute_sliding_pac_for_segment(), compute_sliding_pac_for_split(), compute_tort_mi(), find_contiguous_segments(), main(), Compute sliding-window PAC labels for all processed EEG windows.  Instead of the (+10 more)

### Community 42 - "Multiscale Dataset Builder"
Cohesion: 0.18
Nodes (18): build_multiscale_dataset(), _build_split_samples(), _causal_moving_average(), _causal_target_smooth(), _load_spectral_cache(), _load_split(), main(), _normalize_with_train_stats() (+10 more)

### Community 43 - "TRIBE V2 Backend Panels"
Cohesion: 0.14
Nodes (19): Claim: Simulation backend choice (exponential vs TRIBE V2) dominates absolute PAC levels and efficiency metrics more than controller strategy does, TRIBE V2 vs Original Exponential Backend Comparison Figure, Panel: PAC Improvement per Unit Stimulation (efficiency ratio), Panel: Energy Efficiency (Stimulation Time %), Panel: PAC by Strategy and Backend (bar chart), Panel: Predictive Controller PAC Dynamics (time series 0-6 min), Finding: Predictive PAC dynamics under TRIBE V2 saturate lower (~0.15) and more rhythmically than exponential backend (~0.20-0.27), Finding: Efficiency per unit stimulation is much higher under exponential backend (Reactive/Predictive ~3.5) versus TRIBE V2 (~1.5); Fixed/Oracle under TRIBE V2 go slightly negative (+11 more)

### Community 44 - "Cross-Epoch Transition Analysis"
Cohesion: 0.25
Nodes (14): analyze_cross_epoch_transitions(), _corr(), _denorm(), evaluate_model(), get_device(), main(), persistence_baseline(), _r2() (+6 more)

### Community 45 - "v7 Raw EEG Models"
Cohesion: 0.12
Nodes (11): AttentionModel, CNN1D, CNNAttentionHybrid, evaluate_model(), V7: Lightweight Deep Learning on Raw EEG  Different approach: Learn features dir, Multi-head attention over time points.      Learns which time points are importa, Hybrid: CNN extracts features, Attention pools them.      Combines local pattern, Train model with early stopping. (+3 more)

### Community 46 - "Alzheimer Simulation Results"
Cohesion: 0.18
Nodes (18): TRIBE V2 Alzheimer's Disease Simulation Figure, Finding: Predictive maintains flat efficiency ratio near ~0.25 while Fixed/Reactive collapse toward 0 at severe stages (Panel D), Finding: Predictive controller's benefit over Fixed is largest in healthy/preclinical/mild and vanishes in moderate/severe, Finding: PAC response and benefit degrade monotonically from healthy to severe across all strategies, Finding: Fixed and Predictive sustain late-session PAC better than Reactive, which droops in the last 25% across severity levels (Panel F), Fixed Schedule Stimulation Strategy, Method: 10-minute closed-loop 40Hz entrainment simulation comparing three controllers across 5 AD severity levels, PAC (Theta-Gamma Phase-Amplitude Coupling) Outcome Metric (+10 more)

### Community 47 - "Alzheimer Simulation Script"
Cohesion: 0.17
Nodes (6): FixedSchedule, main(), Predictive, Alzheimer's Disease Simulation with TRIBE V2-Enhanced Closed-Loop Control  Demon, Reactive, run_trial()

### Community 48 - "Poster v2 Builder"
Cohesion: 0.15
Nodes (16): add_body_block(), add_callout(), add_content_bg(), add_gradient_rect(), add_rect(), add_section_header(), add_text(), clear_slide() (+8 more)

### Community 49 - "Closed-Loop Demo Benchmark"
Cohesion: 0.21
Nodes (16): Validation Comparison: Four-Panel Strategy Benchmark, Finding: Fixed Schedule yields highest raw PAC improvement but at 66.7% stimulation time (worst efficiency ratio 5.4), making it energetically wasteful, Finding: Predictive Look-Ahead matches Oracle on both PAC improvement (~300%) and stimulation-time (~47%), while beating Reactive Threshold on PAC lift, Finding: Reactive Threshold is most efficient per stim unit (7.5) but undershoots on total PAC lift (176.7%), trading effectiveness for thrift, Metric: Efficiency Ratio (Fixed 5.4, Reactive 7.5, Predictive 6.3, Oracle 6.4), Metric: PAC Improvement vs Baseline (Fixed 353.4%, Reactive 176.7%, Predictive 300.6%, Oracle 302.0%), Metric: Stimulation Time % (Fixed 66.7, Reactive 23.3, Predictive 47.5, Oracle 47.2), Panel D: Energy Efficiency (Stimulation Time %) (+8 more)

### Community 50 - "Temporal Leakage Validation"
Cohesion: 0.18
Nodes (15): audit_code(), load_data(), main(), Code Validation & Audit Script (runs without PyTorch)  Validates the temporal, Test 2: Verify no subject appears in multiple splits., Test 3: Characterize PAC temporal autocorrelation per subject.     This determi, Test 4: Sklearn Ridge baseline for temporal prediction.     Uses PAC history +, Test 5: How does prediction quality change with horizon? (+7 more)

### Community 51 - "Multiscale Comparison Study"
Cohesion: 0.27
Nodes (15): _dataset_base_4ch(), _dataset_base_7ch(), _dataset_dir(), _device(), _ensure_dataset(), main(), _n_features(), parse_args() (+7 more)

### Community 52 - "Core Figure Generation"
Cohesion: 0.22
Nodes (15): _controller_order(), fig_controller_comparison(), fig_pac_targeting_gap(), fig_per_subject_utility(), fig_stim_vs_alignment(), main(), Bar chart of (mean PAC during rest - mean PAC during stim) per controller., Scatter: Reactive utility (x) vs TCN utility (y), colored by split. (+7 more)

### Community 53 - "Claims Verification Audit"
Cohesion: 0.12
Nodes (16): Claims Verification: TRUE vs FALSE, data_loader.py VERIFIED (HDF5 .set + Fortran .fdt), EEGNet 1,457 parameters verified, pac_computation.py VERIFIED (Tort MI), preprocessing.py VERIFIED, Rationale: 73 features (61 spectral + 7 PAC + 5 stim context), Rationale: EEGNet chosen (1457 params, 12 samples/param, 8 archs tested all plateau at R2=0.287), Rationale: GroupNorm over BatchNorm (stable across subjects) (+8 more)

### Community 54 - "Research Paper Sections"
Cohesion: 0.22
Nodes (16): Acknowledgements section, Background Section (prior work, fixed vs adaptive 40Hz stim), Conclusions: TCN closed-loop delivers +8% alignment, 35/35 subjects benefit, Data Source & Models: OpenNeuro ds005048, N=35 subjects, 7 frontal channels, Figure: Bar chart comparing Fixed / Reactive / Predictive / Oracle strategies, Figure: Horizon sweep (TCN R^2 vs persistence/Ridge at 1-10s), Further Research directions, Hypothesis: Closed-loop predictive TCN stimulation outperforms fixed/reactive schedules on PAC entrainment (+8 more)

### Community 55 - "Alzheimer Severity Sweep"
Cohesion: 0.15
Nodes (16): TRIBE V2 Alzheimer's Disease Simulation, TRIBE V2 Alzheimer's Disease Simulation Sweep (Predictive Controller), Panel 2: PAC Dynamics over Time by Severity (time-series), Panel 1: Mean PAC vs Disease Severity (bar chart), Panel 3: Stimulation Efficiency Ratio vs Severity (bar chart), Disease Severity: Healthy, Disease Severity: Mild, Disease Severity: Moderate (+8 more)

### Community 56 - "Citation Research"
Cohesion: 0.16
Nodes (15): Canolty & Knight 2010, Iaccarino et al. 2016 (Nature), Found OpenNeuro ds005048 Dataset, Original Music Therapy Dead End, AD vs PD Decision (Dec 10 2025), Lahijanian et al. 2024 (Scientific Reports), Lawhern et al. 2018 EEGNet, Digital Research Log Notebook (+7 more)

### Community 57 - "Original Poster Builder"
Cohesion: 0.2
Nodes (13): add_body_text(), add_box(), add_callout_box(), add_content_bg(), add_section_header(), add_text_box(), Generate CSEF 2026 poster board PPTX — 24x32 inches (prints at 200% → 48x64)., Add a gold metric callout box. (+5 more)

### Community 58 - "Enhanced EEG Features"
Cohesion: 0.19
Nodes (13): compute_hjorth_params(), compute_sample_entropy(), compute_zero_crossing_rate(), extract_enhanced_features(), extract_enhanced_features_batch(), get_enhanced_feature_names(), Enhanced time-domain feature extraction from raw EEG windows.  Adds Hjorth param, Compute zero-crossing rate: fraction of samples where sign changes.      Args: (+5 more)

### Community 59 - "Submission Audit"
Cohesion: 0.29
Nodes (13): _ablation_tests(), _basic_integrity(), _corr(), _feature_group_indices(), _fit_ridge(), _load(), main(), parse_args() (+5 more)

### Community 60 - "Reactive vs Predictive Panel"
Cohesion: 0.2
Nodes (14): Actual PAC Signal (Ground Truth) — Sub-15, High-PAC Epoch (can rest), Low-PAC Epoch (need stim), Matched Conditions: same patient, EEG, threshold (z +/- 0.5), 3s hysteresis, Only Difference: current PAC (reactive) vs predicted PAC 5s ahead (TCN), Reactive Controller Decisions Panel, Reactive WRONG Events (misfired stim), Figure 7: Real-Data Controller Timeline (Sub-15, Test Set) (+6 more)

### Community 61 - "Simulator Parameter Fitting"
Cohesion: 0.22
Nodes (12): collapse_to_epochs(), fit_population_tau(), fit_subject_tau(), load_all_splits(), main(), print_results(), Fit simulator tau parameters from real PAC transition data.  Extracts tau_rise a, Fit tau_rise and tau_decay for a single subject at epoch level.      For consecu (+4 more)

### Community 62 - "Sliding Dataset Builder"
Cohesion: 0.23
Nodes (12): build_sliding_dataset(), _causal_moving_average(), main(), _pac_multiscale_features(), Build temporal dataset using sliding-window PAC labels.  Constructs 20-step look, Build temporal dataset with sliding-window PAC targets and features.      Return, Causal trailing average including the current sample., Causal PAC-derived features from past/current values only. (+4 more)

### Community 63 - "Controller Comparison Figure"
Cohesion: 0.23
Nodes (13): Alignment (%) metric, OpenNeuro ds005048 dataset (N=35 subjects), Figure 8: Controller Comparison (grouped bar chart), Finding: TCN-based controllers (Predictive and Hybrid) outperform Fixed Schedule, Reactive, and PI controllers on alignment and low-PAC targeting, approaching Oracle upper bound, Fixed Schedule controller (clinical standard): 45% alignment, 61% low-PAC stim, 29% high-PAC rest, High-PAC Rest Rate (%) metric, Hybrid TCN+Reactive controller: 74% alignment, 85% low-PAC stim, 62% high-PAC rest, Low-PAC Stim Rate (%) metric (+5 more)

### Community 64 - "Per-Subject Utility Scatter"
Cohesion: 0.24
Nodes (13): X-axis: Reactive Clinical Utility (0.35-0.75), Y-axis: TCN Predictive Clinical Utility (0.35-0.75), All 35/35 subjects show TCN Predictive > Reactive clinical utility, Reactive (threshold-triggered) closed-loop strategy, Cross-subject generalization across train/val/test splits, TCN Predictive closed-loop strategy, Per-Subject Alignment Scatter Plot (35/35 favor TCN), Identity line y = x (parity reference) (+5 more)

### Community 65 - "Horizon Sweep Figure"
Cohesion: 0.23
Nodes (13): Causal TCN (ours), Claim: The 5-10s horizon is the operationally useful range for proactive closed-loop control, and only the TCN delivers usable predictions there, Figure: PAC Forecasting Performance vs. Prediction Horizon, Finding: At 5-10s horizons, Persistence and Ridge collapse to negative R-squared (-0.2 to -0.4), Finding: Crossover at ~3s horizon where all three methods converge near R-squared ~0.25, Finding: At short horizons (1-2s), Persistence and Ridge match or beat TCN (R-squared ~0.75-0.81), Finding: Causal TCN maintains R-squared ~0.24-0.28 at 5-10s horizons, giving ~+0.5 R-squared margin over baselines, R-squared (PAC forecasting accuracy) (+5 more)

### Community 66 - "Controller Timeline Figure"
Cohesion: 0.24
Nodes (13): Real-Data Controller Timeline (sub-15, test set), High-PAC Epochs (can rest, yellow shaded), Low-PAC Epochs (need stim, blue shaded), PAC Time Series (x10^-4, ~0-550s), Claim: Reactive stim onset lags behind low-PAC epoch starts, Reactive Controller Decision Lane, Reactive Control Strategy (threshold-based), REST decision (gray bars) (+5 more)

### Community 67 - "Clinical Vision & Roadmap"
Cohesion: 0.22
Nodes (13): 30-60 Min Sessions (Full Habituation Curve), At-Home Wearable Therapy (Daily 30 Min Sessions), Clinical Vision, Figure 10: Future Directions Roadmap, Live Muse EEG Streaming, MCI / Alzheimer's Clinical Trials, Multi-Biomarker Control (PAC + Power + Coherence), Muse 2 Prototype ($249) (+5 more)

### Community 68 - "35/35 Utility Statistics"
Cohesion: 0.24
Nodes (13): Binomial test p < 0.001 (35/35 favor TCN), Claim: all 35/35 subjects benefit from TCN predictive over reactive, y = x (no advantage) diagonal reference line, OpenNeuro ds005048 (data source), Figure 14: Per-Subject Clinical Utility (35/35 Favor TCN), Reactive Clinical Utility (normalized) — x-axis, Reactive closed-loop strategy, TCN Advantage Region (all 35 subjects above y=x) (+5 more)

### Community 69 - "Long-Window Reprocessing"
Cohesion: 0.23
Nodes (11): compute_pac_modulation_index(), compute_temporal_autocorrelation(), extract_spectral_features(), main(), process_subject(), Reprocess OpenNeuro ds005048 with longer PAC windows for temporal prediction., Process one subject with longer PAC windows.      Args:         subject_id: S, Compute PAC autocorrelation at various lags.      With 4-second hop size: (+3 more)

### Community 70 - "PAC Direction Classifier"
Cohesion: 0.3
Nodes (11): eval_classifier(), main(), majority_baseline(), make_direction_labels(), parse_args(), persistence_direction_baseline(), PAC direction classifier: 3-class prediction of future PAC change.  Classes:, Predict direction = 0 (STABLE) always — PAC doesn't change. (+3 more)

### Community 71 - "Pareto Frontier Figure"
Cohesion: 0.26
Nodes (12): Stimulation Efficiency vs Alignment Trade-off Scatter, Fixed Schedule Strategy (~67% stim, ~45% alignment), Hybrid Strategy (~61% stim, ~74% alignment), Ideal Region Annotation (low stim, high align, top-left), Oracle Strategy (~48% stim, ~100% alignment), Pareto Frontier (PI to Oracle dashed line), PI Strategy (~22% stim, ~66% alignment), Reactive Strategy (~37% stim, ~65% alignment) (+4 more)

### Community 72 - "End-to-End Pipeline Diagram"
Cohesion: 0.36
Nodes (12): 40 Hz Audio Stim. (STIMULATE / REST / MAINTAIN), Causal TCN (31K params, 20 s lookback), Closed-Loop Controller (z-score +/-0.5, 5 s hysteresis), Decision / Control (category), EEGNet (1,457 params, MSE trained), Entrainment feedback (40 Hz gamma-theta coupling), Feature Extraction (73 features, 61+7+5), Closed-Loop 40 Hz Entrainment System Architecture (Figure) (+4 more)

### Community 73 - "Adaptive vs Fixed Schedule"
Cohesion: 0.21
Nodes (12): Adaptive Schedule (This Project), Fixed 40s ON / 20s OFF pattern, Fixed Schedule (Current Practice), 3-second hysteresis (minimum hold time), Figure 3: Fixed vs. Adaptive Stimulation Scheduling, Missed rests during low PAC, Fixed schedule has no adaptation; treats every moment the same, Phase-Amplitude Coupling (PAC) signal axis (+4 more)

### Community 74 - "Notebook Finalization Check"
Cohesion: 0.33
Nodes (9): check_chronology(), check_packaging(), check_preservation(), main(), parse_args(), read_text(), report(), run_selected_checks() (+1 more)

### Community 75 - "PAC Gap Effect Size Figure"
Cohesion: 0.27
Nodes (11): TCN vs Reactive PAC Gap Contrast: Hedges g=1.57 (*** highly significant), Fixed Schedule Controller (PAC gap ~ -6 x10^-6, negative), Hybrid Controller (PAC gap ~ 34 x10^-6), Oracle Controller (PAC gap ~ 33.5 x10^-6, upper bound), PI Controller (PAC gap ~ 27 x10^-6), Reactive Controller (PAC gap ~ 21 x10^-6), TCN Predictive Controller (PAC gap ~ 30.5 x10^-6), PAC Targeting Gap by Controller (Bar Chart) (+3 more)

### Community 76 - "Controller Performance Figure"
Cohesion: 0.27
Nodes (11): Alignment (%) Metric, Figure 13: Controller Performance Comparison (N=35), Finding: TCN Predictive achieves 72.1% alignment vs Reactive's 64.5%, approaching Oracle's 100%, Fixed Schedule Controller, High-PAC Rest Rate (%) Metric, Low-PAC Stim Rate (%) Metric, N=35 Subjects (OpenNeuro ds005048), Oracle Controller (+3 more)

### Community 77 - "Timeline Comparison Figure"
Cohesion: 0.29
Nodes (11): 240-second Comparison Timeline, Adaptive Schedule Alignment: 72%, Claim: Adaptive scheduling yields 72% alignment vs 45% fixed, Fixed Schedule Alignment: 45%, Figure 1: Fixed vs. Adaptive Stimulation Scheduling, Missed Opportunity (no stim during low PAC), PAC (Theta-Gamma) Time Series Waveform, Panel A: Fixed Schedule (Current Approach) (+3 more)

### Community 78 - "Horizon Sweep Runner"
Cohesion: 0.36
Nodes (9): main(), parse_args(), persistence_baseline(), _r2(), Horizon sweep: evaluate persistence, Ridge and TCN baselines at multiple predict, Persistence baseline: predict future PAC = current PAC (last_pac)., Ridge regression on flattened feature sequences., ridge_baseline() (+1 more)

### Community 79 - "Dataset Overview Figure"
Cohesion: 0.27
Nodes (10): 40 Hz Amplitude-Modulated Stimulus, 2-second Analysis Window (7 channels x 500 samples), Figure 8: Dataset Overview (EEG Channels, Protocol, Splits), No Within-Subject Data Leakage (subject-level splits), OpenNeuro ds005048 Dataset (35 Subjects), Panel A: 7 Frontal EEG Channels (Fp1, Fp2, F7, F3, Fz, F4, F8), Panel B: Stimulus / Rest Protocol (40 Hz AM, 20-40s blocks), Panel C: Subject-Level Train/Val/Test Split (n=24/5/6) (+2 more)

### Community 80 - "Metric Definitions Figure"
Cohesion: 0.31
Nodes (10): Alignment = (Low-PAC Stim Rate + High-PAC Rest Rate) / 2, High-PAC Rest Rate Metric, Low-PAC Stim Rate Metric, Figure 12: Metric Definitions Diagram, PAC Time Series (illustrative), Rest Windows (during high-PAC conditions), Sensitivity (correctly stimulating low-PAC states), Specificity (correctly resting during high-PAC states) (+2 more)

### Community 81 - "PAC Mechanism Figure"
Cohesion: 0.27
Nodes (10): Rationale: High PAC indicates 40Hz therapy is working, Gamma Oscillations (38-42 Hz), High PAC State (4-8 Hz theta), Hippocampal Attribution (origin of PAC coupling), Low PAC State (poor entrainment), Figure 2: Phase-Amplitude Coupling (PAC) Mechanism, Theta Phase Modulates Gamma Amplitude, Theta Rhythm (4-8 Hz) (+2 more)

### Community 82 - "Feature Ablation Figure"
Cohesion: 0.36
Nodes (10): Claim: Removing 61 spectral features yields 5x R2 improvement, All 73 Features Condition (R2 = -0.025), Figure 4: Feature Ablation Study (73 to 12 features), PAC Feature Group (7 features), PAC + Stim 12 Features (R2 = 0.606), Finding: Spectral features overfit to individual patient anatomy, R2 Performance Colorbar (-0.420 to +0.606), Spectral Feature Group (61 features) (+2 more)

### Community 83 - "Sklearn Temporal Baseline"
Cohesion: 0.31
Nodes (8): create_dataset(), create_temporal_features(), main(), Lightweight sklearn-based temporal PAC predictor for 8-second windows.  This v, Train Ridge and MLP models, evaluate on test set., Create flat feature vector from temporal sequence.      Args:         windows, Create temporal dataset for sklearn.      Returns:         X_train, y_train,, train_and_evaluate()

### Community 84 - "PAC Method Comparison"
Cohesion: 0.31
Nodes (8): analyze_subject(), compute_within_epoch_variance(), lag1_autocorrelation(), main(), Diagnostic: compare epoch-level PAC vs per-window PAC.  For each subject, comput, Compute lag-1 autocorrelation of a 1D signal., Compute mean within-epoch variance of per-window PAC.      Windows sharing the s, Compute diagnostics for one subject.

### Community 85 - "Multiscale TCN Trainer"
Cohesion: 0.42
Nodes (8): _corr(), _denorm(), evaluate(), main(), _metrics(), parse_args(), _r2(), train_one_epoch()

### Community 86 - "Threshold Sensitivity Analysis"
Cohesion: 0.42
Nodes (9): Closed-loop controller delta-z decision threshold (config.yaml / controller.py), Delta-z threshold sweep (0.1 to 1.0), TCN Robustness: Threshold Sensitivity Analysis (Figure), Low-threshold regime (delta-z 0.1 to 0.2): TCN underperforms reactive baseline, Finding: TCN alignment plateaus at ~74% for delta-z >= 0.3, robustly above reactive baseline, Reactive baseline reference (64.5% alignment), Stimulation Rate (%) vs Delta-z Threshold, TCN Advantage Zone (delta-z >= 0.2) (+1 more)

### Community 87 - "Enhanced Dataset Builder"
Cohesion: 0.36
Nodes (7): build_enhanced_dataset(), _build_split_samples_enhanced(), main(), parse_args(), Build enhanced multiscale temporal datasets for PAC forecasting.  Extends the ba, Build an enhanced multiscale temporal dataset.      Loads existing spectral cach, Build sequence samples with enhanced features concatenated after spectral.

### Community 88 - "Checkpoint Deployment Audit"
Cohesion: 0.46
Nodes (7): _corr(), _eval(), main(), parse_args(), print_summary(), _r2(), run_audit()

### Community 89 - "Feature Ablation Runner"
Cohesion: 0.46
Nodes (7): corr_score(), denorm(), evaluate(), main(), r2_score(), train_one_epoch(), train_subset()

### Community 90 - "Real-Data Fatigue Analysis"
Cohesion: 0.38
Nodes (6): analyze_fatigue(), load_subject_pac_and_events(), main(), Habituation/fatigue analysis: does PAC decline across repeated stimulation block, Analyze habituation patterns across subjects., Load PAC values and align with BIDS events for each subject.

### Community 91 - "Multiscale Pipeline Audit"
Cohesion: 0.48
Nodes (6): _finite_check(), _load_npz(), main(), parse_args(), Audit script for multiscale temporal dataset and training artifacts.  Checks: 1), run_audit()

### Community 92 - "Paper Figure Generator"
Cohesion: 0.33
Nodes (5): generate_horizon_sweep(), generate_system_block_diagram(), Generate publication-quality figures for the research paper.  Figures produced, Horizontal left-to-right block diagram showing the full closed-loop     EEG-to-, Line graph showing R² vs. prediction horizon for three models:     - Persistenc

### Community 93 - "AI Image Generator"
Cohesion: 0.47
Nodes (5): generate_image(), load_api_key(), main(), Load OpenRouter API key from ~/.claude/apis.env, Generate an image from a text prompt and save to output_path.

### Community 94 - "Paper Figure Regeneration"
Cohesion: 0.6
Nodes (5): fig_controller_comparison(), fig_horizon_sweep(), fig_per_subject(), fig_timeline(), save()

### Community 95 - "R² Ceiling Analysis"
Cohesion: 0.33
Nodes (6): EEGNetLarge 141K params hits same R2=0.287 ceiling, SNR Ceiling Rationale (-4.73 dB), Honest Baseline R2=0.287 (Ridge), Shannon Information Theory Ceiling, Master Model Infeasibility Verdict, EEG Prediction R2 Study Comparison

### Community 96 - "V4 ViT-TCNet Plan"
Cohesion: 0.33
Nodes (6): 10+ Samples Per Parameter Rule, ViT-TCNet Architecture Plan, ImageNet-to-EEG Transfer Domain Mismatch, V4 Severe Overparameterization (1.1M params), V4 Test R2=0.252 Result, V4 ViT-TCNet Hybrid Design

### Community 97 - "Errata & Late Corrections"
Cohesion: 0.33
Nodes (6): Fatigue Model Robustness (4 models), Erratum 1: Controller Results Table, Erratum 2: TCN Validation Date Correction, Erratum 3: PAC Gap Units (dimensionless x10^-6), TCN Real-Data Validation Locked (Feb 26), Final Controller Table (TCN 72.1% vs Reactive 64.5%)

### Community 98 - "Consumer Hardware Figure"
Cohesion: 0.53
Nodes (6): Alzheimer's Disease Application, 40 Hz Auditory Stimulation Modality, Clinical Deployment on Consumer Hardware, Closed-Loop Personalized Auditory Therapy for Alzheimer's, Figure 11: Consumer Hardware for Clinical Deployment, Muse 2 Consumer EEG Headband

### Community 99 - "NumPy Diagnostic"
Cohesion: 0.4
Nodes (3): kl_divergence_approx(), Pure NumPy Diagnostic - No dependencies except NumPy  Analyzes why V4 ViT-TCNet, Approximate KL divergence using histograms

### Community 100 - "Config Sweep Utility"
Cohesion: 0.6
Nodes (4): main(), parse_args(), Small sweep utility for lookback/horizon settings.  Example:     python temporal, run_cmd()

### Community 101 - "12-Feature Dataset"
Cohesion: 0.5
Nodes (3): build_original_12feat(), Extract 12 PAC+Stim features from the existing 73-feature multiscale dataset to, Extract 12 PAC+Stim features and re-normalize from scratch.      This ensures th

### Community 102 - "AI Figure Generator"
Cohesion: 0.67
Nodes (3): generate_image(), main(), Generate an image using a chat-based image model on OpenRouter.

### Community 103 - "JS Build Helper"
Cohesion: 0.83
Nodes (3): cell(), hdr(), main()

### Community 104 - "Project README Structure"
Cohesion: 0.5
Nodes (4): Data Flow Architecture, Full Pipeline Command Sequence, Quick Start Commands, Repository Structure

### Community 105 - "Synopsys Judging Rubric"
Cohesion: 0.5
Nodes (4): Claire Xu 2025 Alzheimer's Graph RL (comparable), Danielle Steinbach 2025 EEG Foundation Model (comparable), Synopsys 4-Dimension Judging Rubric (40 pts), Synopsys Winning Analysis

### Community 106 - "Early Research Spec"
Cohesion: 0.5
Nodes (4): Cognito Therapeutics Phase II Trial, PING Pyramidal-Interneuron Network Gamma, Research Notebook Enhancement Spec, V1 Research Paper Format Notebook

### Community 107 - "Flyer PDF Generator"
Cohesion: 1.0
Nodes (2): build_pdf(), main()

### Community 108 - "QR Code Generator"
Cohesion: 1.0
Nodes (2): main(), make_qr()

### Community 109 - "Controller Comparison Chart"
Cohesion: 0.67
Nodes (1): Generate Figure 8: Controller Comparison bar chart from real data.

### Community 110 - "Habituation Literature"
Cohesion: 0.67
Nodes (3): Rankin et al. 2009 (habituation revisited), Thompson & Spencer 1966 (habituation), Habituation/Fatigue Analysis (real data)

### Community 111 - "Original R² Hypothesis"
Cohesion: 0.67
Nodes (3): Brain Intensify 2024 (ref 24), Future vs Current PAC Prediction Tasks, Original Hypothesis: R2>0.80 PAC prediction

### Community 112 - "Abstract Draft Iterations"
Cohesion: 0.67
Nodes (3): Round1 Draft2 Engineering Focus, Round1 Draft5 Concise High-Impact, Round2 Draft B: Technical Precision (Draft 2 + 5 merge)

### Community 113 - "Venue Submission Plan"
Cohesion: 0.67
Nodes (3): AIClub Email Draft, Paper: 5,500 words / 7 figs / 5 tables / 23 refs / 8 limitations, IEEE COMPSAC 2026 Target Venue

### Community 114 - "Flyer Asset"
Cohesion: 1.0
Nodes (3): Research Flyer Distribution Asset, Feedback QR Code (Flyer), Audience Feedback Collection Mechanism

### Community 115 - "Leakage Debug Script"
Cohesion: 1.0
Nodes (1): Debug Data Leakage  Identify which features are causing R² = 0.9999 perfect pred

### Community 116 - "Architecture Figure Script"
Cohesion: 1.0
Nodes (1): Generate system architecture figure v7 with correct specs using matplotlib.

### Community 117 - "Closed-Loop vs Fixed Chart"
Cohesion: 1.0
Nodes (0): 

### Community 118 - "Dependency Specs"
Cohesion: 1.0
Nodes (2): Deployment Requirements (streamlit CPU), Full Dev Requirements (PyTorch/MNE/tensorpac)

### Community 119 - "Per-Subject Scatter Note"
Cohesion: 1.0
Nodes (2): Figure: Per-Subject Utility Scatter (35/35 favor TCN), Result 2: 35/35 subjects benefit with TCN

### Community 120 - "Judging Prep Notes"
Cohesion: 1.0
Nodes (2): Competitive Edge vs 2025 Synopsys Projects, Judge Interview Preparation Guide

### Community 121 - "R² Target Strategies"
Cohesion: 1.0
Nodes (2): Option A: Maximize Honest Performance, Target R2=0.46-0.55 Gap

### Community 122 - "Ridge Feature Lesson"
Cohesion: 1.0
Nodes (2): Lesson: Start Simple, Features > Architecture, Ridge Regression (135 features, alpha=1526)

### Community 123 - "Wavelet Features Plan"
Cohesion: 1.0
Nodes (2): Wavelet Features (CWT + WPD) Plan, Wavelet Features (74 features: CWT+WPD)

### Community 124 - "Sprint Milestones (Archive)"
Cohesion: 1.0
Nodes (2): 48-Hour Pipeline Sprint (Feb 5-6), Fortran Order .fdt Load Discovery

### Community 125 - "Flyer QR Asset"
Cohesion: 1.0
Nodes (2): Flyer Asset (QR for app), QR Code linking to App/Demo

### Community 126 - "Causal Trailing Mean"
Cohesion: 1.0
Nodes (1): Apply causal trailing mean within each subject block.          Causal (trailing)

### Community 127 - "System Arch v5 Script"
Cohesion: 1.0
Nodes (0): 

### Community 128 - "System Arch v4 Script"
Cohesion: 1.0
Nodes (0): 

### Community 129 - "Notebook Scaffolder"
Cohesion: 1.0
Nodes (0): 

### Community 130 - "Feature Count Constant"
Cohesion: 1.0
Nodes (1): Total number of output features: 8 * n_channels + 5.

### Community 131 - "CLAUDE.md Instructions"
Cohesion: 1.0
Nodes (1): CLAUDE.md Project Instructions

### Community 132 - "Validation Matrix"
Cohesion: 1.0
Nodes (1): Validation Matrix

### Community 133 - "Fatigue Result Claim"
Cohesion: 1.0
Nodes (1): Result 3: Adaptive advantage grows with fatigue severity

### Community 134 - "Robustness Result Claim"
Cohesion: 1.0
Nodes (1): Result 4: Robust across 4 fatigue model assumptions

### Community 135 - "Meta-Learning Plan"
Cohesion: 1.0
Nodes (1): Meta-Learning Transfer Phase 3A

### Community 136 - "Multi-Task Learning Plan"
Cohesion: 1.0
Nodes (1): Multi-Task Learning (MTEEG) Phase 3B

### Community 137 - "V4 Distribution Shift"
Cohesion: 1.0
Nodes (1): V4 Distribution Shift (KL Divergence)

### Community 138 - "Classification Reframe Idea"
Cohesion: 1.0
Nodes (1): Reframe: binary/ordinal classification vs continuous regression

### Community 139 - "Latency Budget Note"
Cohesion: 1.0
Nodes (1): Latency budget: <5ms EEGNet+TCN+control

### Community 140 - "Alzheimer Sim PDF"
Cohesion: 1.0
Nodes (1): TRIBE V2 Alzheimer Simulation PDF

## Knowledge Gaps
- **1167 isolated node(s):** `Fit simulator tau parameters from real PAC transition data.  Extracts tau_rise a`, `Load and concatenate train/val/test multiscale splits.      Returns dict with ke`, `Collapse window-level data to epoch-level.      PAC is computed at the epoch lev`, `Fit tau_rise and tau_decay for a single subject at epoch level.      For consecu`, `Fit tau parameters across all subjects.      Groups sequences by subject, recons` (+1162 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Leakage Debug Script`** (2 nodes): `debug_leakage.py`, `Debug Data Leakage  Identify which features are causing R² = 0.9999 perfect pred`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Architecture Figure Script`** (2 nodes): `gen_arch_figure.py`, `Generate system architecture figure v7 with correct specs using matplotlib.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Closed-Loop vs Fixed Chart`** (2 nodes): `generate_closedloop_vs_fixed_v3.py`, `draw_stim_bar()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Dependency Specs`** (2 nodes): `Deployment Requirements (streamlit CPU)`, `Full Dev Requirements (PyTorch/MNE/tensorpac)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Per-Subject Scatter Note`** (2 nodes): `Figure: Per-Subject Utility Scatter (35/35 favor TCN)`, `Result 2: 35/35 subjects benefit with TCN`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Judging Prep Notes`** (2 nodes): `Competitive Edge vs 2025 Synopsys Projects`, `Judge Interview Preparation Guide`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `R² Target Strategies`** (2 nodes): `Option A: Maximize Honest Performance`, `Target R2=0.46-0.55 Gap`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Ridge Feature Lesson`** (2 nodes): `Lesson: Start Simple, Features > Architecture`, `Ridge Regression (135 features, alpha=1526)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Wavelet Features Plan`** (2 nodes): `Wavelet Features (CWT + WPD) Plan`, `Wavelet Features (74 features: CWT+WPD)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Sprint Milestones (Archive)`** (2 nodes): `48-Hour Pipeline Sprint (Feb 5-6)`, `Fortran Order .fdt Load Discovery`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Flyer QR Asset`** (2 nodes): `Flyer Asset (QR for app)`, `QR Code linking to App/Demo`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Causal Trailing Mean`** (1 nodes): `Apply causal trailing mean within each subject block.          Causal (trailing)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `System Arch v5 Script`** (1 nodes): `generate_system_architecture_v5.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `System Arch v4 Script`** (1 nodes): `generate_system_architecture_v4.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Notebook Scaffolder`** (1 nodes): `create_research_notebook.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Feature Count Constant`** (1 nodes): `Total number of output features: 8 * n_channels + 5.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `CLAUDE.md Instructions`** (1 nodes): `CLAUDE.md Project Instructions`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Validation Matrix`** (1 nodes): `Validation Matrix`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Fatigue Result Claim`** (1 nodes): `Result 3: Adaptive advantage grows with fatigue severity`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Robustness Result Claim`** (1 nodes): `Result 4: Robust across 4 fatigue model assumptions`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Meta-Learning Plan`** (1 nodes): `Meta-Learning Transfer Phase 3A`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Multi-Task Learning Plan`** (1 nodes): `Multi-Task Learning (MTEEG) Phase 3B`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `V4 Distribution Shift`** (1 nodes): `V4 Distribution Shift (KL Divergence)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Classification Reframe Idea`** (1 nodes): `Reframe: binary/ordinal classification vs continuous regression`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Latency Budget Note`** (1 nodes): `Latency budget: <5ms EEGNet+TCN+control`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Alzheimer Sim PDF`** (1 nodes): `TRIBE V2 Alzheimer Simulation PDF`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RealtimePACForecaster` connect `Closed-Loop Controller` to `Multiscale TCN Training`, `Live EEG Streaming & UI`?**
  _High betweenness centrality (0.080) - this node is a cross-community bridge._
- **Why does `MultiscaleCausalTCN` connect `Multiscale TCN Training` to `Closed-Loop Controller`, `Cross-Epoch Transition Analysis`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._
- **Why does `ModelConfig` connect `Multiscale TCN Training` to `Closed-Loop Controller`, `Cross-Epoch Transition Analysis`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Are the 195 inferred relationships involving `StimAction` (e.g. with `FixedScheduleCtrl` and `ReactiveCtrl`) actually correct?**
  _`StimAction` has 195 INFERRED edges - model-reasoned connections that need verification._
- **Are the 133 inferred relationships involving `EntrainmentSimulator` (e.g. with `FixedScheduleControl` and `ReactiveThresholdControl`) actually correct?**
  _`EntrainmentSimulator` has 133 INFERRED edges - model-reasoned connections that need verification._
- **Are the 136 inferred relationships involving `FatigueAwareSimulator` (e.g. with `FixedScheduleControl` and `ReactiveThresholdControl`) actually correct?**
  _`FatigueAwareSimulator` has 136 INFERRED edges - model-reasoned connections that need verification._
- **Are the 125 inferred relationships involving `MultiscaleCausalTCN` (e.g. with `SeqDataset` and `Train and compare TCN models on epoch-level vs sliding-window PAC targets.  Trai`) actually correct?**
  _`MultiscaleCausalTCN` has 125 INFERRED edges - model-reasoned connections that need verification._