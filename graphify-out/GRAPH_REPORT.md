# Graph Report - .  (2026-05-31)

## Corpus Check
- 519 files · ~1,812,656 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 4465 nodes · 7906 edges · 205 communities detected
- Extraction: 72% EXTRACTED · 28% INFERRED · 0% AMBIGUOUS · INFERRED: 2247 edges (avg confidence: 0.56)
- Token cost: 0 input · 0 output

## God Nodes (most connected - your core abstractions)
1. `StimAction` - 197 edges
2. `EntrainmentSimulator` - 142 edges
3. `FatigueAwareSimulator` - 142 edges
4. `MultiscaleCausalTCN` - 141 edges
5. `ModelConfig` - 136 edges
6. `RealtimePACForecaster` - 118 edges
7. `EEGNet` - 97 edges
8. `SpectralFeatureExtractor` - 59 edges
9. `ClosedLoopController` - 50 edges
10. `StreamingFeatureExtractor` - 47 edges

## Surprising Connections (you probably didn't know these)
- `Generate CSEF Presentation PPTX Script` --semantically_similar_to--> `submission/presentation/CSEF_2026_Presentation.pdf`  [INFERRED] [semantically similar]
  scripts/tools/generate_csef_pptx.py → submission/presentation/CSEF_2026_Presentation.pdf
- `CSEF Poster V3 (Final Print-Ready Poster)` --semantically_similar_to--> `Poster Board V5 (Condensed, Visual-Forward, Synopsys 2026)`  [INFERRED] [semantically similar]
  archive/CSEF_Old/Poster_FINAL/CSEF_poster_v3.pdf → submission/poster/POSTER_BOARD_V5.md
- `QR Code for Feedback (Flyer)` --semantically_similar_to--> `Figure 8: Controller Comparison Bar Chart`  [AMBIGUOUS] [semantically similar]
  archive/CSEF_Old/Flyer/qr_feedback.png → submission/paper/figures/controller_comparison_v2.png
- `PAC Response by Disease Severity (Panel A)` --semantically_similar_to--> `PAC Response vs Disease Severity - Predictive Controller Sweep`  [INFERRED] [semantically similar]
  results/tribe_v2/alzheimer_simulation.pdf → results/tribe_v2/tribe_v2_alzheimer_sweep.png
- `Reference Poster Layout Style (3-Panel, Figure-Dense, Synopsys Format)` --semantically_similar_to--> `Poster Board V5 (Condensed, Visual-Forward, Synopsys 2026)`  [INFERRED] [semantically similar]
  submission/poster/reference/Poster Example 2.pdf → submission/poster/POSTER_BOARD_V5.md

