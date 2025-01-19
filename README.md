## Development

### Build and Test

Ensure that you have [Docker](https://docs.docker.com/engine/install/) and [Docker Compose](https://docs.docker.com/compose/install/) installed.

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

Ensure you have [Minikube](https://minikube.sigs.k8s.io/docs/start/?arch=%2Fmacos%2Farm64%2Fstable%2Fbinary+download) installed.

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
