# TreesN'Qs Django Web App

This is the web app project for TreesN'Qs. A simple Django site hosted via Kubernetes. It is
comprised of a very light-weight e-commerce shop for booking project sessions.

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

### [Optionally] Run local runserver

Sometimes, for quick debugging or front-end tasks etc. it is faster to run the bare minimum
Djangoapp in **local Debug mode**.

**NOTE:** Always try to avoid the local runserver and use minikube skaffold dev instead!!!

Use PYTHONPATH for manual Django manage.py tasks, e.g. reach the built-in Django server in
ditectory `djangoapp/` via:

#### Step 1: Local environment variables

All variables inside the .env file will be automatically picked up by the local runserver. In `djangoapp/`
create the `.env` file:

.env
```
DJANGOAPP_FERNET_KEY=<your SECRET_KEY here>
DJANGO_LOG_LEVEL=INFO
DJANGOAPP_CUSTOM_TIME_ZONE=UTC
DJANGOAPP_ADMIN_DEFAULT_URL=admin
DJANGOAPP_EMAIL_USER=<setup an gmail account>
DJANGOAPP_EMAIL_PASSWORD=<setup an gmail account>
DJANGOAPP_AWS_ACCESS_KEY_ID=<from your aws account>
DJANGOAPP_AWS_SECRET_ACCESS_KEY=<from your aws account>
DJANGOAPP_AWS_STORAGE_BUCKET_NAME=<aws bucket name for media storage>
DJANGOAPP_STRIPE_LIVE_PUBLIC_KEY=""
DJANGOAPP_STRIPE_LIVE_SECRET_KEY=""
DJANGOAPP_STRIPE_TEST_PUBLIC_KEY=<from your stripe account>
DJANGOAPP_STRIPE_TEST_SECRET_KEY=<from your stripe account>
DJANGOAPP_STRIPE_WEBHOOK_SECRET=<optional: from your local stripe cli>


```

#### Step 2: Run local runserver

```
$ make runserver

# LOCAL MIGRATIONS

$ make migrate 

```

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

### S3 Media Files

In order to use S3 Storage for Media files create a new Dev User and Group in the AWS console.
Download the programmatic access credentials and insert them into `djangohelm/values.yml`.

### Step 1: Fetch subcharts

```
$ make charts

```

### Step 2: Initialize local helm repo

Initialize minikube for local development:
```
$ minikube start --vm-driver kvm2 --memory 4096 --cpus 2 --disk-size='40000mb'

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

### Step 3: Prepare helm deployment

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

Create an gmail account and activate [https://support.google.com/accounts/answer/185833?hl=en](https://support.google.com/accounts/answer/185833?hl=en) 
custom app integration. Use the password in `djangoappEmailHostPassword`.

Provide values for deploying `djangohelm`. This is an example for a development `values.yaml` file:
```
replicaCount: 1
image: djangoapp:0.3
initContainerImage: "alpine:3.6"
pullPolicy: Never
djangoappFernetKey: <Your SECRET_KEY here>
djangoappCustomTimezone: "Europe/Zurich"
djangoappLogLevel: INFO
djangoappAdminDefaultUrl: admin
djangoappEmailHostUser: example@gmail.com       <-- Replace with the Gmail account previously created
djangoappEmailHostPassword: "super_secret"
djangoappAwsId: default                         <-- Replace with AWS developer credentials
djangoappAwsKey: default
djangoappBucket: <see cloudformation or from you aws account>
djangoappStripeLivePub: ""
djangoappStripeLiveKey: ""
djangoappStripeTestPub: <from your stripe account>
djangoappStripeTestKey: <from your stripe account>
djangoappStripeWebHook: <from your stripe account>
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
  postgresqlDataDir: /mnt/djangoapp/postgresql/data     <-- NOTE: Needs to match persistence.mountPath
  service:
    port: 5432
  persistence:
    mountPath: /mnt/djangoapp/postgresql
    size: 8Gi
  resources:
    requests:
      memory: 500Mi                 <-- In production set (memory,cpu) to min(1000Mi,1000Mi) 
      cpu: 250m

```

**NOTE:** The host name of the database is `localhost` by default unless the external database option is activated.

#### iii. Create Python Requirements

In `treesnqsweb/djangoapp` run: `pipenv lock -r > requirements.txt`

### Step 5: Run in development mode

```
$ make dev

$ make templates

# Get Minikube IP and the Djangoapp NodePort
$ minikube ip
$ kubectl get all

```

Open the Djangoapp via browser at `https://<minikube ip>:<Node Port>`

**NOTE:** Performing migrations on newly created models during `skaffold dev` might fail. Always pause `skaffold dev`
during new model creation.

### Step 6: Create Djangoapp Superuser

```
$ kubectl exec -ti djangohelm-5fc4fc7b68-rkhnq -- /bin/bash -c \
"cd .. && python manage.py createsuperuser --settings=app.settings.development"

```

