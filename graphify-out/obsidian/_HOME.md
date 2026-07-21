---
type: map-of-content
title: Repository Knowledge Map
nodes: 4465
edges: 7906
communities: 205
tags:
---

# 🧠 Closed-Loop 40 Hz Entrainment — Repository Knowledge Map

Navigable map of the whole repository as a knowledge graph. **4,465 nodes · 7,906 edges · 205 communities.** Open **[[graph.canvas]]** for the visual layout, or use Obsidian's Graph View (nodes are colored by community).

This map links the 30 largest, named communities. The remaining ~175 micro-communities are reachable through the Graph View and through `#community/...` tags.

---

## 🔬 Active Research System

The live pipeline: raw EEG → PAC → temporal forecasting → closed-loop control.

- [[_COMMUNITY_Core Data & PAC Pipeline]] — preprocessing, PAC computation, dataset/trainer (`src/`)
- [[_COMMUNITY_Multiscale TCN & Features]] — `MultiscaleCausalTCN`, feature extraction, dataset builder
- [[_COMMUNITY_TCN Layer Internals]] — causal conv blocks, attention pooling, regression heads
- [[_COMMUNITY_12-Feature TCN Validation]] — the production 12-feature model + controllers
- [[_COMMUNITY_Closed-Loop Control & Simulator]] — `ClosedLoopController`, `EntrainmentSimulator`, `RealtimePACForecaster`
- [[_COMMUNITY_Control Strategies & Validation]] — Fixed / Reactive / Predictive / Oracle controllers
- [[_COMMUNITY_Models, Streaming & Apps]] — `EEGNet`, streaming features, model registry, Streamlit apps

## 🧬 Biophysical Simulators

- [[_COMMUNITY_TRIBE Neural-Mass Simulator]] — Wilson–Cowan / cortical response / Alzheimer profiles
- [[_COMMUNITY_TVB Alzheimer Simulator]] — TVB-based disease-severity simulation
- [[_COMMUNITY_TRIBE-TCN Validation]] — TCN trained/validated against TRIBE simulator

## 📊 Results & Analysis

- [[_COMMUNITY_Controller Results & Judge Prep]] — controller comparison tables, judge interview prep
- [[_COMMUNITY_Rigor Audit Reports]] — leakage audit, feature ablation, robustness verdicts
- [[_COMMUNITY_Replay Analysis & Controllers]] — offline replay on real EEG
- [[_COMMUNITY_Model Ceiling & Leakage Audits]] — R²≈0.29 ceiling, MI-leakage detection

## 📄 Paper & Documentation

- [[_COMMUNITY_Research Paper & Manuscript]] — full manuscript, design-decision rationale
- [[_COMMUNITY_Literature Review & Methodology Docs]] — lit review, bibliography, methodology
- [[_COMMUNITY_Presentation Scripts & Citations]] — talk scripts + core citations

## 🖼️ CSEF 2026 Submission Artifacts

- [[_COMMUNITY_Poster Boards & Figures]] — poster board versions + figures
- [[_COMMUNITY_PaperPresentation PDF Builders]] — paper/presentation PDF generators
- [[_COMMUNITY_CSEF Presentation Generator]] — CSEF pptx generation
- [[_COMMUNITY_PPTX Slide Builder]] — slide builder utilities
- [[_COMMUNITY_Lab Notebook PDF Generation]] — lab notebook → PDF

## 🗄️ Archive (superseded experiments)

- [[_COMMUNITY_Archived Feature Experiments (v4)]] — wavelet/spectral/PAC feature experiments
- [[_COMMUNITY_Archived ImprovedTCN Experiments]] — ImprovedTCN runs
- [[_COMMUNITY_Archived Enhanced-Feature TCN]] — enhanced-feature TCN
- [[_COMMUNITY_Archived Temporal PAC Predictor]] — LSTM-era temporal predictor
- [[_COMMUNITY_Generalization-Gap Experiments]] — spectral-feature generalization failure study
- [[_COMMUNITY_Archived EEGNet V2]] — EEGNet v2 line
- [[_COMMUNITY_Archived SpecTempNet V3]] — SpecTempNet 3-branch
- [[_COMMUNITY_Archived CSEF Paper & Abstract]] — older CSEF paper/abstract

---

## ⭐ Core Abstractions (God Nodes — highest connectivity)

Best single-node entry points into the system.

- [[StimAction]] (197 edges) · [[EntrainmentSimulator]] (142) · [[FatigueAwareSimulator]] (142)
- [[MultiscaleCausalTCN]] (141) · [[ModelConfig]] (136) · [[RealtimePACForecaster]] (118)
- [[EEGNet]] (97) · [[SpectralFeatureExtractor]] (59) · [[ClosedLoopController]] (50) · [[StreamingFeatureExtractor]] (47)

> **`RealtimePACForecaster`** is the highest-betweenness bridge in the graph — the seam where the forecasting model plugs into the live closed-loop controller. Start there to understand integration.
