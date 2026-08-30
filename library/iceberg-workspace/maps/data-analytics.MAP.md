---
domain: data-analytics
description: "Understand how data moves from operational sources through storage, transformation, and orchestration to analyst-facing tools — and how governance keeps it trustworthy"
generated: 2026-08-11
depth: 0
parent: null
leads_to:
  - slug: streaming-architectures
    why: "Real-time version of batch ingestion — same concepts, tighter latency constraints"
  - slug: data-governance-at-scale
    why: "The observability topic here, expanded to org-wide policy and compliance"
  - slug: platform-engineering
    why: "Who builds, operates, and abstracts the stack you just learned"
  - slug: ml-feature-engineering
    why: "Uses the same storage and transformation layers to feed ML models"
  - slug: data-mesh-organizational-patterns
    why: "Decentralizes ownership of the pipeline you learned as a single team's concern"
---

# Modern Data Analytics Stacks

## Orientation

Every organization sits on operational data that only becomes useful when it flows through a deliberate pipeline: captured, stored in queryable formats, transformed into business concepts, orchestrated reliably, and served to the people making decisions. You'll understand each layer of this stack, the tradeoffs driving tool choices, and how they compose into a coherent platform — so you can evaluate architectures, not just memorize vendor names.

## Topics

### ingestion
- **id:** 01M174TQPPZFGSZT3DJNFGXHZ9
- **title:** Data Ingestion & Change Capture
- **why:** Nothing downstream works until data reliably moves from source systems into your analytics layer
- **scope:** substantial
- **prereqs:** []
- **lesson_file:** 0002-data-ingestion-change-capture.html

### storage-and-table-formats
- **id:** 01M174TQPPD0TDSBXSM79ZBZ73
- **title:** Storage & Open Table Formats
- **why:** Where and how data is stored determines query performance, cost, and what operations are even possible
- **scope:** deep
- **prereqs:** [ingestion]
- **lesson_file:** 0001-iceberg-metadata-tree.html

### compute-engines
- **id:** 01M174TQPPQC00AS015ZGRV1R3
- **title:** Compute & Query Engines
- **why:** The engine you pick decides what workloads are fast, what's expensive, and how your storage is actually read
- **scope:** substantial
- **prereqs:** [storage-and-table-formats]

### transformation-and-modeling
- **id:** 01M174TQPP4NSA7HE1FG1ZHHYC
- **title:** Transformation & Data Modeling
- **why:** Raw ingested data is unusable for analysis — transformation turns it into trusted, business-meaningful tables
- **scope:** substantial
- **prereqs:** [storage-and-table-formats]

### orchestration
- **id:** 01M174TQPPPS80V8ZSSXTHTSWK
- **title:** Orchestration & Pipeline Management
- **why:** Pipelines fail, dependencies shift, schedules slip — orchestration is what makes the whole stack run without manual intervention
- **scope:** substantial
- **prereqs:** [ingestion, transformation-and-modeling]

### serving-and-bi
- **id:** 01M174TQPP4Z1ADE34PFAX1GWJ
- **title:** Serving, BI & the Semantic Layer
- **why:** The entire stack exists to put trustworthy answers in front of decision-makers — this is where value is realized
- **scope:** substantial
- **prereqs:** [transformation-and-modeling]

### governance-and-observability
- **id:** 01M174TQPPM488YV8AA7M4TC7E
- **title:** Data Governance & Observability
- **why:** Without quality checks, lineage, and access controls, your stack produces confident wrong answers — the most dangerous kind
- **scope:** substantial
- **prereqs:** [transformation-and-modeling, orchestration]
- **leads_to:** [data-governance-at-scale]
