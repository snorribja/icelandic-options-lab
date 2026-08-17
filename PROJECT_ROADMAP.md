# Icelandic Options Lab — Quant Internship Project Roadmap

## Goal

Turn this repository into a project that demonstrates the skills a quantitative
trading or research recruiter can evaluate quickly:

- mathematical correctness;
- probability, statistics, and experiment design;
- strong Python and numerical programming;
- realistic treatment of market frictions and model limitations;
- reproducible results; and
- precise written communication.

The objective is not to collect the largest number of pricing models. One
well-tested research result is more valuable than ten partially implemented
features.

## Grading scale

Grades measure **expected recruiting value relative to implementation effort for
this repository**.

| Grade | Meaning |
|---|---|
| A+ | Core project-defining work; do before applying or showcasing the project |
| A | Very high value; should be part of the finished project |
| A- | Strong extension after the core result works |
| B | Useful differentiator, but only after the core project is complete |
| C | Technically respectable but weak marginal CV value right now |
| D | Likely distraction or unnecessary infrastructure |
| F | Avoid; it would weaken the project's focus or credibility |

## Executive recommendation

The best version of this project is:

> **Discrete Delta Hedging in an Illiquid Market: The Trade-off Between Hedging
> Error and Transaction Costs**

Build a vectorized Monte Carlo engine, validate it against analytical results,
and use it to test this hypothesis:

> More frequent hedging reduces replication error when trading is free, but
> proportional transaction costs create an optimal finite hedging frequency.

Use Icelandic equities to estimate plausible inputs, state clearly where market
data are unavailable, publish the result in the dashboard, and write a concise
research note. This gives the project a question, method, evidence, result, and
limitations—not merely a collection of calculators.

## Current repository gaps to close first

- The Monte Carlo dashboard currently has controls and renderers but no engine
  output connected to it.
- The Research Lab contains five good experiment designs, but all five still use
  placeholder results.
- `scripts/historical_option_example.py` samples one historical period; it is not yet a
  batch Monte Carlo simulator.
- The historical delta-hedging engine does not yet apply transaction costs.
- Dividend yield is unsupported.
- There is no committed README, focused mathematical test suite, or reproducible
  research report.
- Unfinished pages labelled "Awaiting engine" should not appear in the public
  deployment.

## Master idea backlog

### Core quantitative work

| Idea | Grade | Effort | Why it helps | Recommendation |
|---|---:|---:|---|---|
| Vectorized GBM Monte Carlo engine | A+ | Medium | Demonstrates stochastic modeling and numerical Python | Implement next; support a fixed seed and batch path generation |
| Self-financing discrete delta hedge | A+ | Medium | Shows that the portfolio accounting, not just the formula, is understood | Model stock, cash, option payoff, rebalancing, and terminal replication error explicitly |
| Transaction-cost accounting | A+ | Small | Creates a realistic and interesting research trade-off | Charge proportional cost on absolute traded notional at every rebalance |
| Optimal hedge-frequency experiment | A+ | Medium | Produces a defensible original result rather than another calculator | Minimize a clearly defined loss such as terminal-error RMSE including costs |
| Monte Carlo validation against Black–Scholes | A+ | Small | Makes the simulation credible | Show convergence and a confidence interval containing the analytical price |
| Focused mathematical test suite | A+ | Small | Signals correctness and makes refactoring safe | Test parity, bounds, convergence, accounting, and reproducibility |
| Volatility-misspecification experiment | A | Small | Connects model risk to hedging outcomes | Compare pricing volatility with lower, equal, and higher realized volatility |
| Common random numbers across strategies | A | Small | Makes hedge-frequency comparisons statistically fairer | Reuse the same paths for every strategy in a comparison |
| Confidence intervals and Monte Carlo standard errors | A | Small | Demonstrates statistical discipline | Report uncertainty, not only point estimates |
| Moneyness and maturity robustness checks | A- | Small | Shows whether the main finding generalizes | Use a small predeclared grid rather than every possible combination |
| Tail-risk metrics | A- | Small | Means and standard deviations can hide asymmetric losses | Report 5th/95th percentiles and expected shortfall with a stated sign convention |
| Numerical finite-difference checks for Greeks | A- | Small | Independently validates analytical Delta, Gamma, Vega, Theta, and Rho | Compare central differences with closed-form Greeks away from boundaries |
| No-arbitrage and edge-case checks | A- | Small | Prevents embarrassing failures during a demo | Cover bounds, put-call parity, near-expiry behavior, and invalid inputs |

