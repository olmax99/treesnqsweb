local := http:\/\/127.0.0.1:8879\/charts
remote := https:\/\/raw.githubusercontent.com\/olmax99\/treesnqsweb\/master\/helmdist

AWS_REGION := eu-central-1
PROJECT_NAME := treesnqsweb-dev


all: help

.PHONY: help ## Help
help:
	@grep '^.PHONY:.*' Makefile | sed 's/\.PHONY:[ \t]\+\(.*\)[ \t]\+##[ \t]*\(.*\)/\1	\2/' | expand -t20

.PHONY: templates ## Sync local data with AWS (s3 files and cloudformation)
templates:
	aws s3 cp --recursive media s3://${PROJECT_NAME}-djangoapp-mediastore-${AWS_REGION}

.PHONY: runserver ## Run local Django development server
runserver:
	cd djangoapp/ && \
	PYTHONPATH=$(pwd) python -m pipenv run python manage.py runserver 8081 --settings=app.settings.local

.PHONY: makemigrations ## Make migrations for local Django sqlite3 db
makemigrations:
	cd djangoapp/ && \
	PYTHONPATH=$(pwd) python -m pipenv run python manage.py makemigrations --settings=app.settings.local

.PHONY: migrate ## Migrate local Django sqlite3 db
migrate: makemigrations
	cd djangoapp/ && \
	PYTHONPATH=$(pwd) python -m pipenv run python manage.py migrate --settings=app.settings.local	

.PHONY: charts ## w/o make:   helm fetch --untar -d djangohelm/charts/ stable/postgresql
charts:
	cd djangohelm/ && \
	helm dep update && \
	cd ..

.PHONY: dev ## Continuous local development in Minikube
dev: charts
	aws cloudformation --region ${AWS_REGION} create-stack --stack-name ${PROJECT_NAME} \
	--template-body file://cloudformation/development/cloudformation.dev.mediastore.yml \
	--parameters ParameterKey="ProjectNamePrefix",ParameterValue="${PROJECT_NAME}"
	skaffold dev

.PHONY: dist ## Update and build packages locally. Ensure that local helm server is up.
package:
	for x in */requirements.*; do sed -i -e "s/${remote}/${local}/g" $$x; done
	for x in */Chart.yaml; do helm lint $$(dirname $$x) && helm package -u -d helmdist $$(dirname $$x); done
	for x in */requirements.*; do sed -i -e "s/${local}/${remote}/g" $$x; done

.PHONY: index ## Generate the YAML index to serve the available packages.
dist: package
	helm repo index ./helmdist
