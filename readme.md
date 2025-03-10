# Context
This repo contains resources pertaining to my technical assessment. This includes:
- Architectural Diagram "arch.drawio.png"
- Sample code snippets including: GitHub Actions workflows, AWS CDK code, CloudFormation stacks, Glue jobs, and necessary config files.
- Given that the focus was on the architecture and sample data was not provided, I used a very simple data example and, subsequently, simple transformation jobs to accompany this data. This was to highlight what an example might look like while taking into account how this could scale and be incorporated with future development.
- I haven't run/debugged the sample code snippets I provide. They are better interpreted as pseudo code that shows my thought process and helped me to better visualize the system I was designing.
- In this readme I will provide high-level decisions I made. For further detail on the specifics of the individual pieces, please view "WriteUp.md."
- For the example data transformation I show in this flow, I chose a CSV as the example file. It is a simple structure and can be viewed at `SampleCsvData/sample.csv`.

# Assumptions
- The exercise stated that the client has already migrated the files into S3. However, there might be a future need to add new users, migrate additional data, etc. I wrote a CDK deployment process that addresses this concern.
- S3 buckets should be private and encrypted at rest.
- Data should be encrypted in transit.
- Each company needs its own bucket for data isolation.

## Strategy for Cataloging/Organizing S3 Files
Each company's bucket needs three high-level directories:
- **Raw:** This is where we dump new files from customers that need to be processed.
- **Processed:** Once the initial data processing—such as normalization and addition of calculated values—is completed, the file is moved here.
  - Within the directory, we will organize by year/month.
- **Analytics-ready:** Once files are optimized for consumption by Athena, they are stored here.
  - Within the directory, we will organize by year/month.

**Bucket Name:** `mycompany-{customerid}-{env}-datalake`


    Bucket Name: mycompany-{customerid}-{env}-datalake
    ├── raw/
    │   ├── file1.csv
    │   └── file2.csv
    ├── processed/
    │   └── year=YYYY/
    │       └── month=MM/
    │              └── file_processed.json
    └── analytics-ready/
        └── year=YYYY/
              └── month=MM/
                    └── file.parquet


## Data Processing and Transformation Approach
I decided it would make the most sense, given the requirements of the customer, to use an event-driven approach to our ETL process. I utilize EventBridge triggers to invoke Glue jobs that process and move the data. Additional triggers and Glue jobs can be implemented, which allows the ability to scale the capacity of our ETL process. The data will be encrypted both at rest in the private S3 buckets as well as in transit by utilizing HTTPS, and least privilege permissions will be defined on each resource to secure our environment. Glue provides built-in retries and great logging capabilities with CloudWatch. With proper alerting (set up with SNS), we will have clarity for enhancing the reliability of our ETL process.

## Infrastructure as Code
I chose to take a hybrid approach with the IaC tools.

### CDK
Given the dynamic creation needs for S3 buckets, it seems pertinent to use CDK as the IaC tool of choice. This allows us to provide a list of customers which can be used to iteratively spin up as many buckets as necessary. Given that we might have hundreds and potentially thousands of customers, this is a much more sustainable approach than standard CloudFormation.

### CloudFormation
For the rest of the base infrastructure, I have opted for using CloudFormation. Given the general stability of these resources, the simplicity and developmental ease of CloudFormation makes this a more palatable approach.

### GitHub Actions
I will be utilizing GitHub Actions as a means to orchestrate and handle this deployment. I have written the initial sample workflows using `workflow_dispatch` as the trigger so that we can choose to deploy as needed. These workflows orchestrate the steps, as well as enable the IaC by passing values from files and handling adjacent steps such as uploading the Glue jobs to an S3 bucket that the CF stacks can then reference.

IAM permissions/roles are set in the stacks and can be configured to narrow permissions down to a least privileged approach.

I have provided four sample CF scripts as well as the CDK script to showcase a simple version of what these resources might look like. The CF stacks can be found in the `SampleIAC` directory. The CDK script can be found under the `lib` directory.

## ETL Pipeline Implementation with AWS Glue

### Pipeline Strategy
I am using an event-driven approach with triggers set through EventBridge upon creation of items in specific folders in the data lake. We have three main directories that dictate our dataflow. Raw data triggers the phase one of our pipeline; this would be an AWS Glue job that will do the initial processing/normalization of our data. Once this process is completed, it will drop the new file into the `/processed` directory. The creation of an item in the `/processed` directory will trigger an additional Glue job that will then optimize our data as preparation for analytics ingestion. Data lineage and metadata on the etl process are stored in a lightweight dynamo db database. 

With the current architecture, we can define additional jobs and triggers based on directory structure or, potentially, tags as needed. If the pipeline complexity increases, it could potentially be wise to set up a stronger form of orchestration through Lambda or Step Functions.

### AWS Glue

#### Advantages
- Serverless, allowing for automatic scalability correlating to the data volume.
- Reduces the amount of managed infrastructure in our environment.
- Built-in bookmarks and logging.

#### Limitations
- Is not able to use a direct trigger.
- Less flexibility around reliability/logging given it is a hosted service.
- Startup latency.
- Code needs to be done in a Spark-based environment.
- Potentially higher cost.

#### Addressing Potential Challenges
- Fine-tuning resource allocation/effective partitioning can assist with both latency and cost.
- Increasing our understanding of Spark will help us simplify and optimize our ETL scripts.
- Additional orchestration tools can help mitigate complexity and manage the workload effectively.

### Analytics and Reporting Solution

#### Approach Summary
I chose to go forward with AWS Athena. Athena lets us run queries directly over our S3 data lake. This simplifies our infrastructure, lowers complexity, and helps to optimize costs. Additionally, Athena puts us in a great position for future development by allowing us to build BI tools and various AI/ML tools pulling straight through Athena queries.

#### Key Considerations
- Cost efficiency
- Ease of use through the SQL interface
- Self-service capacity 
- Automatic scalability
- AWS native capabilities/integrations

#### Trade-offs
- Redshift has higher performance for highly complex data sets.
- Redshift has enhanced workload management.
