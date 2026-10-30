# Dataset Source and Licence Verification Report — Project Urja

**Task:** Task 1 — Original Dataset Verification & Data Integrity Audit  
**Date of Verification:** 2026-10-30  
**Verification Status:** VERIFIED (Licence Confirmed & Validated)

---

## 1. Executive Summary

This report establishes the provenance, bibliographic reference, repository metadata, and legal reuse terms for the dataset evaluated under **Project Urja**.

The investigation resolves the critical question of data licensing and portfolio usability:
- **Research Paper:** Published in the *Journal of Environmental Economics and Management* (JEEM), Elsevier, under **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)**.
- **Dataset Package:** Deposited in the official **Harvard Dataverse** repository (`doi:10.7910/DVN/4FLFRE`, Version 1.0) under **Creative Commons Zero 1.0 Universal Public Domain Dedication (CC0 1.0)**.

Because the underlying dataset and replication package are dedicated to the public domain under CC0 1.0, data audit, transformation, secondary research, and technical portfolio demonstration are fully permitted without restriction.

---

## 2. Research Paper Overview

- **Title:** Non-price energy conservation information and household energy consumption in a developing country: Evidence from an RCT
- **Authors:** 
  1. Ahsanuzzaman
  2. Shaikh Eskander (Universitat Autònoma de Barcelona & London School of Economics; ORCID: [0000-0002-3325-5486](https://orcid.org/0000-0002-3325-5486))
  3. Asad Islam (Centre for Development Economics and Sustainability, Monash University)
  4. Liang Choon Wang (Department of Economics, Monash University; ORCID: [0000-0001-5723-9053](https://orcid.org/0000-0001-5723-9053))
- **Journal:** *Journal of Environmental Economics and Management* (JEEM)
- **Publication Details:** Volume 127, September 2024, Article 103022
- **DOI:** [10.1016/j.jeem.2024.103022](https://doi.org/10.1016/j.jeem.2024.103022)
- **Publisher:** Elsevier Inc.
- **Paper Licence:** CC BY-NC 4.0 (Open Access)
  - Allows sharing and adapting the text, tables, and figures with appropriate credit, exclusively for non-commercial purposes.

---

## 3. Harvard Dataverse Dataset Record

- **Dataverse Repository:** Harvard Dataverse (`dataverse.harvard.edu`)
- **Dataset Title:** Replication Data for: Non-price energy conservation information and household energy consumption in a developing country: Evidence from an RCT
- **Persistent Identifier (PID):** `doi:10.7910/DVN/4FLFRE`
- **Dataset Landing Page:** [https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/4FLFRE](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/4FLFRE)
- **Dataverse Internal ID:** 11904926
- **Depositor:** Shaikh Eskander (Deposited: August 12, 2025; Released: August 13, 2025)
- **Contact:** Shaikh Eskander (`smsu_isku@hotmail.com`)
- **Dataset Version:** `1.0` (Version state: `RELEASED`)
- **Subject:** Social Sciences
- **Deposit Description:** "Data and code for replicating the results of the paper 'Non-price energy conservation information and household energy consumption in a developing country: Evidence from an RCT'."
- **Related Publication Link:** Formal relation `IsSupplementTo` linking to `https://www.sciencedirect.com/science/article/pii/S0095069624000962`

---

## 4. Licence and Terms of Use Analysis

### 4.1 Paper Licence vs. Dataset Licence Distinction

It is critical to distinguish between the intellectual property terms of the journal publication and the research dataset:

| Attribute | Journal Paper | Research Dataset Package |
|---|---|---|
| **Repository / Host** | ScienceDirect / Elsevier | Harvard Dataverse |
| **Identifier** | `doi:10.1016/j.jeem.2024.103022` | `doi:10.7910/DVN/4FLFRE` |
| **Governing Licence** | **CC BY-NC 4.0** | **CC0 1.0 Universal (Public Domain Dedication)** |
| **Commercial Use** | Prohibited without publisher license | Permitted under CC0 |
| **Modification / Derivation** | Permitted with attribution | Permitted without restriction |
| **Attribution Requirement** | Legally required by licence | Academic norm (not legally restricted) |
| **Redistribution of Data** | N/A (article PDF/text) | Unrestricted public domain dedication |

### 4.2 Exact Dataverse Metadata Licence Field

Retrieved directly via official Dataverse API (`https://dataverse.harvard.edu/api/datasets/:persistentId/?persistentId=doi:10.7910/DVN/4FLFRE`):

```json
"license": {
  "name": "CC0 1.0",
  "uri": "http://creativecommons.org/publicdomain/zero/1.0",
  "iconUri": "https://licensebuttons.net/p/zero/1.0/88x31.png",
  "rightsIdentifier": "CC0-1.0",
  "rightsIdentifierScheme": "SPDX",
  "schemeUri": "https://spdx.org/licenses/",
  "languageCode": "en"
},
"termsOfUse": null
```

### 4.3 Evaluation for Technical Portfolio and Public Use

- **Intended Purpose:** Independent audit, methodological validation, econometric replication, and technical demonstration.
- **Dataverse Terms:** CC0 1.0 waives all copyright and related rights in the dataset to the fullest extent allowed by law.
- **Portability Assessment:** The CC0 1.0 dedication explicitly permits copying, modifying, and analyzing the data for educational, research, and technical portfolio demonstrations.
- **Safeguard Rule:** Even though CC0 waives copyright, Project Urja maintains a strict policy: raw data files must never be committed to GitHub or redistributed beyond sanctioned project boundaries.

---

## 5. Verification Conclusion

- **Dataset Provenance:** Verified and authenticated against the Harvard Dataverse REST API.
- **Bibliographic Link:** Verified against Elsevier JEEM Volume 127 (2024).
- **Licence Status:** Formally confirmed as **CC0 1.0 Universal**.
- **Portfolio Reuse Permission:** **APPROVED** under CC0 1.0 public domain terms.
