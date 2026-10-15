# AERIS (Adaptive Enterprise Reliability & Intelligence System)

## Table of Contents

* [Assumptions and Ambiguities](#assumptions-and-ambiguities)
* [Epic 1: Platform Architecture](#epic-1-platform-architecture)
* [Epic 2: Enterprise Data Foundation](#epic-2-enterprise-data-foundation)
* [Epic 3: Transformation & Data Quality](#epic-3-transformation--data-quality)
* [Epic 4: Governance](#epic-4-governance)
* [Epic 5: Platform Observability](#epic-5-platform-observability)
* [Epic 6: AI-Ready Data Product](#epic-6-ai-ready-data-product)
* [Epic 7: Reliable Data Processing](#epic-7-reliable-data-processing)
* [Epic 8: SRE & Observability](#epic-8-sre--observability)
* [Epic 9: DevSecOps](#epic-9-devsecops)
* [Epic 10: Security & Governance](#epic-10-security--governance)
* [Epic 11: FinOps](#epic-11-finops)
* [Epic 12: Engineering Operating Model](#epic-12-engineering-operating-model)
* [Epic 13: Engine Abstraction](#epic-13-engine-abstraction)
* [Epic 14: Databricks Integration](#epic-14-databricks-integration)
* [Epic 15: Interoperability](#epic-15-interoperability)
* [Epic 16: Unified Governance & Observability](#epic-16-unified-governance--observability)
* [Epic 17: Workload Placement](#epic-17-workload-placement)
* [Epic 18: Architecture Review](#epic-18-architecture-review)
* [Epic 19: Secure Credential & Secrets Management](#epic-19-secure-credential--secrets-management)
* [Epic 20: Snowflake Live Integration](#epic-20-snowflake-live-integration)
* [Epic 21: Databricks Live Integration](#epic-21-databricks-live-integration)
* [Epic 22: Resiliency & Retry Logic](#epic-22-resiliency--retry-logic)
* [Epic 23: Live Integration Testing](#epic-23-live-integration-testing)

---

## Assumptions and Ambiguities

**V1 Assumptions & Ambiguities:**

* **Target Architecture:** Snowflake is the definitive data engine for V1. `dbt` (or a directly equivalent SQL-based transformation tool) will be used to satisfy the modular transformation requirements.
* **Synthetic Data Generation:** A script-based generator (e.g., Python with Faker/Pandas) will be used to simulate the logistics data, as opposed to purchasing a mock data tool.
* **Tooling:** Standard Git-based version control and a standard CI/CD pipeline (e.g., GitHub Actions or GitLab CI) will be used to satisfy automated validation and TDD workflows.
* **Epic 5 (Dashboard) Ambiguity:** The exact BI or reporting tool for the "lightweight operational dashboard" is unspecified. We will assume a native Snowflake Streamlit app or a lightweight Snowflake dashboard for V1 to minimize infrastructure overhead.
* **Epic 6 (AI-Ready Data Product) Ambiguity:** The prompt asks to "Build a simple Shipment Delay Intelligence use case.". It is unclear if this means training a predictive model or simply surfacing a feature-engineered dataset ready for an ML team. The story will assume the latter (creating the AI-ready feature table/view) to maintain focus on data platform engineering.

**V2 Assumptions & Ambiguities:**

* **Engine & Infrastructure Assumption:** AERIS V1 relies on a local SQLite mock to simulate Snowflake's capabilities. Epics 7–12 will continue to build upon this mocked Python/SQLite foundation (e.g., simulating FinOps metrics via query execution time or row counts) to maintain continuity before introducing multi-engine capabilities in V3.
* **CDC Implementation Ambiguity:** "CDC-style/incremental processing" can mean many things. Assumption: We will implement metadata-driven CDC (tracking operation_type such as INSERT/UPDATE/DELETE and updated_at timestamps) to handle state changes rather than just append-only logic.
* **Operating Model Implementation Assumption:** Epic 12 (Engineering Operating Model) deliverables are primarily organizational. They will be implemented as standardized Markdown artifacts within the docs/ directory, enforced via CI pipeline linting to ensure compliance.

**V3 Assumptions & Ambiguities:**

* **Orchestration Engine:** AERIS utilizes a code-based orchestration tool (e.g., Airflow, Dagster, Prefect) that supports abstraction via custom operators/assets.
* **TDD for Documentation:** For documentation-heavy stories (ADRs, frameworks, matrices), "TDD" is defined as automated CI checks (e.g., markdown linting, required-section validation scripts) and predefined peer-review rubrics.
* **Metadata Tooling:** Epic 16 assumes we are defining an agnostic data model for metadata extraction, not immediately provisioning a net-new enterprise catalog (like Collibra or DataHub), to keep the scope within one sprint.

**V4 Assumptions & Ambiguities:**

* **Secret Provider Context:** Epic 19 requests a `SecretsManager` interface but does not specify a cloud provider (e.g., AWS Secrets Manager, Azure Key Vault). Assumption: The `SecretsManager` will be implemented as an abstract base class, and the initial concrete implementation will use environment variables (`.env`) for local/CI integration, structured so it can be swapped with a cloud provider later.
* **Concurrency Model:** Epic 22 states that long-running jobs should not cause "blocking timeouts in the main orchestrator thread." Assumption: The Python executors will utilize `asyncio` (asynchronous Python) for polling mechanisms, allowing the orchestrator to await results without blocking the main event loop.
* **Databricks Payload:** Epic 21 states we must trigger an "existing Databricks Job." Assumption: The workload `payload` string passed to the `DatabricksExecutor` will contain the Databricks `job_id` (and optional parameters) formatted as JSON, rather than raw SQL or Python code.

---

## Epic 1: Platform Architecture

**US-1.1: Platform Architecture Definition & Repository Skeleton**

* **User Story:** As a Platform Architect, I want to define the core AERIS architecture, establish key Architectural Decision Records (ADRs), and set up the repository skeleton so that all subsequent development follows standardized, decoupled patterns.
* **Business Value:** Ensures structural consistency, reduces technical debt, and provides a clear separation of concerns between platform capabilities and the Snowflake engine.
* **Acceptance Criteria:**
* **Given** a new code repository, **When** a developer clones it, **Then** standard directories exist for `infrastructure`, `transformations`, `ingestion`, and `docs`.
* **Given** the need for architectural guidance, **When** a developer reviews the `docs/adr` folder, **Then** foundational ADRs (Data Engine Selection, Transformation Tooling, Repo Structure) are present and formatted correctly.


* **TDD Test Scenarios:**
* *Positive:* CI pipeline executes a structural linter that verifies required directories (`docs/adr`, `src`, `tests`) exist.
* *Negative:* CI pipeline fails if an ADR document does not follow the standard markdown template.


* **Dependencies:** None.
* **Definition of Done:** Repository is created, standard branches exist, directory structure is pushed, at least 3 core ADRs are documented, and a structural CI check passes.
* **Priority:** High (Sprint 1).

---

## Epic 2: Enterprise Data Foundation

**US-2.1: Logistics Synthetic Data Generation Engine**

* **User Story:** As a Data Engineer, I want to programmatically generate realistic synthetic logistics data (orders, shipments, customers, carriers) so that we can test ingestion and transformation pipelines without relying on sensitive production data.
* **Business Value:** Unblocks end-to-end pipeline development and allows testing at various data volumes.
* **Acceptance Criteria:**
* **Given** the synthetic data generator is triggered, **When** it completes, **Then** it produces structured files (e.g., CSV/JSON/Parquet) for the four core entities with primary/foreign key relationships maintained.
* **Given** a generated shipments dataset, **When** inspected, **Then** timestamps for `delivery_date` must be chronologically after `ship_date`.


* **TDD Test Scenarios:**
* *Positive:* Unit test verifies the generator outputs 4 distinct files with expected headers.
* *Negative:* Unit test asserts that an order cannot have an invalid customer ID (referential integrity).
* *Edge:* Unit test generates an empty batch or a batch of size 1 to ensure the script does not fail.
* *Error:* The script raises a specific error if write permissions to the output directory are denied.


* **Dependencies:** US-1.1.
* **Definition of Done:** Data generation script is merged, unit tests pass, and sample data is successfully generated locally.
* **Priority:** High (Sprint 1).

**US-2.2: Layered Data Ingestion (Batch & Incremental)**

* **User Story:** As a Platform Engineer, I want to ingest the synthetic data into Snowflake across Raw and Staging layers using both batch and incremental patterns so that data is systematically captured for downstream curation.
* **Business Value:** Establishes the foundational EL (Extract, Load) capability of the platform.
* **Acceptance Criteria:**
* **Given** a new batch of synthetic files, **When** the ingestion pipeline runs, **Then** the raw data is loaded into Snowflake's `RAW` database.
* **Given** a subsequent run with new records, **When** the incremental pipeline runs, **Then** only new or updated records are merged into the `STAGING` layer without duplicating existing rows.


* **TDD Test Scenarios:**
* *Positive:* Integration test loads 100 records, verifies `COUNT(*) = 100` in `RAW`.
* *Negative:* Pipeline attempts to ingest a corrupted file; test verifies the pipeline handles the error gracefully and logs the failure without partial commits.
* *Edge:* Ingestion of a file with maximum string lengths to ensure Snowflake schema accommodates the limits.


* **Dependencies:** US-2.1.
* **Definition of Done:** CI/CD pipeline deploys Snowflake schemas via IaC/migration scripts, ingestion runs successfully on sample data, and integration tests pass.
* **Priority:** High (Sprint 2).

---

## Epic 3: Transformation & Data Quality

**US-3.1: Curated Data Products & Automated Data Quality Checks**

* **User Story:** As an Analytics Engineer, I want to build modular transformations from Staging to Curated layers and attach data quality tests so that downstream consumers have a documented, trustworthy "Data Product."
* **Business Value:** Ensures business logic is applied reproducibly and bad data is caught before reaching end-users.
* **Acceptance Criteria:**
* **Given** staged logistics data, **When** transformations execute, **Then** a unified `fct_shipments` and `dim_customers` are produced in the `CURATED` database.
* **Given** the curated tables, **When** data quality tests run, **Then** tests validate uniqueness on primary keys and freshness on timestamp columns.


* **TDD Test Scenarios:**
* *Positive:* Transformation test ensures `fct_shipments.total_cost` equals `base_cost + tax`.
* *Negative:* A mock staging record with a NULL `customer_id` is injected; the automated schema test (e.g., `not_null`) must fail and trigger an alert.
* *Edge:* A shipment with a $0 cost is processed; the test must confirm the transformation allows 0 but flags negative values.


* **Dependencies:** US-2.2.
* **Definition of Done:** Transformation models are merged, documentation is generated (e.g., `dbt docs`), and data quality tests execute successfully in the CI pipeline.
* **Priority:** High (Sprint 2).

---

## Epic 4: Governance

**US-4.1: RBAC and Sensitive Data Controls**

* **User Story:** As a Data Governance Lead, I want to implement Role-Based Access Control and data masking policies in Snowflake so that sensitive data (PII) is protected and users only access authorized domains.
* **Business Value:** Secures the platform and ensures compliance with enterprise data policies by default.
* **Acceptance Criteria:**
* **Given** a user with the `DATA_SCIENTIST` role, **When** they query the `CURATED` database, **Then** they can read the data.
* **Given** a user with the `ANALYST` role, **When** they query `dim_customers`, **Then** the `customer_email` column is dynamically masked (e.g., `***@***.com`).


* **TDD Test Scenarios:**
* *Positive:* Automated permission test authenticates as `ANALYST` and successfully runs `SELECT * FROM curated.fct_shipments`.
* *Negative:* Automated permission test authenticates as `ANALYST` and attempts to `DROP TABLE curated.fct_shipments`; test asserts an `InsufficientPrivileges` exception is raised.
* *Error:* Test verifies that assigning an invalid role to a user via the provisioning script fails cleanly.


* **Dependencies:** US-3.1.
* **Definition of Done:** Infrastructure-as-Code for RBAC and masking policies is deployed, and automated access/masking tests pass in the environment.
* **Priority:** Medium (Sprint 3).

---

## Epic 5: Platform Observability

**US-5.1: Pipeline Telemetry & SLI Operational Dashboard**

* **User Story:** As a Platform Operator, I want to track pipeline execution metadata (success, duration, data quality results) and visualize it on a lightweight dashboard so that I can monitor platform SLIs/SLOs.
* **Business Value:** Enables proactive incident management and provides visibility into platform health.
* **Acceptance Criteria:**
* **Given** a pipeline execution completes (success or failure), **When** it finishes, **Then** metadata (timestamp, job name, status, rows processed) is logged to an internal `ops.audit_log` table.
* **Given** the audit logs, **When** a user opens the operational dashboard, **Then** they see a clear visual indicator of current pipeline health and data freshness SLIs.


* **TDD Test Scenarios:**
* *Positive:* Trigger a successful mock pipeline run; test queries `ops.audit_log` to verify exactly one new "SUCCESS" row was inserted.
* *Negative:* Trigger a forced-failure mock pipeline run; test queries `ops.audit_log` to verify a "FAILED" row was inserted with the corresponding error message.
* *Edge:* Run two pipelines concurrently; test verifies both log entries are captured without locking issues.


* **Dependencies:** US-2.2, US-3.1.
* **Definition of Done:** Audit logging mechanism is implemented, the lightweight dashboard (e.g., Streamlit or native Snowflake dashboard) is deployed and accessible to operators.
* **Priority:** Medium (Sprint 3).

---

## Epic 6: AI-Ready Data Product

**US-6.1: Shipment Delay Intelligence Feature View**

* **User Story:** As a Data Scientist, I want a curated, decoupled view providing historical shipment details combined with weather or carrier performance proxies, so that I have a clean dataset ready for training a predictive delay model.
* **Business Value:** Demonstrates the platform's ability to seamlessly bridge enterprise data engineering with AI/ML consumption without engine lock-in.
* **Acceptance Criteria:**
* **Given** the curated data foundation, **When** the AI feature transformation runs, **Then** it produces a denormalized dataset (`ai_shipment_features`) containing historical delay flags and feature columns.
* **Given** external AI compute (e.g., a local Jupyter notebook or external Python script), **When** it connects via standard drivers, **Then** it can successfully query `ai_shipment_features` independently of internal pipeline logic.


* **TDD Test Scenarios:**
* *Positive:* Test verifies `ai_shipment_features` has 0% nulls in the target variable column (`is_delayed`).
* *Negative:* Test attempts to read the feature view using an unauthorized external application credential; test confirms access is denied.
* *Edge:* Test verifies the dataset correctly calculates carrier delay averages even if a carrier only has 1 historical shipment.


* **Dependencies:** US-3.1, US-4.1.
* **Definition of Done:** The feature view is deployed, external connection documentation is provided, and a sample Python notebook demonstrating data extraction and basic exploratory data analysis (EDA) is checked into the repository.
* **Priority:** Medium (Sprint 4).

---

## Epic 7: Reliable Data Processing

**Objective:** Pipelines can recover from realistic operational failures without corrupting data.

**US-7.1: Idempotent CDC Ingestion & Deduplication**

* **User Story:** As a Data Engineer, I want the ingestion pipeline to process CDC events (inserts, updates, deletes) idempotently so that duplicate executions do not result in duplicated or corrupted staging data.
* **Business Value:** Prevents data duplication during pipeline retries, ensuring downstream data products remain accurate.
* **Acceptance Criteria:**
* **Given** a batch of records containing an update to an existing customer_id, **When** the pipeline processes the batch, **Then** the staging layer reflects only the latest state based on the updated timestamp.
* **Given** the exact same data file is ingested twice, **When** the pipeline completes the second run, **Then** the row count and data state in the staging layer remain unchanged.


* **TDD Test Scenarios:**
* *Positive:* Ingest a file with a mix of new inserts and updates; verify correct final row counts and updated values.
* *Negative:* Ingest a file containing duplicate records for the same primary key in the same batch; verify the pipeline deduplicates before merging.
* *Edge:* Process a CDC delete event; verify the record is logically or physically removed from staging.
* *Error:* Process a batch with missing primary keys; verify the pipeline rejects the specific bad records without failing the entire batch.


* **Dependencies:** None
* **Definition of Done:** CDC merge logic is implemented, idempotency is proven via automated tests, and documentation is updated.
* **Priority:** High

**US-7.2: Late-Arriving Data & Schema Evolution Handling**

* **User Story:** As a Data Engineer, I want the pipeline to seamlessly handle out-of-order data and additive schema changes so that upstream changes do not break downstream processing.
* **Business Value:** Increases pipeline resilience against upstream application changes and network delays.
* **Acceptance Criteria:**
* **Given** a CDC event with a timestamp older than the current record in staging, **When** ingested, **Then** the pipeline ignores the stale update and preserves the newer record.
* **Given** a source file with a newly added column, **When** ingested into the raw layer, **Then** the pipeline dynamically alters the target table to include the new column without failing.


* **TDD Test Scenarios:**
* *Positive:* Ingest a file with an unexpected new column; verify the database schema expands automatically.
* *Negative:* Ingest a record with an older updated_at timestamp than what exists; verify the database does not overwrite the newer data.
* *Edge:* Ingest a file missing a previously known non-required column; verify the pipeline inserts NULLs for that column.


* **Dependencies:** US-7.1
* **Definition of Done:** Late-arrival resolution and schema-evolution logic are merged, tested, and demonstrated in the demo script.
* **Priority:** High

**US-7.3: Automated Retry & Replay Mechanism**

* **User Story:** As a Platform Operator, I want the pipeline to automatically retry transient failures and support manual replay from specific checkpoints so that I can recover from outages without manual data cleanup.
* **Business Value:** Reduces manual operational toil and limits downtime during transient system failures.
* **Acceptance Criteria:**
* **Given** a pipeline step fails due to a simulated transient lock, **When** the retry wrapper triggers, **Then** the step executes again and succeeds.
* **Given** a pipeline failure at the transformation stage, **When** a replay is triggered, **Then** it resumes from the transformation stage without re-running the successful ingestion stage.


* **TDD Test Scenarios:**
* *Positive:* Trigger a pipeline run with a mock that fails exactly once; verify the pipeline eventually reports SUCCESS after the automated retry.
* *Negative:* Trigger a pipeline with a persistent failure (e.g., hard syntax error); verify it exhausts its retry limit and logs a final FAILURE state.
* *Edge:* Trigger a replay for a pipeline that previously succeeded; verify it completes idempotently.


* **Dependencies:** US-7.1
* **Definition of Done:** Retry decorator/wrapper is implemented, checkpoint state is tracked in the audit log, and failure injection is demonstrated.
* **Priority:** Medium

---

## Epic 8: SRE & Observability

**Objective:** AERIS can be operated as a production platform rather than simply executed as a pipeline.

**US-8.1: SLO Definition & Error Budget Tracking**

* **User Story:** As an SRE, I want to define specific Service Level Objectives (SLOs) and track their error budgets based on existing telemetry so that we have quantifiable measures of platform reliability.
* **Business Value:** Aligns engineering priorities with business expectations by providing measurable reliability targets.
* **Acceptance Criteria:**
* **Given** the pipeline telemetry, **When** a failure occurs, **Then** the automated error budget calculation decreases.
* **Given** a request for metrics, **When** the observability dashboard is queried, **Then** it returns the current Data Freshness SLO status and Pipeline Success Rate SLO status.


* **TDD Test Scenarios:**
* *Positive:* Inject 99 successful runs and 1 failure; verify the Success Rate SLO reads 99% and error budget is accurately decremented.
* *Negative:* Query SLO metrics when no pipeline runs have occurred; verify it handles the empty state gracefully (e.g., 100% or N/A).
* *Edge:* Test the freshness SLO by simulating a successful run where the maximum timestamp in the data is older than the 24-hour threshold; verify the freshness SLO drops.


* **Dependencies:** None (builds on V1 TelemetryLogger)
* **Definition of Done:** SLO calculation logic is added to the telemetry module, tests pass, and metrics are exposed in the output.
* **Priority:** High

**US-8.2: Automated Incident Runbooks & Failure Diagnosis**

* **User Story:** As a Platform Operator, I want failure alerts to automatically link to diagnostic runbooks so that I can resolve production incidents quickly and consistently.
* **Business Value:** Reduces Mean Time To Resolution (MTTR) by standardizing the response to common pipeline failures.
* **Acceptance Criteria:**
* **Given** a pipeline failure, **When** the error is logged to the ops_audit_log, **Then** the log entry includes a mapped runbook URL based on the error type (e.g., DataQualityError vs. IngestionError).
* **Given** the repository, **When** explored, **Then** a docs/runbooks/ directory exists containing markdown files for at least 3 distinct failure scenarios.


* **TDD Test Scenarios:**
* *Positive:* Inject a DataQualityError; verify the resulting telemetry log contains a reference to docs/runbooks/dq_failure.md.
* *Negative:* Inject an unknown/unhandled exception; verify the log defaults to a general docs/runbooks/general_triage.md fallback.


* **Dependencies:** US-8.1
* **Definition of Done:** Runbook markdown files are created, error-mapping logic is added to the telemetry logger, and tests pass.
* **Priority:** Medium

---

## Epic 9: DevSecOps

**Objective:** Platform changes follow a repeatable engineering delivery process.

**US-9.1: Comprehensive CI Validation (Linting, Testing, SAST)**

* **User Story:** As a Platform Engineer, I want automated CI checks to enforce code formatting, run unit/integration tests, and perform basic security scanning so that unverified or insecure code cannot be merged.
* **Business Value:** Prevents regression bugs and security vulnerabilities from reaching the primary branch.
* **Acceptance Criteria:**
* **Given** a new pull request, **When** code is pushed, **Then** a Makefile command executes code formatting (e.g., Ruff/Black), type checking (Mypy), and a basic security lint (e.g., Bandit).
* **Given** the test suite execution, **When** coverage falls below 80%, **Then** the CI script returns a non-zero exit code (fails).


* **TDD Test Scenarios:**
* *Positive:* Run the make test command on a clean codebase; verify it exits with code 0 and reports >80% coverage.
* *Negative:* Introduce a syntax error or a failing unit test; verify the CI command fails and halts execution.
* *Error:* Introduce a hardcoded secret in a dummy file; verify the security linter catches it and fails the build.


* **Dependencies:** None
* **Definition of Done:** Makefile is updated with robust CI targets, test coverage thresholds are enforced, and documentation details how to run the suite locally.
* **Priority:** High

**US-9.2: Environment Promotion & Rollback Simulation**

* **User Story:** As a Release Manager, I want a standardized deployment script that promotes code across isolated environments (Dev -> Staging -> Prod) and supports rollback, so that releases are safe and reversible.
* **Business Value:** Minimizes production downtime during bad deployments by providing a fast, tested rollback path.
* **Acceptance Criteria:**
* **Given** a successful CI build, **When** the deployment script is run for "Staging", **Then** it creates a separate database file or namespace (e.g., aeris_staging.db).
* **Given** a deployed version in "Prod", **When** the rollback command is executed, **Then** the system reverts to the previously saved database state or code version.


* **TDD Test Scenarios:**
* *Positive:* Execute deployment to "Prod"; verify aeris_prod.db is initialized and migrations are applied.
* *Negative:* Execute deployment to "Prod" with a faulty migration script; verify the deployment halts and does not corrupt the existing production state.
* *Edge:* Execute a rollback when no previous version exists; verify the script exits cleanly with a descriptive warning.


* **Dependencies:** US-9.1
* **Definition of Done:** Deployment/rollback Python script is implemented, tested against the SQLite backend, and demonstrated.
* **Priority:** Medium

---

## Epic 10: Security & Governance

**Objective:** Security and governance become enforceable platform capabilities.

**US-10.1: Strengthened Least Privilege & Data Access Auditing**

* **User Story:** As a Governance Lead, I want strict enforcement of least privilege RBAC and immutable query audit logs so that we can track exactly who accessed what data and when.
* **Business Value:** Ensures regulatory compliance (e.g., GDPR/SOC2) by proving data access is controlled and monitored.
* **Acceptance Criteria:**
* **Given** a user executing a query, **When** the query completes, **Then** the GovernanceEngine logs the username, role, query_text, and timestamp into a secure gov_audit_log table.
* **Given** a user with an ANALYST role, **When** they attempt to access a strictly restricted table (e.g., hr_salary_data), **Then** access is denied and a security violation is logged.


* **TDD Test Scenarios:**
* *Positive:* Execute a valid SELECT as DATA_SCIENTIST; verify the exact query text and user are recorded in gov_audit_log.
* *Negative:* Attempt an unauthorized SELECT; verify an exception is raised AND a "DENIED" event is written to the audit log.
* *Edge:* Execute an extremely long query string; verify the audit log truncates or stores it without crashing the engine.


* **Dependencies:** V1 Governance module
* **Definition of Done:** Audit logging is built into the GovernanceEngine, RBAC boundaries are expanded, and tests validate audit trail creation.
* **Priority:** High

**US-10.2: Document Governance Policies & Responsibilities**

* **User Story:** As a Compliance Officer, I want documented governance policies mapping roles to data domains so that platform users understand access boundaries and data ownership.
* **Business Value:** Translates technical RBAC implementations into understandable corporate policy.
* **Acceptance Criteria:**
* **Given** the codebase, **When** audited, **Then** a docs/governance/ directory exists containing an access matrix and data ownership definitions.
* **Given** the CI pipeline, **When** executed, **Then** a structural test validates the presence of these governance documents.


* **TDD Test Scenarios:**
* *Positive:* CI linter verifies docs/governance/access_matrix.md exists and contains required headers.
* *Negative:* If the file is deleted or renamed, the CI linter fails.


* **Dependencies:** None
* **Definition of Done:** Governance documentation is written, peer-reviewed, and enforced by the repository linter.
* **Priority:** Low

---

## Epic 11: FinOps

**Objective:** Engineering decisions can be evaluated in terms of reliability, performance and cost.

**US-11.1: Workload Resource Tracking & Cost Attribution**

* **User Story:** As a FinOps Analyst, I want the platform to track query execution time and rows processed per workload tag (e.g., ingestion, ai_training) so that we can attribute platform costs to specific teams or products.
* **Business Value:** Creates visibility into which pipelines are driving platform spend, enabling chargebacks.
* **Acceptance Criteria:**
* **Given** a pipeline step execution, **When** it runs, **Then** the elapsed execution time (milliseconds) and workload tag are captured in the telemetry log.
* **Given** the dashboard metrics, **When** queried, **Then** a simulated "Cost" metric is calculated (e.g., $0.001 per ms of execution time) and grouped by workload tag.


* **TDD Test Scenarios:**
* *Positive:* Run the AI feature pipeline tagged as ai_team; verify the audit log captures execution time > 0ms and correctly assigns the tag.
* *Negative:* Run a pipeline without providing a workload tag; verify it defaults to unattributed rather than failing.


* **Dependencies:** US-8.1
* **Definition of Done:** Execution timer is added to platform functions, cost attribution query is added to telemetry, and unit tests pass.
* **Priority:** High

**US-11.2: Identify & Optimize Inefficient Workloads**

* **User Story:** As a Data Engineer, I want to identify a highly inefficient query in the platform and optimize it, verifying the cost reduction via FinOps metrics, so that platform margins improve.
* **Business Value:** Proves the FinOps loop works by demonstrating measurable cost savings through engineering effort.
* **Acceptance Criteria:**
* **Given** an intentionally inefficient transformation query (e.g., a cross join), **When** executed, **Then** it registers a high cost/duration baseline.
* **Given** the inefficient query is replaced with an optimized version (e.g., indexed inner join), **When** executed, **Then** the telemetry proves a reduction in execution time/cost by at least 50%.


* **TDD Test Scenarios:**
* *Positive:* Integration test runs the old query and new query back-to-back, asserting that duration_new < (duration_old * 0.5).
* *Edge:* Verify the resulting data output of the optimized query exactly matches the output of the inefficient query (data integrity is maintained).


* **Dependencies:** US-11.1
* **Definition of Done:** The optimization experiment is coded, the before-and-after metrics are documented in a FinOps ADR, and tests pass.
* **Priority:** Medium

---

## Epic 12: Engineering Operating Model

**Objective:** AERIS demonstrates how an engineering leader would organize and operate the platform.

**US-12.1: Platform Operating Model & Engineering KPIs**

* **User Story:** As an Engineering Manager, I want to define team boundaries, platform ownership, and engineering KPIs (e.g., deployment frequency, lead time) so that scaling the team is structured and measurable.
* **Business Value:** Establishes clear operating boundaries, preventing code ownership disputes and operational bottlenecks as the team grows.
* **Acceptance Criteria:**
* **Given** the repository, **When** queried by a new engineer, **Then** a docs/operating_model/team_boundaries.md exists detailing who owns Ingestion vs. Transformations.
* **Given** the CI pipeline, **When** executed, **Then** the structural linter ensures the operating_model directory and KPI definitions exist.


* **TDD Test Scenarios:**
* *Positive:* Update the repo_linter.py to check for docs/operating_model/; verify the test passes when the files are present.


* **Dependencies:** None
* **Definition of Done:** Operating model documents are created and structural linter tests are updated to enforce them.
* **Priority:** High

**US-12.2: Platform Roadmap & Risk Register**

* **User Story:** As a Platform Lead, I want a documented short-term roadmap and risk register so that stakeholders have visibility into future capabilities (like V3 Multi-Engine) and accepted technical debts.
* **Business Value:** Manages stakeholder expectations and explicitly tracks technical risks before they become incidents.
* **Acceptance Criteria:**
* **Given** the repository, **When** checked, **Then** a docs/operating_model/roadmap.md and risk_register.md exist.
* **Given** the risk register, **When** reviewed, **Then** it must contain at least 3 categorized risks (e.g., SQLite limitation, unencrypted local data) with mitigation strategies.


* **TDD Test Scenarios:**
* *Positive:* CI linter parses risk_register.md and asserts it contains standard headers (Risk, Impact, Mitigation).


* **Dependencies:** US-12.1
* **Definition of Done:** Roadmap and risk register are published, peer-reviewed, and enforced by CI.
* **Priority:** Medium

---

## Epic 13: Engine Abstraction

**Objective:** AERIS can add another execution engine without redesigning the entire platform.

**US-13.1: Engine Capability Matrix Definition**

* **User Story:** As a Platform Architect, I want to define an engine capability matrix for the AERIS Data Platform, so that we have a standardized baseline to compare Snowflake, Databricks, and future execution engines.
* **Business Value:** Prevents vendor lock-in by clearly defining the baseline capabilities any engine must meet to be integrated into the platform.
* **Acceptance Criteria:**
* **Given** the need to evaluate platform engines, **When** the capability matrix is accessed, **Then** it must include dimensions for SQL compliance, DataFrame support, streaming, governance integration, and compute isolation.
* **Given** the capability matrix, **When** mapped against Snowflake and Databricks, **Then** all current platform capabilities must be explicitly supported by at least one engine.


* **TDD Test Scenarios:**
* *Positive:* CI script validates that the Markdown table contains all required columns (Capability, Snowflake Support, Databricks Support, Priority).
* *Error:* CI pipeline fails if the document violates ADR/Markdown formatting standards.


* **Dependencies:** None.
* **Definition of Done:** Matrix document is committed to the architecture repository, passes markdown-lint, and is approved by the Principal Engineer.
* **Priority:** High

**US-13.2: Abstract Orchestration Execution Layer**

* **User Story:** As a Data Engineer, I want an abstract execution interface in the orchestrator, so that I can trigger a workload without hardcoding engine-specific connection logic in the data product definition.
* **Business Value:** Decouples workload definitions from engine-specific deployment, fulfilling the core engine-agnostic requirement.
* **Acceptance Criteria:**
* **Given** a generic `ExecuteWorkload` task, **When** the target engine is set to "Snowflake", **Then** the orchestrator triggers a Snowflake query/procedure.
* **Given** a generic `ExecuteWorkload` task, **When** the target engine is set to "Databricks", **Then** the orchestrator triggers a Databricks job.


* **TDD Test Scenarios:**
* *Positive (Snowflake):* Pass `engine='snowflake'` with a valid SQL payload; assert the Snowflake API wrapper is called with correct parameters.
* *Positive (Databricks):* Pass `engine='databricks'` with a valid Job ID; assert the Databricks Jobs API wrapper is called.
* *Negative (Unsupported):* Pass `engine='redshift'`; assert an `UnsupportedEngineException` is raised before network execution.
* *Edge (Missing payload):* Pass `engine='snowflake'` with a `None` payload; assert a `MalformedWorkloadException` is raised.


* **Dependencies:** US-13.1
* **Definition of Done:** Unit tests pass with >90% coverage, abstraction classes are merged, and orchestrator documentation is updated.
* **Priority:** High

---

## Epic 14: Databricks Integration

**Objective:** AERIS demonstrates genuine multi-engine capability rather than merely documenting it.

**US-14.1: Deploy Databricks Workspace via IaC**

* **User Story:** As a Platform DevOps Engineer, I want to deploy a Databricks workspace using Infrastructure as Code (IaC), so that the environment is reproducible, secure, and integrated with our cloud networking.
* **Business Value:** Establishes the foundational infrastructure required to introduce the second execution engine securely.
* **Acceptance Criteria:**
* **Given** the IaC repository, **When** the Terraform/Bicep pipeline runs, **Then** a Databricks workspace is created in the designated subnets.
* **Given** the deployed workspace, **When** a user authenticates via SSO, **Then** they are granted baseline access based on their IDP group.


* **TDD Test Scenarios:**
* *Positive:* IaC testing framework (e.g., Terratest) provisions the workspace and asserts the API returns HTTP 200 for workspace status.
* *Negative:* Terratest attempts to deploy with public IP access enabled; assert the deployment is rejected by organizational policy constraints.


* **Dependencies:** None.
* **Definition of Done:** IaC code is merged, workspace is active in the development environment, network routing is verified, and security scan passes.
* **Priority:** High

**US-14.2: Implement PySpark Transformation Workload**

* **User Story:** As a Data Engineer, I want to implement a data transformation pipeline using Databricks PySpark, so that we can demonstrate a meaningful workload running on the new engine while keeping Snowflake operational.
* **Business Value:** Proves genuine multi-engine capability by successfully executing a workload optimized for Spark.
* **Acceptance Criteria:**
* **Given** raw data in object storage, **When** the PySpark job executes, **Then** it transforms the data according to business rules and writes it to a Delta table.
* **Given** the existing Snowflake workload, **When** the Databricks workload runs concurrently, **Then** the Snowflake workload continues executing without interference.


* **TDD Test Scenarios:**
* *Positive:* Input a mocked DataFrame with known rows; assert the output DataFrame matches the expected transformed schema and values.
* *Edge (Empty Data):* Input an empty DataFrame; assert the job completes successfully and writes an empty Delta table without throwing a NullPointerException.
* *Error (Malformed Schema):* Input a DataFrame missing required columns; assert a custom `SchemaValidationException` is logged and the job fails gracefully.


* **Dependencies:** US-13.2, US-14.1
* **Definition of Done:** PySpark logic is unit-tested, deployed to the dev Databricks workspace, orchestrated via the abstraction layer, and successfully completes a run.
* **Priority:** High

---

## Epic 15: Interoperability

**Objective:** A defensible architecture for cross-engine data consumption.

**US-15.1: Implement Cross-Engine Data Access (External Tables/Federation)**

* **User Story:** As a Data Consumer, I want Snowflake to be able to query the Databricks Delta tables directly (and vice versa), so that I can join data across both engines without duplicating storage.
* **Business Value:** Provides a defensible, low-cost architecture for cross-engine consumption, avoiding the overhead of ETL data movement.
* **Acceptance Criteria:**
* **Given** a Delta table written by Databricks, **When** a query is executed in Snowflake using External Tables (or Iceberg), **Then** the query returns the current data accurately.
* **Given** cross-engine queries, **When** performance is measured, **Then** latency, cost, and operational trade-offs are recorded for documentation.


* **TDD Test Scenarios:**
* *Positive:* Insert a test record via Databricks; execute a Snowflake `SELECT` query via integration tests; assert the new record is returned.
* *Edge (Schema Evolution):* Add a new column in Databricks; execute `ALTER EXTERNAL TABLE REFRESH` programmatically; assert Snowflake returns the new column.
* *Error (Access Denied):* Revoke cloud storage IAM read access from the Snowflake role; assert the Snowflake query fails with an explicit `AccessDenied` error, not a generic timeout.


* **Dependencies:** US-14.2
* **Definition of Done:** Cross-engine query executes successfully in dev, IAM roles are locked down to least-privilege, and performance/cost findings are drafted for Epic 18.
* **Priority:** Medium

---

## Epic 16: Unified Governance & Observability

**Objective:** Platform governance and observability remain consistent even when workloads use different engines.

**US-16.1: Define and Extract Common Metadata Model**

* **User Story:** As a Data Steward, I want a unified metadata extraction pipeline that captures ownership, quality, and lineage from both engines, so that platform governance remains consistent.
* **Business Value:** Ensures data products are discoverable and governed under one standard, regardless of whether they execute on Snowflake or Databricks.
* **Acceptance Criteria:**
* **Given** the AERIS metadata schema, **When** the extraction job runs, **Then** it must parse Snowflake object tags and Databricks Unity Catalog tags into a common JSON format.
* **Given** a transformed table, **When** lineage is requested, **Then** the source and destination are tracked identically for both engines.


* **TDD Test Scenarios:**
* *Positive (Snowflake extraction):* Mock a Snowflake API response containing an owner tag; assert the parser maps it to `aeris_owner_id`.
* *Positive (Databricks extraction):* Mock a Unity Catalog API response; assert the parser maps it to the same `aeris_owner_id`.
* *Error (Missing Tags):* Parse a table with no governance tags; assert the parser flags the table in a `non_compliant_objects` list instead of failing the pipeline.


* **Dependencies:** US-14.1
* **Definition of Done:** Unit tests pass, extraction scripts execute successfully against both engines, and the unified JSON model is validated against a JSON schema.
* **Priority:** High

**US-16.2: Unified Health Metrics Aggregation API**

* **User Story:** As a Platform Operator, I want a single API endpoint exposing health metrics from both engines, so that I can monitor platform observability centrally.
* **Business Value:** Reduces operational overhead by eliminating the need to monitor two separate, disconnected engine dashboards.
* **Acceptance Criteria:**
* **Given** a request to the health API, **When** executed, **Then** it returns active warehouse/cluster counts, current compute costs, and failed jobs for both Snowflake and Databricks.


* **TDD Test Scenarios:**
* *Positive:* API returns a 200 OK with a combined JSON payload containing metrics from both platforms.
* *Negative (Engine Down):* Mock a timeout from the Databricks REST API; assert the unified API returns a 206 Partial Content, successfully displaying Snowflake metrics alongside a "Databricks: Unavailable" status.


* **Dependencies:** US-14.1
* **Definition of Done:** API is deployed, Swagger/OpenAPI spec is generated, and a test dashboard successfully consumes the endpoint.
* **Priority:** Medium

---

## Epic 17: Workload Placement

**Objective:** Engine selection becomes an engineering decision rather than a technology preference.

**US-17.1: Develop Workload Placement Decision Framework**

* **User Story:** As a Platform Architect, I want a decision framework, so that engineering teams can objectively evaluate performance, cost, and ecosystem requirements to determine whether a workload belongs in Snowflake or Databricks.
* **Business Value:** Transforms engine selection from a subjective preference into a defensible engineering decision.
* **Acceptance Criteria:**
* **Given** a new workload request, **When** evaluating placement, **Then** the framework must provide a scoring rubric for scalability, data locality, operational complexity, and cost.
* **Given** the framework, **When** applied to the workloads built in Epics 13/14, **Then** the framework accurately justifies their current placement.


* **TDD Test Scenarios:**
* *Positive (CI Lint):* CI script validates the presence of sections for: "Characteristics", "Performance", "Cost", and "Ecosystem Requirements".
* *Edge (Ties):* Manual test simulation: Apply the framework to a theoretical workload that scores equally on both engines; assert the framework contains a "Tie-Breaker / Default" policy.


* **Dependencies:** US-15.1 (to inform performance/cost realities)
* **Definition of Done:** The framework is documented, approved by the architecture board, and a sample evaluation template is published.
* **Priority:** High

---

## Epic 18: Architecture Review

**Objective:** AERIS demonstrates platform-level architectural decision making.

**US-18.1: Formalize Multi-Engine & Interoperability ADRs**

* **User Story:** As a Lead Engineer, I want to document the architectural decisions regarding multi-engine interoperability, governance, and operational ownership, so that future development aligns with these platform-level decisions.
* **Business Value:** Institutionalizes the knowledge and trade-offs discovered during Epics 13-17 into persistent Architecture Decision Records.
* **Acceptance Criteria:**
* **Given** the completed interoperability implementations, **When** creating the ADR, **Then** it must explicitly detail the chosen method (e.g., Open Formats/Iceberg) and rejected alternatives.
* **Given** governance requirements, **When** creating the ADR, **Then** operational ownership boundaries between Platform Engineering and Data Engineering must be defined.


* **TDD Test Scenarios:**
* *Positive (CI Validation):* ADR markdown files pass strict regex checks for standard ADR headers: `Context`, `Decision`, `Consequences`, and `Status`.
* *Error (Invalid Status):* Commit an ADR with a status of "Drafting" instead of accepted statuses (Proposed, Accepted, Rejected); assert the CI pipeline fails.


* **Dependencies:** Epics 13, 14, 15, 16, 17.
* **Definition of Done:** All five specified ADRs are merged into the `main` branch of the architecture repository and socialized with the engineering organization.
* **Priority:** High

---

## Epic 19: Secure Credential & Secrets Management

**Objective:** The platform can authenticate securely to external engines without leaking secrets into environment variables or source control.

**US-19.1: Define SecretsManager Interface & Environment Provider**

* **User Story:** As a Platform Security Engineer, I want a standardized `SecretsManager` interface, so that I can abstract the retrieval of database credentials and access tokens from the underlying execution logic.
* **Business Value:** Decouples credential management from application code, paving the way for cloud-native secret store integration (e.g., Key Vault) without refactoring the executors.
* **Acceptance Criteria:**
* **Given** a request for a database credential, **When** the `SecretsManager.get_secret()` method is called, **Then** it securely returns the expected string.
* **Given** a missing secret, **When** the method is called, **Then** a `SecretNotFoundException` is raised immediately.


* **TDD Test Scenarios:**
* *Positive:* Mock an environment variable `SNOWFLAKE_PASS`; call `get_secret("SNOWFLAKE_PASS")`; assert it returns the correct value.
* *Negative:* Call `get_secret("NON_EXISTENT_SECRET")`; assert `SecretNotFoundException` is raised.
* *Edge:* Store an empty string as a secret; assert `SecretNotFoundException` or `InvalidSecretException` is raised to prevent invalid authentications.


* **Dependencies:** None.
* **Definition of Done:** `SecretsManager` abstract class and `EnvVarSecretsProvider` are implemented. Unit tests pass. No hardcoded credentials exist in the codebase.
* **Priority:** High

**US-19.2: Implement Execution Credential Masking**

* **User Story:** As a Platform Operator, I want all dynamically injected credentials to be explicitly masked in platform logs, so that sensitive tokens are not inadvertently leaked into observability tools.
* **Business Value:** Ensures strict compliance with enterprise security and DevSecOps guidelines.
* **Acceptance Criteria:**
* **Given** an execution log containing a connection string, **When** the log is written, **Then** the password/token portion is replaced with `***`.


* **TDD Test Scenarios:**
* *Positive:* Pass a mock connection URL `user:mySecret123@host` to the logger; assert the output matches `user:***@host`.
* *Negative:* Pass a payload containing no secrets to the logger; assert the original payload is logged unmodified.


* **Dependencies:** US-19.1
* **Definition of Done:** Log formatter is updated with a regex-based masking utility. Tests pass.
* **Priority:** High

---

## Epic 20: Snowflake Live Integration

**Objective:** AERIS can successfully execute live SQL payloads and retrieve operational metadata from a real Snowflake virtual warehouse.

**US-20.1: Implement Live Snowflake Executor via Python Connector**

* **User Story:** As a Data Engineer, I want the `SnowflakeExecutor` to use the official `snowflake-connector-python` to connect and execute queries, so that the platform can drive live database workloads.
* **Business Value:** Transforms the orchestrator from a mocked abstraction into a fully functional SQL execution engine.
* **Acceptance Criteria:**
* **Given** valid Snowflake credentials and a SQL payload, **When** `ExecuteWorkload` runs, **Then** it authenticates, executes the query, closes the cursor/connection securely, and returns a success payload containing affected row counts.


* **TDD Test Scenarios:**
* *Positive:* Mock the `snowflake.connector.connect` and `cursor.execute` methods; pass a valid `SELECT 1`; assert the executor returns a success dictionary containing `rows_processed`.
* *Negative:* Mock an invalid SQL query response; assert the executor captures the error and returns a failed status payload.
* *Edge:* Execute a query that returns 0 rows (e.g., an empty `UPDATE`); assert the executor handles the empty result set gracefully without raising a `TypeError`.


* **Dependencies:** US-19.1
* **Definition of Done:** Live execution logic is merged. Unit tests successfully mock the connector. Cursor context managers (`with` blocks) are used to guarantee connection closure.
* **Priority:** High

**US-20.2: Map Engine-Specific Exceptions (Snowflake)**

* **User Story:** As a Platform Architect, I want Snowflake-specific operational errors (like warehouse suspension delays or syntax errors) to be mapped to standard AERIS exception classes, so that the orchestrator can respond uniformly regardless of the underlying engine.
* **Business Value:** Standardizes error handling and alerting across all supported platform engines.
* **Acceptance Criteria:**
* **Given** a query timeout, **When** it occurs, **Then** a `snowflake.connector.errors.TimeoutError` is intercepted and re-raised as an `AerisEngineTimeoutException`.


* **TDD Test Scenarios:**
* *Positive:* Mock a `ProgrammingError` (syntax issue); assert it is raised as `AerisWorkloadException`.
* *Positive:* Mock a warehouse suspension error; assert it is raised as `AerisInfrastructureException`.


* **Dependencies:** US-20.1
* **Definition of Done:** Exception mapping dictionary/logic is implemented. Tests assert proper translation of at least 3 core Snowflake errors.
* **Priority:** Medium

---

## Epic 21: Databricks Live Integration

**Objective:** AERIS can orchestrate Databricks clusters, trigger PySpark jobs, and reliably wait for their completion states.

**US-21.1: Implement Databricks Job Trigger**

* **User Story:** As a Data Engineer, I want the `DatabricksExecutor` to utilize the `databricks-sdk` to trigger an existing job via the `run_now` endpoint, so that I can orchestrate live PySpark workloads.
* **Business Value:** Brings Databricks compute into the live orchestration layer.
* **Acceptance Criteria:**
* **Given** a valid Databricks PAT and a Job ID, **When** the executor runs, **Then** it initiates the job and captures the resulting `run_id`.


* **TDD Test Scenarios:**
* *Positive:* Mock `databricks.sdk.WorkspaceClient.jobs.run_now`; assert the executor parses the payload, calls the method, and returns a pending status with the mocked `run_id`.
* *Negative:* Mock a 404 Not Found error for an invalid Job ID; assert it raises an `AerisWorkloadException`.


* **Dependencies:** US-19.1
* **Definition of Done:** SDK implementation is merged. The executor successfully parses JSON payloads containing a `job_id`. Unit tests mock the SDK behavior.
* **Priority:** High

**US-21.2: Asynchronous Job Polling & Error Fetching**

* **User Story:** As a Platform Operator, I want the Databricks executor to asynchronously poll the `run_id` status and fetch logs on failure, so that the platform accurately tracks state transitions (PENDING -> SUCCESS/FAILED) and surfaces debug information.
* **Business Value:** Enables the orchestrator to confirm task completion and aids in rapid incident resolution by pulling relevant logs directly into the platform telemetry.
* **Acceptance Criteria:**
* **Given** an active `run_id`, **When** the executor polls the workspace, **Then** it yields control back to the event loop until the status changes from `PENDING`/`RUNNING` to a terminal state.
* **Given** a `FAILED` job status, **When** detected, **Then** the executor immediately queries the Databricks execution logs and appends the standard error string to the failure exception.


* **TDD Test Scenarios:**
* *Positive:* Mock a sequence of API responses (`PENDING`, `RUNNING`, `SUCCESS`); assert the async polling loop eventually returns a success object.
* *Negative:* Mock a terminal `FAILED` response; assert the polling loop breaks, triggers the log-fetching mock API, and raises an exception containing the mocked stack trace.
* *Edge:* Mock a run that remains `PENDING` longer than the maximum platform timeout; assert an `AerisEngineTimeoutException` is raised.


* **Dependencies:** US-21.1
* **Definition of Done:** Asynchronous polling (`asyncio.sleep`) is implemented. Error-fetching API logic is added. Tests pass using mocked sequential API responses.
* **Priority:** High

---

## Epic 22: Resiliency & Retry Logic

**Objective:** The platform handles external API unreliability gracefully without failing the overarching pipeline.

**US-22.1: Implement Exponential Backoff Decorator**

* **User Story:** As a Platform Engineer, I want an exponential backoff retry mechanism for network interactions, so that the platform is resilient against transient API failures (e.g., HTTP 429 Too Many Requests, temporary disconnects).
* **Business Value:** Prevents spurious pipeline failures that require manual intervention, improving overall platform SLOs.
* **Acceptance Criteria:**
* **Given** a transient API exception, **When** executing a workload, **Then** the platform automatically retries the call up to 3 times, exponentially increasing the wait time between attempts.
* **Given** a non-transient error (e.g., SQL Syntax Error), **When** executing, **Then** it fails immediately without retrying.


* **TDD Test Scenarios:**
* *Positive:* Mock a function that fails twice with a `TransientNetworkError` and succeeds on the third try; assert the decorator eventually returns the success value and logs the retries.
* *Negative:* Mock a function that fails with an `AerisWorkloadException` (syntax); assert the decorator raises the error instantly on the first attempt.
* *Error:* Mock a function that continually fails with transient errors; assert it exhausts the retry limit and finally raises an `AerisInfrastructureException`.


* **Dependencies:** Epics 20, 21 (for defining the transient exception boundaries).
* **Definition of Done:** `@retry_with_backoff` decorator is implemented. It is applied to the core execution methods in both Snowflake and Databricks executors. Unit tests pass.
* **Priority:** High

---

## Epic 23: Live Integration Testing

**Objective:** AERIS maintains high confidence in its live engine connectivity without sacrificing the speed and isolation of its unit tests.

**US-23.1: Establish Integration Testing Framework & Live Fixtures**

* **User Story:** As a QA Engineer, I want a dedicated `tests/integration/` Pytest suite that connects to live Sandbox environments, so that we can validate the full execution chain with real network requests.
* **Business Value:** Verifies that external SDK updates or API changes do not break the AERIS platform, providing absolute confidence in production readiness.
* **Acceptance Criteria:**
* **Given** the integration test command, **When** executed, **Then** it uses secure test credentials to establish real network connections to Snowflake and Databricks.
* **Given** a live Snowflake connection, **When** the test runs, **Then** it physically creates, queries, and asserts data from a temporary table.


* **TDD Test Scenarios:**
* *Positive:* Test executes `SELECT CURRENT_VERSION()` on live Snowflake and asserts a string is returned.
* *Negative:* Pass explicitly invalid credentials to a live integration fixture; assert it raises a concrete authentication failure from the respective SDK.


* **Dependencies:** Epics 19, 20, 21.
* **Definition of Done:** Integration directory is established. `pytest.ini` is configured to skip integration tests by default unless explicitly invoked (e.g., `pytest -m integration`). Tests execute successfully against Sandbox.
* **Priority:** High

**US-23.2: Implement Idempotent Integration Teardown**

* **User Story:** As a Release Manager, I want integration tests to clean up after themselves regardless of success or failure, so that the Sandbox environment is not polluted with hanging jobs or orphaned tables.
* **Business Value:** Ensures automated CI/CD runs remain idempotent and do not run out of cloud resources over time.
* **Acceptance Criteria:**
* **Given** a test creates a Databricks run, **When** the test completes (or crashes), **Then** a Pytest teardown fixture explicitly cancels the job run if it is still active.
* **Given** a test creates a Snowflake table, **When** the test completes, **Then** the teardown fixture executes a `DROP TABLE IF EXISTS`.


* **TDD Test Scenarios:**
* *Positive:* Run an integration test that creates a resource and intentionally assert a `False` statement to fail it; verify the Pytest `yield` teardown block still executes the cleanup scripts.


* **Dependencies:** US-23.1
* **Definition of Done:** `conftest.py` is updated with teardown fixtures utilizing generator blocks. Sandbox environments show 0 orphaned artifacts after a full test suite execution.
* **Priority:** High