### Research and market extensions

| Idea | Grade | Effort | Why it helps | Recommendation |
|---|---:|---:|---|---|
| Historical-return bootstrap versus GBM | A | Medium | Uses the Icelandic focus to test fat tails and non-normal returns | Add after the GBM study; compare hedging-error tails under both path models |
| Continuous dividend yield | A- | Small | Improves correctness for dividend-paying equities | Add `q` consistently to prices, Greeks, simulation drift, tests, and UI |
| Historical hedge as an out-of-sample case study | A- | Medium | Connects simulation findings to an observed path | Present it as one case study, not proof of general performance |
| Liquid US option-chain benchmark | A- | Medium | Allows comparison with real option quotes when Icelandic option quotes are scarce | Use one liquid underlying and explain that it is external validation |
| Implied-volatility solver | B+ | Small | Demonstrates numerical root finding and supports real-option comparisons | Add only when reliable option prices are available |
| Implied-volatility smile/surface | B+ | Medium | Shows awareness of the main Black–Scholes limitation | Use actual clean quotes; do not manufacture a synthetic "market" surface |
| Variance reduction | B+ | Small | Adds statistical and computational depth | Compare antithetic variates or a control variate using measured estimator variance |
| Monte Carlo convergence and runtime benchmark | B+ | Small | Demonstrates numerical judgment and vectorization | Plot error and runtime against path count; avoid premature low-level optimization |
| Volatility estimator comparison | B+ | Medium | Adds an empirical forecasting question | Compare rolling volatility and EWMA out of sample before considering GARCH |
| Regime or stress scenarios | B | Medium | Shows risk awareness beyond normal conditions | Add a few predeclared volatility/jump scenarios after the main study |
| Discrete cash dividends | B | Medium | More realistic than continuous yield around ex-dividend dates | Add only if dividend timing is central to the study |
| Bid/ask spread scenarios | B | Small | Relevant to illiquid markets | Treat spreads as explicit scenarios unless defensible historical quote data exist |
| Block bootstrap of returns | B | Medium | Preserves some serial dependence missing from an ordinary bootstrap | Add only if dependence diagnostics justify it |
| GARCH volatility | B- | Medium | Can improve volatility modeling but easily becomes a separate project | Add only after a simpler estimator comparison produces a clear limitation |
| Jump-diffusion paths | B- | Medium | Useful for tail hedging and gap-risk experiments | Add as a robustness model, not as a new main project |

### Additional option-pricing models

| Idea | Grade | Effort | Why it helps | Recommendation |
|---|---:|---:|---|---|
| Asian option priced by Monte Carlo | B | Small | Reuses the simulation engine naturally | Good first exotic only after the research report is finished |
| Barrier option priced by Monte Carlo | B | Medium | Exercises path dependence and monitoring assumptions | Add only with bias/convergence discussion |
| American option with Longstaff–Schwartz | B | Large | More research-oriented than a basic tree and reuses Monte Carlo | Worthwhile only if early exercise becomes a genuine research question |
| American option with a binomial tree | C+ | Medium | Standard textbook implementation with limited differentiation | Add for completeness only after all A-grade work |
| Binomial convergence to Black–Scholes | B- | Small | Provides another numerical validation exercise | Useful if a tree already exists; not a reason to build one by itself |
| Heston stochastic volatility | C+ | Large | Mathematically interesting but calibration and validation are substantial | Skip until real implied-volatility data justify it |
| Finite-difference PDE solver | C | Large | Strong numerics exercise but disconnected from the best research story | Build only if targeting a derivatives-pricing role specifically |
| Basket or multi-asset options | C | Large | Requires correlation estimation and adds scope quickly | Prefer a separate future project |

### Communication and presentation

