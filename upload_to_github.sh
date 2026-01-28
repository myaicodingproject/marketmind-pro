#!/bin/bash

# Quick GitHub upload script for hackathon submission
# Run this from your project root directory

echo "Setting up GitHub repository..."

# Initialize git if not already done
if [ ! -d ".git" ]; then
    git init
fi

# Add GitHub remote (replace with your actual repo name)
git remote add origin https://github.com/myaicodingproject/marketmind-pro.git

# Stage all files
git add .

# Commit with hackathon message
git commit -m "Hackathon submission: MarketMind Pro - AI-Powered Stock Research Platform

- Complete 25-30 page stock report generation in 5-8 minutes
- 6 core sections: Executive Summary, Company Analysis, Financial Analysis, Valuation, Risk Assessment, Interactive Q&A
- Built with FastAPI + React + Pydantic AI + Kiro CLI
- Production-ready architecture with comprehensive testing
- Professional PDF generation and interactive features

Developed for Dynamous Kiro Hackathon 2026"

# Push to GitHub
git push -u origin main

echo "Upload complete! Check your repository at:"
echo "https://github.com/myaicodingproject/marketmind-pro"
