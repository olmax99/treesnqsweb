# TreesN'Qs Django Web App

This is the web app project for TreesN'Qs. A simple Django site hosted via Kubernetes in AWS EKS.

---

**Project Design**

...  
  
  
  ## Prerequisites

For local development, the following components are required on the local machine:

+ Pipenv
+ Python Version 3.8
+ Docker installed [official Docker docs](https://docs.docker.com/)
+ Minikube [https://kubernetes.io/docs/tasks/tools/install-minikube/](https://kubernetes.io/docs/tasks/tools/install-minikube/)
+ Helm [https://helm.sh/docs/](https://helm.sh/docs/)
+ [Optionally] Skaffold [https://skaffold.dev/docs/](https://skaffold.dev/docs/)

---

## Quickstart Development

**NOTE:** Reach the build-in django server via `PYTHONPATH=$(pwd) python -m pipenv run n python manage.py runserver 8081`.

### Step 1: Initialize local helm repo

```
$ helm serve

$ helm package -u -d helmdist ./djangohelm

$ helm repo index .

```

### Step 2: Use local docker images with Minikube

```
$ eval $(minikube docker-env)

$ docker build -t djangoapp:0.1 ./djangoapp

```

### Step 3: Run in development mode

```
$ skaffold dev

```


## FAQ


### Helm/Skaffold

- What is the `skaffold builder` indicated in `.build.artifacts.image` and `.deploy.helm.releases.values.image`?


- How does `skaffold.yaml` executes nginx image as well as images of subcharts?


- How are the releases being picked up by skaffold?         <-- helm repo and docker images do not contain `nginx:stable`


- Where is the image coming from? Which revision package is being used?

**Helm/Skaffold:** It is definitely coming from `local repo`, unless it does not exist locally. The revision
being used is always the top one indicated in `index.yaml`. 

- How to use a local docker image in Minikube without a remote docker registry?

1. Load Minikube docker environment variables into the local shell: `eval $(minikube docker-env)`
2. Verify that `docker ps` now is showing all docker running inside minikube
3. Build the image inside Minikube: `docker build -t <imag_name> .`
4. In Deployments, set `.Values.pullPolicy: Never`

### Django

- What is the entry `ALLOWED_HOSTS` in `djangoapp/settings.py` being used for? 

#### Useful resources

- [https://pythonspeed.com/articles/gunicorn-in-docker/](https://pythonspeed.com/articles/gunicorn-in-docker/)

- [https://skaffold.dev/docs/workflows/dev/](https://skaffold.dev/docs/workflows/dev/)

- [https://github.com/APSL/kubernetes-charts](https://github.com/APSL/kubernetes-charts)

- [https://helm.sh/docs/intro/getting\_started/](https://helm.sh/docs/intro/getting_started/)
