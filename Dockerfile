# Multi-stage build for Liberation System
FROM node:18-alpine AS frontend-builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build frontend
RUN npm run build

# Python backend stage
FROM python:3.9-slim AS backend-builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    pkg-config \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Final production stage
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=backend-builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# Copy frontend build
COPY --from=frontend-builder /app/.next /app/.next
COPY --from=frontend-builder /app/public /app/public
COPY --from=frontend-builder /app/node_modules /app/node_modules

# Copy application code
COPY core/ /app/core/
COPY mesh/ /app/mesh/
COPY security/ /app/security/
COPY transformation/ /app/transformation/
COPY interface/ /app/interface/
COPY package.json /app/

# Create non-root user
RUN useradd -m -u 1001 liberation && \
    chown -R liberation:liberation /app

USER liberation

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Expose ports
EXPOSE 3000 8000

# Environment variables
ENV NODE_ENV=production
ENV LIBERATION_MODE=production
ENV TRUST_LEVEL=maximum

# Start command
CMD ["sh", "-c", "python core/automation-system.py & npm start"]

# Labels for better organization
LABEL org.opencontainers.image.title="Liberation System"
LABEL org.opencontainers.image.description="A minimal system to flip everything on its head"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.source="https://github.com/tiation/liberation-system"
LABEL org.opencontainers.image.vendor="Tiation"
LABEL org.opencontainers.image.licenses="MIT"
