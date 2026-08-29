---
domain: storage-and-table-formats
description: "Deep dive into how analytical data is stored — file formats, table formats, metadata management, and the tradeoffs that determine query speed, cost, and operational complexity"
generated: 2026-08-12
depth: 1
parent: modern-data-analytics-stacks
leads_to:
  - slug: lakehouse-architecture
    why: "Combines the best of data lakes and warehouses — the natural evolution of open table formats"
  - slug: storage-cost-optimization
    why: "Once you understand formats and compaction, optimizing storage cost becomes tractable"
---

# Storage & Open Table Formats

## Orientation

Your data has to live somewhere, and HOW it's stored determines everything downstream: what queries are fast, what operations are possible, how much you pay, and how much operational burden you carry. This sub-map breaks storage into its constituent concerns — from the physical file layout on object storage to the metadata layer that makes it behave like a database table.

## Topics

### object-storage-fundamentals
- **id:** 01M174TQPS85HE7F2EZ0R7KH09
- **title:** Object Storage Fundamentals
- **why:** Every modern analytics stack sits on object storage (S3, GCS, ADLS) — understanding its constraints and strengths is prerequisite to everything else
- **scope:** substantial
- **prereqs:** []

### columnar-file-formats
- **id:** 01M174TQPS2E30N1MYEGNRRZ8E
- **title:** Columnar File Formats (Parquet, ORC)
- **why:** The file format determines compression ratios, read patterns, and which queries can skip data — it's the physical foundation of performance
- **scope:** substantial
- **prereqs:** [object-storage-fundamentals]

### table-format-metadata
- **id:** 01M174TQPS0PX6V614C6042P1Q
- **title:** Table Format Metadata (Iceberg, Delta, Hudi)
- **why:** Open table formats add transactional semantics, schema evolution, and time travel on top of raw files — this is where "data lake" becomes "lakehouse"
- **scope:** deep
- **prereqs:** [columnar-file-formats]

### partitioning-strategies
- **id:** 01M174TQPSND5QFHZNG077E898
- **title:** Partitioning & Clustering Strategies
- **why:** How you partition data determines whether queries read megabytes or terabytes — the single biggest lever for query cost and speed
- **scope:** substantial
- **prereqs:** [columnar-file-formats]

### compaction-and-maintenance
- **id:** 01M174TQPSF6F95WXFXT0VAPRP
- **title:** Compaction & Table Maintenance
- **why:** Without regular maintenance, small files accumulate and metadata bloats — turning fast queries into slow, expensive ones over time
- **scope:** lightweight
- **prereqs:** [table-format-metadata]
