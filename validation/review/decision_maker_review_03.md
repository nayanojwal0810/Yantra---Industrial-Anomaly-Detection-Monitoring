# Decision-Maker Review: Modeling-Value Gate

**Decision: Reject the LBNL FCU dataset as the main candidate for the requested DL-centered project. Keep the reports and scripts as a documented validation record. Resume broad problem discovery.**

The pilot provided useful evidence for rejecting this particular dataset/task combination. It does not prove deep learning is generally ineffective; it shows that the single small CNN autoencoder tested here did not establish an advantage on the selected scenarios.

## What the pilot actually supports

The worker tested one normal-only Isolation Forest and one small 1D-CNN autoencoder against hand-written physical rules across five simulated FCU fault scenarios at 1-, 5-, and 15-minute sampling. The report's own 15-minute summary shows:

- Physical-rule detection rates: 100% on the cooling valve leak, about 35% on airside fouling and filter restriction, and below 1% on the sensor-bias and damper-leak scenarios.
- Isolation Forest: about 3% detection across scenarios, close to or below its reported normal false-alarm rate.
- The 1D-CNN autoencoder: 100% on the cooling valve leak, but below 1% on each of the other four scenarios.
- Thus the CNN has not shown a useful overall advantage on this candidate and benchmark.

These results should be described as **scenario-window flagging rates from a small pilot**, not as proof of production diagnostic performance. The scenario files encode one continuously simulated fault for an entire year; the 2,190 test windows within a scenario are temporally dependent and do not represent 2,190 independent faults or machines.

## Why we should stop investing in this candidate

1. **No demonstrated DL value-add:** The tested CNN probe did not outperform physical rules overall. The CNN was only trained for five epochs with a compact architecture, so this is not a proof against all deep models, but it is enough to say we have not justified making DL the main model here.
2. **Limited real-world diversity:** Official LBNL documentation describes a simulated fan-coil-unit system in one zone using HVACSIM+, one Des Moines weather year, 29 data points and 49 files representing 17 fault types at varying severities plus one fault-free case. This is valuable benchmark data, but it is not a collection of independent real buildings or field incidents: https://faultdetection.lbl.gov/dataset/simulated-fan-coil-unit-data-set/
3. **High prior-art overlap:** Seasonal HVAC fault generalization has been studied in a peer-reviewed 2023 paper: https://doi.org/10.1016/j.energy.2023.128180. A 2026 SSRN preprint also benchmarks HVAC fault models under downsampling and sensor degradation, including LBNL DataFDD: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7438633. We should not present seasonal holdouts, resampling, or MLOps packaging as genuine problem-level novelty.
4. **The remaining contribution is mainly engineering:** A robust data pipeline, API, tests, experiment tracking, and monitoring would be valuable, but those elements alone do not satisfy the goal of a standout ML/DL-focused project.

## Quality caveats in the pilot report

These do not reverse the decision, but any future use of the results must state them accurately:

- The code uses contiguous non-overlapping 60-minute windows, but does not actually drop a 60-minute embargo window at split boundaries as some report text claims. There is no window overlap, but a separate temporal gap was not implemented.
- The code reports the percentage of windows flagged within each fault scenario. It does not explicitly calculate a combined precision/recall confusion matrix, so claims of “100% precision/recall” should be narrowed to the measured 100% scenario detection rate.
- Each scenario shares the same timestamps and weather trajectory as the fault-free baseline. Treat these as paired counterfactual simulations, not independent real-world tests.
- The full 49-file Parquet footprint is extrapolated from a selected subset; it was not produced as a complete dataset in this gate.
- The single five-epoch CNN probe is an early feasibility test only. Do not claim that all DL architectures have been ruled out.

## Final disposition

- **Reject FCU as the principal dataset for the intended DL-centered project.**
- **Do not expand the FCU pilot or begin its production implementation.**
- Preserve the current reports, evidence and cleanup record as documentation of the candidate-rejection decision.
- Search for a better task/data pair where the problem structure gives deep learning a credible role beyond simple rules, while keeping classical ML comparisons, data volume, licenses, time, and free compute practical.

The next step is a rigorous, broader discovery screen across multiple domains and datasets. It should produce a ranked shortlist of two or three finalists with documented hard-stop risks. Do not select the final project or write the full implementation plan until that shortlist has been reviewed.

## Initial source leads for the next discovery round

These are starting points only, not approved candidates:

- Recent production telemetry: https://zenodo.org/records/21526135 — Multi-Block Vibration and Motor-Current Dataset from an Industrial Wire-Drawing Machine. The record reports 47,706 30-second records across three run-to-maintenance cycles and is only 10.2 MB, but the license, labels and independent-episode sufficiency need validation.
- Industrial robot telemetry: https://zenodo.org/records/17855686 — seven-axis robot joint-motion and energy telemetry, 269.2 MB archive. The Zenodo page's license field appears blank; treat that as a hard-stop risk until the data-use terms are verified.
- Composite power-quality disturbances: https://zenodo.org/records/22816322 — 100.9 MB of 10 kHz experimental signal data for 10 single/composite disturbance classes. Verify data license, independent recordings and prior-art saturation.
- Rotating machinery under changing conditions: https://mb.uni-paderborn.de/en/kat/research/bearing-datacenter/data-sets-and-download — high-resolution current and vibration data across operating conditions; non-commercial license restrictions and total data volume need consideration.
- MIMII DG industrial sound anomaly dataset: https://zenodo.org/records/6529888 — useful domain-shift framing, but 4.4 GB and CC BY-NC-SA 4.0; prior-art saturation and licensing are significant risks.
- Recent industrial power-quality monitoring: https://repository.londonmet.ac.uk/11442/ — a small train/test bundle from proprietary-source measurements; provenance, allowed use, labels and whether the minute-level data justify DL must be checked.

Do not simply choose the newest dataset. Establish whether its data and problem make a strong, feasible, defensible project.
