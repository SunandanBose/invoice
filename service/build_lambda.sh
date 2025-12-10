#!/bin/bash

# Build Lambda deployment package using Docker
# This ensures compatibility with AWS Lambda runtime

echo "🐳 Building Lambda package with Docker..."

# Build Docker image
docker build -t invoice-lambda .

# Create container
docker create --name temp-invoice invoice-lambda

# Copy files from container
echo "📦 Extracting files..."
rm -rf package
docker cp temp-invoice:/asset ./package

# Remove container
docker rm temp-invoice

# Create zip file
echo "📦 Creating deployment package..."
cd package
zip -r ../lambda_deployment.zip .
cd ..

# Show file size
echo "✅ Package created!"
ls -lh lambda_deployment.zip

echo ""
echo "📤 Next steps:"
echo "1. Upload lambda_deployment.zip to AWS Lambda"
echo "2. Set handler to: lambda_function.lambda_handler"
echo "3. Set memory to: 512 MB"
echo "4. Set timeout to: 30 seconds"
echo "5. Runtime: Python 3.9"
echo ""
echo "⚠️  NO LAYER NEEDED - Dependencies are included!"

