local := http:\/\/127.0.0.1:8879\/charts
remote := https:\/\/raw.githubusercontent.com\/olmax99\/treesnqsweb\/master\/helmdist

all: help

.PHONY: help # Help
help:
	@grep '^.PHONY:.*' Makefile | sed 's/\.PHONY:[ \t]\+\(.*\)[ \t]\+#[ \t]*\(.*\)/\1	\2/' | expand -t20

.PHONY: dev # Continuous local development in Minikube
dev:
	skaffold dev

.PHONY: dist # Update and build packages locally. Ensure that local helm server is up.
package:
	for x in */requirements.*; do sed -i -e "s/${remote}/${local}/g" $$x; done
	for x in */Chart.yaml; do helm package -u -d helmdist $$(dirname $$x); done
	for x in */requirements.*; do sed -i -e "s/${local}/${remote}/g" $$x; done

.PHONY: index # Generate the YAML index to serve the available packages.
dist: package
	helm repo index packages