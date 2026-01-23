# Makefile for LazyBacktest Kubernetes Deployment

# Image names
BACKEND_IMAGE := lazybacktest-backend:latest
FRONTEND_IMAGE := lazybacktest-frontend:latest

# K8s manifest files
MANIFESTS := ingress.yaml backend.yaml frontend.yaml
POSTGRES_MANIFEST := postgres.yaml
SECRET_FILE := config-secret.yaml
SECRET_EXAMPLE := config-secret.example.yaml

.PHONY: help build deploy deploy-host-db clean secret-check

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  build             Build Docker images for backend and frontend"
	@echo "  deploy            Deploy PostgreSQL (in-cluster) and all services"
	@echo "  deploy-host-db    Deploy services connecting to Host DB (Orbstack/Docker Desktop)"
	@echo "  clean             Delete all resources from K8s"
	@echo "  restart           Restart backend and frontend pods"
	@echo ""

secret-check:
	@if [ ! -f $(SECRET_FILE) ]; then \
		echo "❌ Error: $(SECRET_FILE) not found!"; \
		echo "👉 Please copy $(SECRET_EXAMPLE) to $(SECRET_FILE) and set your DATABASE_URL."; \
		echo "   Run: cp $(SECRET_EXAMPLE) $(SECRET_FILE)"; \
		exit 1; \
	fi

build: ## Build Docker images
	@echo "🏗️  Building Backend Image..."
	docker build -t $(BACKEND_IMAGE) ../backend
	@echo "🏗️  Building Frontend Image..."
	docker build -t $(FRONTEND_IMAGE) ../frontend
	@echo "✅ Images built successfully."

deploy: secret-check ## Deploy with in-cluster PostgreSQL
	@echo "🚀 Deploying PostgreSQL..."
	kubectl apply -f $(POSTGRES_MANIFEST)
	@echo "🚀 Deploying Application..."
	kubectl apply -f $(SECRET_FILE)
	kubectl apply -f backend.yaml
	kubectl apply -f frontend.yaml
	kubectl apply -f ingress.yaml
	@echo "✅ Deployment complete! Access at http://localhost"

deploy-host-db: secret-check ## Deploy connecting to Host DB (skips internal Postgres)
	@echo "⚠️  Note: Make sure $(SECRET_FILE) points to 'host.docker.internal'!"
	@echo "🚀 Deploying Application (connecting to Host DB)..."
	kubectl apply -f $(SECRET_FILE)
	kubectl apply -f backend.yaml
	kubectl apply -f frontend.yaml
	kubectl apply -f ingress.yaml
	@echo "✅ Deployment complete! Access at http://localhost"

clean: ## Delete all K8s resources
	@echo "🧹 Cleaning up..."
	-kubectl delete -f ingress.yaml
	-kubectl delete -f frontend.yaml
	-kubectl delete -f backend.yaml
	-kubectl delete -f $(POSTGRES_MANIFEST)
	-kubectl delete -f $(SECRET_FILE)
	@echo "✅ Cleanup complete."

restart: ## Restart pods to pick up new images/config
	@echo "🔄 Restarting pods..."
	kubectl rollout restart deployment/lazybacktest-backend
	kubectl rollout restart deployment/lazybacktest-frontend
