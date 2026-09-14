# Content Opportunity Scoring

## FlyRank ML Internship Capstone

**Applied Search Intelligence: Google Search Ranking & Discoverability**

A leakage-aware machine learning workflow for prioritising content that may need human review for declining search performance.

Built during the FlyRank ML Internship.

---

## Project Overview

Content teams often manage thousands of pages, making it difficult to manually identify which pages deserve attention first.

This project investigates:

> **Can a leakage-aware machine learning model provide a useful directional signal for prioritising content that may need review for declining performance?**

The goal is not to automatically modify content or predict Google's algorithm.

Instead, this project builds a:

**human-in-the-loop decision-support system**

that helps answer:

> **Which pages should a reviewer investigate first?**

---

## Final Result

The final model was evaluated using a leakage-aware workflow and a client-grouped holdout validation strategy.

### Model Performance

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC | Average Precision |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Majority Baseline | 0.391 | 0.391 | 1.000 | 0.562 | 0.500 | 0.391 |
| Random Forest | **0.769** | **0.642** | **0.924** | **0.758** | **0.874** | **0.752** |

### Interpretation

The Random Forest model produced stronger ranking and classification performance than the simple baseline on the evaluated holdout.

The result supports the following conclusion:

> **The evaluated feature set contains useful directional signal for prioritising content review.**

The model does **not** claim:

- Google's ranking algorithm was discovered.
- Content changes will definitely improve traffic.
- Predictions represent causal SEO impact.
- Automatic content decisions should be made.

The output is strictly:

**Observed → Measured → Directional → Decision-support**

---

## Project Architecture

```text
FlyRank Dataset
       |
       v
Data Validation
       |
       v
Label Construction
       |
       v
Leakage-Aware Feature Selection
       |
       v
Client Grouped Validation
       |
       v
Machine Learning Model
       |
       v
Baseline Comparison
       |
       v
Evaluation
       |
       v
Ranked Review Recommendations
       |
       v
Human Content Decision
```

---

## Dataset

This project uses the public-safe FlyRank ML Internship content-refresh dataset.

### Dataset Characteristics

- 30,000 content rows
- 32 clients
- Declining-content classification task
- Anonymized search performance information

### Public-Safety Boundary

The repository does not contain:

- Client names
- Private domains
- Private queries
- Credentials
- Private exports
- Confidential business information

---

## Machine Learning Problem

### Target

The classification target is:

```text
is_declining_label = 1
when trend_direction == "down"
```

The model predicts whether content belongs to the declining performance class.

---

## Data Preparation

The workflow applies:

- Missing-data checks
- Duplicate removal
- Content maturity filtering
- Label creation
- Feature selection
- Validation preparation

Rows are filtered to focus on established content rather than newly created pages.

---

## Leakage Prevention

A major engineering decision was creating a conservative feature boundary.

The model avoids using:

- Direct label fields
- Future-looking information
- Overlapping outcome-window metrics

### Excluded Examples

```text
trend_direction
trend_pct
current performance aggregates
current outcome indicators
```

The final model focuses on safer pre-outcome information:

- Content age
- Update history
- Previous performance signals
- Search/context variables
- Content attributes
- Categorical features

---

## Model Choice

The final model uses:

### Random Forest Classifier

Reasons:

- Handles structured tabular data well
- Captures nonlinear relationships
- Requires limited preprocessing
- Provides useful ranking probabilities
- Works well for decision-support workflows

---

## Validation Strategy

The evaluation uses:

### Client-Grouped Holdout Validation

Instead of randomly splitting rows, entire clients are held out.

Example:

**Training**

```text
Client A
Client B
Client C
```

**Testing**

```text
Client X
Client Y
Client Z
```

This creates a more realistic generalisation test.

The question becomes:

> **Can the model identify useful patterns on clients it has not seen before?**

---

## Repository Structure