| Idea | Grade | Effort | Why it helps | Recommendation |
|---|---:|---:|---|---|
| Strong repository README | A+ | Small | Most reviewers will see this before the code | Lead with the research question, one result, one figure, live demo, and reproduction steps |
| Four-to-six-page research note | A+ | Medium | Demonstrates precise quantitative communication | Include question, method, validation, results, limitations, and references |
| Main finding on the dashboard homepage | A | Small | Lets a recruiter understand the project in seconds | Show one headline result with its assumptions and uncertainty |
| Public deployment on a personal subdomain | A | Small | Removes friction for nontechnical reviewers | Deploy only pages that work and provide a GitHub link |
| Reproducible experiment command | A | Small | Shows that results are not hand-produced | One command should regenerate the report tables and figures from a fixed seed |
| Downloadable experiment data | A- | Small | Makes results inspectable | Export the displayed aggregate results and metadata as CSV |
| Architecture diagram | B | Small | Can help readers understand data, model, experiment, and dashboard flow | Keep it to one small diagram; skip if the README is already clear |
| Short demo GIF or video | B | Small | Helps when the live deployment is slow or unavailable | Add after the interface and results stop changing |
| Long tutorial or extensive documentation site | D | Large | Little additional signal beyond a good README and report | Do not build |

### Engineering and deployment

| Idea | Grade | Effort | Why it helps | Recommendation |
|---|---:|---:|---|---|
| Deterministic seeds and saved experiment metadata | A | Small | Makes every result reproducible | Record seed, parameters, code version, and simulation count |
| Minimal continuous integration | A- | Small | Proves tests run from a clean checkout | Run the focused test file on pushes |
| Dependency versions or lock file | A- | Small | Reduces deployment and reproducibility failures | Pin only after confirming the working environment |
| Input validation and clear financial conventions | A- | Small | Prevents misleading outputs | Define units, option position, cash signs, day count, and cost convention centrally |
| Profile before optimizing | B+ | Small | Supports credible performance claims | Benchmark first; optimize only the measured bottleneck |
| Cache external market data | B | Small | Improves dashboard reliability and rate-limit behavior | Use Streamlit's existing cache facilities where appropriate |
| Package restructuring | C | Medium | May make imports cleaner but does not create a research result | Do the minimum needed for tests and deployment |
| Docker image | C | Medium | Helpful only if the deployment platform requires it | Skip otherwise |
| REST API | D | Medium | Adds infrastructure without strengthening the research | Do not build for this project |
| User accounts, database, or saved portfolios | F | Large | Turns a research project into an unfinished SaaS product | Do not build |
| Mobile application | F | Large | Does not support the quant-research objective | Do not build |

### Tempting but weak ideas

| Idea | Grade | Why to avoid it now |
|---|---:|---|
| Neural network option pricer | D | A model that relearns Black–Scholes is less accurate, less interpretable, and not a useful ML result |
| Generic finance chatbot | F | It dilutes the quantitative story and is difficult to evaluate rigorously |
| Add every available Icelandic ticker | D | More dropdown entries are not more research |
| Add many chart types | D | Presentation volume does not replace a result |
| Claim live-market accuracy | F | Historical volatility and sparse market inputs do not justify that claim |
| Generate synthetic findings or interpretations | F | Every conclusion must come from committed, reproducible experiment output |

## Recommended implementation order

### Phase 1 — Make the simulation real

1. Implement vectorized GBM path generation with `numpy.random.Generator` and a
   fixed seed.
2. Implement a self-financing hedge with a documented sign convention.
3. Add hedge frequency and proportional transaction costs.
4. Return tidy per-simulation results and aggregate statistics expected by the
   existing renderers.
5. Connect the engine to the Monte Carlo dashboard and remove its placeholder
   state.

**Definition of done:** the dashboard runs the same seeded experiment twice and
returns identical results without hidden manual steps.

### Phase 2 — Prove correctness

Add one focused test file covering:

- put-call parity and no-arbitrage bounds;
- analytical Greeks versus finite differences;
- Monte Carlo price convergence to Black–Scholes;
- analytical price inside an appropriately constructed confidence interval;
- exact reproducibility with a fixed seed;
- self-financing cash and share accounting on a tiny deterministic path; and
- lower zero-cost hedge RMSE as the time step becomes sufficiently small.

**Definition of done:** a clean checkout can run one command and verify the
financial and numerical invariants.

### Phase 3 — Produce the main research result

Keep the first experiment deliberately small:

- hedge frequencies: daily, weekly, and monthly;
- transaction costs: zero plus two or three plausible scenarios;
- realized/pricing volatility ratios: `0.8`, `1.0`, and `1.2`;
- moneyness: one main at-the-money result, then in/out-of-the-money robustness;
- identical underlying paths across competing hedge strategies; and
- enough simulations for stable confidence intervals, justified by a convergence
  plot rather than an arbitrary round number.

