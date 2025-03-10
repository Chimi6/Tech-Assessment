# Modern Data Architecture on AWS

# Table of Contents

1. [Introduction](#introduction)
   - [Background](#background)
   - [Objective](#objective)
2. [Data Architecture Design](#data-architecture-design)
   - [Cataloging & Organizing Data](#cataloging--organizing-data)
     - [Current State](#current-state)
     - [Proposed Strategy](#proposed-strategy)
       - [Bucket Naming Convention](#bucket-naming-convention)
       - [Folder Structure](#folder-structure)
       - [Metadata Tagging & Lineage Manifest](#metadata-tagging--lineage-manifest)
   - [Data Processing & Transformation](#data-processing--transformation)
     - [Tools and Techniques](#tools-and-techniques)
     - [Error Handling](#error-handling)
     - [Logging and Monitoring](#logging-and-monitoring)
     - [Transformation Formats](#transformation-formats)
   - [Storage Layer Organization](#storage-layer-organization)
     - [Data Layers](#data-layers)
     - [Isolation and Security](#isolation-and-security)
   - [Analytics & Reporting Capabilities](#analytics--reporting-capabilities)
     - [Analytics Tools](#analytics-tools)
     - [Reporting Strategy](#reporting-strategy)
   - [Monitoring & Alerting Framework](#monitoring--alerting-framework)
     - [Monitoring Tools](#monitoring-tools)
     - [Alerting Strategy](#alerting-strategy)
3. [Infrastructure as Code Approach](#infrastructure-as-code-approach)
   - [Tool Selection](#tool-selection)
   - [Core Resources](#core-resources)
     - [Data Storage](#data-storage)
     - [Compute Resources](#compute-resources)
     - [Analytics Resources](#analytics-resources)
   - [IAM and Security](#iam-and-security)
     - [Roles and Policies](#roles-and-policies)
     - [Compliance](#compliance)
   - [Tagging, Error Handling, and Documentation](#tagging--error-handling--documentation)
4. [ETL Pipeline Implementation with AWS Glue](#etl-pipeline-implementation-with-aws-glue)
   - [Pipeline Strategy](#pipeline-strategy)
     - [Data Flow](#data-flow)
     - [Automation](#automation)
   - [Advantages & Limitations of AWS Glue for ETL](#advantages--limitations-of-aws-glue-for-etl)
     - [Advantages](#advantages-of-aws-glue)
     - [Limitations](#limitations-of-aws-glue)
     - [My Approach](#my-approach)
   - [Mitigation Strategies](#mitigation-strategies)
     - [Optimization](#optimization)
     - [Fallback Options](#fallback-options)
5. [Analytics and Reporting Solution](#analytics-and-reporting-solution)
   - [Service Selection](#service-selection)
     - [AWS Services](#aws-services)
     - [Integration](#integration)
   - [Key Considerations and Tradeoffs](#key-considerations-and-tradeoffs)
     - [Performance vs. Cost](#performance-vs-cost)
     - [Scalability](#scalability)
     - [Ease of Use](#ease-of-use)


## Introduction
- **Background:** Briefly introduce the client's situation and migration journey.
- **Objective:** Outline the goal of the assessment and the benefits of the proposed solution.

## Data Architecture Design

### Cataloging & Organizing Data
- **Current State:**  
  Currently, data is stored as flat CSV files in S3 buckets, with files segregated by customer. The current setup simply ingests these files without further organization or metadata, making it challenging to track data lineage, processing status, or perform targeted queries.

- **Proposed Strategy:**  
  - **Bucket Naming Convention:**  
    Each customer will have a dedicated S3 bucket named using the format `mycompany-{customerid}-{env}-datalake`, ensuring clear isolation and easy identification.  
  - **Folder Structure:**  
    Within each customer bucket, the structure will be:
    ```
    raw/
       └── (original CSV files)
    processed/
       └── year=YYYY/
              └── month=MM/
                   └── (processed files with schema version metadata)
    analytics-ready/
       └── year=YYYY/
              └── month=MM/
                   └── (curated files optimized for query and analytics)
    ```
  - **Metadata Tagging & Lineage Manifest:**  
    - **S3 Object Tags:** Each file will be tagged with metadata such as file type and upload timestamp.  
    - **Lineage Manifest:** A lightweight manifest (stored in DynamoDB) will track file lineage and processing status, including schema version for processed data.

---

### Data Processing & Transformation
- **Tools and Techniques:**  
  - **AWS Glue:** I will use two AWS Glue ETL jobs in an event-driven architecture:
    - **Job 1:** Triggered by an EventBridge rule when new CSV files are uploaded to the `raw/` folder. This job performs initial processing—such as cleanup, basic transformation, and conversion to JSON—and writes the output to the `processed/` layer.
    - **Job 2:** Triggered by an EventBridge rule when new files appear in the `processed/` folder. This job further transforms the data by converting the JSON output into a columnar format (Parquet) and writes the results to the `analytics-ready/` layer.
  
- **Error Handling:**  
  - AWS Glue jobs come with built-in retry mechanisms and detailed logging. I will rely on job bookmarks and CloudWatch logs to monitor errors and ensure any processing failures are identified and addressed promptly.

- **Logging and Monitoring:**  
  - CloudWatch will capture detailed logs and metrics from the Glue jobs, enabling real-time monitoring and alerting for any failures or anomalies.

- **Transformation Formats:**  
  - The initial processing job converts CSV files into JSON (with added metadata), and the analytics transformation job converts the JSON data into Parquet. This columnar format is optimized for analytical queries, improving performance and reducing query costs.

---

### Storage Layer Organization
- **Data Layers:**  
  - **raw:** Contains the unmodified, ingested CSV files.  
  - **processed:** Contains data that has undergone initial transformation, stored in a structured format (with metadata indicating the schema version), partitioned by year/month.  
  - **analytics-ready:** Contains fully transformed and curated data, optimized for querying and analytics, also partitioned by year/month.
- **Isolation and Security:**  
  - **Customer Isolation:** Each customer’s data is stored in its dedicated S3 bucket, ensuring complete isolation.
  - **Encryption:**  
    - Data will be encrypted at rest using SSE-KMS to provide enhanced key management and auditing capabilities.
    - In-transit encryption will be enforced via HTTPS.
  - **Access Control:**  
    - I will implement strict IAM roles and S3 bucket policies to enforce least-privilege access.  
    - I will use resource-level permissions to restrict access only to authorized services and users.  

### Analytics & Reporting Capabilities
- **Analytics Tools:**  
  I will use **Amazon Athena** as the primary analytics engine. Athena enables serverless, ad-hoc SQL querying directly over the analytics-ready data stored in S3. While I considered Redshift and QuickSight, Athena was selected for its cost-effectiveness and ease of integration with the S3-based data lake. Dashboarding can be implemented with QuickSight or other BI tools if required by the client.

- **Reporting Strategy:**  
  Data in the analytics-ready layer (partitioned by year/month) will be queried using SQL via Athena. This approach supports self-service BI, allowing business users to run ad-hoc queries without provisioning infrastructure. For more advanced reporting or dashboards, the output from Athena can be integrated with tools like Amazon QuickSight.

---

### Monitoring & Alerting Framework
- **Monitoring Tools:**  
  - **AWS CloudWatch:** To capture logs and metrics from all Glue Jobs, monitor S3 bucket activity, and track DynamoDB operations.
  - **AWS Config & CloudTrail:** For auditing resource configurations and tracking API calls, ensuring compliance and data integrity.

- **Alerting Strategy:**  
  - CloudWatch Alarms will be configured to trigger on key metrics such as Glue error counts, invocation failures.
  - Notifications can be sent through Amazon SNS to alert the operations team of any critical issues in the data pipelines.
  - Alerts will cover processing failures, unusual data latencies, or any deviations from expected patterns in the pipeline.

---



## Infrastructure as Code Approach

### Tool Selection
- **Chosen IaC Tools:**  
  I will use a combination of **AWS CDK (in Python)** and traditional **CloudFormation stacks**.

- **Rationale:**  
  The **AWS CDK** is ideal for dynamically scaling resources—such as customer-specific S3 buckets—since it allows me to programmatically loop over customer configurations from a JSON file and create multiple similar resources with ease. For the more stable components of the infrastructure (such as AWS Glue, and the DynamoDB manifest table), traditional **CloudFormation stacks** provide a straightforward and well-understood approach for defining and deploying these resources. This hybrid approach leverages the flexibility of CDK where dynamic scaling is required while maintaining a consistent deployment model for the base infrastructure.

### Core Resources
- **Data Storage:**  
  - **S3 Buckets:** Dedicated buckets per customer (with folders for `raw/`, `processed/`, and `analytics-ready/`), configured with SSE-KMS encryption.
  - **DynamoDB:** A table to serve as a lineage manifest that tracks file processing metadata (e.g., file type, upload timestamps, schema versions).

- **Compute Resources:**  
  - **Glue Jobs:** Two functions to handle data processing:  
    - **process_csv.py:** Converts CSV files from the `raw/` folder into JSON, adds metadata, and writes to the `processed/` folder.
    - **analytics_transform.py:** Transforms JSON data from the processed layer into a columnar format (Parquet) in the `analytics-ready/` folder.
  - Both functions incorporate error handling via a Dead Letter Queue (DLQ).

- **Analytics Resources:**  
  - **Amazon Athena:** Enables serverless SQL queries over the analytics-ready S3 data, supporting ad-hoc queries and integration with BI tools.

### IAM and Security
- **Roles and Policies:**  
  - IAM roles are defined with least-privilege access for Glue jobs to interact with S3 buckets and DynamoDB.  
  - Resource-level policies ensure that each customer's bucket is only accessible to authorized services and users.

- **Compliance:**  
  - Data at rest is secured using SSE-KMS encryption on all S3 buckets.  
  - In-transit encryption is enforced via HTTPS.  
  - CloudTrail and AWS Config are used to audit changes and monitor resource configurations to ensure compliance with internal and regulatory requirements.

### Tagging, Error Handling, and Documentation
- **Tagging Strategy:**  
  Resources are tagged with identifiers for project name, environment (e.g., prod, dev), and owner, supporting cost allocation and resource management.

- **Error Handling:**  
  - AWS Glue jobs are configured with built-in retry mechanisms and detailed logging to CloudWatch. 
  - Errors are logged using CloudWatch Logs, and alarms are set up to trigger notifications via SNS on critical failures.
  - The data processing pipeline is designed with retries and error notifications to ensure resiliency.

- **Documentation:**  
  - All infrastructure code is documented inline (in both the CDK and CloudFormation templates) to explain resource configurations and design decisions.

## ETL Pipeline Implementation with AWS Glue

### Pipeline Strategy
- **Data Flow:**  
  - **Ingestion:** Data is ingested as flat CSV files into the S3 `raw/` folder.
  - **Transformation:** Two Glue Jobs process the data in stages:
    1. **ProcessCSVFunction:** Reads CSV files from the `raw/` folder, performs basic cleaning, converts rows to JSON (adding metadata such as a processed timestamp), and writes the output to the `processed/` folder (organized by year/month).
    2. **AnalyticsTransformFunction:** Reads the JSON data from the `processed/` folder, converts it to a columnar format (Parquet), and writes the output to the `analytics-ready/` folder (partitioned by year/month).
  - **Loading:** The transformed data is stored in the analytics-ready layer for querying via Amazon Athena.

- **Automation:**  
  The pipeline is fully automated using an event-driven architecture. S3 event notifications trigger the Glue jobs immediately upon file arrival utilizing event bridge, ensuring near-real-time processing. CloudWatch monitors the pipeline, and retries along with a Dead Letter Queue (DLQ) are in place to handle any processing failures.

### Advantages & Limitations of AWS Glue for ETL
- **Advantages of AWS Glue:**  
  - **Serverless and Scalable:** AWS Glue is a fully managed, serverless ETL service that automatically scales to accommodate large data volumes, eliminating the need to provision or manage infrastructure.
  - **Integrated Data Catalog:** It seamlessly integrates with the AWS Glue Data Catalog, enabling automatic schema discovery and centralized metadata management for efficient data processing.
  - **Rich Transformation Capabilities:** Built on Apache Spark, Glue supports complex, computationally intensive transformations and a wide range of built-in data transformations.
  - **Job Bookmarks and Detailed Logging:** Glue provides job bookmarks for incremental processing and detailed CloudWatch logging, making it easier to track job progress, monitor failures, and troubleshoot issues.

- **Limitations of AWS Glue:**  
  - **Startup Latency:** Glue jobs may incur startup delays, which can affect processing in scenarios that require near-real-time data handling.
  - **Cost Considerations:** While cost-effective for large-scale processing, Glue can be more expensive for smaller or infrequent workloads due to its Spark-based processing model.
  - **Overhead for Simple Tasks:** For very straightforward ETL tasks, the complexity and overhead of a Spark-based Glue job might be more than what is required.

  
- **My Approach:**  
  Given the current requirements, AWS Glue is the optimal choice for the ETL pipeline. It provides a robust and scalable solution for processing CSV/JSON files and converting them into analytics-ready formats using a managed Spark environment. I will monitor job performance and adjust configurations as needed. If future data volumes or transformation complexity increase, I can reevaluate the approach to ensure continued efficiency and cost-effectiveness.


### Mitigation Strategies
- **Optimization:**  
  - **Partitioning:** Output data is partitioned by year and month to improve query performance and manageability.
  - **Resource Tuning:** Monitor Glue job performance using CloudWatch metrics and adjust job parameters—such as allocated DPUs and timeout settings—as needed.

- **Fallback Options:**  
  - If data volumes or transformation complexity increase significantly, I may consider integrating additional orchestration tools or further optimizing Glue job configurations to handle larger workloads while maintaining efficiency and cost-effectiveness.


## Analytics and Reporting Solution

### Service Selection
- **AWS Services:**  
  I have selected **Amazon Athena** as the primary analytics service. Athena is a serverless query engine that allows me to run standard SQL queries directly on data stored in the S3 analytics-ready layer. This decision was based on its ease of use, cost-effectiveness for ad-hoc queries, and seamless integration with the S3-based data lake. While services like Redshift offer high-performance data warehousing and QuickSight provides rich visualization capabilities, Athena meets the current requirements for self-service BI and rapid query development. Athena also provides easily accessible queryable data that prepares the solution for further analytics as well as ML/AI consumption.

- **Integration:**  
  - **Data Storage:** The analytics-ready data is stored in S3 with partitions (year/month) to optimize query performance.
  - **Query Access:** Athena directly queries the S3 data without the need for ETL or data movement.
  - **BI Integration:** Athena can integrate with BI tools (e.g., Amazon QuickSight) to provide visualization and reporting, supporting self-service analytics for business users.
  - **AI/ML:** Athena provides easy data consumption for future tooling such as AI and ML offerings.

---

### Key Considerations and Tradeoffs
- **Performance vs. Cost:**  
  - **Performance:** Athena is highly performant for ad-hoc, interactive queries, especially when data is well-partitioned and optimized. However, for extremely high query loads or very complex analytical workloads, performance might be lower compared to a dedicated data warehouse like Redshift.
  - **Cost:** Athena operates on a pay-per-query model, which makes it cost-effective for infrequent or ad-hoc queries. Over time, heavy query usage might incur higher costs, so monitoring and cost optimization strategies (such as optimizing file formats and partitions) are essential.

- **Scalability:**  
  - **Storage Scalability:** S3 scales virtually without limits, ensuring that the analytics-ready layer can handle significant data growth.
  - **Query Scalability:** Athena scales automatically with query demand. With proper partitioning and query optimization, it can support increasing workloads while maintaining performance.
  
- **Ease of Use:**  
  - **Self-Service BI:** Athena’s SQL interface makes it accessible to business users and data analysts, lowering the barrier to entry for self-service BI.
  - **Integration with Visualization Tools:** Athena integrates natively with visualization services like Amazon QuickSight, allowing for easy dashboard creation and reporting.
  - **Minimal Operational Overhead:** As a fully managed service, Athena reduces the need for infrastructure management, letting teams focus on data analysis rather than maintenance.
