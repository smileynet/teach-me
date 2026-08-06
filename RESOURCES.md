# Apache Iceberg on AWS — Resources

## Knowledge

- [Apache Iceberg Table Spec](https://iceberg.apache.org/spec/)
  The formal specification of the Iceberg table format. Use for: understanding metadata layers, snapshot isolation, manifest files, partition evolution. The source of truth.

- [Apache Iceberg Docs (latest)](https://iceberg.apache.org/docs/latest/)
  Official docs covering configuration, API, engine integrations. Use for: hands-on configuration, Spark/Flink DDL syntax, table properties.

- [AWS Prescriptive Guidance: Using Apache Iceberg on AWS](https://docs.aws.amazon.com/prescriptive-guidance/latest/apache-iceberg-on-aws/introduction.html)
  Comprehensive AWS-specific guide covering architecture, service integration, and best practices. Use for: which AWS services to use where, reference architectures, operational guidance. Also available as [PDF](https://docs.aws.amazon.com/pdfs/prescriptive-guidance/latest/apache-iceberg-on-aws/apache-iceberg-on-aws.pdf).

- [AWS: What is Apache Iceberg?](https://aws.amazon.com/what-is/apache-iceberg/)
  AWS explainer of Iceberg fundamentals. Use for: quick reference on core concepts from an AWS lens.

- [Amazon SageMaker Lakehouse Architecture — Iceberg Support](https://docs.aws.amazon.com/sagemaker-lakehouse-architecture/latest/userguide/lakehouse-iceberg.html)
  The new unified lakehouse layer (Glue Data Catalog + Lake Formation + Iceberg REST API). Use for: understanding AWS's current recommended architecture, automated table optimization.

- [Confluent: Apache Iceberg Course (free)](https://developer.confluent.io/courses/apache-iceberg/introduction/)
  14-module video course by Tim Berglund covering architecture, catalogs, time travel, schema evolution. Use for: conceptual grounding with visuals, streaming integration context.

- [AWS Prescriptive Guidance: Best Practices (General)](https://docs.aws.amazon.com/prescriptive-guidance/latest/apache-iceberg-on-aws/best-practices-general.html)
  Compression, file sizing, partitioning, compaction recommendations. Use for: operational tuning decisions.

## Wisdom (Communities)

- [Apache Iceberg Slack](https://iceberg.apache.org/community/)
  Official Slack workspace. High-signal, core committers active. Use for: implementation questions, edge cases, catalog behavior.

- [r/dataengineering](https://reddit.com/r/dataengineering)
  Active subreddit covering real-world lakehouse builds. Use for: war stories, architecture critiques, vendor-neutral perspectives.

- [Iceberg Summit (annual conference)](https://iceberg.apache.org/blog/announcing-iceberg-summit-2026/)
  Practitioner-focused conference. Use for: advanced patterns, production case studies.

## Gaps

- No hands-on tutorial found yet that walks through a complete AWS PoC end-to-end (Glue catalog → ingestion → query → compaction) — may need to build this ourselves as we go.