## Hyperedges (group relationships)
- **Two-Stage PAC Prediction Pipeline (EEGNet → TCN → Controller)** — README_eegnet_stage1, README_multiscale_tcn_stage2, README_closed_loop_validation [EXTRACTED 1.00]
- **Feature Ablation as Core Scientific Finding (Spectral vs PAC+Stim)** — README_feature_ablation, CLAUDE_spectral_feature_gotcha, CLAUDE_12feat_description [EXTRACTED 1.00]
- **Closed-Loop Validation Evidence Chain (Simulation → Fatigue Sweep → Real-Data)** — FINDINGS_simulation_comparison, FINDINGS_fatigue_model_sensitivity, FINDINGS_real_data_validation [INFERRED 0.85]
- **Muse 2 Consumer EEG Adaptation Pipeline (channel mapping + data processing + model retraining)** — retrain_pipeline_muse4ch_pipeline, channel_mapping_muse2_proxy, retrain_pipeline_muse_proxy_channels [EXTRACTED 0.92]
- **Notebook Version Evolution (V1 → V2 → V3-early → final corrected versions)** — P10_Lab_Notebook_V1_notebook_v1, P10_Lab_Notebook_V2_notebook_v2, P10_Lab_Notebook_V3_early_notebook_v3_early, LAB_NOTEBOOK_ERRATA_errata [INFERRED 0.88]
- **Static Ceiling → Temporal Pivot Pipeline (ceiling + leakage discovery → temporal reformulation)** — LOG_NOTEBOOK_static_pac_ceiling, LOG_NOTEBOOK_feature_leakage_discovery, LOG_NOTEBOOK_temporal_prediction_pivot, LOG_NOTEBOOK_horizon_sweep_experiment [EXTRACTED 0.95]
- **TCN Design Decisions (causal padding + GroupNorm + attention pooling)** — v1_research_paper_format_causal_padding_rationale, v1_research_paper_format_groupnorm_rationale, v1_research_paper_format_multiscale_tcn_design [EXTRACTED 0.92]
- **Legacy LSTM Temporal Prediction Pipeline (Dataset → Model → Training)** — temporal_dataset_TemporalPACDataset, temporal_model_TemporalPACPredictor, train_temporal_train_temporal_predictor [EXTRACTED 0.95]
- **8-Second Long-Window Temporal Experiment (Reprocess → Dataset → Train LSTM + sklearn)** — reprocess_long_process_subject, train_temporal_long_LongWindowTemporalDataset, train_sklearn_train_and_evaluate [INFERRED 0.85]
- **Source of Truth: FINDINGS + RESULTS_REPORT + Current Methodology** — INDEX_findings, INDEX_results_report, INDEX_current_methodology [EXTRACTED 0.95]
- **Abstract Iterative Refinement: Round 1 Drafts → Round 2 Combinations → Round 3 Final** — draft1_clinical_hook_abstract, draft3_problem_solution_abstract, draft4_judges_perspective_abstract, draft_A_best_narrative_abstract, draft_B_technical_precise_abstract, draft_C_impact_driven_abstract, final_abstract_round3 [EXTRACTED 0.95]
- **Synopsys Championship P10 Abstract — Submission Artifacts (MD + PDFs)** — final_abstract_round3, p10_abstract_pdf_v1, p10_abstract_pdf_v2 [INFERRED 0.90]
- **Core Quantitative Claims Repeated Across All Abstract Drafts** — abstract_core_claim_tcn_horizon, abstract_core_claim_predictive_vs_reactive, abstract_core_claim_pac_targeting [EXTRACTED 0.98]
- **PAC Temporal Prediction Failure: 2s Windows → Near-Zero Autocorr → Failed R² → Reactive Fallback** — TEMPORAL_PREDICTION_REPORT_zero_autocorrelation_finding, TEMPORAL_PREDICTION_REPORT_data_limitation, TEMPORAL_FINAL_REPORT_recommendation_reactive [EXTRACTED 0.95]
- **Architecture Simplification: Proposed GAT-Transformer → EEGNet (Dataset Size Rationale)** — 04_Research_Methodology_proposed_gat_transformer, STATUS_REPORT_v2_eegnet_rationale, AD_IEEE_paper_eegnet_architecture [INFERRED 0.88]
- **V1-V8 Lessons (Leakage, SNR, Overfitting) Converge on Ridge R²=0.287 Ceiling** — COMPREHENSIVE_ANALYSIS_v1_data_leakage, COMPREHENSIVE_ANALYSIS_snr_limit, COMPREHENSIVE_ANALYSIS_v5_ridge_best [EXTRACTED 0.92]
- **Leakage Audit Triad: Subject Split, Temporal Causality, Normalization** — COMPREHENSIVE_SUBMISSION_AUDIT_REPORT_subject_split_leakage_check, COMPREHENSIVE_SUBMISSION_AUDIT_REPORT_temporal_causality_leakage_check, COMPREHENSIVE_SUBMISSION_AUDIT_REPORT_normalization_leakage_check [EXTRACTED 0.95]
- **Target Smoothing + PAC Oracle Inflate R² Pattern** — COMPREHENSIVE_SUBMISSION_AUDIT_REPORT_target_smoothing_effect, PIPELINE_AUDIT_REPORT_pac_autocorrelation_inflates_r2, PIPELINE_AUDIT_REPORT_pac_zeroed_ablation [INFERRED 0.85]
- **Deployment Realism Failure Cluster: PAC Oracle + Noisy Estimates + Collapse** — COMPREHENSIVE_SUBMISSION_AUDIT_REPORT_pac_oracle_dependency, PIPELINE_AUDIT_REPORT_deployment_realism_failure, TEMPORAL_MULTISCALE_AUDIT_REPORT_realtime_inference_audit [INFERRED 0.78]
- **Closed-Loop Control Pipeline: Controller + Personalization + Simulation** — CURRENT_METHODOLOGY_controller, CURRENT_METHODOLOGY_personalization, CURRENT_METHODOLOGY_simulation [EXTRACTED 1.00]
- **TCN Temporal Prediction: 73-Feature Input + MultiscaleCausalTCN + 5-10s Horizon Value** — CODE_MAP_multiscale_features_73, CODE_MAP_multiscale_tcn_model, CURRENT_METHODOLOGY_tcn_horizon_value [EXTRACTED 0.95]
- **Static PAC Ceiling: EEGNet + Ridge + R²=0.287 Convergence** — CODE_MAP_eegnet_model, CODE_MAP_ridge_baseline, CODE_MAP_r2_ceiling_0287 [EXTRACTED 1.00]
- **Closed-Loop 40Hz Entrainment System: EEGNet + Personalization + MPC Controller** — comprehensive_methodology_eegnet_impl, comprehensive_methodology_personalization_impl, comprehensive_methodology_controller_impl [EXTRACTED 1.00]
- **Proposed Spatiotemporal DL Architecture: GAT + Transformer + MPC** — research_methodology_gat_architecture, research_methodology_transformer_module, research_methodology_mpc_formulation [EXTRACTED 0.95]
- **Scientific Rationale: PAC Disruption + Open-Loop Failure + Personalization Need** — foundational_concepts_pac_mechanism, literature_review_research_gaps, AD_40Hz_ieee_inter_individual_variability [INFERRED 0.85]
- **Closed-Loop Pipeline: EEG Acquisition -> PAC Estimation -> TCN Prediction -> Stimulation Decision** — neurocare_live_RealEEGAdapter, neurocare_live_PACComputer, neurocare_live_ImprovedTCN, neurocare_live_closed_loop_decision [EXTRACTED 0.95]
- **Caregiver Session Pipeline: SimulatedEEG -> FeatureExtractor -> EEGNet -> TCN -> Decision** — caregiver_app_SimulatedEEGAdapter, caregiver_app_StreamingFeatureExtractor, caregiver_app_EEGNet, caregiver_app_TCNTemporalModel [EXTRACTED 0.95]
- **Demo Controller Comparison: Fixed vs Reactive vs Predictive vs Oracle vs TCN** — demo_FixedScheduleControl, demo_ReactiveThresholdControl, demo_TCNController, demo_OracleControl [EXTRACTED 0.95]
- **Horizon Sweep Full Pipeline: Build Dataset → Train TCN → Report Results per horizon** — training_output_build_multiscale_dataset, training_output_train_multiscale_tcn, training_output_horizon_sweep_table [EXTRACTED 0.95]
- **TCN vs Baselines at Long Horizons: TCN maintains R2>0.24 where Persistence and Ridge both go negative** — training_output_tcn_hz5_result, training_output_tcn_hz8_result, training_output_tcn_hz10_result [EXTRACTED 0.95]
- **Closed-Loop Strategy Quartet: Fixed / Reactive / Predictive / Oracle compared in simulation** — training_output_fixed_schedule_strategy, training_output_reactive_threshold_strategy, training_output_predictive_lookahead_strategy, training_output_oracle_strategy [EXTRACTED 1.00]
- **12-Feature TCN Replay Targeting-Alignment Tradeoff** — PAPER_STATUS_causal_tcn, PAPER_STATUS_replay_targeting, PAPER_STATUS_replay_alignment [INFERRED 0.85]
- **Tier 1 Conference Target Set for Closed-Loop BCI Paper** — targets_ieee_embc_target, targets_neurips_workshop, targets_iclr_workshop [EXTRACTED 0.95]
- **TCN Predictive Controller Validated on Real EEG Producing Key Clinical Metrics** — 00_abstract_causal_tcn, 00_abstract_openneuro_ds005048, 00_abstract_epoch_alignment_result, 00_abstract_low_pac_targeting, 00_abstract_oracle_bound [EXTRACTED 0.95]
- **Existing Publication Figures Generated by Scripts** — figures_source_readme_horizon_sweep_figure, figures_source_readme_controller_comparison_figure, figures_source_readme_pac_targeting_gap_figure, figures_source_readme_per_subject_utility_figure, figures_source_readme_threshold_sensitivity_figure, figures_source_readme_timeline_example_figure [EXTRACTED 1.00]
- **Paper Narrative Structure: Clinical Framing + Feature Discovery + Clinical Validation** — BRAINSTORM_recommended_framing, narrative_one_paragraph_story, narrative_introduction_arc [INFERRED 0.85]
- **Acknowledged Limitations Cluster for Reviewer Response** — BRAINSTORM_offline_replay_limitation, BRAINSTORM_dataset_size_limitation, BRAINSTORM_simulator_not_validated [EXTRACTED 0.90]
- **Controller Evaluation Framework: Alignment, PAC Gap, Per-Subject Consistency** — results_report_controller_comparison, results_report_epoch_alignment_metric, results_report_pac_gap_metric, results_report_per_subject_consistency [INFERRED 0.90]
- **4ch vs 7ch Channel Comparison Analysis: Hardware, EEGNet, TCN** — 4ch_vs_7ch_hardware_config, 4ch_vs_7ch_eegnet_comparison, 4ch_vs_7ch_tcn_comparison [EXTRACTED 0.95]
- **Three-Phase Rigor Audit (Compliance + Content + Model Rigor)** — STATUS_csef_compliance_phase, STATUS_content_accuracy_phase, STATUS_model_rigor_phase [EXTRACTED 1.00]
- **7-Check Data Leakage Audit Framework** — 07_leakage_audit_subject_split_disjoint, 07_leakage_audit_temporal_causality_check, 07_leakage_audit_permutation_test [EXTRACTED 0.90]
- **Feature Selection as Primary Driver (validated by ablation, architecture comparison, and hyperparam sensitivity)** — 09_feature_validation_ablation_validation, 10_architecture_exploration_tier1_equivalence, 11_hyperparam_sensitivity_feature_vs_hyperparam_gap [INFERRED 0.88]
- **Three-Strategy (Fixed/Reactive/Predictive) Comparison Across Five Disease Severity Stages** — alzheimer_simulation_fixed_strategy, alzheimer_simulation_reactive_strategy, alzheimer_simulation_predictive_strategy, alzheimer_simulation_disease_severity_gradient [EXTRACTED 0.95]
- **Pre-Training Leakage Audit Gate: Sequence Validity + Subject Disjointness + Code Integrity** — validate_leakage_test_temporal_sequence_logic, validate_leakage_test_no_subject_leakage, validate_leakage_audit_code [EXTRACTED 0.95]
- **CSEF/Synopsys 2026 Submission Package** — ABSTRACT_csef_old_abstract, research_paper_v3, lab_notebook_vfinal, isef_form_1a [EXTRACTED 0.95]
- **Controller Evaluation: Offline Replay + Effect Sizes + Multiple Metrics** — research_paper_v3_offline_replay, supplementary_effect_sizes, research_paper_v3_controller_variants [INFERRED 0.88]
- **Judge Presentation Preparation Suite** — short_version_presentation, synopsys_winning_analysis, qa_bank_danger_zones [EXTRACTED 0.92]
- **TRIBE Simulator Alignment Evaluation Harness (All 4 Pipeline Scripts Share Alignment Metric Logic)** — run_tribe_tcn_validation_evaluate_alignment, run_tribe_alignment_validation_evaluate_alignment, run_tvb_alignment_script, run_12feat_validation_script [INFERRED 0.88]
- **Closed-Loop Controller Strategy Family (Fixed / Reactive / Predictive / Oracle appear in all pipeline scripts)** — run_alzheimer_simulation_FixedSchedule, run_alzheimer_simulation_Reactive, run_alzheimer_simulation_Predictive, run_tribe_alignment_validation_OracleCtrl [INFERRED 0.85]
- **12-Feature TCN Training and Replay Pipeline (train → checkpoint → controller → evaluation)** — run_12feat_validation_train_12feat_tcn, run_12feat_validation_TCN12FeatCtrl, run_12feat_validation_run_replay [EXTRACTED 0.95]
- **Paper Figure Generation Pipeline (sweep JSON -> figure scripts -> results/figures/)** — models_sweep_horizons_json, generate_paper_figures_generate_horizon_sweep, regenerate_paper_figures_fig_horizon_sweep, results_figures_dir [EXTRACTED 0.92]
- **End-to-End Streaming Inference Demo (Adapter -> Feature Extraction -> EEGNet -> TCN -> Controller)** — demo_streaming_simulated_eeg_adapter, demo_streaming_streaming_feature_extractor, src_eegnet_module, temporal_multiscale_model_registry, src_personalization_module [EXTRACTED 0.95]
- **CSEF Submission Document Generation (PDF + PPTX presentation generators)** — generate_csef_presentation_script, generate_csef_pptx_script, submission_presentation_csef_pdf [INFERRED 0.85]
- **CSEF Judges Pre-Read Abstracts and 13-Page Presentation Before Interviews** — csef_vs_synopsys_rules_csef_judging, csef_vs_synopsys_rules_13page_presentation, csef_vs_synopsys_rules_forms_paperwork [EXTRACTED 0.90]
- **PAC Forecasting Closed-Loop Pipeline (Dataset → TCN → Controller → Results)** — ABSTRACT_openneuro_dataset, ABSTRACT_tcn_model, ABSTRACT_closed_loop_controller, ABSTRACT_alignment_result [EXTRACTED 0.95]
- **Feature Ablation Scientific Finding (73-feat overfits, 12-feat generalizes)** — ABSTRACT_73_feature_engineering, v2_abstract_feature_ablation, v2_abstract_spectral_overfitting, v2_abstract_12feat_tcn [EXTRACTED 0.95]
- **NeuroCare 40Hz Key Claims: 72% Accuracy, R²=0.60, Non-invasive Personalized Therapy** — facility_flyer_72pct_result, facility_flyer_key_result_r2, flyer_key_result_72pct [EXTRACTED 0.90]
- **Complete P10 Submission Package — All Required Forms for SCVSEFA Competition** — p10_ethics_ethics_statement, p10_permission_hold_harmless, p10_1a_student_checklist, p10_1_checklist_adult_sponsor, p10_1b_approval_student_ack, p10_media_release, p10_plan_engineering_goal, p10_page1_application_form [EXTRACTED 0.95]
- **Research Plan Core — Goal, Criteria, Constraints, Design, Test, Bibliography** — p10_plan_engineering_goal, p10_plan_design_criteria, p10_plan_constraints, p10_plan_system_design, p10_plan_system_flowchart, p10_plan_test_method, p10_plan_bibliography [EXTRACTED 0.95]
- **Guardian/Sponsor Approval Chain — Irfan Chughtai + John Crandall Signatures Across All Forms** — p10_permission_parent_irfan, p10_media_parent_consent, p10_1b_parent_approval, p10_1_checklist_adult_sponsor [EXTRACTED 0.90]
- **Lab Notebook Chronological Record of Full Pipeline from EEG to Closed-Loop Controller (Synopsys + CSEF)** — P10_Lab_Notebook_VFINAL_pipeline_build_feb6, P10_Lab_Notebook_VFINAL_causal_tcn_design, P10_Lab_Notebook_VFINAL_controller_comparison_feb26 [EXTRACTED 0.95]
- **Feature Ablation → Multi-Seed Validation → Model Size Sweep → Deployed 12-Feature h=32 TCN** — vfinal_lab_notebook_feature_ablation_mar3_8, extension_5seed_benchmark, vfinal_lab_notebook_model_size_sweep_mar13_14 [EXTRACTED 0.92]
- **TRIBE V2 Failure → CorticalResponseConfig → Wilson-Cowan Neural Mass → Alzheimer Severity Profiles** — extension_tribe_v2_attempt, extension_cortical_response_model, extension_wilson_cowan_model [EXTRACTED 0.90]
- **Two-Stage Closed-Loop Pipeline: EEGNet Static Estimator → Feature Engineering → MultiscaleCausalTCN → Controller** — RESEARCH_PAPER_v3_eegnet_arch, RESEARCH_PAPER_v3_73features, RESEARCH_PAPER_v3_tcn_arch, RESEARCH_PAPER_v3_controller_variants [EXTRACTED 1.00]
- **Core Result: TCN Horizon Sweep + Controller Comparison + Per-Subject Universality** — RESEARCH_PAPER_v3_horizon_sweep_results, RESEARCH_PAPER_v3_controller_results, RESEARCH_PAPER_v3_contribution3 [EXTRACTED 0.95]
- **Architecture Pivot Rationale: Static Ceiling → PAC Autocorrelation → Temporal TCN** — RESEARCH_PAPER_v3_contribution1, rationale_temporal_over_static, RESEARCH_PAPER_v3_contribution2 [EXTRACTED 0.95]
- **12-Feature PAC+Stim TCN → Closed-Loop Controller → Validated on 35-Subject EEG** — v4_paper_pac_stim_12feat, v4_paper_multiscale_causal_tcn, v4_paper_controller_comparison_results [EXTRACTED 1.00]
- **Static Ceiling (R²=0.287) → Temporal Pivot → Feature Ablation → 12-Feature Model** — 05_architecture_search_static_ceiling, 05_architecture_search_temporal_pivot_rationale, v4_paper_feature_ablation_study [EXTRACTED 0.95]
- **Paper Version Progression: v2 (73-feat) → v3 PDF → v4 (12-feat ablation)** — v2_26pages_md_earlier_version, research_paper_v3_pdf_published, v4_paper_paper_v4 [INFERRED 0.85]
- **Poster Version Lineage: V1 → V2 → V3 → V5 → V6/V8 (Synopsys → CSEF)** — poster_board_orig_doc, poster_board_v5_doc, poster_board_v8_doc [INFERRED 0.85]
- **Poster Coherence Audit Flags Three Critical Result Gaps** — poster_coherence_audit_doc, poster_coherence_audit_coherence_issue_1, poster_coherence_audit_coherence_issue_2 [EXTRACTED 0.95]
- **Poster Build Toolchain: Builder Scripts → PDF Outputs** — v1_builder_py, v2_builder_py, poster_archive_dimensions_md [INFERRED 0.80]
- **CSEF 2026 Submission Evidence Package: poster, presentation, abstract, results report all reporting same core findings** — csef_poster_v2_project_title, csef_presentation_intro_slide, abstract_p10_synopsys, results_report_tcn_vs_reactive_stats [EXTRACTED 0.95]
- **Controller Validation Evidence: figures, results report, and Q&A all corroborating 72.1% alignment and 82.6% low-PAC targeting** — fig_controller_comparison_v2_chart, results_report_controller_comparison, qa_complete_tier3_results [EXTRACTED 0.92]
- **Architecture Decision Chain: code map timeline + marathon rationale + methodology all explain V1-V8 → TCN pivot** — code_map_timeline_phases, qa_complete_architecture_marathon_rationale, current_methodology_tcn_architecture [INFERRED 0.88]
- **Poster Version Lineage: V4 → V5 → V7 → vFinal PDF** — POSTER_BOARD_V4_poster_v4, POSTER_BOARD_V5_poster_v5, POSTER_BOARD_V7_poster_v7, vfinal_poster_pdf [INFERRED 0.92]
- **Numerical Integrity Chain: Verification Table → Hysteresis Note → Results Callout** — POSTER_BOARD_V7_numerical_verification, POSTER_BOARD_V7_hysteresis_note, POSTER_BOARD_V7_results_callout [INFERRED 0.85]
- **Feature Ablation Narrative: Key Discovery Box → V7 Figure Inventory → vFinal Ablation Figure** — POSTER_BOARD_V7_key_discovery_box, POSTER_BOARD_V7_figure_inventory, vfinal_poster_feature_ablation_fig [INFERRED 0.88]
- **Presentation Preparation System (Scripts + Q&A + Memorization + Citations)** — vfinal_script_presentation, csef_interview_qa_tier4_hard, reference_map_number_clusters, key_citations_core_citations [INFERRED 0.85]
- **Core Scientific Discovery Narrative (Ceiling → Ablation → TCN → Validation)** — architecture_marathon_ceiling, feature_ablation_discovery, causal_tcn_system, horizon_sweep_key_finding [INFERRED 0.90]
- **Judge-Facing Citation Framework (Iaccarino → Murdock → Lahijanian → Tort)** — key_citations_iaccarino_2016, key_citations_murdock_2024, key_citations_lahijanian_2024, key_citations_tort_2010 [EXTRACTED 0.95]
- **Full Presentation Script Ecosystem (All Lengths and Versions)** — main_script_01, short_version_02, elevator_pitch, v1_script_2min [INFERRED 0.85]
- **Judge Preparation Materials (Interview, Depth Guide, Danger Zones)** — judge_interview_prep, answer_depth_guide, final_04_qa_danger_zones [INFERRED 0.88]
- **Memorization System (Rooms, Guide, Pocket Card)** — memorization_guide_03, v1_memo_guide, v1_memo_rooms [INFERRED 0.82]
- **Full Presentation Preparation Ecosystem (scripts, memorization, Q&A, danger zones)** — vfinal_mindmap_9beat_spine, vfinal_memo_guide_unlock_phrases, danger_zones_v2_condensed, numbers_sheet_v2_key_metrics, v2_qa_complete_tier1_basic [INFERRED 0.88]
- **Key Scientific Findings Cluster (ceiling, feature discovery, horizon sweep)** — current_methodology_eegnet_static, current_methodology_spectral_overfit_finding, current_methodology_horizon_sweep_finding [INFERRED 0.90]
- **Clinical Framing Materials for Medical Judges (medical deep dive, FDA pathway, drug comparison)** — medical_deep_dive_amyloid_cascade, medical_deep_dive_glymphatic_aqp4, medical_deep_dive_fda_pathway, medical_deep_dive_lecanemab_comparison [INFERRED 0.85]
- **Two-Stage Pipeline Key Metrics (EEGNet → TCN → Controller)** — numbers_sheet_old_eegnet_stage1, numbers_sheet_old_tcn_stage2, numbers_sheet_old_controller_comparison [EXTRACTED 0.95]
- **Synopsys Fair Preparation Package (Reference Guide + Winning Analysis + Judge Interview Prep)** — synopsys_reference_guide, synopsys_winning_analysis, judge_interview_prep_ref [INFERRED 0.85]
- **TCN Design Decisions Cluster (TCN over LSTM, GroupNorm, 12-feat, 5s horizon)** — rationale_tcn_over_lstm, rationale_groupnorm_over_batchnorm, rationale_12feat_vs_73feat, rationale_5s_horizon [INFERRED 0.80]
- **Judge-Facing Presentation Materials (Script + Elevator Pitch + Deep Dive + CSEF Strategy)** — presentation_script, elevator_pitch_ref, project_deep_dive_quick_reference, csef_judging_strategy [INFERRED 0.80]
- **TCN Pipeline: EEGNet + Causal TCN jointly evaluated on 35-subject dataset to produce alignment and targeting results** — vfinal_submission_eegnet_architecture, vfinal_submission_causal_tcn, vfinal_submission_dataset, vfinal_submission_result1_tcn_vs_reactive [EXTRACTED 0.95]
- **Feature Ablation as Central Scientific Finding: spectral leakage explains generalization failure; 12-feature model is the production result** — vfinal_submission_feature_ablation, vfinal_submission_12feat_input, vfinal_submission_spectral_leakage_rationale, vfinal_submission_causal_tcn [EXTRACTED 1.00]
- **Clinical Translation: 35/35 universal benefit + <$300 hardware + no GPU = pathway to accessible AD therapy** — vfinal_submission_35_subjects_benefit, vfinal_submission_clinical_use, vfinal_submission_future_directions [INFERRED 0.85]
- **Temporal Pipeline: Build → Train → Audit Flow** — temporal_multiscale_readme_build_multiscale_dataset, temporal_multiscale_readme_train_multiscale_tcn, temporal_multiscale_readme_audit_multiscale_pipeline [EXTRACTED 0.95]
- **TCN Dual-Head Output: Future PAC + Delta PAC** — temporal_multiscale_readme_causal_multiscale_tcn, temporal_multiscale_readme_future_pac_target, temporal_multiscale_readme_delta_pac_target [EXTRACTED 1.00]
- **Validation Rigor: Audit Findings Addressed by Three New Modules** — AUDIT_REPORT_pipeline_audit, rigorous_validation_main, multi_seed_training_main, eegnet_enhanced_EEGNetEnhanced [INFERRED 0.90]
- **EEGNet Capacity Scaling Experiment: original/enhanced/large vs R²=0.287 ceiling** — eegnet_enhanced_EEGNetEnhanced, eegnet_enhanced_EEGNetLarge, multi_seed_training_model_registry [EXTRACTED 0.95]
- **Closed-Loop Control Strategy Comparison: Fixed/Reactive/Predictive/Oracle** — rigorous_validation_FixedScheduleControl, rigorous_validation_ReactiveThresholdControl, rigorous_validation_PredictiveLookAheadControl, rigorous_validation_OracleControl [EXTRACTED 1.00]
- **TCN Variant Architecture Comparison (DeepDilation, MultiTask, Wider, Transformer vs Baseline)** — tcn_variants_DeepDilationTCN, tcn_variants_MultiTaskTCN, tcn_variants_WiderTCN, tcn_variants_TransformerTCN, tcn_variants_VARIANT_REGISTRY [EXTRACTED 1.00]
- **Fatigue Model Sensitivity Suite (4 Models Testing Adaptive Scheduling Robustness)** — fatigue_model_sensitivity_ExponentialDecaySimulator, fatigue_model_sensitivity_StepFunctionSimulator, fatigue_model_sensitivity_HeterogeneousPopulationSimulator, fatigue_model_sensitivity_SaturationModelSimulator [EXTRACTED 0.95]
- **TCN Interpretability Analysis (Attention Weights + Feature Ablation + Stim-Conditional)** — tcn_interpretability_analyze_attention_weights, tcn_interpretability_run_ablation_experiment, tcn_interpretability_analyze_stimulation_conditional [EXTRACTED 0.95]
- **Synopsys Championship Poster + Presentation Materials Suite** — POSTER_BOARD_V5_poster_v5, 03_memorization_guide_rooms, JUDGE_INTERVIEW_PREP_qa_bank [INFERRED 0.92]
- **TCN Universal Benefit Evidence Cluster (figure + table + poster)** — per_subject_utility_figure, per_subject_utility_tcn_universal_benefit, POSTER_BOARD_V5_controller_comparison_table [INFERRED 0.88]
- **Data Ceiling Discovery → Motivates Temporal Pivot** — POSTER_BOARD_V5_architecture_exploration, POSTER_BOARD_V5_data_ceiling_rationale, POSTER_BOARD_V5_two_stage_pipeline [EXTRACTED 0.97]
- **TCN Predictive Advantage Evidence (Poster + Figure 6 + Threshold Sensitivity)** — Slide1_print_tcn_predictive_control, figure6_tcn_advantage_zone, threshold_sensitivity_archive_tcn_advantage_zone [INFERRED 0.85]
- **Consumer Deployment Pipeline (Muse 4ch + TCN + Closed-Loop Therapy)** — figure6_pac_stim_tcn_4ch_muse, figure11_muse2_headband, figure11_closed_loop_personalized_therapy [INFERRED 0.80]
- **Controller Comparison: Metrics Defined in Fig12, Applied in Timeline (Fig timeline), Aggregated in Fig13 (N=35)** — figure12_metric_definitions, timeline_example_controller_comparison, figure13_controller_performance [INFERRED 0.85]
- **TCN Predictive vs Reactive Controller Evidence Chain (Timeline → Bar Chart → Effect Sizes)** — timeline_example_tcn_controller, figure13_tcn_predictive, figure13_effect_size_g131 [INFERRED 0.82]
- **Controller Types Compared Across PAC Gap and Threshold Sensitivity Figures** — pac_targeting_gap_png_tcn_controller, pac_targeting_gap_png_reactive_controller, threshold_sensitivity_png_reactive_baseline_645 [INFERRED 0.85]
- **System Architecture ML Pipeline: EEGNet + Feature Extraction + Causal TCN** — system_block_diagram_png_eegnet_block, system_block_diagram_png_feature_extraction_block, system_block_diagram_png_causal_tcn_block [EXTRACTED 1.00]
- **TRIBE V2 Backend: Strategy Comparison across PAC, Efficiency, and Dynamics** — tribe_v2_backend_comparison_png_pac_by_strategy, tribe_v2_backend_comparison_png_predictive_pac_dynamics, tribe_v2_backend_comparison_png_energy_efficiency [EXTRACTED 0.90]
- **TCN Advantage Evidence: Per-Subject Utility, Horizon Sweep, Protocol Validation** — figure14_per_subject_clinical_utility, horizon_sweep_causal_tcn_curve, figure9_real_eeg_replay_validation [INFERRED 0.85]
- **Baseline Collapse vs TCN Robustness at 5–10s Horizon** — horizon_sweep_persistence_baseline, horizon_sweep_ridge_regression_baseline, horizon_sweep_causal_tcn_curve [EXTRACTED 1.00]
- **Causal TCN Maintains Positive R² at 5-10s Where Both Baselines Collapse** — horizon_sweep_causal_tcn, horizon_sweep_persistence_baseline, horizon_sweep_ridge_regression_baseline [EXTRACTED 0.95]
- **Controller Comparison on Stimulation-Alignment Pareto Trade-off** — stim_vs_alignment_oracle_controller, stim_vs_alignment_tcn_controller, stim_vs_alignment_reactive_controller, stim_vs_alignment_fixed_controller, stim_vs_alignment_hybrid_controller, stim_vs_alignment_pi_controller [EXTRACTED 1.00]
- **Feature Ablation Demonstrating Spectral Overfitting vs PAC+Stim Generalization** — figure4_all73_r2_negative, figure4_spectral_only_r2_worse, figure4_pac_stim_12feat_r2 [EXTRACTED 1.00]
- **Dataset Overview: Channels, Protocol, Subject-Level Splits** — figure8_7_frontal_channels, figure8_stimulus_rest_protocol, figure8_subject_level_split [EXTRACTED 1.00]
- **Closed-Loop Pipeline: EEG → Preprocessing → EEGNet → Feature Extraction → TCN → Controller → Stimulation** — system_block_diagram_patient_eeg_node, system_block_diagram_preprocessing_stage, system_block_diagram_eegnet_model, system_block_diagram_feature_extraction, system_block_diagram_causal_tcn, system_block_diagram_closedloop_controller, system_block_diagram_audio_stimulation [EXTRACTED 1.00]
- **Controller Comparison on Sub-15 Test Set: PAC Signal + Reactive + TCN** — figure7_pac_signal_ground_truth, figure7_reactive_controller_decisions, figure7_tcn_predictive_controller_decisions [EXTRACTED 1.00]
- **PAC Coupling: Theta Phase Modulates Gamma Amplitude → Modulation Index** — figure2_theta_rhythm, figure2_gamma_oscillations, figure2_pac_modulation_index [EXTRACTED 1.00]
- **TCN Prediction Enables Adaptive Scheduling to Target Low-PAC Windows (72% vs 45%)** — figure1_tcn_prediction, figure1_adaptive_schedule, figure1_fixed_schedule [EXTRACTED 0.95]
- **Controller Comparison Trade-off Space (Alignment, Low-PAC Targeting, Stim Rate) across Fixed/Reactive/PI/TCN/Hybrid/Oracle** — stim_vs_alignment_figure, controller_comparison_v2_figure, per_subject_utility_figure [INFERRED 0.90]
- **Complete Closed-Loop Pipeline: EEG → EEGNet → Feature Extraction → Causal TCN → Controller → Audio Output → Simulation** — figure5_raw_eeg_input, figure5_eegnet_block, figure5_feature_extraction_12, figure5_causal_tcn_block, figure5_closed_loop_controller, figure5_audio_signal_generator, figure5_simulation_update [EXTRACTED 1.00]
- **TRIBE V2 Alzheimer Simulation Suite: Disease Severity x Controller Strategy Evaluation** — alzheimer_simulation_tribe_v2_alzheimer_simulation, tribe_v2_alzheimer_sweep_figure, alzheimer_simulation_pac_heatmap_strategy_severity [INFERRED 0.85]
- **Controller Comparison via PAC Targeting Gap: Fixed vs Reactive vs TCN vs Oracle** — pac_targeting_gap_fixed_controller, pac_targeting_gap_tcn_controller, pac_targeting_gap_oracle_controller [EXTRACTED 1.00]
- **Predictive Closed-Loop 40Hz Entrainment System** — methodology_eegnet_static, methodology_multiscale_causal_tcn, methodology_closed_loop_controller [EXTRACTED 0.95]
- **TCN vs Reactive Key Results (Alignment, Targeting, PAC Gap)** — results_controller_comparison, results_statistical_significance, results_pac_targeting_quality [EXTRACTED 0.90]
- **73-Dimensional Feature Vector (Spectral + PAC + Stim)** — methodology_spectral_features, methodology_pac_derived_features, methodology_stim_context_features [EXTRACTED 1.00]
- **Three Evaluation Metrics Jointly Assessed Across All Six Controllers** — controller_comparison_v2_alignment_metric, controller_comparison_v2_lowpac_stim_metric, controller_comparison_v2_highpac_rest_metric [EXTRACTED 1.00]
- **V1-V5 Model Iteration Arc: Leakage Discovery → Architecture Search → Simple Wins** — AUDIT_REPORT_v3_audit_mi_leakage, V4_FAILURE_ANALYSIS_vit_tcnet_failure, FINAL_ASSESSMENT_honest_baseline_ridge [INFERRED 0.90]
- **EEG PAC Prediction Ceiling: SNR + Circular Reasoning + Dataset Size** — FINAL_VERDICT_MASTER_MODEL_snr_ceiling, FINAL_VERDICT_MASTER_MODEL_circular_reasoning_constraint, FINAL_VERDICT_MASTER_MODEL_information_theoretic_limit [INFERRED 0.88]
- **SpecTempNet V3 Architecture: Multi-Scale CNN + Spectral Features + Attention Fusion** — V3_IMPLEMENTATION_SUMMARY_multiscale_temporal_cnn, V3_CLEAN_NO_MI_feature_breakdown_61, V3_IMPLEMENTATION_SUMMARY_multihead_attention_fusion [EXTRACTED 0.95]
- **PAC+Stim Feature Discovery Pipeline (experiment, analysis, reporting)** — run_generalization_FeatureAblation, run_pac_stim_focused_ArchitectureSearch, AUDIT_AND_REPORT_PACStimFinding [INFERRED 0.85]
- **Sliding-PAC vs Epoch-PAC Comparison Pipeline** — compute_sliding_pac_SlidingPACComputation, build_sliding_dataset_BuildSlidingDataset, train_and_compare_TrainAndCompare [EXTRACTED 0.95]
- **TCN Generalization Experiments (mixup, regularization, feature subset)** — run_generalization_GeneralizationExperiments, run_generalization_MixupSeqDataset, run_generalization_TinyTCN [EXTRACTED 0.90]
- **ImprovedTCN Full Training Pipeline: enhanced features → ImprovedTCN → multi-task loss** — build_enhanced_dataset_build_enhanced_dataset, improved_tcn_model_ImprovedTCN, train_improved_tcn_multi_task_loss [INFERRED 0.90]
- **Time-Domain Feature Set: Hjorth + SampEn + ZCR per channel** — enhanced_features_compute_hjorth_params, enhanced_features_compute_sample_entropy, enhanced_features_compute_zero_crossing_rate [EXTRACTED 1.00]
- **Three-Head Output: future PAC + delta PAC + smoothed auxiliary PAC** — improved_tcn_model_three_heads, train_improved_tcn_multi_task_loss, train_improved_tcn_evaluate [EXTRACTED 1.00]

