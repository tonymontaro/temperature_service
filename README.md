## Development

### Build and Test

Ensure that you have [Docker](https://docs.docker.com/get-started/) and [Docker Compose](https://docs.docker.com/compose/) installed.

```sh
make build
make test
```

### Run the app for local development

```sh
make run
```

The app docs will be available on http://localhost:8000/docs

## kubernetes

### Local machine kubernetes deployment

Ensure you have [Minikube](https://minikube.sigs.k8s.io/docs/start/) installed.

Rename the file `secret.yaml.example` (found in the folder kubernetes/config/) to `secret.yaml`, and replace `TIMESCALE_DB_URL_IN_BASE64` with your actual timescaledb url (NOTE: the url should start with postgresql and converted to base64). You can get the url to a managed timescale db [here](https://console.cloud.timescale.com/signup) (free for 30 days).

Apply the kubernetes configurations:

```sh
make kub_apply
```

[Optional] Inspect the api on your browser:

```sh
minikube service temperature-service
```

Delete the resources after inspection:

```sh
make kub_delete
```

### Deploying to Production

The steps depend on where the Kubernetes cluster is hosted. The standard practice is to configure a CI/CD pipeline that deploys to the production environment based on a trigger (for example, when a PR is merged into the main branch). It is also standard to have development and staging environments for testing and verifying new features. Below, I will describe the process for deploying to a Kubernetes cluster hosted on AWS.

- Install [eksctl](https://eksctl.io/installation/)

- Create a cluster

```sh
eksctl create cluster --name temperature-service --region eu-central-1 --nodes 2
```

- Verify that the nodes were created with `kubectl get nodes`. Note: If you have Minikube installed and running, you might want to switch between that and the aws cluster for deployment. You can view available contexts with `kubectl config get-contexts`, and switch to one with `kubectl config use-context <context-name>`

- Deploy the application to EKS

```sh
kubectl apply -f kubernetes/config
kubectl apply -f kubernetes/app
```

- To make the API externally accessible, configure an [Ingress Resource](https://kubernetes.io/docs/concepts/services-networking/ingress/) and apply it.

## Continuous Integration and deployment (CI / CD)

CI/CD is currently set up using CircleCI. When code is pushed, tests are run automatically, and deployment can be configured to occur only when the tests pass. It can also be used to configure and deploy to development or staging environments.

# Assumptions and Design Considerations

### Assumptions:

- This service focuses on temperature data. Although the design is flexible enough to allow for additional data-points like Pressure, Humidity etc.
- A room can have many sensors (from one to possibly thousands of sensors).

### Managing Data:

A system’s design depends on its scale. A system that processes less than a thousand requests per second is fundamentally different from one that processes millions of request per second.
For example, when considering a database setup:

- For a system with relatively small QPS requirements, a single database instance with backups is usually sufficient and very simple to work with.
- As the system scales to thousands of QPS, database replicas can be used to maintain availability.
- For systems with very high QPS requirements, horizontal scaling via partitioning becomes a requirement. Even though this introduces complexities that make the system much more difficult to work with.

While the temperature service itself is very simple, a major consideration is data storage and retrieval. As the number of sensors increases to thousands or even millions, the system design must handle these requests without significant slowdowns (or crashes).

There are many articles/books that compare various databases and their uses ([example](https://www.altexsoft.com/blog/comparing-database-management-systems-mysql-postgresql-mssql-server-mongodb-elasticsearch-and-others/)). One option to consider is PostgreSQL, an open-source relational database used by many organizations and supported by a large community. However, we need a database that can handle time series data efficiently. TimescaleDB is another open-source database built on top of PostgreSQL, specifically designed for ingesting and querying vast amounts of live time series data. Since it is built on PostgreSQL, it also retains all of its advantages.

### Managed vs Self-Hosted Database System

A managed DB system has the following advantages: ease of use, easily configurable availability/reliability/scalability options, security, and focus on core business.
It’s cons include; vendor lock-in, less fine-tuned control and (debatably) cost.

A self-hosted DB system has the following advantages: full control, cost control, no vendor lock-in.
Its cons include; maintenance and management overhead, availability/reliability/scalability challenges, security risks.

TimescaleDB’s managed database service was used in this project.
This [article](https://www.timescale.com/blog/how-high-availability-works-in-our-cloud-database) discusses in detail how they are able to achieve high availability for the cloud database. Essentially;

- AWS components with high availability were used; Compute (EC2), Storage (EBS or elastic block storage), and distributed file system (S3).
- By separating compute and db storage, each component can be scaled independently.
- Replication can be configured to increase availability and fault tolerance.

Another interesting [article](https://www.timescale.com/learn/is-postgres-partitioning-really-that-hard-introducing-hypertables) that discusses automatic postgresSQL partitioning using hypertables.

### Read and Write Optimization

Assuming a relatively equal write to read ratio; We can optimize the reads at the database level. This can be achieved using TImescaleDB’s [continuous aggregates](https://docs.timescale.com/use-timescale/latest/continuous-aggregates/about-continuous-aggregates/).

Another option to consider is an In-Memory cache: Usually suitable for read heavy systems; Write requests are sent to the database for storage, and the rolling averages are computed and stored in-memory. Read requests are served from the in-momory cache. This might work because we only need to store the last 15mins of data for each room in memory.

## Other Topics

- Security; Only authorized sensors should access the API. Options to consider can include assymetric encryptions.
- Rate limiting; To prevent malfunctioning or hacked sensors from overwhelming the system.
- Datadog or similar services can be used for logs and metrics.
- Sentry or similar services can be used for monitoring and alerting when there are issues with the services.
- Terraform, which is a tool for infrastructure as code, can be used to manage cloud resources.