## FAQ


### Kubernetes, Helm, Skaffold 

- How to access the postgres Pod and postgres client for querying the database manually?

```
$ kubectl run djangohelm-postgresql-client --rm --tty -i --restart='Never' --namespace default --image docker.io/bitnami/postgresql:11.6.0-debian-9-r0 --env="PGPASSWORD=super_secret" --command -- psql --host djangohelm-postgresql -U postgres -d postgres -p 5432

```

- How to create an local backup from current postgres and how restore it?

```
# BACKUP
$ kubectl exec -ti djangohelm-postgresql-0 -- /bin/bash -c "pg_dump -U postgres djangoapp" > \
/tmp/$(date +"%Y_%m_%d_%I_%M_%p")_psql_djangoapp.bak

# RESTORE
cat 2019_12_08_10_18_AM_psql_djangoapp.bak | kubectl exec -i djangohelm-postgresql-0 -- /bin/bash \
-c "PGPASSWORD="super_secret" psql -U postgres -d djangoapp"


```


- What is the directory the actual data is written to?

```
$ kubectl get pv
$ kubectl describe pv <pv_name>

# ----- More Info on Minikube Image--------
$ sudo virsh list
$ sudo virsh domblklist minikube
$ sudo qemu-img info <image_name>

```

- How to free up space from released persistent volumes? How to free up space from minikube `dev/vda1`?

Currently, the only option seems to stop, delete, and restart Minikube. All data will be lost. 
<-- Try: Delete PV manually, and restart djangohelm 

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

- How do signals work and what is the connection to djstrip webhooks?



### iii. Stripe stuff

- How can webhooks be debugged?

Install the stripe cli locally and run `stripe listen`. Then from the stripe cli you can trigger
mock events: 

  - `stripe trigger payment_intent.created`

These mock events can be observed from the stripe cli directly via `stripe listen`. Further, they 
can be forwarded to your local development environment via: 

  - `stripe listen --forward-to localhost:8081/stripe/webhook/` (This url is provided by dj-stripe)

**NOTE** That way you will alse receive a new webhook token, which can be used for local testing.

- How to create a dj-stripe customer and sync it with Stripe? Is a customer needed for syncing 
charges and ppayment_intents?



### Useful resources

- [https://pythonspeed.com/articles/gunicorn-in-docker/](https://pythonspeed.com/articles/gunicorn-in-docker/)

- [https://skaffold.dev/docs/workflows/dev/](https://skaffold.dev/docs/workflows/dev/)

- [https://github.com/APSL/kubernetes-charts](https://github.com/APSL/kubernetes-charts)

- [https://helm.sh/docs/intro/getting\_started/](https://helm.sh/docs/intro/getting_started/)

## Where to go from here?

- Create a minimum cost cluster using kops and spot instances:
  * [https://www.replex.io/blog/the-ultimate-guide-to-deploying-kubernetes-cluster-on-aws-ec2-spot-instances-using-kops-and-eks#walkthrough](https://www.replex.io/blog/the-ultimate-guide-to-deploying-kubernetes-cluster-on-aws-ec2-spot-instances-using-kops-and-eks#walkthrough)
  * [https://itnext.io/the-definitive-guide-to-running-ec2-spot-instances-as-kubernetes-worker-nodes-68ef2095e767](https://itnext.io/the-definitive-guide-to-running-ec2-spot-instances-as-kubernetes-worker-nodes-68ef2095e767)
  
- Production level monitoring [https://medium.com/@markgituma/kubernetes-local-to-production-with-django-6-add-prometheus-grafana-monitoring-with-helm-926fafbe1d](https://medium.com/@markgituma/kubernetes-local-to-production-with-django-6-add-prometheus-grafana-monitoring-with-helm-926fafbe1d)

- Use sidecar approach for monitoring [https://kubernetes.io/docs/concepts/cluster-administration/logging/#using-a-sidecar-container-with-the-logging-agent](https://kubernetes.io/docs/concepts/cluster-administration/logging/#using-a-sidecar-container-with-the-logging-agent)

- Build a CI/CD pipeline for facilitating automated tests - ckeck with skaffold run .. [https://docs.djangoproject.com/en/2.2/topics/testing/tools/#django.test.LiveServerTestCase](https://docs.djangoproject.com/en/2.2/topics/testing/tools/#django.test.LiveServerTestCase)

- User authentication with google [https://medium.com/trabe/oauth-authentication-in-django-with-social-auth-c67a002479c1](https://medium.com/trabe/oauth-authentication-in-django-with-social-auth-c67a002479c1)

- Deploy a Lambda function that creates thumbnails from uploaded user profile pictures. (OR simply remove the upload functionality in the early version!!!)

- Use EBS volume for PersistentVolumes, otherwise data will be lost if the cluster is being shut down

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


