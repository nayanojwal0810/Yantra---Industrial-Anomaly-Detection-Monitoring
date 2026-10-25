# Candidate Validation: Research Sources and Initial Hypotheses

This document is a source starting point, not a final literature review. Verify every item and claim during the audit.

## Candidate A — Water network event diagnosis

- WDSEventDB repository: https://github.com/Moazeni-s-Concise-Lab/WDSEventDB
- Repository data archive: https://github.com/Moazeni-s-Concise-Lab/WDSEventDB/blob/main/WDSEventDB.zip
- Main question: Can event categories (e.g. leak, cyber manipulation, sensor failure) be distinguished from multivariate sensor signals in a way that is useful beyond generic anomaly detection?
- Primary risks to investigate: number of independent events; scenario/run overlap; labels derived from setup or filenames; synthetic/testbed-only faults; class balance; whether cross-scenario tests are possible.
- Initial view: promising differentiation; dataset sufficiency remains unproven.

## Candidate B — HVAC fault diagnosis

- OpenEI / LBNL data collection: https://data.openei.org/submissions/5763
- Related research overview: https://pmc.ncbi.nlm.nih.gov/articles/PMC10235024/
- Main question: Can a model diagnose faults robustly across operating regimes, equipment instances, or data sources instead of merely classifying familiar examples from the same setup?
- Primary risks: source and license details by subset; dataset size; different files may have different schemas; synthetic versus lab versus field cases; split leakage; related work already using these benchmarks.
- Initial view: strong modeling and engineering potential; differentiation needs a precise evaluation setting.

## Candidate C — HPC thermal risk

- HazardNet dataset: https://zenodo.org/records/10050368
- Main question: Can thermal-risk predictions support earlier or better operational action beyond general temperature forecasting?
- Primary risks: large download; label definition and construction; event frequency; relationships between timestamps, nodes and target labels; whether decision outcomes can be evaluated from available measurements; related published framework.
- Initial view: relevant infrastructure problem; data and originality risks are elevated.

## Additional sources to seek

- Original papers linked from each official dataset page.
- Documentation and code repositories for the data-generation or preprocessing pipeline.
- Papers published after the original benchmark introducing relevant approaches.
- Replications, benchmark comparisons and evaluations across sites/devices/runs.
- Official data licenses and dataset version/change history.

## Evidence rules

- Prefer canonical data pages, primary research papers and original code.
- Record source publication date and access date.
- Cite a source next to the claim it supports in the research reports.
- A paper discussing a problem does not prove the data are suitable for this proposed project.
- A dataset's total row count does not prove independent sample sufficiency.
- Benchmark results should not be compared directly when evaluation protocols differ.