## Communities

### Community 0 - "Closed-Loop Control & Simulator"
Cohesion: 0.02
Nodes (240): ClosedLoopController, PredictiveLookAheadController, Closed-Loop Controller for Real-Time PAC-Based Neuromodulation  Implements thr, Execute one control step.          Processes incoming EEG window and makes sti, Make stimulation decision based on z-score.          Logic:             - If, Reset controller for new session.          Clears all state, baseline, and his, Get current controller state.          Returns:             state: Dictionary, Get full history of decisions and measurements.          Returns: (+232 more)

### Community 1 - "Multiscale TCN & Features"
Cohesion: 0.01
Nodes (272): CausalDSConvBlock, Checkpoint deployment realism audit.  Evaluates a trained checkpoint under multi, SeqDataset, _eval_denorm(), _eval_r2_norm(), Baseline and comparison model architectures for the architecture comparison stud, Causal Transformer encoder for sequence-to-scalar PAC prediction.      A causal, Train any nn.Module that takes (B, T, F) and outputs (B,) scalar predictions. (+264 more)

### Community 2 - "Models, Streaming & Apps"
Cohesion: 0.02
Nodes (227): Critical Finding: Validation Does Not Test Trained TCN, High Finding: Cohen's d Mathematically Wrong, High Finding: EEGNet Under-Parameterized (~1457 params), High Finding: No Cross-Validation (Single Seed 42 Split), Key Result: TCN R²=0.25 at 5-10s Horizons vs Negative Persistence, Rigorous Pipeline Audit Report, Clarification: Predictive Look-Ahead is Trend-Based Not TCN, Rationale: R²=0.287 Is Data Limitation Not Model Bottleneck (+219 more)

### Community 3 - "Archived Feature Experiments (v4)"
Cohesion: 0.02
Nodes (117): Critical audit: Check if spectral features include target PAC, AddGaussianNoise, ChannelDropout, Compose, EEGAugmentation, MagnitudeWarp, Time-Series Data Augmentation for EEG  Implements augmentation techniques specif, Shift the signal in time (circular shift).      This makes the model robust to t (+109 more)

### Community 4 - "Core Data & PAC Pipeline"
Cohesion: 0.03
Nodes (71): EEGWindowDataset, main(), BIDS Data Loader for Closed-Loop 40Hz Entrainment Research  Loads OpenNeuro ds, Get subject ID for a sample., Get session ID for a sample., Initialize BIDS data processor.          Args:             bids_root: Path to, Get list of subjects in BIDS dataset.          Returns:             subjects:, Load raw EEG data for a subject.          Handles MATLAB v7.3 (HDF5) .set file (+63 more)

### Community 5 - "Research Paper & Manuscript"
Cohesion: 0.02
Nodes (117): 04 QA Bank: Judge Strategy Brief and Danger Zones, 73-Dimensional Causal Feature Vector (61 spectral + 7 PAC + 5 stim context), Abstract: TCN achieves 72.1% vs 64.5% alignment, 91% oracle, 35/35 subjects, Architecture Search: 8 Models, All Converge to R²≈0.287, Contribution 1: R²=0.287 Static PAC Ceiling (8 architectures converge), Contribution 2: Causal TCN for 5-10s PAC Forecasting (+0.5 R² margin), Contribution 3: Closed-Loop Controller Validated on 35 EEG Subjects, Contribution 4: Prediction Horizon Inflection Point (~3 seconds) (+109 more)

### Community 6 - "TRIBE Neural-Mass Simulator"
Cohesion: 0.04
Nodes (84): AlzheimerProfile, get_profile(), interpolate_profile(), Alzheimer's Disease Modeling Layer for TRIBE V2 Integration  Models the effects, Apply region-specific disease modification to ROI activations.          Differen, Modify neural mass model external drive for AD simulation.          Args:, Modify exponential simulator parameters for AD simulation.          Compatible w, Get Alzheimer's profile by severity name.      Args:         severity: One of "h (+76 more)

### Community 7 - "Archived ImprovedTCN Experiments"
Cohesion: 0.05
Nodes (72): ensemble_evaluate(), main(), Best combination experiments: 1. Target smoothing (ts=5) + deep TCN architecture, Evaluate ensemble of models by averaging predictions., Train model and evaluate., train_and_eval(), CausalConvBlock, compute_metrics() (+64 more)

### Community 8 - "Paper/Presentation PDF Builders"
Cohesion: 0.04
Nodes (54): FPDF, CSEF, main(), p01_title(), p02_intro1(), p03_intro2(), p04_methods1(), p05_methods2() (+46 more)

### Community 9 - "Control Strategies & Validation"
Cohesion: 0.06
Nodes (68): Critical Finding: ANOVA on n=1 Samples, ExponentialDecaySimulator (Fatigue Model 1: Exponential Decay), HeterogeneousPopulationSimulator (Fatigue Model 3: 50% No-Fatigue / 50% High-Fatigue), SaturationModelSimulator (Fatigue Model 4: Synaptic Adaptation Ceiling Decay), StepFunctionSimulator (Fatigue Model 2: Sudden Threshold Drop), create_simulator(), ExponentialDecaySimulator, FatigueModelConfig (+60 more)

### Community 10 - "Poster Boards & Figures"
Cohesion: 0.03
Nodes (89): Presentation Chain Transitions (9 Room-to-Room Bridges), Emotional Anchoring Table (Feeling Per Room), Key Number Clusters for Memorization (6 Groups), Blank Recovery Protocol (5-Step On-Stage Recovery), Poster Memory Palace (9 Rooms, Left-to-Right Journey), Feature Ablation Figure on Poster (73 vs 12 features, R² comparison), CSEF Poster V3 (Final Print-Ready Poster), System Architecture Flowchart on Poster (EEGNet→Features→TCN→Controller) (+81 more)

