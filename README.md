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
+ Helm v2 [https://helm.sh/docs/](https://helm.sh/docs/)
+ [Optionally] Skaffold [https://skaffold.dev/docs/](https://skaffold.dev/docs/) - NOTE: skaffold currently only supports helm v2

---

## Quickstart Development

Use PYTHONPATH for manual Django manage.py tasks, e.g. reach the built-in Django server via:
`PYTHONPATH=$(pwd) python -m pipenv run python manage.py  runserver 8081`.

### Packages

To use this repository as a k8s charts repository for deploying the Djangoapp, configure helm:

```
$ helm repo add treesnqsweb https://raw.githubusercontent.com/olmax99/treesnqsweb/master/helmdist

$ helm repo list
# EXPECTED
NAME            URL                                                                  
stable          https://kubernetes-charts.storage.googleapis.com                     
local           http://127.0.0.1:8879/charts                                         
treesnqsweb     https://raw.githubusercontent.com/olmax99/treesnqsweb/master/helmdist

```

### Step 1: Fetch subcharts

```
$ make charts

```

### Step 2: Initialize local helm repo

Initialize the local repo for development:
```
$ minikube start --vm-driver kvm2 --memory 4096 --cpus 2

# Install Tiller (Helm v2)
$ helm init --history-max 200

$ helm serve

$ make dist

```

In case docker image needs to be present inside minikube dockerd:
```
$ eval $(minikube docker-env)

$ docker build -t djangoapp:0.2 ./djangoapp

```

### Step 4: Prepare helm deployment

#### i. Create password secrets

It is best practise to NOT version secrets and manually remove them after the Helm deployment.

In `djangohelm/templates/` add the following `secrets.yaml` file:
```
apiVersion: v1
kind: Secret
metadata:
  name: {{ template "djangohelm.fullname" . }}
    labels:
      app: "{{ template "djangohelm.fullname" . }}"
      chart: "{{ template "djangohelm.chart" . }}"
      release: {{ .Release.Name | quote }}
      heritage: {{ .Release.Service | quote }}
  type: Opaque
  data:
    {{- if .Values.postgresqlPassword }}
    postgresql-password: {{ default "super_secret" .Values.postgresqlPassword | b64enc | quote }}
    {{- else }}
    postgresql-password: {{ randAlphaNum 10 | b64enc | quote }}
    {{- end }}

```


#### ii. Provide default values

Provide values for deploying `djangohelm`. This is an example for a development `values.yaml` file:
```
replicaCount: 1
image: djangoapp:0.3
initContainerImage: "alpine:3.6"
pullPolicy: Never
service:
  type: NodePort
  name: djangoapp
  externalPort: 8000
  internalPort: 8000
externalDatabase:
  host: localhost
  user: django_user
  password: ""
  database: djangoapp
  port: 5432
ingress:
  enabled: false
  hosts:
    - chart-example.local
  annotations:
  tls:
resources: {}
postgresql:
  enabled: true
  nameOverride: postgresql
  postgresqlUsername: postgres
  postgresqlPassword: super_secret
  postgresqlDatabase: djangoapp
  postgresqlDataDir: /mnt/djangoapp/postgresql/data
  service:
    port: 5432
  persistence:
    mountPath: /mnt/djangoapp/postgresql
    size: 8Gi
  resources:
    requests:
      memory: 500Mi
      cpu: 250m

```

**NOTE:** The host name of the database is `localhost` by default unless the external database option is activated.

### Step 5: Run in development mode

```
$ make dev

```

**NOTE:** Performing migrations on newly created models during `skaffold dev` might fail. Always pause `skaffold dev`
during new model creation.

## FAQ


### Helm/Skaffold

- How to access the postgres Pod for querying the database? 
- What is the directory the actual data is written to? 
- How to free up space from released persistent volumes? How to free up space from minikube `dev/vda1`?

```
$ kubectl run djangohelm-postgresql-client --rm --tty -i --restart='Never' --namespace default --image docker.io/bitnami/postgresql:11.6.0-debian-9-r0 --env="PGPASSWORD=super_secret" --command -- psql --host djangohelm-postgresql -U postgres -d postgres -p 5432

$ kubectl get pv
$ kubectl describe pv <pv_name>

# ----- More Info on Minikube Image--------
$ sudo virsh list
$ sudo virsh domblklist minikube
$ sudo qemu-img info <image_name>

```

- How to configure the connection credentials and pass them on from main Chart?

The main chart `values.yaml` file contains the appropriate subchart sections, which start according to the subcharts'
dependeny name. E.g.
```
...
postgresql:
  <parameter to override>: <your paramter>
  ...

```
  * **HOSTNAME:** Custom Helm template definition as a combination of `{{ printf "%s-%s" .Release.Name .Values.postgresql.nameOverride }}`.
  * **POSTGRES_USER:** Directly defined in `.Values.postgresql.postgresqlUsername`, which is a superuser when named `postgres`.
                   If name is changed, you also need to change `.Values.postgresql.postgresqlPostgresPassword`.
  * **POSTGRES_PASSWORD:** The default behavior for `_helper.tpl` is to set `true` for `{{- define "postgresql.createSecret" -}}`.
                   This will activate the `secrets.yaml` file, which in turn gets the `postgresql.password` from the `_helpers.tpl`
                   if `.Values.postgresqlPassword` exist or provides a random alphanumeric with 10 chars instead.
  * **POSTGRESQL_PORT_NUMBER:** Defined in `_helper.tpl`, and coming from `.Values.postgresql.service.port`.
  * **POSTGRES_DB:** Defined in `_helper.tpl`, and coming from `.Values.postgresqlDatabase`.


- Which `values.yaml` is being used by `skaffold dev` and `skaffold run`? And how to switch between dev and (multiple) prod?


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

### Where to go from here?

- Create a minimum cost cluster using kops and spot instances:
  * [https://www.replex.io/blog/the-ultimate-guide-to-deploying-kubernetes-cluster-on-aws-ec2-spot-instances-using-kops-and-eks#walkthrough](https://www.replex.io/blog/the-ultimate-guide-to-deploying-kubernetes-cluster-on-aws-ec2-spot-instances-using-kops-and-eks#walkthrough)
  * [https://itnext.io/the-definitive-guide-to-running-ec2-spot-instances-as-kubernetes-worker-nodes-68ef2095e767](https://itnext.io/the-definitive-guide-to-running-ec2-spot-instances-as-kubernetes-worker-nodes-68ef2095e767)
  
- Production level monitoring [https://medium.com/@markgituma/kubernetes-local-to-production-with-django-6-add-prometheus-grafana-monitoring-with-helm-926fafbe1d](https://medium.com/@markgituma/kubernetes-local-to-production-with-django-6-add-prometheus-grafana-monitoring-with-helm-926fafbe1d)

- Use sidecar approach for monitoring [https://kubernetes.io/docs/concepts/cluster-administration/logging/#using-a-sidecar-container-with-the-logging-agent](https://kubernetes.io/docs/concepts/cluster-administration/logging/#using-a-sidecar-container-with-the-logging-agent)

- Build a CI/CD pipeline for facilitating automated tests - ckeck with skaffold run .. [https://docs.djangoproject.com/en/2.2/topics/testing/tools/#django.test.LiveServerTestCase](https://docs.djangoproject.com/en/2.2/topics/testing/tools/#django.test.LiveServerTestCase)

- Serve staticfiles separately in production [https://testdriven.io/blog/dockerizing-django-with-postgres-gunicorn-and-nginx/](https://testdriven.io/blog/dockerizing-django-with-postgres-gunicorn-and-nginx/)

- User authentication email + google [https://medium.com/trabe/oauth-authentication-in-django-with-social-auth-c67a002479c1](https://medium.com/trabe/oauth-authentication-in-django-with-social-auth-c67a002479c1)


## General Instructions

### i. Static Files

The static files are being served using [http://whitenoise.evans.io/en/stable/](http://whitenoise.evans.io/en/stable/) middleware for simplified
in-docker wsgi static file serving.

```
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',

STATIC_URL = '/opt/static/'
STATIC_ROOT = '/opt/static/'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

```

This will automatically create a folder `/opt/static`:
```
/opt/static/
├── admin           <-- Default static files from /usr/local/lib/python3.8/site-packages/django/contrib/admin/static
│   ├── css
│   ├── fonts
│   ├── img
│   └── js
├── staticfiles.json
└── trees                       <-- created from custom Django app incl. directory /djangoapp/<custom_app>/static/<custom_app>
    ├── images
    ├── style.279196452539.css
    └── style.css

```



### ii. Djangohelm Parameters

The following table lists the configurable parameters of the Djangohelm main chart and subcharts
configurable from main chart `values.yaml`.

**TODO:** Verify that all relevant Parameters are configurable including for postgresql.


|            Parameter                      |                                  Description                                  |                           Default                            |
| ----------------------------------------- | ----------------------------------------------------------------------------- | ------------------------------------------------------------ |
| `global.imageRegistry`                    | Global Docker image registry                                                  | `nil`                                                        |
| `global.imagePullSecrets`                 | Global Docker registry secret names as an array                               | `[]` (does not add image pull secrets to deployed pods)      |
| `global.storageClass`                     | Global storage class for dynamic provisioning                                 | `nil`                                                        |
| `image.registry`                          | WordPress image registry                                                      | `docker.io`                                                  |
| `image.repository`                        | WordPress image name                                                          | `bitnami/wordpress`                                          |
| `image.tag`                               | WordPress image tag                                                           | `{TAG_NAME}`                                                 |
| `image.pullPolicy`                        | Image pull policy                                                             | `IfNotPresent`                                               |
| `image.pullSecrets`                       | Specify docker-registry secret names as an array                              | `[]` (does not add image pull secrets to deployed pods)      |
| `nameOverride`                            | String to partially override wordpress.fullname template with a string (will prepend the release name) | `nil`                               |
| `fullnameOverride`                        | String to fully override wordpress.fullname template with a string                                     | `nil`                               |
| `wordpressSkipInstall`                    | Skip wizard installation                                                      | `false`                                                      |
| `wordpressUsername`                       | User of the application                                                       | `user`                                                       |
| `wordpressPassword`                       | Application password                                                          | _random 10 character long alphanumeric string_               |
| `wordpressEmail`                          | Admin email                                                                   | `user@example.com`                                           |
| `wordpressFirstName`                      | First name                                                                    | `FirstName`                                                  |
| `wordpressLastName`                       | Last name                                                                     | `LastName`                                                   |
| `wordpressBlogName`                       | Blog name                                                                     | `User's Blog!`                                               |
| `wordpressTablePrefix`                    | Table prefix                                                                  | `wp_`                                                        |
| `wordpressScheme`                         | Scheme to generate application URLs [`http`, `https`]                         | `http`                                                       |
| `allowEmptyPassword`                      | Allow DB blank passwords                                                      | `true`                                                       |
| `allowOverrideNone`                       | Set Apache AllowOverride directive to None                                    | `false`                                                      |
| `customHTAccessCM`                        | Configmap with custom wordpress-htaccess.conf directives                      | `nil`                                                        |
| `smtpHost`                                | SMTP host                                                                     | `nil`                                                        |
| `smtpPort`                                | SMTP port                                                                     | `nil`                                                        |
| `smtpUser`                                | SMTP user                                                                     | `nil`                                                        |
| `smtpPassword`                            | SMTP password                                                                 | `nil`                                                        |
| `smtpUsername`                            | User name for SMTP emails                                                     | `nil`                                                        |
| `smtpProtocol`                            | SMTP protocol [`tls`, `ssl`, `none`]                                          | `nil`                                                        |
| `replicaCount`                            | Number of WordPress Pods to run                                               | `1`                                                          |
| `extraEnv`                                | Additional container environment variables                                    | `[]`                                                         |
| `extraVolumeMounts`                       | Additional volume mounts                                                      | `[]`                                                         |
| `extraVolumes`                            | Additional volumes                                                            | `[]`                                                         |
| `mariadb.enabled`                         | Deploy MariaDB container(s)                                                   | `true`                                                       |
| `mariadb.rootUser.password`               | MariaDB admin password                                                        | `nil`                                                        |
| `mariadb.db.name`                         | Database name to create                                                       | `bitnami_wordpress`                                          |
| `mariadb.db.user`                         | Database user to create                                                       | `bn_wordpress`                                               |
| `mariadb.db.password`                     | Password for the database                                                     | _random 10 character long alphanumeric string_               |
| `externalDatabase.host`                   | Host of the external database                                                 | `localhost`                                                  |
| `externalDatabase.user`                   | Existing username in the external db                                          | `bn_wordpress`                                               |
| `externalDatabase.password`               | Password for the above username                                               | `nil`                                                        |
| `externalDatabase.database`               | Name of the existing database                                                 | `bitnami_wordpress`                                          |
| `externalDatabase.port`                   | Database port number                                                          | `3306`                                                       |
| `service.annotations`                     | Service annotations                                                           | `{}`                                                         |
| `service.type`                            | Kubernetes Service type                                                       | `LoadBalancer`                                               |
| `service.port`                            | Service HTTP port                                                             | `80`                                                         |
| `service.httpsPort`                       | Service HTTPS port                                                            | `443`                                                        |
| `service.httpsTargetPort`                 | Service Target HTTPS port                                                     | `https`                                                      |
| `service.metricsPort`                     | Service Metrics port                                                          | `9117`                                                       |
| `service.externalTrafficPolicy`           | Enable client source IP preservation                                          | `Cluster`                                                    |
| `service.nodePorts.http`                  | Kubernetes http node port                                                     | `""`                                                         |
| `service.nodePorts.https`                 | Kubernetes https node port                                                    | `""`                                                         |
| `service.nodePorts.metrics`               | Kubernetes metrics node port                                                  | `""`                                                         |
| `service.extraPorts`                      | Extra ports to expose in the service (normally used with the `sidecar` value) | `nil`                                                        |
| `healthcheckHttps`                        | Use https for liveliness and readiness                                        | `false`                                                      |
| `livenessProbe.initialDelaySeconds`       | Delay before liveness probe is initiated                                      | `120`                                                        |
| `livenessProbe.periodSeconds`             | How often to perform the probe                                                | `10`                                                         |
| `livenessProbe.timeoutSeconds`            | When the probe times out                                                      | `5`                                                          |
| `livenessProbe.failureThreshold`          | Minimum consecutive failures for the probe                                    | `6`                                                          |
| `livenessProbe.successThreshold`          | Minimum consecutive successes for the probe                                   | `1`                                                          |
| `livenessProbeHeaders`                    | Headers to use for livenessProbe                                              | `nil`                                                        |
| `readinessProbe.initialDelaySeconds`      | Delay before readiness probe is initiated                                     | `30`                                                         |
| `readinessProbe.periodSeconds`            | How often to perform the probe                                                | `10`                                                         |
| `readinessProbe.timeoutSeconds`           | When the probe times out                                                      | `5`                                                          |
| `readinessProbe.failureThreshold`         | Minimum consecutive failures for the probe                                    | `6`                                                          |
| `readinessProbe.successThreshold`         | Minimum consecutive successes for the probe                                   | `1`                                                          |
| `readinessProbeHeaders`                   | Headers to use for readinessProbe                                             | `nil`                                                        |
| `ingress.enabled`                         | Enable ingress controller resource                                            | `false`                                                      |
| `ingress.certManager`                     | Add annotations for cert-manager                                              | `false`                                                      |
| `ingress.hostname`                        | Default host for the ingress resource                                         | `wordpress.local`                                            |
| `ingress.annotations`                     | Ingress annotations                                                           | `[]`                                                         |
| `ingress.hosts[0].name`                   | Hostname to your Wordpress installation                                       | `wordpress.local`                                            |
| `ingress.hosts[0].path`                   | Path within the url structure                                                 | `/`                                                          |
| `ingress.tls[0].hosts[0]`                 | TLS hosts                                                                     | `wordpress.local`                                            |
| `ingress.tls[0].secretName`               | TLS Secret (certificates)                                                     | `wordpress.local-tls`                                        |
| `ingress.secrets[0].name`                 | TLS Secret Name                                                               | `nil`                                                        |
| `ingress.secrets[0].certificate`          | TLS Secret Certificate                                                        | `nil`                                                        |
| `ingress.secrets[0].key`                  | TLS Secret Key                                                                | `nil`                                                        |
| `schedulerName`                           | Name of the alternate scheduler                                               | `nil`                                                        |
| `persistence.enabled`                     | Enable persistence using PVC                                                  | `true`                                                       |
| `persistence.existingClaim`               | Enable persistence using an existing PVC                                      | `nil`                                                        |
| `persistence.storageClass`                | PVC Storage Class                                                             | `nil` (uses alpha storage class annotation)                  |
| `persistence.accessMode`                  | PVC Access Mode                                                               | `ReadWriteOnce`                                              |
| `persistence.size`                        | PVC Storage Request                                                           | `10Gi`                                                       |
| `nodeSelector`                            | Node labels for pod assignment                                                | `{}`                                                         |
| `tolerations`                             | List of node taints to tolerate                                               | `[]`                                                         |
| `affinity`                                | Map of node/pod affinities                                                    | `{}`                                                         |
| `podAnnotations`                          | Pod annotations                                                               | `{}`                                                         |
| `metrics.enabled`                         | Start a side-car prometheus exporter                                          | `false`                                                      |
| `metrics.image.registry`                  | Apache exporter image registry                                                | `docker.io`                                                  |
| `metrics.image.repository`                | Apache exporter image name                                                    | `bitnami/apache-exporter`                                    |
| `metrics.image.tag`                       | Apache exporter image tag                                                     | `{TAG_NAME}`                                                 |
| `metrics.image.pullPolicy`                | Image pull policy                                                             | `IfNotPresent`                                               |
| `metrics.image.pullSecrets`               | Specify docker-registry secret names as an array                              | `[]` (does not add image pull secrets to deployed pods)      |
| `metrics.podAnnotations`                  | Additional annotations for Metrics exporter pod                               | `{prometheus.io/scrape: "true", prometheus.io/port: "9117"}` |
| `metrics.resources`                       | Exporter resource requests/limit                                              | `{}`                                                         |
| `metrics.serviceMonitor.enabled`          | Create ServiceMonitor Resource for scraping metrics using PrometheusOperator  | `false`                                                      |
| `metrics.serviceMonitor.namespace`        | Namespace where servicemonitor resource should be created                     | `nil`                                                        |
| `metrics.serviceMonitor.interval`         | Specify the interval at which metrics should be scraped                       | `30s`                                                        |
| `metrics.serviceMonitor.scrapeTimeout`    | Specify the timeout after which the scrape is ended                           | `nil`                                                        |
| `metrics.serviceMonitor.relabellings`     | Specify Metric Relabellings to add to the scrape endpoint                     | `nil`                                                        |
| `metrics.serviceMonitor.honorLabels`      | honorLabels chooses the metric's labels on collisions with target labels.     | `false`                                                      |
| `metrics.serviceMonitor.additionalLabels` | Used to pass Labels that are required by the Installed Prometheus Operator    | `{}`                                                         |
| `sidecars`                                | Attach additional containers to the pod                                       | `nil`                                                        |
| `updateStrategy`                          | Set up update strategy                                                        | `RollingUpdate`                                              |
