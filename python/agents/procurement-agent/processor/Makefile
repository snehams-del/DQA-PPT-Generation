PROJECT_ID ?= your-project-id
REGION ?= your-region
REPO_NAME ?= contract-agent
IMAGE_NAME ?= processor
TAG ?= latest

# Construct the full image URI for Google Cloud Artifact Registry
IMAGE_URI := $(REGION)-docker.pkg.dev/$(PROJECT_ID)/$(REPO_NAME)/$(IMAGE_NAME):$(TAG)

.PHONY: help build configure-docker push all

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Build the Docker image for linux/amd64 architecture
	docker build --platform linux/amd64 -t $(IMAGE_URI) .

configure-docker: ## Configure Docker to authenticate with Google Cloud Artifact Registry
	gcloud auth configure-docker $(REGION)-docker.pkg.dev --quiet

push: configure-docker ## Push the Docker image to Artifact Registry
	docker push $(IMAGE_URI)

all: build push ## Build and push the image