### Community 11 - "Archived Enhanced-Feature TCN"
Cohesion: 0.04
Nodes (62): build_enhanced_dataset(), _build_split_samples_enhanced(), Enhanced Feature Composition (108-feat 7ch / 69-feat 4ch), main(), Muse 4-Channel Support Flag (--muse-4ch), parse_args(), Build enhanced multiscale temporal datasets for PAC forecasting.  Extends the ba, Build an enhanced multiscale temporal dataset.      Loads existing spectral cach (+54 more)

### Community 12 - "Controller Results & Judge Prep"
Cohesion: 0.03
Nodes (80): 4ch vs 7ch Evaluation Caveats (proxy comparison, Muse 2 noise, overfit), CSEF Defense Narrative: Temporal Context Compensates for Spatial Reduction, EEGNet Static PAC Prediction: 7ch R2=0.287 vs 4ch R2=0.016, Rationale: Why Static Gap Larger Than Temporal Gap, Hardware Configuration: 7ch Research-Grade vs 4ch Muse 2 Proxy, Muse 2 Consumer Headset as Proxy for 4-Channel Configuration, 4-Channel vs 7-Channel EEG Performance Gap Report, Source Files: model checkpoints, metrics JSONs for 4ch and 7ch (+72 more)

### Community 13 - "Lab Notebook PDF Generation"
Cohesion: 0.03
Nodes (75): P10 Lab Notebook V3 PDF (Title Page, TOC, Body), Project P10 Research Log Notebook V3 (Synopsys Submission), 73-Dimensional Temporal Feature Representation, Architecture Marathon and R2=0.287 Ceiling (February 16, 2026), MultiscaleCausalTCN Design (31K params, dilations [1,2,4,8]), Citation: Iaccarino et al. (2016) - 40Hz gamma entrainment reduces amyloid, Citation: Lahijanian et al. (2024) - OpenNeuro ds005048 Dataset, Citation: Lawhern et al. (2018) - EEGNet (+67 more)

### Community 14 - "12-Feature TCN Validation"
Cohesion: 0.04
Nodes (41): Alignment Score Metric (Low-PAC Stim + High-PAC Rest) / 2, PAC Gap Metric (Mean PAC Rest − Mean PAC Stim), FeatureMaskedDataset (73→12 Feature Slice Dataset), TCN12FeatCtrl (12-Feature Predictive Controller for Replay), AlignmentOracleCtrl, evaluate_epoch_alignment(), Rationale: Drop Spectral Features (Indices 0-60) to Prevent Anatomy Overfitting, FixedScheduleCtrl (+33 more)

### Community 15 - "Replay Analysis & Controllers"
Cohesion: 0.04
Nodes (39): CUSUMControl, evaluate_decisions(), _extract_biomarkers_single(), FixedScheduleControl, load_subjects(), main(), MultiBiomarkerReactiveControl, OracleControl (+31 more)

### Community 16 - "PPTX Slide Builder"
Cohesion: 0.1
Nodes (43): _add_paragraph(), _add_textbox(), _first_paragraph(), main(), p01_title(), p02_intro1(), p03_intro2(), p04_methods1() (+35 more)

### Community 17 - "Archived Temporal PAC Predictor"
Cohesion: 0.05
Nodes (42): Rationale: LSTM for Model Predictive Control of 40Hz Entrainment, MultiHorizonPredictor (Multi-Head LSTM), SpatialEncoder (CNN Window Encoder), TemporalPACPredictor (LSTM/GRU Model), MultiHorizonPredictor, Temporal PAC Prediction Models  LSTM and GRU architectures for predicting futu, Args:             n_channels: Number of EEG channels             n_samples: Sa, Args:             batch: Dictionary with keys:                 'eeg': (+34 more)

### Community 18 - "CSEF Presentation Generator"
Cohesion: 0.11
Nodes (55): add_body(), add_body_mixed(), add_bullet(), add_caption(), add_figure(), add_heading(), add_spacer(), add_subheading() (+47 more)

### Community 19 - "TVB Alzheimer Simulator"
Cohesion: 0.06
Nodes (28): evaluate_alignment(), FixedScheduleCtrl, hedges_g(), main(), TVB Jansen-Rit Alignment Evaluation: Closed-Loop Controller Comparison  Runs Fix, ReactiveCtrl, run_oracle_trial(), run_trial() (+20 more)

### Community 20 - "Literature Review & Methodology Docs"
Cohesion: 0.05
Nodes (50): OpenNeuro ds005048 Dataset (IEEE Paper Reference), EEGNet Architecture (IEEE Paper Specification), GENUS: Gamma Entrainment Using Sensory Stimulation, Inter-Individual Variability in Entrainment Response, MPC Decision Engine (IEEE Paper Formulation), PAC Computation Pipeline (IEEE Paper), IEEE Research Paper: Personalized Deep Learning for Closed-Loop 40Hz Entrainment, Personalization Module (IEEE Paper) (+42 more)

### Community 21 - "TCN Layer Internals"
Cohesion: 0.06
Nodes (27): AttentionPool1D, CausalDSConvBlock, CausalSinusoidalPE, _count_parameters(), DeepDilationTCN, LastStepPool, _make_regression_head(), Take last timestep from causal output.      For a causal architecture the last (+19 more)

### Community 22 - "Rigor Audit Reports"
Cohesion: 0.06
Nodes (46): CSEF Presentation Compliance Checklist (18/18 PASS), Page Count and Section Structure Requirements (12 pages, 8 sections), Project Summary Word Count Check (142 words, under 150 limit), CSEF Font Requirements (14pt min, sans-serif recommended), Font Compliance Audit, Times New Roman Font Warning, Figure and Visual Compliance Audit, System Architecture Figure Outdated Specs Warning (73-feat/31K shown vs 12-feat/22914) (+38 more)

### Community 23 - "Presentation Scripts & Citations"
Cohesion: 0.07
Nodes (45): Tier 1 Basic Q&A (Every judge asks these), Tier 5 Hard Challenge Q&A (Architecture, novelty, impact), Architecture Marathon: 8-Model Static PAC Ceiling R2=0.287, Causal TCN System (20s lookback, 5s forecast, 12-feature input), Closed-Loop Controller (z-score thresholds, hysteresis, personalization), Model Zoo Table (All Architectures, Params, R2), Code Map: Phase 1-3 Approach Timeline, Quick-Reference Numbers for CSEF Interview (+37 more)

### Community 24 - "TRIBE-TCN Validation"
Cohesion: 0.07
Nodes (29): CausalConv1dBlock (Dilated Residual Conv Block), TCNTribe Model (TRIBE-trained Causal TCN), TCNTribeController (Proactive Closed-Loop Controller), build_features_from_sequence(), CausalConv1dBlock, Rationale: Domain Mismatch Between Real EEG TCN and TRIBE Simulator, evaluate_alignment(), FixedScheduleCtrl (+21 more)

### Community 25 - "Generalization-Gap Experiments"
Cohesion: 0.06
Nodes (41): Epoch-Level PAC Caveat: 82.2% Same-Epoch Samples, ImprovedTCN Architecture (6338 params, 12-feature input), PAC+Stim Feature Discovery Audit Report, Rationale: Spectral Features Cause Subject-Specific Overfitting, Known Bug: Stim Context hop_sec Mismatch (1s vs 2s window), Approaches That Did NOT Work (architecture, mixup, heavy-reg on all 73), Feature Ablation Table (6 subsets: all→-0.025, pac_stim→0.558), FINDINGS: Spectral Features Cause Catastrophic Generalization Failure (+33 more)

### Community 26 - "Archived EEGNet V2"
Cohesion: 0.07
Nodes (25): EEGDatasetV2, load_processed_data_v2(), Enhanced Data Loader for ΔPAC Prediction (Version 2)  Key improvements over v1, Load preprocessed data and compute ΔPAC labels.      Args:         data_dir:, PyTorch Dataset for EEG windows with ΔPAC labels.      Changes from v1:     -, Test the v2 data loader., Args:             X: EEG windows (n_samples, n_channels, n_timepoints), Apply data augmentation to EEG window.          Techniques:         1. Time j (+17 more)

### Community 27 - "Archived CSEF Paper & Abstract"
Cohesion: 0.06
Nodes (40): Controller Alignment: 72.1% Predictive vs 64.5% Reactive (p<0.001), CSEF Old Project Abstract (247 words), Low-PAC Targeting: 82.6% vs 51.7% Reactive (p<0.001), TCN Reaches 91% of Theoretical Oracle Performance, PAC as Real-Time Entrainment Biomarker, TCN +0.5 R² Margin Over Baselines at 5-10s Horizon, Clinical Roadmap (Research to Practice Pathway), Facility Partners: Mission Villa Memory Care + Valley Medical Center (+32 more)

### Community 28 - "Archived SpecTempNet V3"
Cohesion: 0.07
Nodes (26): compute_r2(), EEGDatasetV3, evaluate(), load_and_preprocess_data(), main(), Evaluate on validation/test set., Dataset with both raw EEG and pre-computed spectral features., Load processed data and extract spectral features. (+18 more)

### Community 29 - "Model Ceiling & Leakage Audits"
Cohesion: 0.06
Nodes (38): Rationale: PAC is Theta-Gamma Frequency Coupling — Explicit Features Required, SpecTempNet Architecture Design (3-Branch: Raw EEG + Spectral + Phase-Amplitude), Subject-Specific Adaptation as V3 Fallback Option, MI Formula in Features Identical to Target PAC Formula (KL Divergence), Data Split Audit Passed: 24 Train / 5 Val / 6 Test Subjects (No Overlap), V3 Audit: MI Feature Leakage Identified (R²=0.69 Inflated), Rationale: Features > Architecture for Small EEG Datasets, Honest Baseline: Ridge Regression R²=0.287 (135 spectral+wavelet features) (+30 more)

### Community 30 - "Community 30"
Cohesion: 0.06
Nodes (37): 05 QA Complete: PAC Computation and EEGNet Methodology Answers, Archive Memorization Guide: 12-Room Poster Memory Palace, Archive Main Script: 4-5 Minute Full Presentation, CSEF Presentation README: Active Working File Set, 12-Feature PAC+Stim Configuration (test R²=0.606), Audit Integrity Checks (no leakage, causal indexing, shuffle-label sanity), Closed-Loop Controller (threshold-based, z-score hysteresis), OpenNeuro ds005048 Dataset (Lahijanian 2024, N=35) (+29 more)

### Community 31 - "Community 31"
Cohesion: 0.08
Nodes (37): Adaptive Stimulation Benefit by Severity (Panel C), Adaptive Stimulation Benefit: Predictive minus Fixed (Panel C), Disease Severity Gradient (healthy→preclinical→mild→moderate→severe), Fixed Schedule Controller Strategy, Fixed Stimulation Strategy (baseline), Largest Predictive Benefit at Healthy and Preclinical Stages, PAC Ceiling / Diminishing Returns at Severe Alzheimer's Stages, PAC Dynamics: Predictive Controller Over Time (Panel B) (+29 more)

### Community 32 - "Community 32"
Cohesion: 0.08
Nodes (23): _NumpySimulatedAdapter, Hardware-agnostic EEG adapters for closed-loop inference.  Provides two adapters, Pure-numpy fallback when brainflow is not installed (e.g. cloud deploy).      Ge, Muse 2 BLE adapter — NOT VIABLE on macOS Darwin 25.4.0.      Attempted: 2026-03-, Attempt to open a Muse 2 BLE session.          Args:             mac_address: Bl, Sleep 2 seconds and return one (n_channels, 500) float32 EEG window.          Re, Stop stream and release BrainFlow session., RealEEGAdapter (+15 more)

### Community 33 - "Community 33"
Cohesion: 0.07
Nodes (35): EEGNet V1 (1457 Params, R²=0.287 Static Baseline), Architecture Search Lessons (3 Key Takeaways), Ridge Regression V5 (135 Coefficients, Matches EEGNet), SpecTempNet V3 Leakage Discovery (R²=0.69→0.236 After Fix), Static PAC Prediction Ceiling (R²=0.287, 8 Architectures), Rationale for Temporal Prediction Pivot (from Static Ceiling), ViT-TCNet V4 (1.1M Params, Overfits N=35), Figure: PAC Forecasting Performance vs Prediction Horizon (TCN vs Baselines) (+27 more)

### Community 34 - "Community 34"
Cohesion: 0.06
Nodes (35): Closed-Loop DBS for Parkinson's (Precedent), Gamma Oscillations and Alzheimer's Disease, Individual Variability in 40Hz Response (30% non-responders), Lahijanian 2024 Auditory Entrainment DMN Study, PAC as Biomarker for Alzheimer's Disease, Research Gap Table (What Exists vs Missing), Tort 2010 Modulation Index Method, Causal Padding Design Decision (+27 more)

### Community 35 - "Community 35"
Cohesion: 0.07
Nodes (29): compute_regression_metrics(), count_parameters(), ensure_dir(), get_device(), load_config(), plot_comparison_bars(), plot_pac_timeseries(), plot_prediction_scatter() (+21 more)

### Community 36 - "Community 36"
Cohesion: 0.1
Nodes (30): Effect Size g=1.57 (TCN vs Reactive PAC Gap), Fixed Controller PAC Gap (negative), Hybrid Controller PAC Gap (~34e-6, best non-oracle), Oracle Controller PAC Gap (~33e-6), PAC Targeting Gap by Controller Figure, PI Controller PAC Gap (~27.5e-6), Reactive Controller PAC Gap (~21e-6), TCN Controller PAC Gap (~30.5e-6, g=1.57 vs Reactive) (+22 more)

### Community 37 - "Community 37"
Cohesion: 0.1
Nodes (26): Demo Streaming Inference Script, Generate AI Figures via OpenRouter Script, Generate Closed-Loop vs Fixed v3 Figure Script, Generate CSEF Presentation PPTX Script, Generate CSEF Presentation PDF Script, Generate Image via OpenRouter API Script, generate_horizon_sweep(), generate_system_block_diagram() (+18 more)