Primary output:

- terminal replication-error distribution;
- transaction-cost distribution;
- RMSE or another predeclared loss by hedge frequency;
- confidence intervals for strategy comparisons; and
- the optimal frequency under each cost scenario, conditional on the chosen
  loss function.

**Definition of done:** the code can regenerate every number and figure used in
the conclusion.

### Phase 4 — Communicate it

Create:

1. a README that a recruiter can scan in 30 seconds;
2. a four-to-six-page PDF research note;
3. one homepage result card and one decisive chart;
4. a live subdomain with unfinished pages hidden; and
5. a CV bullet using measured results.

Do not describe the project as a trading strategy or claim profitability. It is
an option-pricing and hedging-risk study.

### Phase 5 — Add one differentiating extension

Choose only one:

1. **Historical-return bootstrap versus GBM** — best research extension;
2. **continuous dividend yield** — best correctness extension; or
3. **real liquid-option benchmark and implied volatility** — best market-data
   extension.

Do not begin American, Heston, PDE, or multi-asset models until the report and
public deployment are complete.

## Proposed research note

### Working title

**Discrete Delta Hedging in an Illiquid Market: Transaction Costs, Volatility
Misspecification, and Icelandic Equities**

### Suggested structure

1. **Abstract** — question, method, main numerical result, and limitation.
2. **Motivation** — why discrete hedging and market frictions matter.
3. **Model** — Black–Scholes assumptions, GBM dynamics, dividend convention,
   and option/portfolio sign conventions.
4. **Experiment** — path generation, rebalancing, costs, common random numbers,
   seeds, metrics, and confidence intervals.
5. **Validation** — parity, Greeks, Monte Carlo convergence, and accounting
   checks.
6. **Results** — frequency/cost trade-off, volatility misspecification, and one
   robustness analysis.
7. **Limitations** — GBM, constant volatility, data quality, liquidity, lack of
   Icelandic option quotes, and scenario-based transaction costs.
8. **Conclusion** — what was learned without overstating generality.

### Figures worth keeping

Limit the note to figures that answer a question:

1. Monte Carlo convergence to the analytical Black–Scholes price.
2. Terminal hedging-error distributions by rebalance frequency at zero cost.
3. RMSE and average transaction cost by frequency under several cost rates.
4. Optimal frequency or loss surface by volatility gap and transaction cost.

## README outline

1. One-sentence project description.
2. One headline quantitative result with assumptions.
3. Screenshot or decisive research figure.
4. Live dashboard and research-note links.
5. Implemented models and experiments.
6. Validation summary.
7. Reproduction command.
8. Data sources and limitations.

Avoid starting with installation instructions or a long feature list. The reader
should see the question and result first.

## CV bullet template

Fill in the brackets only after the experiment is finalized:

> Built and deployed a vectorized Python options-research platform; ran
> **[N]** seeded simulations of discrete delta hedging under volatility
> misspecification and transaction costs, validated Monte Carlo prices against
> Black–Scholes within **[error/CI]**, and found **[measured result]** across
> daily, weekly, and monthly rebalancing.

Never invent a speedup, accuracy number, optimal frequency, or statistical result.

## Questions the finished project should let you answer in an interview

- Why does Monte Carlo converge at approximately a square-root rate?
- Why use common random numbers when comparing hedge frequencies?
- What exactly makes the hedge self-financing?
- Why can the mean hedging error and RMSE lead to different decisions?
- How do transaction costs change the optimal rebalancing policy?
- What happens when realized volatility differs from pricing volatility?
- What assumptions make Black–Scholes unsuitable for an illiquid equity?
- Why can historical adjusted prices, raw prices, and dividends produce
  inconsistent volatility or return estimates?
- How did you validate the simulator independently of the dashboard?
- Which conclusion is robust, and which depends strongly on assumptions?

## Final definition of success

The project is ready to lead a CV when a reviewer can:

1. open the repository and understand the question in 30 seconds;
2. open the live dashboard and see a real result rather than a placeholder;
3. run one command to reproduce the central figures;
4. run one command to validate the core mathematics;
5. inspect a short report that states assumptions and limitations honestly; and
6. ask you about any result and receive a precise explanation of how it was
   generated.

That is enough. Additional pricing models should be added only when they answer a
new question that the finished core study cannot answer.
