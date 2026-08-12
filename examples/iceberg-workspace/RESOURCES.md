# Apache Iceberg on AWS — Resources

## Primary Sources

| Resource | Type | Trust | Status | Use for |
|----------|------|-------|--------|---------|
| [Apache Iceberg Table Spec](https://iceberg.apache.org/spec/) | Spec | Authoritative | ✅ Current (V3, Aug 2025) | Ground truth for metadata structure, terminology, format details |
| [Apache Iceberg Docs (latest)](https://iceberg.apache.org/docs/latest/) | Docs | Authoritative | ✅ Current | Configuration, API, engine DDL syntax, table properties |
| [AWS Prescriptive Guidance: Iceberg on AWS](https://docs.aws.amazon.com/prescriptive-guidance/latest/apache-iceberg-on-aws/introduction.html) | Guide | High | ✅ Updated 2025 | AWS-specific architecture, service integration, best practices |
| [Amazon SageMaker Lakehouse — Iceberg](https://docs.aws.amazon.com/sagemaker-lakehouse-architecture/latest/userguide/lakehouse-iceberg.html) | Docs | High | ✅ Current | Glue REST Catalog API, S3 Tables, unified lakehouse layer |
| [Game Programming Patterns: Game Loop](https://gameprogrammingpatterns.com/) | Book (free) | High | ✅ Evergreen | Analogy resource — Iceberg's OCC commit cycle parallels game state management |

## Practitioner Sources

| Resource | Type | Trust | Notes |
|----------|------|-------|-------|
| [IOMETE: Iceberg Metadata Management](https://iomete.com/resources/reference/iceberg-metadata-management) | Blog | Medium-high | Real production numbers on metadata growth rates, maintenance scheduling |
| [RisingWave: Iceberg Pitfalls](https://risingwave.com/) | Blog | Medium | Practitioner warnings about small files, delete file accumulation |
| [Onehouse: Table Format Comparison](https://www.onehouse.ai/) | Vendor blog | Medium | ⚠️ Hudi-affiliated vendor but comparison data is useful |
| [Dremio: Iceberg Best Practices](https://www.dremio.com/) | Vendor blog | Medium | Iceberg-affiliated but practical maintenance guidance |
| [Berkeley LHBench](https://github.com/microsoft/LHBench) | Benchmark | High | TPC-DS comparison: Delta 1.7x faster than Iceberg on queries; engine matters more than format |

## AWS-Specific Facts (verified 2025-2026)

| Fact | Source | Implication |
|------|--------|-------------|
| Glue REST Catalog is GA | AWS docs | Non-AWS engines (Trino, Snowflake) can access via standard Iceberg REST spec |
| S3 Tables (managed Iceberg) GA Dec 2024 | AWS re:Invent 2024 | 3x query throughput claimed, 10x TPS — but you lose S3 bucket control |
| Write concurrency ~15 TPS | Practitioner reports + AWS limits docs | Hard limit on catalog pointer updates. Serialized OCC commits. |
| Athena: merge-on-read ONLY | AWS docs | No copy-on-write option. Affects update/delete performance. |
| Iceberg V3 supported (Nov 2025) | AWS blog | Deletion vectors + row lineage across EMR 7.12, Glue, SageMaker |
| 5 mandatory maintenance operations | Iceberg docs + practitioner consensus | expire_snapshots → remove_orphan_files → rewrite_manifests → rewrite_data_files → remove_delete_files. Order matters. |
| Firehose Iceberg delivery capped at 5 MiB/s | AWS docs | Not suitable for high-throughput streaming without fan-out |

## When Iceberg Does NOT Fit

| Scenario | Why not | Better alternative |
|----------|---------|-------------------|
| Small data (< 100 GB) | Metadata overhead adds friction with zero benefit | Plain Parquet + Athena |
| Databricks-native shop | Delta is tighter integrated; UniForm bridges external readers | Delta Lake |
| Real-time / sub-second visibility | Batch atomicity model delays visibility | Hudi (or streaming-native store) |
| High-frequency keyed upserts | Record-level index needed; Iceberg rewrites entire files | Hudi MOR |
| Simple append-only workload | No need for snapshots, time travel, schema evolution | Raw Parquet + Glue Crawler |
| Wide/sparse schemas (observability, 1000+ columns) | Per-column stats in manifests bloat | Specialized formats or column pruning |

## Communities

| Community | Why | Link |
|-----------|-----|------|
| Apache Iceberg Slack | High-signal, core committers active | https://iceberg.apache.org/community/ |
| r/dataengineering | War stories, architecture critiques, vendor-neutral | https://reddit.com/r/dataengineering |
| Iceberg Summit (annual) | Advanced patterns, production case studies | https://iceberg.apache.org/ |

## Gaps Still Open

- No verified end-to-end AWS PoC tutorial (Glue catalog → ingest → query → maintenance) — may need to build
- S3 Tables pricing vs self-managed cost comparison not independently verified
- FSRS-4.5 parameter tuning for table format concepts (how fast do learners forget metadata tree details vs operational patterns?)
