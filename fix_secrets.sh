#!/bin/bash

echo "Removing secrets from files..."

# Remove or replace secrets in the identified files
if [ -f ".env.linear" ]; then
    sed -i 's/lin_api_[a-zA-Z0-9_]*/YOUR_LINEAR_API_KEY_HERE/g' .env.linear
fi

if [ -f "scripts/setup-github-linear.sh" ]; then
    sed -i 's/ghp_[a-zA-Z0-9_]*/YOUR_GITHUB_TOKEN_HERE/g' scripts/setup-github-linear.sh
    sed -i 's/lin_api_[a-zA-Z0-9_]*/YOUR_LINEAR_API_KEY_HERE/g' scripts/setup-github-linear.sh
fi

if [ -f "scripts/test-integration.sh" ]; then
    sed -i 's/ghp_[a-zA-Z0-9_]*/YOUR_GITHUB_TOKEN_HERE/g' scripts/test-integration.sh
    sed -i 's/lin_api_[a-zA-Z0-9_]*/YOUR_LINEAR_API_KEY_HERE/g' scripts/test-integration.sh
fi

if [ -f "scripts/update-linear-status.py" ]; then
    sed -i 's/lin_api_[a-zA-Z0-9_]*/YOUR_LINEAR_API_KEY_HERE/g' scripts/update-linear-status.py
fi

echo "Secrets replaced with placeholders"

# Add and commit the changes
git add .
git commit -m "Remove API keys and tokens for security"

# Push again
git push -u origin main

echo "Push completed!"