```text
ml-engineering-playground/
│
├── data/
│   └── raw/
│       └── content_refresh_anonymized.csv
│
├── docs/
│   └── ...
│
├── scripts/
│   ├── 01_prepare_features.py
│   ├── 02_baseline_score.py
│   ├── 03_train_model.py
│   ├── 04_evaluate_and_export.py
│   ├── 05_build_pdf_report.py
│   └── run_all.py
│
├── work/
│   ├── notebooks/
│   │   ├── w01_research_question.ipynb
│   │   ├── w02_ml_task_framing.ipynb
│   │   ├── w03_data_contract.ipynb
│   │   ├── w03_feature_leakage_check.ipynb
│   │   ├── w04_signal_audit.ipynb
│   │   ├── w04_baseline_score.ipynb
│   │   ├── w05_model.ipynb
│   │   ├── w06_validation_audit.ipynb
│   │   ├── w07_action_playbook.ipynb
│   │   └── capstone.ipynb
│   │
│   ├── figures/
│   ├── outputs/
│   └── README.md
│
├── docs/
│   └── index.html
│
├── submission/
│   └── paper_url.txt
│
└── README.md
```

> **Note:** The structure above preserves the repository layout supplied in the original project README, including the existing `docs/` entries.

---

## Setup

### Option A — Google Colab

The easiest way to reproduce the capstone is Google Colab.

Open:

**Capstone notebook**

Then:

1. Open the notebook.
2. Run the cells from top to bottom.
3. Allow the notebook to clone the public repository when prompted.
4. Confirm the dataset is loaded.
5. Review the data-quality checks.
6. Review the model and validation outputs.
7. Review the final evaluation table.
8. Save the executed notebook if you want to preserve the run.

The notebook contains the complete capstone workflow.

### Option B — Local Environment

Clone the repository:

```bash
git clone https://github.com/smaharx/ml-engineering-playground.git
cd ml-engineering-playground
```

Create an environment:

```bash
python -m venv .venv
```

Activate it on Linux/macOS:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

The repository also contains the reference pipeline:

```bash
python scripts/run_all.py
```

For the final capstone methodology and leakage-aware evaluation, use:

```text
work/notebooks/capstone.ipynb
```

because that notebook contains the final research framing and validation choices.

---

## Reproducing the Final Evaluation

The final capstone notebook performs the following sequence:

1. Load the anonymized dataset
2. Validate required columns
3. Construct the declining label
4. Remove insufficient/improper rows
5. Remove duplicate content IDs
6. Define the conservative feature set
7. Create a client-grouped holdout
8. Train the Random Forest
9. Generate the majority baseline
10. Evaluate both systems
11. Compare the metrics
12. Inspect model behaviour
13. Produce decision-support outputs

---

## Decision-Support Interpretation

A high model score means:

> This page looks more similar to pages associated with the declining class under the evaluated feature boundary.

It does **not** mean:

> This page definitely needs a content refresh.

The recommended workflow is therefore:

```text
High decline signal
        ↓
Human investigation
        ↓
Check content freshness
        ↓
Check search intent / relevance
        ↓
Check recent performance context
        ↓
Choose an appropriate action
```

Possible human-review outcomes include:

- Refresh review
- Performance investigation
- Continued monitoring
- No action after contextual review

---

## Limitations

This project has important limitations.

### 1. Historical Evaluation

The evaluation is performed on historical data. Strong holdout performance does not guarantee identical performance on future data.

### 2. Temporal-Overlap Risk

The original modelling workflow contained fields that could overlap the outcome window. The final capstone uses a more conservative feature boundary to reduce this risk, but this should not be described as a formal proof of leakage-free production deployment.

### 3. Client Distribution

The dataset is a bounded internship dataset. A client-grouped holdout improves the generalisation test, but it does not establish universal performance across all websites, industries, countries, or search environments.

### 4. Directional Label

The declining label represents an observed directional performance state. It does not establish why performance changed.

### 5. No Causal Claim

The model does not establish that updating content causes rankings or traffic to improve.

### 6. Human Review Remains Necessary

A model score cannot understand every content, business, brand, search-intent, or editorial constraint.

