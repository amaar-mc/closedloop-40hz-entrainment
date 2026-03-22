---
phase: 15-deploy-and-finalize-qr-codes
plan: 01
subsystem: deployment
tags: [huggingface, qr-codes, google-forms, deployment]

requires:
  - phase: 13-caregiver-app-and-pilot-preparation
    provides: "Caregiver app code, flyer PDF, QR generation scripts"
provides:
  - "Live HF Spaces deployment at https://huggingface.co/spaces/amaarc/neurocare-40hz"
  - "Google Form for pilot feedback at https://forms.gle/NFkh2oWA1st3YrZT8"
  - "Real QR codes embedded in facility flyer PDF"

requirements-completed: [APP-05, PRES-02, PRES-04]
duration: manual
completed: 2026-03-22
---

# Phase 15 Plan 01: Deploy and Finalize QR Codes Summary

**Deployed caregiver app to HF Spaces, created Google Form, regenerated QR codes with real URLs, rebuilt facility flyer PDF**

## Accomplishments
- Deployed caregiver_app.py to HF Spaces (Docker + Streamlit) with brainflow-free numpy fallback adapter
- Created pilot feedback Google Form with 5 structured questions
- Regenerated QR codes with real deployed URLs
- Rebuilt facility flyer PDF with real QR codes
- Created docs/PILOT_LINKS.md documenting all live URLs

## Task Commits
1. **Task 1: Deploy + Create Form** — manual (HF Spaces + Google Forms)
2. **Task 2: QR + PDF regeneration** — `203853d` (feat)

## Deviations from Plan
- Deployed to HF Spaces instead of Streamlit Cloud (repo is private, Streamlit Cloud requires public)
- Required Dockerfile, requirements-deploy.txt, and brainflow-free adapter fallback for cloud deployment
- Multiple deploy iterations to fix: missing README config, brainflow import error, numpy 2.x np.trapz removal

## Self-Check: PASSED
All 3 requirements verified complete in REQUIREMENTS.md.
