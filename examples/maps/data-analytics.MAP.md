---
domain: modern-data-analytics-stacks
description: "Understand how data moves from operational sources through storage, transformation, and orchestration to analyst-facing tools — and how governance keeps it trustworthy"
generated: 2026-08-11
depth: 0
parent: null
leads_to:
  - streaming-architectures
  - data-governance-at-scale
  - platform-engineering
  - ml-feature-engineering
  - data-mesh-organizational-patterns
---

# Modern Data Analytics Stacks

## Orientation

Every organization sits on operational data that only becomes useful when it flows through a deliberate pipeline: captured, stored in queryable formats, transformed into business concepts, orchestrated reliably, and served to the people making decisions. You'll understand each layer of this stack, the tradeoffs driving tool choices, and how they compose into a coherent platform — so you can evaluate architectures, not just memorize vendor names.

## Topics

### ingestion
- **title:** Data Ingestion & Change Capture
- **why:** Nothing downstream works until data reliably moves from source systems into your analytics layer
- **scope:** substantial
- **prereqs:** []
- **status:** not-started

### storage-and-table-formats
- **title:** Storage & Open Table Formats
- **why:** Where and how data is stored determines query performance, cost, and what operations are even possible
- **scope:** deep
- **prereqs:** [ingestion]
- **lesson_file:** 0001-iceberg-metadata-tree.html
- **status:** in-progress

### compute-engines
- **title:** Compute & Query Engines
- **why:** The engine you pick decides what workloads are fast, what's expensive, and how your storage is actually read
- **scope:** substantial
- **prereqs:** [storage-and-table-formats]
- **status:** not-started

### transformation-and-modeling
- **title:** Transformation & Data Modeling
- **why:** Raw ingested data is unusable for analysis — transformation turns it into trusted, business-meaningful tables
- **scope:** substantial
- **prereqs:** [storage-and-table-formats]
- **status:** not-started

### orchestration
- **title:** Orchestration & Pipeline Management
- **why:** Pipelines fail, dependencies shift, schedules slip — orchestration is what makes the whole stack run without manual intervention
- **scope:** substantial
- **prereqs:** [ingestion, transformation-and-modeling]
- **status:** not-started

### serving-and-bi
- **title:** Serving, BI & the Semantic Layer
- **why:** The entire stack exists to put trustworthy answers in front of decision-makers — this is where value is realized
- **scope:** substantial
- **prereqs:** [transformation-and-modeling]
- **status:** not-started

### governance-and-observability
- **title:** Data Governance & Observability
- **why:** Without quality checks, lineage, and access controls, your stack produces confident wrong answers — the most dangerous kind
- **scope:** substantial
- **prereqs:** [transformation-and-modeling, orchestration]
- **leads_to:** [data-governance-at-scale]
- **status:** not-started