### 7. Production Deployment Is Not Demonstrated

This repository demonstrates an evaluated research workflow. It is not presented as a production-grade autonomous content optimisation system.

---

## Public-Safety Boundary

This repository is intentionally public-safe.

Do not add:

- Client names
- Private domains
- Private search queries
- Credentials
- Private exports
- Proprietary screenshots
- Other identifying information

Results should be described as:

- Observed
- Measured
- Directional
- Decision-support

Avoid claims such as:

> "The model predicts Google's algorithm."

Prefer:

> "The model provides a directional signal for prioritising content review."

---

## Research Paper

The final research paper is deployed through GitHub Pages:

https://smaharx.github.io/ml-engineering-playground/

The paper presents:

- The research question
- Data definition
- Methodology
- Leakage considerations
- Evaluation results
- Limitations
- Ranked recommendations
- Reproducibility notes
- Data acknowledgement

The exact paper URL is also stored in:

```text
submission/paper_url.txt
```

---

## Demo

### Live Demo

**Demo link:** `ADD_YOUR_DEMO_LINK_HERE`

The demo is designed to be 3–5 minutes and shows the real project rather than slides.

### Demo Flow

1. Show the project goal
2. Show the repository structure
3. Open the capstone notebook
4. Show the data and label construction
5. Show the leakage-aware feature boundary
6. Show the client-grouped validation
7. Show model vs. baseline results
8. Explain one design decision
9. Explain one limitation
10. Close with the decision-support use case

---

## One Important Design Decision

### Why Use a Client-Grouped Holdout?

The same client can have many content rows.

A random row split could therefore place very similar client-specific patterns in both training and test data.

Grouping by client creates a harder evaluation:

> **Can the model generalise to clients that were not used during training?**

That better matches the intended generalisation question.

---

## One Important Limitation

The strongest limitation is temporal validity.

Even though the final feature boundary is more conservative than the earlier Week-5 feature set, the historical evaluation cannot prove that the same metrics will hold on future traffic or future content.

The honest interpretation is therefore:

> **The model shows useful signal on the evaluated holdout; it is not proof of future production performance.**

---

## Where AI Helped

An honest description of AI assistance:

> AI helped accelerate implementation, debugging, documentation, and iteration, but the project decisions, validation boundaries, interpretation of results, and final claims were reviewed and owned by me.

AI assistance was used as a development and reasoning aid, not as a substitute for evaluating the model or deciding what the results mean.

---

## Project Deliverables

| Deliverable | Location |
| --- | --- |
| Research notebooks | `work/notebooks/` |
| Final capstone | `work/notebooks/capstone.ipynb` |
| Research paper | `docs/index.html` |
| Paper URL | `submission/paper_url.txt` |
| Evaluation outputs | `work/outputs/` |
| Figures | `work/figures/` |
| Project documentation | `README.md` |

---

## Final Takeaway

The main result of this project is not simply a high model score.

The important engineering lesson is the workflow:

```text
Frame the question
      ↓
Define the decision
      ↓
Protect against leakage
      ↓
Choose a defensible validation design
      ↓
Compare against a simple baseline
      ↓
Measure honestly
      ↓
Translate predictions into human-review priorities
      ↓
State limitations clearly
```

The Random Forest achieved **0.874 ROC-AUC** and **0.752 Average Precision** on the evaluated client-grouped holdout, compared with **0.500 ROC-AUC** and **0.391 Average Precision** for the majority baseline.

The appropriate conclusion is therefore:

> **The evaluated feature set contains useful directional signal for prioritising content review, while future performance, causality, and production generalisation remain unproven.**

---

## Credits

Built during the FlyRank AI/ML Internship.

Public-safe project developed using the FlyRank internship dataset and workflow.

**FlyRank:** https://flyrank.ai/

**Research paper:** https://smaharx.github.io/ml-engineering-playground/

---

## Important

There is **one intentional placeholder**:

```text
ADD_YOUR_DEMO_LINK_HERE
```

Do not invent a demo URL. Replace it after recording the demo.
