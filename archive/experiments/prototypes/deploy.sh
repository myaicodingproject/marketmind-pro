#!/bin/bash

# MarketMind Pro Production Deployment Script
set -e

echo "🚀 MarketMind Pro Production Deployment"
echo "========================================"

# Configuration
COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.production"

# Check prerequisites
check_prerequisites() {
    echo "📋 Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not installed"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ Docker Compose is not installed"
        exit 1
    fi
    
    if [ ! -f "$ENV_FILE" ]; then
        echo "❌ Production environment file not found: $ENV_FILE"
        echo "Please copy .env.production.example to .env.production and configure it"
        exit 1
    fi
    
    echo "✅ Prerequisites check passed"
}

# Generate secure secrets
generate_secrets() {
    echo "🔐 Generating secure secrets..."
    
    if ! grep -q "CHANGE_THIS" "$ENV_FILE"; then
        echo "✅ Secrets already configured"
        return
    fi
    
    SECRET_KEY=$(openssl rand -hex 32)
    JWT_SECRET=$(openssl rand -hex 32)
    DB_PASSWORD=$(openssl rand -hex 16)
    
    sed -i.bak \
        -e "s/CHANGE_THIS_TO_LONG_RANDOM_STRING_FOR_PRODUCTION/$SECRET_KEY/" \
        -e "s/CHANGE_THIS_TO_ANOTHER_LONG_RANDOM_STRING/$JWT_SECRET/" \
        -e "s/CHANGE_THIS_DATABASE_PASSWORD/$DB_PASSWORD/" \
        "$ENV_FILE"
    
    echo "✅ Secrets generated and updated in $ENV_FILE"
}

# Create necessary directories
setup_directories() {
    echo "📁 Setting up directories..."
    
    mkdir -p data/reports data/chroma logs/nginx ssl config
    chmod 755 data logs
    chmod 700 ssl
    
    echo "✅ Directories created"
}

# Build and deploy
deploy() {
    echo "🏗️  Building and deploying services..."
    
    # Pull latest images
    docker-compose -f "$COMPOSE_FILE" pull
    
    # Build application
    docker-compose -f "$COMPOSE_FILE" build --no-cache
    
    # Start services
    docker-compose -f "$COMPOSE_FILE" up -d
    
    echo "✅ Services deployed"
}

# Wait for services to be healthy
wait_for_services() {
    echo "⏳ Waiting for services to be healthy..."
    
    max_attempts=30
    attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if docker-compose -f "$COMPOSE_FILE" ps | grep -q "healthy"; then
            echo "✅ Services are healthy"
            return
        fi
        
        echo "Waiting... ($((attempt + 1))/$max_attempts)"
        sleep 10
        attempt=$((attempt + 1))
    done
    
    echo "❌ Services failed to become healthy"
    docker-compose -f "$COMPOSE_FILE" logs
    exit 1
}

# Run database migrations
run_migrations() {
    echo "🗄️  Running database migrations..."
    
    docker-compose -f "$COMPOSE_FILE" exec app python -c "
import asyncio
from app.core.database import init_db
asyncio.run(init_db())
"
    
    echo "✅ Database migrations completed"
}

# Show deployment status
show_status() {
    echo "📊 Deployment Status"
    echo "===================="
    
    docker-compose -f "$COMPOSE_FILE" ps
    
    echo ""
    echo "🌐 Application URLs:"
    echo "   - API: http://localhost:8000"
    echo "   - Health Check: http://localhost:8000/health"
    echo "   - API Docs: http://localhost:8000/docs"
    
    echo ""
    echo "📝 Logs:"
    echo "   docker-compose -f $COMPOSE_FILE logs -f"
}

# Main deployment flow
main() {
    check_prerequisites
    generate_secrets
    setup_directories
    deploy
    wait_for_services
    run_migrations
    show_status
    
    echo ""
    echo "🎉 MarketMind Pro deployed successfully!"
}

# Handle script arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "stop")
        echo "🛑 Stopping services..."
        docker-compose -f "$COMPOSE_FILE" down
        ;;
    "restart")
        echo "🔄 Restarting services..."
        docker-compose -f "$COMPOSE_FILE" restart
        ;;
    "logs")
        docker-compose -f "$COMPOSE_FILE" logs -f
        ;;
    "status")
        show_status
        ;;
    *)
        echo "Usage: $0 {deploy|stop|restart|logs|status}"
        exit 1
        ;;
esac