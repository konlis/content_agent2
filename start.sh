#!/bin/bash

# Content Agent Quick Start Script
# This script helps you get Content Agent up and running quickly

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE} $1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        echo "Visit: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        echo "Visit: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    print_status "Docker and Docker Compose are available"
}

# Setup environment file
setup_env() {
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            cp .env.example .env
            print_status "Created .env file from template"
            print_warning "Please edit .env file with your API keys before starting"
        else
            print_error ".env.example file not found"
            exit 1
        fi
    else
        print_status ".env file already exists"
    fi
}

# Create necessary directories
create_directories() {
    mkdir -p logs data uploads exports scripts
    print_status "Created necessary directories"
}

# Create database initialization script
create_db_init() {
    cat > scripts/init_db.sql << EOF
-- Content Agent Database Initialization
-- This file is run when the PostgreSQL container starts for the first time

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- You can add any additional database setup here
EOF
    print_status "Created database initialization script"
}

# Start services
start_services() {
    print_status "Starting Content Agent services..."
    
    # Build and start services
    docker-compose up --build -d
    
    print_status "Services started successfully!"
    print_status "Content Agent is now running at:"
    echo "  🌐 Frontend (Streamlit): http://localhost:8501"
    echo "  🔧 Backend API: http://localhost:8000"
    echo "  📊 API Docs: http://localhost:8000/docs"
    echo "  🌸 Celery Monitor: http://localhost:5555"
}

# Stop services
stop_services() {
    print_status "Stopping Content Agent services..."
    docker-compose down
    print_status "Services stopped"
}

# Show logs
show_logs() {
    docker-compose logs -f
}

# Show status
show_status() {
    print_header "Service Status"
    docker-compose ps
    
    print_header "Health Checks"
    docker-compose exec content-agent curl -f http://localhost:8000/health || print_error "Backend health check failed"
}

# Clean up (remove containers and volumes)
cleanup() {
    print_warning "This will remove all containers and data. Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        print_status "Cleaning up..."
        docker-compose down -v --remove-orphans
        docker system prune -f
        print_status "Cleanup completed"
    else
        print_status "Cleanup cancelled"
    fi
}

# Show help
show_help() {
    echo "Content Agent Quick Start Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start     Start all services (default)"
    echo "  stop      Stop all services" 
    echo "  restart   Restart all services"
    echo "  logs      Show service logs"
    echo "  status    Show service status"
    echo "  cleanup   Remove all containers and data"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0              # Start services"
    echo "  $0 start        # Start services"
    echo "  $0 logs         # Show logs"
    echo "  $0 stop         # Stop services"
}

# Main function
main() {
    print_header "Content Agent Quick Start"
    
    # Check prerequisites
    check_docker
    
    # Setup environment
    setup_env
    create_directories
    create_db_init
    
    # Handle commands
    case "${1:-start}" in
        start)
            start_services
            ;;
        stop)
            stop_services
            ;;
        restart)
            stop_services
            sleep 2
            start_services
            ;;
        logs)
            show_logs
            ;;
        status)
            show_status
            ;;
        cleanup)
            cleanup
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
