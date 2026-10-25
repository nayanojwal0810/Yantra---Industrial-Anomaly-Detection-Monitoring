# Decision-Maker Review: Candidate Validation Findings

**Review status: Candidate B remains a conditional data candidate; the proposed problem framing is not approved yet.**

The validation work is substantial and the branch delivery was verified. However, several claims need correction, and the current novelty claim is not strong enough to authorize full project planning.

## What is accepted

- WDSEventDB is a poor fit for the intended DL-led project because the audited files represent only a small number of fault episodes on a single testbed. Its row count must not be mistaken for independent event diversity.
- HazardNet is not currently a clean choice for reproducible supervised hazard classification if the published target-label construction and needed artifacts cannot be recovered and verified.
- The LBNL/OpenEI FCU data are a credible candidate source for a controlled HVAC fault-detection study. The official source describes 17 fault types at varying severity levels, 49 CSV files, HVACSIM+ simulation, 29 data points, one year of operation, and one-minute sampling. The primary data descriptor is Granderson et al., Scientific Data 10, 342 (2023), DOI 10.1038/s41597-023-02197-w.

## Required corrections to the worker reports

1. **Correct the primary paper citation.** Several reports cite DOI 10.1038/s41597-023-02206-8 and article 344. The official paper is DOI 10.1038/s41597-023-02197-w, Scientific Data 10, article 342 (2023). Update every occurrence and verify all bibliographic entries.

2. **Do not call the 48 fault CSV files 48 independent fault modes.** The official FCU page describes 17 faults at varying severity levels. Use precise terms: fault type, severity-specific scenario/file, time-series rows, and independent equipment/site. The 48 fault scenario files are not 48 independent buildings, physical devices, or real-world field trials.

3. **Describe Candidate B labels accurately.** The FCU dataset is generated using HVACSIM+ simulation. Its labels are controlled simulation-scenario labels, not field-confirmed physical-fault ground truth. This dataset can support controlled benchmark claims, not a claim of validated real-building performance.

4. **Separate detection from diagnosis.** A model trained only on healthy data can score anomalies; by itself it cannot identify the fault's root cause. Training on other severities of a known fault and testing the minor severity measures severity generalization, not zero-shot discovery of an unseen fault type. Pick one main task and define exactly what the model sees at training, threshold selection, validation, and test time.

5. **Do not claim cross-season generalization is a new research gap.** Zhong, Calautit, and Wu (2023), “Fault data seasonal imbalance and insufficiency impacts on data-driven HVAC fault detection and diagnosis performances for energy-efficient building operations,” explicitly studies season coverage and unseen-season generalization (Energy, 282, 128180; DOI 10.1016/j.energy.2023.128180). A 2026 SSRN preprint titled “Explainable Robustness Assessment of Data-Driven HVAC Fault Detection under Noise, Drift, Bias, Missingness, and Downsampling” also reports an evaluation using LBNL DataFDD and a real AHU dataset. Treat it as a preprint, not peer-reviewed evidence, but include it in the up-to-date novelty check. The current Framing B.1 needs a clearly narrower, evidence-backed contribution or must be rejected as insufficiently differentiated.

6. **Treat a within-year seasonal split as a stress test, not broad deployment transfer.** The FCU dataset represents one simulated unit and one Des Moines weather year. A held-out-season test can reveal sensitivity to seasonal regimes in this simulation, but it does not establish generalization to new buildings, years, climates, or live field data.

7. **Do not present estimates as measured results.** The current reports state CPU training times, model runtime, compressed/processed sizes, and some operational cost estimates without a model run or a reproducible calculation. Mark these as estimates with assumptions, or remove them until measured and sourced. Do not claim that 15-minute aggregation preserves minor-fault signatures before testing it.

8. **Revisit the baseline claims.** Do not claim that ASHRAE Guideline 36 itself is an off-the-shelf FDD classifier. If rules are used, cite the exact publicly accessible rule and map it to the FCU points/control sequence. Do not choose LightGBM by default. The comparative model families should follow the final task definition.

9. **Correct the score confidence.** Candidate B should not receive 5/5 for dataset quality or 4/5 for independent sample sufficiency without noting that the dataset is simulated and tied to one FCU model/weather-year. Scoring must distinguish many time points and severity scenarios from independent physical systems and field episodes.

## Decision

**Do not start the end-to-end implementation plan yet.** Candidate B is retained for one focused feasibility-and-novelty gate. The current “Cross-Season Zero-Shot Nascent Fault Diagnostic” framing is not approved in its current form because it mixes detection with diagnosis and overstates the novelty of seasonal generalization.

The next review must answer:
- Can representative normal and low-severity CSVs be accessed and inspected without committing a large data archive?
- Do the actual file labels and scenario inventory support a clean task definition and honest grouping?
- How much does 1-, 5-, and 15-minute aggregation change the observable low-severity fault signatures?
- What specific project contribution remains after comparing with the 2023 seasonal-generalization paper and current 2026 preprint?
- Does the project still stand out as a practical portfolio system, or should we return to problem discovery and choose another candidate?

No model selection, final training, production code, or public-facing resume claims are approved at this point.

## Sources checked for this review

- Official LBNL FCU dataset page: https://faultdetection.lbl.gov/dataset/simulated-fan-coil-unit-data-set/
- Official LBNL FDD data portal: https://faultdetection.lbl.gov/data/
- OpenEI submission 5763: https://data.openei.org/submissions/5763
- Primary data descriptor: https://www.nature.com/articles/s41597-023-02197-w
- 2023 seasonal-insufficiency paper: https://doi.org/10.1016/j.energy.2023.128180
- 2026 robustness preprint (SSRN): https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7438633