### Community 38 - "Community 38"
Cohesion: 0.08
Nodes (14): ATCNet, AugmentedDataset, EEGNet, evaluate_model(), PhaseSwapAugmentation, V8: Specialized EEG Architectures from Research  Based on recent literature (202, EEGNet: Compact CNN for EEG-based BCIs.      Original paper: Lawhern et al. (201, ATCNet: Attention Temporal Convolutional Network.      Combines multi-head self- (+6 more)

### Community 39 - "Community 39"
Cohesion: 0.07
Nodes (27): 12 PAC+Stim Feature Set Description (indices 61–72), Full Pipeline Command Reference (CLAUDE.md), Critical Gotcha: Spectral Features Cause Generalization Failure, Rationale: Causal Convolutions to Prevent Future Leakage, Clinical Relevance: Adaptive Scheduling for Alzheimer's Therapy, Data Integrity Audit (No Leakage, Shuffle-Label Sanity), Dataset Description: ds005048 Processing Pipeline & Splits, EEGNet Architecture Detail (Block 1 + Block 2 + FC Head) (+19 more)

### Community 40 - "Community 40"
Cohesion: 0.11
Nodes (27): EEGNet Static PAC Model (src/eegnet.py, 1457 params), MultiscaleCausalTCN (temporal_multiscale/multiscale_tcn.py, 31K params), PAC Features (Circular — Never Used, R²=0.9999), Phase 1: Static PAC Prediction (V1–V8, Feb 5–16 2026), Phase 2: Temporal PAC Prediction (Feb 16–17 2026), Phase 3: Multiscale Causal TCN (Feb 17 2026), R²=0.287 Static PAC Prediction Ceiling, Repository Organization & Approach History (+19 more)

### Community 41 - "Community 41"
Cohesion: 0.1
Nodes (26): Poster Board V1 (Original, Synopsys), Poster Board V2 (Print-Ready, Synopsys), Poster Board V3 (Print-Ready, Synopsys), Poster Board V5 (Condensed, Visual-Forward, Audit-Verified), V6 Key Change: 12-Feature PAC+Stim Discovery Narrative, 4ch vs 7ch Channel Configuration Table (Muse Compatibility), Controller Comparison Result: 72.1% vs 64.5% Alignment, Poster Board V6 (PAC+Stim Feature Discovery Update) (+18 more)

### Community 42 - "Community 42"
Cohesion: 0.12
Nodes (24): Clinical Vision: Multi-biomarker PAC+connectivity control, IRB Crossover Trial, At-home Wearable Therapy, Figure 10: Future Directions Roadmap, Next Steps: Live Closed-Loop EEG Streaming, 30-60 min Sessions, Reinforcement Learning Controller, This Project Summary (Offline EEG, N=35, TCN R²=0.606, Muse 2 prototype), Binomial p < 0.001 (35/35 Subjects Favor TCN), Figure 14: Per-Subject Clinical Utility (35/35 Favor TCN), Reactive vs Predictive Clinical Utility Scatter (Normalized), TCN Advantage Region (All 35/35 Subjects Above y=x Line) (+16 more)

### Community 43 - "Community 43"
Cohesion: 0.1
Nodes (23): Controller Table Correction (Fixed alignment definition, oracle 100%), TCN Validation Date Correction (Feb 26, not Feb 21), PAC Gap Unit Correction (dimensionless x10⁻⁶, not µV²), Controller Comparison Results (72.1% TCN vs 64.5% Reactive, N=35), Fatigue Model Robustness (4 fatigue models, all p<0.001), Feature Leakage Discovery (MI features circular in static prediction), Habituation Heterogeneity Finding (17/35 habituate, 18/35 do not), Horizon Sweep Experiment (TCN vs Persistence vs Ridge across 1–10s) (+15 more)

### Community 44 - "Community 44"
Cohesion: 0.15
Nodes (21): apply_unicode_replacements(), convert_citations(), convert_inline_formatting(), escape_latex(), fix_common_issues(), generate_latex(), main(), make_label() (+13 more)

### Community 45 - "Community 45"
Cohesion: 0.3
Nodes (21): _arrow(), box_with_text(), build_section_11(), build_section_15(), build_section_19(), build_section_2(), build_section_3(), build_section_6() (+13 more)

### Community 46 - "Community 46"
Cohesion: 0.13
Nodes (13): MultiChannelPersonalization, Compute z-score of current PAC relative to rolling baseline.          Z-score, Return current number of samples in baseline buffer., Personalization module for multi-channel PAC with separate baselines.      Mai, Initialize multi-channel personalization.          Args:             n_channe, Update baseline for all channels.          Args:             pac_values: PAC, Compute z-scores for all channels.          Args:             pac_values: Cur, Compute average z-score across all channels (ignoring NaN).          Args: (+5 more)

### Community 47 - "Community 47"
Cohesion: 0.12
Nodes (22): Comprehensive Submission Audit Report, Label-Shuffle Sanity Check, Metadata Mismatch Guard (train_multiscale_tcn.py), Normalization Leakage Check, PAC Oracle Dependency (Deployment Risk), Subject Split Leakage Check, Target Smoothing Effect on R² (ts1/ts5/ts15), Temporal Causality Leakage Check (+14 more)

### Community 48 - "Community 48"
Cohesion: 0.11
Nodes (22): Checklist for Adult Sponsor (1) — John Crandall Signed, No SRC/IRB/IACUC Pre-Approval Required (computational-only project), Required Forms Confirmed: Adult Sponsor Checklist, Student Checklist 1A, Research Plan, Approval Form 1B, Adult Sponsor: Mr. John Crandall (jcrandall@vcs.net), Data Source: OpenNeuro ds005048 (external dataset), Experimentation Dates: 01/12/26 – 02/15/26 (home-based), Project Title: Personalized Deep Learning Model for Closed-Loop 40 Hz Entrainment to Optimize Theta-Gamma Coupling in Alzheimer's, Research Plan/Project Summary Instructions (ISEF Form Requirements) (+14 more)

### Community 49 - "Community 49"
Cohesion: 0.15
Nodes (20): audit_code(), load_data(), main(), Persistence Baseline — Predict PAC(t) = PAC(t-1), Code Validation & Audit Script (runs without PyTorch)  Validates the temporal, Test 2: Verify no subject appears in multiple splits., Test 3: Characterize PAC temporal autocorrelation per subject.     This determi, Test 4: Sklearn Ridge baseline for temporal prediction.     Uses PAC history + (+12 more)

### Community 50 - "Community 50"
Cohesion: 0.12
Nodes (21): 12 TCN Input Features: PAC trajectory (7) + stimulation context (5), 35/35 Subjects Benefit from TCN Predictive vs Reactive (Figure 14), Causal TCN Temporal PAC Forecaster — 5,154 params, 12 PAC+Stim features, 5s horizon, Towards Clinical Use: Muse 2 headband, <$300 total, no GPU, 40Hz audio delivery, Controller Comparison Table: Fixed Schedule, Reactive, TCN Predictive, Oracle (Figure 13), Dataset: OpenNeuro ds005048, 35 subjects, 7 frontal EEG channels, 17,283 windows, subject-level splits, EEGNet (V4) Static PAC Predictor — 1,457 params, R²=0.287, Feature Ablation Finding: 73-feature model R²=−0.025; 12 PAC+Stim features R²=0.606 (+13 more)

### Community 51 - "Community 51"
Cohesion: 0.11
Nodes (20): Model 2: Causal TCN (Poster Figure), CSEF Poster Print Version (Slide1_print.png), Model 1: EEGNet (Poster Figure), Model Approach Section (Poster), Prediction Horizon Sweep (Poster Figure 5), System Architecture Flowchart (Poster Figure 6), TCN Predictive Control Result (72.1% vs 64.5% alignment), Validation Protocol (Poster Figure) (+12 more)

### Community 52 - "Community 52"
Cohesion: 0.15
Nodes (18): _bandpass_filter(), compute_multichannel_pac(), compute_sliding_pac_for_segment(), compute_sliding_pac_for_split(), compute_tort_mi(), find_contiguous_segments(), main(), Compute sliding-window PAC labels for all processed EEG windows.  Instead of the (+10 more)

### Community 53 - "Community 53"
Cohesion: 0.18
Nodes (18): build_multiscale_dataset(), _build_split_samples(), _causal_moving_average(), _causal_target_smooth(), _load_spectral_cache(), _load_split(), main(), _normalize_with_train_stats() (+10 more)

### Community 54 - "Community 54"
Cohesion: 0.12
Nodes (19): Core Claim: PAC Targeting 82.6% vs 51.7% Reactive, 91% of Oracle, Core Claim: Predictive Controller 72.1% vs Reactive 64.5% Alignment, Core Claim: TCN Maintains R²=0.25 at 5-10s Horizons Where Baselines Fail, Abstract Framing Strategy: Clinical Hook (Disease Impact First), Abstract Framing Strategy: Engineering-First (System Design Focus), Abstract Framing Strategy: Judge-Friendly (Biology Hook then AI), Rationale for Final Abstract Selection: Structure Analysis and Strengths, Abstract Draft 1: Clinical Hook Approach (+11 more)

### Community 55 - "Community 55"
Cohesion: 0.13
Nodes (19): 40 Hz Auditory Stimulation Therapy, 73 Causal Features (spectral + PAC-history + stim-context), Alignment Result: 72.1% (TCN) vs 64.5% (reactive), p<0.001, Alzheimer's Disease Motivation (55M affected, amyloid-β clearance), Closed-Loop Controller (PAC-forecast-driven stimulation), Fixed-Schedule Protocol Limitation (habituation ignored), Horizon Sweep: Baselines collapse at 5-10s, TCN R²≈0.25, Low-PAC Window Targeting: 82.6% vs 51.7%, 91% of Oracle (+11 more)

### Community 56 - "Community 56"
Cohesion: 0.25
Nodes (14): analyze_cross_epoch_transitions(), _corr(), _denorm(), evaluate_model(), get_device(), main(), persistence_baseline(), _r2() (+6 more)

### Community 57 - "Community 57"
Cohesion: 0.12
Nodes (11): AttentionModel, CNN1D, CNNAttentionHybrid, evaluate_model(), V7: Lightweight Deep Learning on Raw EEG  Different approach: Learn features dir, Multi-head attention over time points.      Learns which time points are importa, Hybrid: CNN extracts features, Attention pools them.      Combines local pattern, Train model with early stopping. (+3 more)

### Community 58 - "Community 58"
Cohesion: 0.13
Nodes (18): Build Multiscale Dataset Script (build_multiscale_dataset.py), Comprehensive Submission Audit Script (comprehensive_submission_audit.py), 73-Feature Multiscale Dataset (lookback=20, 73 features, train/val/test splits), Horizon Sweep Summary Table (TCN advantage at 5-10s horizons), Per-Subject Adaptation Script (per_subject_adaptation.py), Per-Subject Adaptation Results (TCN adapted vs persistence, 6 test subjects), NVIDIA GeForce RTX 3080 GPU (Training Hardware), Submission Audit Result (PASS - ablation: pac_only R2=0.8589, spectral_only R2=0.0551) (+10 more)

### Community 59 - "Community 59"
Cohesion: 0.14
Nodes (18): 12 PAC+Stim Features: PAC trajectory + stimulation context, Causal TCN with 12 PAC-Trajectory and Stimulation-Context Features, Paper Draft Status: All sections in draft, none reviewed or finalized, EEGNet Metric: 1,457 params, test R²=0.287 (static PAC ceiling), Feature Ablation: 73-feature R²=−0.025 vs 12 PAC+Stim R²=0.558, Figure: Controller Comparison v2 (results/figures/controller_comparison_v2.pdf), Figure: Horizon Sweep (results/figures/horizon_sweep.pdf), Figure: PAC Targeting Gap (results/figures/pac_targeting_gap.pdf) (+10 more)

### Community 60 - "Community 60"
Cohesion: 0.15
Nodes (18): Data Limitation as Performance Ceiling Rationale, DeepDilationTCN Hypothesis (Extended Receptive Field), MultiTaskTCN Hypothesis (Delta Head Regularization), Synthetic Benchmark Results (All Variants PASS), TCN Architecture Experiment Design, TransformerTCN Hypothesis (Self-Attention vs Fixed Dilation), WiderTCN Hypothesis (64-dim Bottleneck Limit), AttentionWeightCapture (Hook-Based Attention Weight Capture) (+10 more)

### Community 61 - "Community 61"
Cohesion: 0.14
Nodes (18): Alignment Metric (Average of Low-PAC Stim Rate and High-PAC Rest Rate), High-PAC Rest Rate Metric, Low-PAC Stimulation Rate Metric, Figure 12: Metric Definitions (Low-PAC Stim Rate & High-PAC Rest Rate), Subject Median PAC Threshold for Stimulation Decision, Figure 13: Controller Performance Comparison (N=35), Effect Size g=1.31 (TCN vs Reactive Alignment, p<0.001), Effect Size g=4.47 (TCN vs Reactive Low-PAC Stim Rate, p<0.001) (+10 more)

### Community 62 - "Community 62"
Cohesion: 0.17
Nodes (6): FixedSchedule, main(), Predictive, Alzheimer's Disease Simulation with TRIBE V2-Enhanced Closed-Loop Control  Demon, Reactive, run_trial()

### Community 63 - "Community 63"
Cohesion: 0.15
Nodes (16): add_body_block(), add_callout(), add_content_bg(), add_gradient_rect(), add_rect(), add_section_header(), add_text(), clear_slide() (+8 more)

### Community 64 - "Community 64"
Cohesion: 0.15
Nodes (17): Figure 7: Real-Data Controller Timeline — Sub-15 (Test Set), Actual PAC Signal Ground Truth (Sub-15 test set), Reactive Controller Stimulation Decisions (Sub-15), TCN Catches PAC Decline Early and Avoids Wasted Stimulation, TCN Predictive Controller Decisions (Sub-15, 5s ahead), 40Hz Audio Stimulation Output (STIMULATE / REST / MAINTAIN), Causal TCN (31K params, 20s lookback), Closed-Loop 40Hz Entrainment System Architecture Diagram (+9 more)

### Community 65 - "Community 65"
Cohesion: 0.27
Nodes (15): _dataset_base_4ch(), _dataset_base_7ch(), _dataset_dir(), _device(), _ensure_dataset(), main(), _n_features(), parse_args() (+7 more)

### Community 66 - "Community 66"
Cohesion: 0.22
Nodes (15): _controller_order(), fig_controller_comparison(), fig_pac_targeting_gap(), fig_per_subject_utility(), fig_stim_vs_alignment(), main(), Bar chart of (mean PAC during rest - mean PAC during stim) per controller., Scatter: Reactive utility (x) vs TCN utility (y), colored by split. (+7 more)

### Community 67 - "Community 67"
Cohesion: 0.18
Nodes (16): Abstract Archive (Historical CSEF Drafts), Superseded Implementation Archive, Audits Documentation Directory, Code Architecture Map, CSEF 2026 Submission Archive, Current Technical Methodology, Documentation Index, Consolidated Findings (FINDINGS.md) (+8 more)

### Community 68 - "Community 68"
Cohesion: 0.12
Nodes (16): Limitation: Dataset Size (N=35), Differentiators vs Prior Work, Framing A: Feature Selection > Architecture, Limitation: No Comparison to Prior Closed-Loop BCI Systems, Limitation: Offline Replay Not Live Closed-Loop, Open Questions Before Submission, Limitation: PAC Label Granularity (Epoch-Level), Framing B: Proactive vs Reactive Neurostimulation (+8 more)

### Community 69 - "Community 69"
Cohesion: 0.17
Nodes (16): 13-Page Project Presentation PDF (CSEF Requirement), CSEF Action Items and Preparation Checklist, AI / Generative AI Use Policy (ISEF-based), Awards Structure and ISEF Advancement Paths, Conduct and Disqualification Rules, California State Science Fair (CSEF), CSEF Consensus-Based Judging Process, Display Board Dimension and Content Rules (+8 more)

### Community 70 - "Community 70"
Cohesion: 0.19
Nodes (14): collapse_to_epochs(), fit_population_tau(), fit_subject_tau(), load_all_splits(), main(), print_results(), Fit simulator tau parameters from real PAC transition data.  Extracts tau_rise a, Fit tau_rise and tau_decay for a single subject at epoch level.      For consecu (+6 more)

### Community 71 - "Community 71"
Cohesion: 0.13
Nodes (15): PAC SNR=-4.73dB: Noise 3x Signal, Maximum Achievable R²~0.25-0.35, V1 Data Leakage: MI Features Used to Predict PAC (R²=0.69, Circular), Comprehensive Analysis: V1-V8 Model Attempt History for PAC Prediction, V5 Verdict: Ridge Regression R²=0.287 is Honest Ceiling for This Dataset, 8-Second Window Experiment: Autocorrelation r=0.45 But R²=0.125 (Failed Target), Key Insight: Temporal PAC Prediction Fails Without Stimulation Context, Architecture Decision: Causal Multiscale TCN + Stim Context Chosen Over LSTM/Transformer, Target Smoothing: Causal Denoised PAC State Achieves R²=0.75 vs Raw R²=0.07 (+7 more)

### Community 72 - "Community 72"
Cohesion: 0.16
Nodes (15): 12-Feature PAC+Stim Model (test R²=0.606), Causal Temporal Convolutional Network (TCN), Epoch Alignment Result (72.1% vs 64.5%, g=1.31), Fixed-Schedule 40Hz Auditory Entrainment Protocol, Horizon Sweep Result (R²=0.577–0.669 at 3–10s), Low-PAC Window Targeting (82.6% vs 51.7%, g=4.47), Key Methodological Finding: Feature Ablation, Neural Habituation / Fatigue Effect (+7 more)

### Community 73 - "Community 73"
Cohesion: 0.13
Nodes (15): Project Limitations: offline replay only, single dataset, short sessions (6-10 min), static PAC ceiling, heuristic thresholds, Active src/ Modules: data_loader, preprocessing, pac_computation, eegnet, training, controller, personalization, simulator, validation, utils, spectral_features, Feature Engineering Summary: raw EEG (1,7,500), spectral 61-dim, wavelet 74-dim, PAC features 116-dim (circular), multiscale 73-dim, Model Zoo: EEGNet R²=0.287, EEGNetV2 R²=0.06, SpecTempNet R²=0.236, ViT-TCNet R²=0.252, LSTM R²=−0.05, MultiscaleCausalTCN R²=0.74*, Architecture Timeline: Phase 1 (V1-V8 static, Feb 5-16), Phase 2 (temporal LSTM, Feb 16-17), Phase 3 (multiscale TCN, Feb 17), Closed-Loop Controller Design Slide: z-score thresholds ±0.5, 5s hysteresis, offline counterfactual replay validation, Discussion Slide: spectral features encode anatomy, 3s inflection = PAC autocorrelation timescale, single-site limitation, 73-Feature Breakdown: 61 spectral (28 band power + 7 theta/gamma ratio + 21 PAC-structure + 5 global) + 7 PAC-derived + 5 stim context (+7 more)

### Community 74 - "Community 74"
Cohesion: 0.29
Nodes (13): _ablation_tests(), _basic_integrity(), _corr(), _feature_group_indices(), _fit_ridge(), _load(), main(), parse_args() (+5 more)

### Community 75 - "Community 75"
Cohesion: 0.2
Nodes (13): add_body_text(), add_box(), add_callout_box(), add_content_bg(), add_section_header(), add_text_box(), Generate CSEF 2026 poster board PPTX — 24x32 inches (prints at 200% → 48x64)., Add a gold metric callout box. (+5 more)

### Community 76 - "Community 76"
Cohesion: 0.14
Nodes (14): Graph Attention Network (GAT) Spatial Processing Module, Hypothesis: GAT-Transformer Achieves R²>0.80 for PAC Prediction 5-10s Ahead, In Silico Closed-Loop Validation Methodology, Leave-One-Subject-Out Cross-Validation Strategy, Model Predictive Control (MPC) Framework for Stimulation Optimization, Proposed GAT-Transformer Architecture for EEG PAC Prediction, Temporal Transformer Encoder for EEG Sequence Modeling, 30% Non-Responder Problem: Inter-Individual Variability in 40Hz Entrainment (+6 more)

### Community 77 - "Community 77"
Cohesion: 0.19
Nodes (14): Architecture Search Comparison Figure (TODO), Controller Comparison Figure, Feature Ablation Bar Chart (TODO), Figure Style Guide, Paper Figures Source Directory, Generate Figures Script (generate_figures.py), Generate Timeline Figure Script (generate_timeline_figure.py), Horizon Sweep Figure (+6 more)

### Community 78 - "Community 78"
Cohesion: 0.19
Nodes (14): 72% Targeting Accuracy (d=1.31, p<0.001, N=35), Key Result: R² = 0.60 PAC Prediction 5s Ahead (5x improvement), NeuroCare 40Hz Facility Flyer Markdown Source, NeuroCare 40Hz Facility Flyer (Enhanced Layout), 4-Step Clinical Workflow: Wear EEG, Read Activity, Predict 5-10s Ahead, Stimulate, CSEF 2026 Presentation Context, How It Works: 4-Step Wear-Read-Predict-Stimulate Pipeline, Key Result: 72% Targeting Accuracy vs 64% Reactive Baseline (+6 more)

### Community 79 - "Community 79"
Cohesion: 0.18
Nodes (14): audit_multiscale_pipeline.py, build_multiscale_dataset.py, Causal Multiscale TCN Model, 1 Hz Closed-Loop Decision Loop, Delta PAC Target (PAC[t+h] - PAC[t]), Future PAC Target (Horizon h), Leakage-Safe Temporal Pipeline Design, Multiscale Input Features (Spectral + PAC History + Stimulation Context) (+6 more)

### Community 80 - "Community 80"
Cohesion: 0.23
Nodes (12): build_sliding_dataset(), _causal_moving_average(), main(), _pac_multiscale_features(), Build temporal dataset using sliding-window PAC labels.  Constructs 20-step look, Build temporal dataset with sliding-window PAC targets and features.      Return, Causal trailing average including the current sample., Causal PAC-derived features from past/current values only. (+4 more)

### Community 81 - "Community 81"
Cohesion: 0.36
Nodes (12): _corr(), _flatten(), load_test_by_subject(), main(), parse_args(), persistence_eval(), _r2(), ridge_global() (+4 more)

### Community 82 - "Community 82"
Cohesion: 0.23
Nodes (11): compute_pac_modulation_index(), compute_temporal_autocorrelation(), extract_spectral_features(), main(), process_subject(), Reprocess OpenNeuro ds005048 with longer PAC windows for temporal prediction., Process one subject with longer PAC windows.      Args:         subject_id: S, Compute PAC autocorrelation at various lags.      With 4-second hop size: (+3 more)

### Community 83 - "Community 83"
Cohesion: 0.3
Nodes (11): eval_classifier(), main(), majority_baseline(), make_direction_labels(), parse_args(), persistence_direction_baseline(), PAC direction classifier: 3-class prediction of future PAC change.  Classes:, Predict direction = 0 (STABLE) always — PAC doesn't change. (+3 more)

### Community 84 - "Community 84"
Cohesion: 0.26
Nodes (4): FixedScheduleControl, main(), PredictiveLookAheadControl, run_trial()

### Community 85 - "Community 85"
Cohesion: 0.23
Nodes (12): Adaptive Schedule (This Project) - 72% Alignment, Fixed Schedule (Current Approach) - 45% Alignment, Figure 1: Fixed vs. Adaptive Stimulation Scheduling Comparison, Missed Stimulation Opportunity (Fixed Schedule Waste), TCN Predicts Low-PAC Windows for Personalized Targeting, Gamma Oscillations (38-42 Hz) Amplitude Signal, High PAC = 40Hz Therapy is Working (Entrainment State), Figure 2: Phase-Amplitude Coupling (PAC) Mechanism Diagram (+4 more)

### Community 86 - "Community 86"
Cohesion: 0.23
Nodes (12): Alignment Metric (%) — TCN 72% vs Fixed 45%, g=1.31, p<0.001, Figure 8: Controller Comparison Bar Chart, Fixed Schedule Controller (Clinical Standard Baseline), High-PAC Rest Rate (%) — TCN 62% vs Fixed 29%, Hybrid TCN+Reactive Controller, Low-PAC Stimulation Rate (%) — TCN 83% vs Fixed 61%, g=4.47, p<0.001, Oracle Controller (Upper Bound, 100% All Metrics), PI Controller (+4 more)

### Community 87 - "Community 87"
Cohesion: 0.33
Nodes (9): check_chronology(), check_packaging(), check_preservation(), main(), parse_args(), read_text(), report(), run_selected_checks() (+1 more)

### Community 88 - "Community 88"
Cohesion: 0.33
Nodes (11): 12 PAC+Stim Features (pac_current, pac_ma*, pac_diff*, stim context), Controller Comparison (Fixed/Reactive/TCN/Hybrid/Oracle, N=35), OpenNeuro ds005048 Dataset (35 Subjects), Numbers Sheet (Old v1 Reference), EEGNet Stage 1 Static PAC Estimator (1,457 params, R²=0.287), Feature Ablation Results (73-feat: -0.025, 12-feat: 0.558), Horizon Sweep Results (TCN vs Persistence, 1–10s), Key Single Numbers (oracle 91%, 35/35 subjects, $250 hardware) (+3 more)

### Community 89 - "Community 89"
Cohesion: 0.18
Nodes (11): Horizon Sweep Central Finding, Project: Personalized DL for Closed-Loop 40Hz Entrainment, TCN Closed-Loop Validation Result (247-word Abstract), Core Finding: TCN Advantage at 5-10s Horizons, 91% of Theoretical Oracle Bound, Controller Comparison Table (Poster), Controller Comparison Results (N=35 Real EEG), Horizon Sweep Results Table (1-10s) (+3 more)

### Community 90 - "Community 90"
Cohesion: 0.36
Nodes (9): main(), parse_args(), persistence_baseline(), _r2(), Horizon sweep: evaluate persistence, Ridge and TCN baselines at multiple predict, Persistence baseline: predict future PAC = current PAC (last_pac)., Ridge regression on flattened feature sequences., ridge_baseline() (+1 more)

### Community 91 - "Community 91"
Cohesion: 0.31
Nodes (10): Audio Engine (40 Hz click-train via sounddevice), Closed-Loop 40Hz Entrainment Demo (Real EEG Replay), Fixed Schedule Controller (40s ON/20s OFF), Oracle Controller (perfect knowledge baseline), Predictive Look-Ahead Controller (trend+hysteresis), Reactive Threshold Controller (Z-score), RealtimePACForecaster (temporal_multiscale), StimAction Enum (STIMULATE/REST) (+2 more)

### Community 92 - "Community 92"
Cohesion: 0.31
Nodes (8): create_dataset(), create_temporal_features(), main(), Lightweight sklearn-based temporal PAC predictor for 8-second windows.  This v, Train Ridge and MLP models, evaluate on test set., Create flat feature vector from temporal sequence.      Args:         windows, Create temporal dataset for sklearn.      Returns:         X_train, y_train,, train_and_evaluate()

### Community 93 - "Community 93"
Cohesion: 0.31
Nodes (8): analyze_subject(), compute_within_epoch_variance(), lag1_autocorrelation(), main(), Diagnostic: compare epoch-level PAC vs per-window PAC.  For each subject, comput, Compute lag-1 autocorrelation of a 1D signal., Compute mean within-epoch variance of per-window PAC.      Windows sharing the s, Compute diagnostics for one subject.

### Community 94 - "Community 94"
Cohesion: 0.42
Nodes (8): _corr(), _denorm(), evaluate(), main(), _metrics(), parse_args(), _r2(), train_one_epoch()

### Community 95 - "Community 95"
Cohesion: 0.22
Nodes (9): P10 Research Log Notebook V1 (Daily Format), P10 Lab Notebook V1 (PDF), Approval-Era Chronology Anchor (Jan 15 as fair-facing start date), P10 Research Log Notebook V2 (Corrected Review Candidate), P10 Lab Notebook V2 (PDF render), P10 Research Log Notebook V3 Early (Jan 15 - Mar 1 2026), P10 Research Log Notebook V3 Early (PDF render), Research Notebook Enhancement Prompt (Formatting/Content Guidelines) (+1 more)

### Community 96 - "Community 96"
Cohesion: 0.31
Nodes (9): 4-Page + 1-Page References Format Constraint, Double-Blind Review Process, IEEE EMBC Conference, IEEEtran LaTeX Template, ICLR Workshop — Tier 1 Target, IEEE EMBC — Tier 1 Target, MIT URTC 2026 — Selected Primary Target, NeurIPS Workshop — Tier 1 Target (+1 more)

### Community 97 - "Community 97"
Cohesion: 0.46
Nodes (7): _corr(), _eval(), main(), parse_args(), print_summary(), _r2(), run_audit()

### Community 98 - "Community 98"
Cohesion: 0.46
Nodes (7): corr_score(), denorm(), evaluate(), main(), r2_score(), train_one_epoch(), train_subset()

### Community 99 - "Community 99"
Cohesion: 0.25
Nodes (8): h5py (>=3.8.0), Matplotlib (>=3.7.0), NumPy (>=1.24.0), PyWavelets (>=1.4.1), SciPy (>=1.10.0), PyTorch (>=2.0.0), tqdm (>=4.65.0), ViT-TCNet V4 Requirements

### Community 100 - "Community 100"
Cohesion: 0.5
Nodes (8): Audio Signal Generator (Adaptive): 40 Hz Audio Output to speaker, Causal TCN: 5,154 params, dilated causal convolutions (d=1,2,4,8), Closed-Loop Controller: STIMULATE/MAINTAIN/REST decision with 30s baseline, 3-sec hysteresis, EEGNet Block: 1,457 params, temporal + spatial convolutions, Feature Extraction: 12 features (spectral PAC features removed — encodes anatomy/dynamics), Raw EEG Input: Patient with EEG headset, 7 frontal channels, Simulation Update: <5s param TCN, Simul. PAC/EEG, Stim effects, Figure 5: System Architecture Flowchart — Complete Closed-Loop Pipeline

### Community 101 - "Community 101"
Cohesion: 0.38
Nodes (6): analyze_fatigue(), load_subject_pac_and_events(), main(), Habituation/fatigue analysis: does PAC decline across repeated stimulation block, Analyze habituation patterns across subjects., Load PAC values and align with BIDS events for each subject.

### Community 102 - "Community 102"
Cohesion: 0.48
Nodes (6): _finite_check(), _load_npz(), main(), parse_args(), Audit script for multiscale temporal dataset and training artifacts.  Checks: 1), run_audit()

### Community 103 - "Community 103"
Cohesion: 0.29
Nodes (7): archive/notebooks/P10_Lab_Notebook_V1.md (Original Notebook), submission/lab_notebook/generate_notebook_pdf.py, submission/lab_notebook/P10_Lab_Notebook_V3.md, check_chronology (Notebook Finalization Verifier), check_packaging (Notebook Finalization Verifier), check_preservation (Notebook Finalization Verifier), Verify Notebook Finalization Script

### Community 104 - "Community 104"
Cohesion: 0.33
Nodes (7): Clinical Roadmap (Phase A/B/C + Hardware Tiers), FDA Regulatory Pathway (De Novo Class II, 2026-2030 Timeline), Hardware Scaling Tiers (Muse 2 → OpenBCI → 64-ch Clinical), Clinical Testing Phases A, B, C (Observational to Comparative), Remote Monitoring Architecture (Cloud Dashboard + Clinician Portal), Product Framing 25/75 Research-Product Balance, Productization Roadmap (Muse 2 + Caregiver App + Pilot)

### Community 105 - "Community 105"
Cohesion: 0.47
Nodes (5): generate_image(), load_api_key(), main(), Load OpenRouter API key from ~/.claude/apis.env, Generate an image from a text prompt and save to output_path.

### Community 106 - "Community 106"
Cohesion: 0.4
Nodes (5): Generate Flyer PDF Script, main(), make_qr(), Generate QR Codes Script, submission/flyer/ (QR Code Output Directory)

### Community 107 - "Community 107"
Cohesion: 0.33
Nodes (6): Closed-Loop Demo Script (run_closed_loop_demo.py), Closed-Loop Strategy Comparison (Fixed/Reactive/Predictive/Oracle), Fixed Schedule Strategy (PAC=0.2299, stim=66.7%, eff=5.398), Oracle Strategy (PAC=0.2000, stim=49.1%, eff=6.108), Predictive Look-Ahead Strategy (PAC=0.1878, stim=52.1%, eff=5.302), Reactive Threshold Strategy (PAC=0.1361, stim=25.4%, eff=6.779)

### Community 108 - "Community 108"
Cohesion: 0.33
Nodes (6): Approval Form (1B) — Student Acknowledgment, Amaar Chughtai, Approval Form (1B) — Parent Approval, Irfan Chughtai, Final ISEF Affiliated Fair SRC Approval — Required, Pending Signature, SRC Ethics Statement (ISEF Rules), SCVSEFA Rule #2 — Scientific Fraud and Misconduct Prohibition, Ethics Statement Student Signature — Amaar Chughtai

### Community 109 - "Community 109"
Cohesion: 0.33
Nodes (6): Alzheimer Severity Profiles (Healthy, Mild AD, Severe AD), Citation: Soula et al. (2023) - 40Hz Light Doesn't Entrain Native Gamma in AD Mice, Citation: Meta AI (2026) - TRIBE V2 Brain Foundation Model, CorticalResponseConfig Biophysical Model (ASSR-calibrated), TRIBE V2 Integration Attempt and Biophysical Workaround (April 8, 2026), Wilson-Cowan Neural Mass Model (E/I dynamics for theta-gamma PAC)

### Community 110 - "Community 110"
Cohesion: 0.33
Nodes (6): CSEF 2026 Poster Board Blueprint (36x48 Cobalt Template), PowerPoint Box Dimensions Spec (24x32 → prints 48x64), Poster Builder v1 (python-pptx, 24x32 slide), Poster v1 (PDF, 24x32 layout), Poster Builder v2 (Cobalt Template, 36x48 slide), Poster v2 (PDF)

### Community 111 - "Community 111"
Cohesion: 0.33
Nodes (6): Body Language and Presentation Technique, Caucus Retellable Sentence, Five Judge Types (Warm, Cold, Skeptical, Expert, Confused), Judge Interaction Guide, Past CSEF/ISEF Winners Analysis and Strategy, Winner Narrative vs Report Framing Strategy

### Community 112 - "Community 112"
Cohesion: 0.33
Nodes (6): 5 Danger Zone Answers (AI Code, R2 Low, Simulation, N=35, vs Reactive), Final Q&A Bank and Danger Zones (FINAL_04, Archived), 40+ Q&A Bank (Technical, Process, Results, Creativity), Original Poster Presentation Script (v0, Synopsys Championship), Top 5 Danger Zone Questions (v0 Script), Poster Navigation Map (v0 Script, Full Panel Coordinates)

### Community 113 - "Community 113"
Cohesion: 0.33
Nodes (6): EEG Demo Video Recommendation with Annotations, Lab Notebook Advice: Consolidate with Dates, Place in Physical Folder, Kushal Khare Poster Feedback Meeting (March 4, 2026), Two Oral Presentation Versions (Simple and Technical), Poster Design Advice: Reduce Text, Enlarge Figures, Lab Notebook Requirements Guidelines (Rice University Standard Protocol)

### Community 114 - "Community 114"
Cohesion: 0.4
Nodes (3): kl_divergence_approx(), Pure NumPy Diagnostic - No dependencies except NumPy  Analyzes why V4 ViT-TCNet, Approximate KL divergence using histograms

### Community 115 - "Community 115"
Cohesion: 0.6
Nodes (4): main(), parse_args(), Small sweep utility for lookback/horizon settings.  Example:     python temporal, run_cmd()

### Community 116 - "Community 116"
Cohesion: 0.4
Nodes (5): Fatigue Model Sensitivity: 4 Mechanisms Compared, Fatigue Sensitivity Sweep (6 Levels, Adaptive vs Fixed), Real-Data Habituation / Fatigue Analysis (N=35), Rigorous Re-Evaluation: N=50 Trials, Bootstrap CIs, Hedges g, Closed-Loop Simulation: 4 Controller Strategies Compared

### Community 117 - "Community 117"
Cohesion: 0.4
Nodes (5): CSEF Display Prohibited Items (QR codes, handouts, AC power, school name), CSEF 2026 Day-of Logistics Checklist, Demo Items: Muse 2, Laptop, Poster (48x64 in), Judge Interaction Flow: Reading Engagement Signals, Muse 2 Product Demo Protocol (30-60 second booth demo)

### Community 118 - "Community 118"
Cohesion: 0.4
Nodes (5): Chan 2025 Cognito Therapeutics Phase II Trial, Glymphatic Clearance Pathway (40Hz Mechanism), Iaccarino 2016 Optogenetic 40Hz Stimulation, Microglial Activation Pathway (40Hz Mechanism), Iaccarino 2016 Landmark Study (40Hz Mice)

### Community 119 - "Community 119"
Cohesion: 0.5
Nodes (3): build_original_12feat(), Extract 12 PAC+Stim features from the existing 73-feature multiscale dataset to, Extract 12 PAC+Stim features and re-normalize from scratch.      This ensures th

### Community 120 - "Community 120"
Cohesion: 0.67
Nodes (3): generate_image(), main(), Generate an image using a chat-based image model on OpenRouter.

### Community 121 - "Community 121"
Cohesion: 0.83
Nodes (3): cell(), hdr(), main()

### Community 122 - "Community 122"
Cohesion: 0.5
Nodes (4): Lab Notebook Errata (Corrections to LAB_NOTEBOOK.md), Laboratory Research Notebook (Structured Study Format), P10 Research Notebook V1 (Research Paper Format), P10 Research Notebook V1 Paper Format (PDF render)

### Community 123 - "Community 123"
Cohesion: 0.5
Nodes (4): Horizon Sweep and Controller Integration (February 19, 2026), Horizon Sweep Results (TCN R2~0.25 at 5-10s, Baselines Collapse), Two-Stage EEGNet+TCN Controller Pipeline, Config YAML Hysteresis Bug Fix (3.0s vs 5.0s hold_time_sec)

### Community 124 - "Community 124"
Cohesion: 0.5
Nodes (4): Amyloid Cascade Hypothesis and 40Hz Mechanism (Iaccarino + Murdock pathways), FDA De Novo Classification Pathway for Novel Device, Glymphatic Clearance via AQP4/VIP Interneuron Pathway (Murdock 2024), Lecanemab vs 40Hz: Cost and Mechanism Comparison ($26,500/yr vs $250 one-time)

### Community 125 - "Community 125"
Cohesion: 0.5
Nodes (4): FixedScheduleControl (40s ON / 20s OFF Fixed Protocol), OracleControl (Perfect PAC Knowledge Upper Bound), ReactiveThresholdControl (Z-Score Rolling Baseline Controller), TCNPredictiveControl (Neural Network Look-Ahead Controller)

### Community 126 - "Community 126"
Cohesion: 1.0
Nodes (2): build_pdf(), main()

### Community 127 - "Community 127"
Cohesion: 0.67
Nodes (1): Generate Figure 8: Controller Comparison bar chart from real data.

### Community 128 - "Community 128"
Cohesion: 0.67
Nodes (1): Generate a standalone References Sheet PDF to bring to CSEF. Print this and keep

### Community 129 - "Community 129"
Cohesion: 0.67
Nodes (3): compute_pac_modulation_index (8-sec Window MI), process_subject (Per-Subject Long-Window Extractor), Rationale: 8-sec Windows for Temporal Structure (vs 2-sec R²=-0.05)

### Community 130 - "Community 130"
Cohesion: 0.67
Nodes (3): Key Literature Citations (Iaccarino, Martorell, Tort, Bai), Related Work Section Arc, Paper Tone Guidance (ML + Neuroscience Dual Audience)

### Community 131 - "Community 131"
Cohesion: 0.67
Nodes (3): Rationale: Empirical Tau Fitting for Simulator Defense (RSRCH-04), Simulator Tau Rise/Decay Parameters, src/simulator.py (EntrainmentSimulator)

### Community 132 - "Community 132"
Cohesion: 0.67
Nodes (3): Research Plan Bibliography: 5 References (Shakya 2026, Martorell 2019, Lahijanian 2024, Tort 2010, Yang 2025), Citation: Martorell et al. 2019 — Multi-sensory Gamma Stimulation Ameliorates AD Pathology (Cell), Citation: Tort et al. 2010 — Measuring Phase-Amplitude Coupling (J Neurophysiol)

### Community 133 - "Community 133"
Cohesion: 0.67
Nodes (3): Fatigue Sensitivity Results (+9-11% adaptive advantage, all fatigue models), Replay Framework and Robustness (February 21, 2026), Threshold Sensitivity Analysis (delta-z 0.1 to 1.0)

### Community 134 - "Community 134"
Cohesion: 0.67
Nodes (3): Achievement: TCN Only Useful Method at 5-10s Horizons (Persistence and Ridge collapse to negative R²), Horizon Sweep Table: PAC+Stim TCN R²=0.37-0.67 at 3-10s while persistence collapses, Figure: PAC Forecasting Performance vs Prediction Horizon — TCN maintains R²≈0.25 while Persistence and Ridge collapse below 0 at 5-10s

### Community 135 - "Community 135"
Cohesion: 0.67
Nodes (3): CSEF Final Poster (CSEF_FINAL.pdf): Complete CSEF 2026 submission poster, Personalized Deep Learning Model for Closed-Loop 40 Hz Entrainment (CSEF Poster v2), CSEF Poster vF2 Small (print-optimized version of CSEF final poster)

### Community 136 - "Community 136"
Cohesion: 0.67
Nodes (3): Hedges' g Effect Size, Statistical Analysis Framework, Wilcoxon Signed-Rank Test

### Community 137 - "Community 137"
Cohesion: 1.0
Nodes (1): Debug Data Leakage  Identify which features are causing R² = 0.9999 perfect pred

### Community 138 - "Community 138"
Cohesion: 1.0
Nodes (1): Generate system architecture figure v7 with correct specs using matplotlib.

### Community 139 - "Community 139"
Cohesion: 1.0
Nodes (0): 

### Community 140 - "Community 140"
Cohesion: 1.0
Nodes (2): Architecture Overview: Data Flow (CLAUDE.md), Repository Directory Structure

### Community 141 - "Community 141"
Cohesion: 1.0
Nodes (2): P10 Daily Research Notebook (v2 daily log draft), P10 Daily Research Notebook V2 (PDF render)

### Community 142 - "Community 142"
Cohesion: 1.0
Nodes (2): Status Report v1: Project Status Feb 2026 (Duplicate of v2), Status Report: Project ~45% Complete Toward Synopsys Submission (Feb 2026)

### Community 143 - "Community 143"
Cohesion: 1.0
Nodes (2): Multiscale Temporal Features (73 dims: 61 spectral + 7 PAC-derived + 5 stim context), Spectral Features (61 dims, src/spectral_features.py)

### Community 144 - "Community 144"
Cohesion: 1.0
Nodes (2): Transition Analysis Script (transition_analysis.py), Transition Analysis Results (transition vs steady-state windows)

### Community 145 - "Community 145"
Cohesion: 1.0
Nodes (2): PAC Direction Classifier Script (direction_classifier.py), PAC Direction Classifier Results (3-class: balanced acc Ridge=0.497)

### Community 146 - "Community 146"
Cohesion: 1.0
Nodes (2): Audit Multiscale Pipeline Script (audit_multiscale_pipeline.py), Pipeline Audit Result (PASS - no subject overlap, temporal causality valid)

### Community 147 - "Community 147"
Cohesion: 1.0
Nodes (2): Framing C: Horizon-Dependent Generalization in PAC Forecasting, Results Section Arc

### Community 148 - "Community 148"
Cohesion: 1.0
Nodes (2): Clinical Motivation: Alzheimer's Scale + No Cure, Introduction Section Arc

### Community 149 - "Community 149"
Cohesion: 1.0
Nodes (2): CSEF Old Repository Guidelines, Source-of-Truth Edit Workflow (Markdown → PDF)

### Community 150 - "Community 150"
Cohesion: 1.0
Nodes (2): Generate System Architecture v4 Script, Generate System Architecture v5 Script

### Community 151 - "Community 151"
Cohesion: 1.0
Nodes (2): Generate Paper LaTeX Script, submission/paper/RESEARCH_PAPER_v3.md

### Community 152 - "Community 152"
Cohesion: 1.0
Nodes (2): Media Release Parent Consent — Irfan Chughtai (granted permission), Photo/Video/Website/Media Release Form

### Community 153 - "Community 153"
Cohesion: 1.0
Nodes (2): Audit and Methodology Hardening (February 18, 2026), Habituation Pattern Analysis (17/35 habituators, 18/35 facilitators)

### Community 154 - "Community 154"
Cohesion: 1.0
Nodes (2): Synopsys Poster Final Flat (Text Extraction from PDF), Synopsys Poster Final (Print PDF)

### Community 155 - "Community 155"
Cohesion: 1.0
Nodes (2): CSEF Presentation Methods: Dataset breakdown (AD n=17, MCI n=6, controls n=10), preprocessing, PAC computation, Current Methodology Dataset: OpenNeuro ds005048, 35 subjects, BIDS HDF5/FDT format, 250Hz, 40s ON/20s OFF

### Community 156 - "Community 156"
Cohesion: 1.0
Nodes (2): Project Achievement Report Executive Summary, Project Summary Final (one-paragraph submission summary)

### Community 157 - "Community 157"
Cohesion: 1.0
Nodes (2): Danger Zone: AI Tools Disclosure (Claude/ChatGPT for assistance, all science decisions mine), Q&A Tier 4: Process and Independence Questions (SpecTempNet leakage discovery, AI tool disclosure)

### Community 158 - "Community 158"
Cohesion: 1.0
Nodes (2): Poster Figure Set (6 figures), Poster Board Layout (48x56 tri-fold)

### Community 159 - "Community 159"
Cohesion: 1.0
Nodes (1): Apply causal trailing mean within each subject block.          Causal (trailing)

### Community 160 - "Community 160"
Cohesion: 1.0
Nodes (0): 

### Community 161 - "Community 161"
Cohesion: 1.0
Nodes (0): 

### Community 162 - "Community 162"
Cohesion: 1.0
Nodes (0): 

### Community 163 - "Community 163"
Cohesion: 1.0
Nodes (1): Total number of output features: 8 * n_channels + 5.

### Community 164 - "Community 164"
Cohesion: 1.0
Nodes (1): Per-Subject Adaptation via Head Fine-Tuning

### Community 165 - "Community 165"
Cohesion: 1.0
Nodes (1): ML Libraries (scikit-learn, xgboost, optuna, captum)

### Community 166 - "Community 166"
Cohesion: 1.0
Nodes (1): BrainFlow Real-Time EEG Streaming Dependency

### Community 167 - "Community 167"
Cohesion: 1.0
Nodes (1): Temporal Legacy Package (Option B LSTM)

### Community 168 - "Community 168"
Cohesion: 1.0
Nodes (1): Technical Methods: EEG Signal Processing and Deep Learning

### Community 169 - "Community 169"
Cohesion: 1.0
Nodes (1): LSTM/GRU for EEG Temporal Sequence Modeling

### Community 170 - "Community 170"
Cohesion: 1.0
Nodes (1): Rationale: Spectral Features Cause Generalization Failure (CLAUDE.md finding)

### Community 171 - "Community 171"
Cohesion: 1.0
Nodes (1): PRNI — Pattern Recognition in NeuroImaging (Tier 2)

### Community 172 - "Community 172"
Cohesion: 1.0
Nodes (1): AIME — Artificial Intelligence in Medicine (Tier 2)

### Community 173 - "Community 173"
Cohesion: 1.0
Nodes (1): IEEE TNSRE Journal (Tier 2)

### Community 174 - "Community 174"
Cohesion: 1.0
Nodes (1): Paper Title Candidates

### Community 175 - "Community 175"
Cohesion: 1.0
Nodes (1): Methods Section Arc

### Community 176 - "Community 176"
Cohesion: 1.0
Nodes (1): Conclusion Section Arc

### Community 177 - "Community 177"
Cohesion: 1.0
Nodes (1): PaperPDF Class (fpdf2-based PDF generator)

### Community 178 - "Community 178"
Cohesion: 1.0
Nodes (1): CSEF PDF Class (12-page landscape generator)

### Community 179 - "Community 179"
Cohesion: 1.0
Nodes (1): Documentation Freeze and Synopsys Submission (March 1, 2026)

### Community 180 - "Community 180"
Cohesion: 1.0
Nodes (1): CSEF Preparation: File Reorganization and Outreach Flyer (March 24, 2026)

### Community 181 - "Community 181"
Cohesion: 1.0
Nodes (1): Poster V8 and Coherence Audit (April 7-8, 2026)

### Community 182 - "Community 182"
Cohesion: 1.0
Nodes (1): Paper Title: Personalized Deep Learning for Closed-Loop 40 Hz Entrainment

### Community 183 - "Community 183"
Cohesion: 1.0
Nodes (1): 4-Channel vs 7-Channel Comparison (Muse-Compatible)

### Community 184 - "Community 184"
Cohesion: 1.0
Nodes (1): Synopsys VFinal Poster (PDF)

### Community 185 - "Community 185"
Cohesion: 1.0
Nodes (1): Poster Board V5 (PDF Archive)

### Community 186 - "Community 186"
Cohesion: 1.0
Nodes (1): Synopsys VFinal Poster EDB (PDF)

### Community 187 - "Community 187"
Cohesion: 1.0
Nodes (1): Synopsys Poster Final EDB (PDF)

### Community 188 - "Community 188"
Cohesion: 1.0
Nodes (1): Poster Example (Reference PDF)

### Community 189 - "Community 189"
Cohesion: 1.0
Nodes (1): Poster Exports Slide1 Print PNG

### Community 190 - "Community 190"
Cohesion: 1.0
Nodes (1): CSEF 2026 Presentation: Research Question and Hypothesis (PAC forecasting 5-10s ahead)

### Community 191 - "Community 191"
Cohesion: 1.0
Nodes (1): Q&A Tier 1 Basic: Project overview, hypothesis, data, timeline (~4 months)

### Community 192 - "Community 192"
Cohesion: 1.0
Nodes (1): Q&A Tier 4 Process & Independence: progression from hypothesis to results, SpecTempNet leakage discovery, AI tool use disclosure

### Community 193 - "Community 193"
Cohesion: 1.0
Nodes (1): 4-5 Minute Full Presentation Script (v1 archive)

### Community 194 - "Community 194"
Cohesion: 1.0
Nodes (1): Competitive Advantages at CSEF (Individual, Real Data, Rigor)

### Community 195 - "Community 195"
Cohesion: 1.0
Nodes (1): Q&A Tier 1: Basic Judge Questions (project summary, hypothesis, data)

### Community 196 - "Community 196"
Cohesion: 1.0
Nodes (1): Honest Limitations: Low R2, Epoch Labels, Offline Replay, N=35, No Clinical Data

### Community 197 - "Community 197"
Cohesion: 1.0
Nodes (1): Adaptive Closed-Loop 40Hz Presentation Script (Slide-by-Slide)

### Community 198 - "Community 198"
Cohesion: 1.0
Nodes (1): LastStepPool (Last Timestep Pooling)

### Community 199 - "Community 199"
Cohesion: 1.0
Nodes (1): Per-Subject Circuit Utility (Poster Figure 8)

### Community 200 - "Community 200"
Cohesion: 1.0
Nodes (1): QR Code: Feedback Link (Submission Flyer)

### Community 201 - "Community 201"
Cohesion: 1.0
Nodes (1): CSEF Poster Compliance Checklist

### Community 202 - "Community 202"
Cohesion: 1.0
Nodes (1): Personal Motivation (Grandmother + Piano)

### Community 203 - "Community 203"
Cohesion: 1.0
Nodes (1): Alzheimer's Disease Global Scale ($300B, 55M patients)

### Community 204 - "Community 204"
Cohesion: 1.0
Nodes (1): improved_tcn Package

## Ambiguous Edges - Review These
- `Adaptive Schedule (This Project) - 72% Alignment` → `QR Code for App (Flyer)`  [AMBIGUOUS]
  submission/flyer/qr_app.png · relation: conceptually_related_to
- `QR Code for Feedback (Flyer)` → `Figure 8: Controller Comparison Bar Chart`  [AMBIGUOUS]
  archive/CSEF_Old/Flyer/qr_feedback.png · relation: semantically_similar_to

## Knowledge Gaps
- **1241 isolated node(s):** `Experimental ML research for improving temporal PAC prediction.  Approaches test`, `Residual causal depthwise-separable conv block.`, `Improved TCN with configurable width/depth and GELU activation.`, `Causal Transformer encoder for sequence-to-scalar regression.`, `TCN that predicts residual from persistence (last_pac).` (+1236 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 137`** (2 nodes): `debug_leakage.py`, `Debug Data Leakage  Identify which features are causing R² = 0.9999 perfect pred`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 138`** (2 nodes): `gen_arch_figure.py`, `Generate system architecture figure v7 with correct specs using matplotlib.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 139`** (2 nodes): `generate_closedloop_vs_fixed_v3.py`, `draw_stim_bar()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 140`** (2 nodes): `Architecture Overview: Data Flow (CLAUDE.md)`, `Repository Directory Structure`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 141`** (2 nodes): `P10 Daily Research Notebook (v2 daily log draft)`, `P10 Daily Research Notebook V2 (PDF render)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 142`** (2 nodes): `Status Report v1: Project Status Feb 2026 (Duplicate of v2)`, `Status Report: Project ~45% Complete Toward Synopsys Submission (Feb 2026)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 143`** (2 nodes): `Multiscale Temporal Features (73 dims: 61 spectral + 7 PAC-derived + 5 stim context)`, `Spectral Features (61 dims, src/spectral_features.py)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 144`** (2 nodes): `Transition Analysis Script (transition_analysis.py)`, `Transition Analysis Results (transition vs steady-state windows)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 145`** (2 nodes): `PAC Direction Classifier Script (direction_classifier.py)`, `PAC Direction Classifier Results (3-class: balanced acc Ridge=0.497)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 146`** (2 nodes): `Audit Multiscale Pipeline Script (audit_multiscale_pipeline.py)`, `Pipeline Audit Result (PASS - no subject overlap, temporal causality valid)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 147`** (2 nodes): `Framing C: Horizon-Dependent Generalization in PAC Forecasting`, `Results Section Arc`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 148`** (2 nodes): `Clinical Motivation: Alzheimer's Scale + No Cure`, `Introduction Section Arc`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 149`** (2 nodes): `CSEF Old Repository Guidelines`, `Source-of-Truth Edit Workflow (Markdown → PDF)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 150`** (2 nodes): `Generate System Architecture v4 Script`, `Generate System Architecture v5 Script`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 151`** (2 nodes): `Generate Paper LaTeX Script`, `submission/paper/RESEARCH_PAPER_v3.md`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 152`** (2 nodes): `Media Release Parent Consent — Irfan Chughtai (granted permission)`, `Photo/Video/Website/Media Release Form`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 153`** (2 nodes): `Audit and Methodology Hardening (February 18, 2026)`, `Habituation Pattern Analysis (17/35 habituators, 18/35 facilitators)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 154`** (2 nodes): `Synopsys Poster Final Flat (Text Extraction from PDF)`, `Synopsys Poster Final (Print PDF)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 155`** (2 nodes): `CSEF Presentation Methods: Dataset breakdown (AD n=17, MCI n=6, controls n=10), preprocessing, PAC computation`, `Current Methodology Dataset: OpenNeuro ds005048, 35 subjects, BIDS HDF5/FDT format, 250Hz, 40s ON/20s OFF`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 156`** (2 nodes): `Project Achievement Report Executive Summary`, `Project Summary Final (one-paragraph submission summary)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 157`** (2 nodes): `Danger Zone: AI Tools Disclosure (Claude/ChatGPT for assistance, all science decisions mine)`, `Q&A Tier 4: Process and Independence Questions (SpecTempNet leakage discovery, AI tool disclosure)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 158`** (2 nodes): `Poster Figure Set (6 figures)`, `Poster Board Layout (48x56 tri-fold)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 159`** (1 nodes): `Apply causal trailing mean within each subject block.          Causal (trailing)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 160`** (1 nodes): `generate_system_architecture_v5.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 161`** (1 nodes): `generate_system_architecture_v4.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 162`** (1 nodes): `create_research_notebook.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 163`** (1 nodes): `Total number of output features: 8 * n_channels + 5.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 164`** (1 nodes): `Per-Subject Adaptation via Head Fine-Tuning`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 165`** (1 nodes): `ML Libraries (scikit-learn, xgboost, optuna, captum)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 166`** (1 nodes): `BrainFlow Real-Time EEG Streaming Dependency`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 167`** (1 nodes): `Temporal Legacy Package (Option B LSTM)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 168`** (1 nodes): `Technical Methods: EEG Signal Processing and Deep Learning`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 169`** (1 nodes): `LSTM/GRU for EEG Temporal Sequence Modeling`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 170`** (1 nodes): `Rationale: Spectral Features Cause Generalization Failure (CLAUDE.md finding)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 171`** (1 nodes): `PRNI — Pattern Recognition in NeuroImaging (Tier 2)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 172`** (1 nodes): `AIME — Artificial Intelligence in Medicine (Tier 2)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 173`** (1 nodes): `IEEE TNSRE Journal (Tier 2)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 174`** (1 nodes): `Paper Title Candidates`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 175`** (1 nodes): `Methods Section Arc`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 176`** (1 nodes): `Conclusion Section Arc`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 177`** (1 nodes): `PaperPDF Class (fpdf2-based PDF generator)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 178`** (1 nodes): `CSEF PDF Class (12-page landscape generator)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 179`** (1 nodes): `Documentation Freeze and Synopsys Submission (March 1, 2026)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 180`** (1 nodes): `CSEF Preparation: File Reorganization and Outreach Flyer (March 24, 2026)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 181`** (1 nodes): `Poster V8 and Coherence Audit (April 7-8, 2026)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 182`** (1 nodes): `Paper Title: Personalized Deep Learning for Closed-Loop 40 Hz Entrainment`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 183`** (1 nodes): `4-Channel vs 7-Channel Comparison (Muse-Compatible)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 184`** (1 nodes): `Synopsys VFinal Poster (PDF)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 185`** (1 nodes): `Poster Board V5 (PDF Archive)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 186`** (1 nodes): `Synopsys VFinal Poster EDB (PDF)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 187`** (1 nodes): `Synopsys Poster Final EDB (PDF)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 188`** (1 nodes): `Poster Example (Reference PDF)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 189`** (1 nodes): `Poster Exports Slide1 Print PNG`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 190`** (1 nodes): `CSEF 2026 Presentation: Research Question and Hypothesis (PAC forecasting 5-10s ahead)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 191`** (1 nodes): `Q&A Tier 1 Basic: Project overview, hypothesis, data, timeline (~4 months)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 192`** (1 nodes): `Q&A Tier 4 Process & Independence: progression from hypothesis to results, SpecTempNet leakage discovery, AI tool use disclosure`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 193`** (1 nodes): `4-5 Minute Full Presentation Script (v1 archive)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 194`** (1 nodes): `Competitive Advantages at CSEF (Individual, Real Data, Rigor)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 195`** (1 nodes): `Q&A Tier 1: Basic Judge Questions (project summary, hypothesis, data)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 196`** (1 nodes): `Honest Limitations: Low R2, Epoch Labels, Offline Replay, N=35, No Clinical Data`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 197`** (1 nodes): `Adaptive Closed-Loop 40Hz Presentation Script (Slide-by-Slide)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 198`** (1 nodes): `LastStepPool (Last Timestep Pooling)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 199`** (1 nodes): `Per-Subject Circuit Utility (Poster Figure 8)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 200`** (1 nodes): `QR Code: Feedback Link (Submission Flyer)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 201`** (1 nodes): `CSEF Poster Compliance Checklist`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 202`** (1 nodes): `Personal Motivation (Grandmother + Piano)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 203`** (1 nodes): `Alzheimer's Disease Global Scale ($300B, 55M patients)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 204`** (1 nodes): `improved_tcn Package`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Adaptive Schedule (This Project) - 72% Alignment` and `QR Code for App (Flyer)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `QR Code for Feedback (Flyer)` and `Figure 8: Controller Comparison Bar Chart`?**
  _Edge tagged AMBIGUOUS (relation: semantically_similar_to) - confidence is low._
- **Why does `RealtimePACForecaster` connect `Closed-Loop Control & Simulator` to `Multiscale TCN & Features`, `Models, Streaming & Apps`?**
  _High betweenness centrality (0.084) - this node is a cross-community bridge._
- **Why does `MultiscaleCausalTCN` connect `Multiscale TCN & Features` to `Community 56`, `Closed-Loop Control & Simulator`, `12-Feature TCN Validation`?**
  _High betweenness centrality (0.054) - this node is a cross-community bridge._
- **Why does `ModelConfig` connect `Multiscale TCN & Features` to `Community 56`, `Closed-Loop Control & Simulator`, `12-Feature TCN Validation`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Are the 195 inferred relationships involving `StimAction` (e.g. with `FixedScheduleCtrl` and `ReactiveCtrl`) actually correct?**
  _`StimAction` has 195 INFERRED edges - model-reasoned connections that need verification._
- **Are the 133 inferred relationships involving `EntrainmentSimulator` (e.g. with `FixedScheduleControl` and `ReactiveThresholdControl`) actually correct?**
  _`EntrainmentSimulator` has 133 INFERRED edges - model-reasoned connections that need verification._