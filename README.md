# NGO Compliance Verification System

An internship project developed in collaboration with the NITI Aayog Informatics Division, focused on building an AI-assisted decision-support system for NGO compliance verification.

The system is designed to help assess NGO registration and compliance documents against applicable state-specific and central legal requirements. Rather than acting as an automated authority, it supports structured review by extracting evidence from uploaded documents, retrieving relevant legal provisions, and generating an auditable compliance assessment.

## Project Overview

The current NGO Darpan ecosystem primarily verifies registration identity rather than validating the documentary evidence behind it. This creates a gap where registration documents may not be cross-checked against the legal framework that governs them. This project addresses that challenge by creating a local, evidence-based workflow for document review and compliance analysis.

## Problem Statement

NGOs often submit registration and compliance documents that are self-declared and not systematically validated against the laws applicable to their legal form and state of registration. This can lead to inconsistencies, missing legal clauses, and compliance issues that are discovered late in grant or regulatory processes.

The proposed system aims to reduce this risk by providing a structured review layer that:

- verifies uploaded documents against relevant laws and regulations,
- highlights missing or non-compliant clauses with supporting evidence,
- cites the legal provisions and document sources used in the assessment, and
- routes uncertain findings to human review for final judgment.

## Objectives

- Build a decision-support system for NGO compliance assessment.
- Cross-check registration documents against relevant state and central regulations.
- Support legal reasoning through retrieval and evidence-backed analysis.
- Provide a transparent workflow for human review and decision-making.
- Keep the system local-first and privacy-conscious.

## Scope

The initial implementation focuses on a limited set of states and core compliance dimensions, including:

- Registration and legal status
- Governance structure
- Membership requirements
- Financial compliance
- Tax compliance
- FCRA compliance
- Audit requirements

## System Architecture

The system is organized into three functional layers:

1. Knowledge Layer
   - Stores legal corpus content from state and central regulations.
   - Organizes legal text into retrievable sections for evidence-based reasoning.

2. Framework Layer
   - Defines compliance dimensions and review logic.
   - Keeps the assessment structure stable while allowing legal requirements to vary by state.

3. Assessment Layer
   - Processes uploaded documents, extracts structured information, retrieves relevant legal content, and generates a compliance assessment.
   - Produces findings with citations, evidence, and confidence-based routing for human review.

## Compliance Framework

| Dimension | Focus Area |
| --- | --- |
| Registration & Legal Status | Validity of registration, legal identity, and recognized status |
| Governance Structure | Board composition, trustee or office bearer structure, and governance requirements |
| Membership Requirements | Minimum membership and eligibility criteria as defined by law |
| Financial Compliance | Financial records, utilization, and financial reporting obligations |
| Tax Compliance | 12A/80G-related compliance and tax exemption requirements |
| FCRA Compliance | Registration, designated account, and reporting obligations |
| Audit Requirements | Audit-related compliance and documentation requirements |

## Tech Stack

| Layer | Technology | Purpose |
| --- | --- | --- |
| Frontend | Next.js | User interface and application experience |
| Frontend Styling | Tailwind CSS | Responsive interface design |
| Backend | FastAPI | API services and application logic |
| Document Processing | PyMuPDF, Tesseract | OCR and text extraction from uploaded documents |
| Vector Search | ChromaDB | Retrieval of relevant legal content |
| Language Model | Ollama | Local reasoning and analysis support |
| Database | PostgreSQL | Structured storage for application and review data |

## Project Structure

```text
NGO-compliance/
├── ngo-compliance-frontend/     # Next.js-based user interface
├── ngo-compliance-backend/      # FastAPI-based backend services
├── compliance-dimensions-card.jsx
├── ngo-compliance-prototype.jsx
└── README.md
```

## Data Sources

The legal corpus is sourced from official government and regulatory materials, including:

- India Code
- State government legal portals and registrars
- FCRA online resources
- Income Tax Department guidance
- NGO Darpan guidelines and compliance materials

## Getting Started

### Frontend

```bash
cd ngo-compliance-frontend
npm install
npm run dev
```

The frontend will be available at http://localhost:3000.

### Backend

```bash
cd ngo-compliance-backend
pip install -r requirements.txt
```

The backend services are intended to be run locally as the application logic is completed and integrated.

## Project Status

This repository contains the initial structure and interface for an internship project focused on NGO compliance verification using AI-assisted review workflows. The work is centered on building an auditable, evidence-based compliance system for legal and regulatory assessment.
