<p align="center">
  <img src="assets/images/roofgrid-wordmark.png" alt="RoofGrid" width="260">
</p>

<h1 align="center">RoofGrid</h1>

<p align="center">
  <strong>An AWS-native rooftop solar planning platform.</strong>
</p>

<p align="center">
  Detect rooftops, design practical panel layouts, estimate solar output and financial impact, and ask an AI assistant—all through a serverless AWS architecture.
</p>

![RoofGrid AWS solar planning architecture](assets/architecture/roofgrid-aws-architecture.png)

## What RoofGrid does

RoofGrid turns a location and rooftop into an early-stage solar plan:

1. Search for a property or navigate to it on the map.
2. detect the building footprint from satellite and map data;
3. draw or refine the usable roof boundary;
4. reserve access paths and exclude rooftop obstacles;
5. place panels using configurable dimensions, spacing, and orientation;
6. calculate energy, cost, savings, payback, and avoided emissions; and
7. ask the AWS-hosted AI assistant questions about the plan.

> RoofGrid's application, compute, AI/ML, storage, orchestration, security, and observability layers run on AWS. The only external data dependencies are map/building data and the NASA POWER public API.

## AWS architecture

A browser request enters through **AWS Amplify Hosting** and is routed over HTTPS to **Amazon API Gateway**. **AWS Lambda** performs the backend work and coordinates longer-running analysis through **AWS Step Functions**. Rooftop detection uses **Amazon SageMaker AI**, while the conversational planning assistant runs on **Amazon Bedrock**.

Project records and usage counters are stored in **Amazon DynamoDB**. Satellite inputs, generated reports, and analysis artifacts are stored in **Amazon S3**. **AWS Secrets Manager** protects private configuration, and **AWS Identity and Access Management (IAM)** enforces least-privilege access between every service. **Amazon CloudWatch** centralizes logs, metrics, and diagnostics, while **Amazon EventBridge** carries asynchronous events between workflow components.

### AWS services used

| AWS service | Role in RoofGrid |
| --- | --- |
| **AWS Amplify Hosting** | Hosts and continuously deploys the web application from GitHub. |
| **Amazon API Gateway** | Publishes the HTTPS `/api/*` interface, CORS policy, and request throttling. |
| **AWS Lambda** | Runs serverless backend logic for rooftop analysis, solar calculations, data processing, AI requests, and project operations. |
| **AWS Step Functions** | Orchestrates the asynchronous rooftop-analysis workflow and coordinates downstream AI/ML tasks. |
| **Amazon SageMaker AI** | Detects and analyzes building rooftops from satellite imagery. |
| **Amazon Bedrock** | Powers the in-product AI assistant for solar-planning questions and result explanations. |
| **Amazon DynamoDB** | Stores project metadata, application state, and daily AI-usage counters. |
| **Amazon S3** | Stores satellite imagery, generated reports, and rooftop-analysis results. |
| **AWS Secrets Manager** | Keeps private backend configuration out of source code and frontend bundles. |
| **AWS IAM** | Applies least-privilege permissions to Lambda, Bedrock, SageMaker AI, DynamoDB, S3, and workflow resources. |
| **Amazon CloudWatch** | Collects logs, metrics, alarms, and runtime diagnostics across the platform. |
| **Amazon EventBridge** | Delivers asynchronous application and workflow events. |
| **AWS CloudFormation / AWS SAM** | Defines, builds, and deploys the serverless AWS infrastructure as code. |

### Request and data flow

```text
User
  |
  v
AWS Amplify Hosting
  |
  v
Amazon API Gateway
  |
  v
AWS Lambda
  |----> AWS Step Functions
  |         |----> Amazon SageMaker AI
  |         `----> Amazon Bedrock
  |
  |----> Amazon DynamoDB
  |----> Amazon S3
  |----> AWS Secrets Manager
  |----> NASA POWER API
  `----> OpenStreetMap / Overpass

Amazon EventBridge carries asynchronous events.
Amazon CloudWatch captures logs, metrics, and diagnostics.
AWS IAM controls access between AWS services.
```

## External data sources

RoofGrid keeps external dependencies deliberately narrow:

| External source | Purpose |
| --- | --- |
| **NASA POWER** | Solar-radiation and temperature data used in production estimates. |
| **OpenStreetMap / Overpass and map imagery** | Location search, basemap context, and building-footprint information. |

All application hosting, APIs, compute, AI/ML inference, workflow orchestration, persistence, object storage, secrets, permissions, events, and monitoring are handled by AWS.

## Core capabilities

- Global rooftop search and interactive map navigation
- Automatic building-footprint detection and manual roof drawing
- Access paths, maintenance clearances, and obstacle exclusion zones
- Configurable panel size, orientation, spacing, and layout density
- NASA POWER solar-resource and temperature inputs
- Energy-production, financial-return, and environmental-impact estimates
- AWS-hosted AI assistant through Amazon Bedrock
- Downloadable project reports
- Serverless scaling, centralized monitoring, and least-privilege security

## Repository layout

```text
.
├── index.html                  # Landing page
├── solar_advanced.html         # Interactive rooftop solar planner
├── privacy.html                # Privacy information
├── sw.js                       # Service worker
├── amplify.yml                 # AWS Amplify build configuration
├── aws/
│   ├── template.yaml           # AWS SAM / CloudFormation template
│   ├── deploy.sh               # AWS deployment helper
│   └── functions/app.py        # AWS Lambda API entry point
├── assets/
│   ├── architecture/           # AWS architecture diagram
│   ├── images/                 # Product and brand assets
│   └── screenshots/            # Application screenshots
└── data/                       # Bundled NASA POWER fallback data
```

## Deploy on AWS

### Prerequisites

- An AWS account
- AWS CLI configured with deployment permissions
- AWS SAM CLI
- GitHub access for AWS Amplify Hosting
- Access to the required Amazon Bedrock and Amazon SageMaker AI models/endpoints

### Deploy the backend

```bash
bash aws/deploy.sh
```

The deployment provisions the serverless API and its supporting AWS resources. For a guided SAM deployment:

```bash
cd aws
sam build
sam deploy --guided
```

After deployment, verify the health endpoint:

```text
https://YOUR_API_ID.execute-api.YOUR_REGION.amazonaws.com/api/health
```

### Deploy the frontend

1. Open AWS Amplify Hosting.
2. Connect `rohanmalhotracodes/roofgridxwemakedevs`.
3. Select the `main` branch.
4. Allow Amplify to use the root `amplify.yml`.
5. Configure the `/api/<*>` rewrite to the Amazon API Gateway URL.
6. Deploy the branch.

The browser uses the same-origin `/api/*` paths; Amplify proxies those calls to API Gateway and Lambda.

## Security and operations

- Do not commit AWS credentials or private configuration.
- Store sensitive values in AWS Secrets Manager.
- Use IAM roles instead of long-lived API keys.
- Restrict API Gateway and Amplify origins for production.
- Review CloudWatch logs, metrics, alarms, and invocation errors.
- Apply request throttling and daily AI limits before exposing the application publicly.
- Keep S3 buckets private and grant access only through scoped IAM policies.

## Planning limitations

RoofGrid provides early-stage decision support. Satellite imagery and map outlines can be incomplete or misaligned, and estimated production, cost, savings, payback, and emissions depend on user-provided assumptions. Structural capacity, shading, fire setbacks, electrical design, permitting, utility rules, tariffs, and equipment selection require local professional verification.

RoofGrid is not an engineering design, structural assessment, permit set, installer quote, or audited carbon-accounting product.

## License

RoofGrid is available under the [MIT License](LICENSE).
