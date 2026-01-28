FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for matplotlib and reportlab
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libfreetype6-dev \
    libpng-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for generated reports
RUN mkdir -p generated_reports

# Expose port
EXPOSE 8002

# Run the application
CMD ["python", "-m", "pdf_generator.api"]