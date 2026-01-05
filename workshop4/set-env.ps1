# PowerShell Environment Setup Script for Workshop 4 Multi-Agent Bedrock
# 
# WHY THIS EXISTS:
# Unfortunately, Kiro IDE is based on VS Code, which forces you to use PowerShell
# on Windows instead of a proper Unix terminal. This script sets the same 
# environment variables that would normally be in your ~/.bashrc file.
#
# WHEN TO USE THIS:
# - Only when you're stuck using PowerShell in Kiro IDE
# - When you have temporary AWS credentials that you don't want to put in ~/.bashrc
# - When you need to quickly set environment variables for testing
#
# PREFERRED ALTERNATIVE:
# Use Git Bash with proper ~/.bashrc setup whenever possible!
#
# USAGE:
# 1. Run this script: .\set-env.ps1
# 2. Set AWS credentials manually (see instructions below)
# 3. Then run your application: uv run streamlit run multi_agent_bedrock/app.py
#
# NOTE: These environment variables only last for the current PowerShell session

Write-Host "🔧 Setting up Workshop 4 environment variables for PowerShell..." -ForegroundColor Green
Write-Host "   VS Code/Kiro forces us to use PowerShell instead of proper Unix tools" -ForegroundColor Yellow
Write-Host ""

# Set Strands Knowledge Base ID (correct one)
$env:STRANDS_KNOWLEDGE_BASE_ID = "IMW46CITZE"
Write-Host "✅ STRANDS_KNOWLEDGE_BASE_ID = $env:STRANDS_KNOWLEDGE_BASE_ID" -ForegroundColor Green

# Set AWS Region
$env:AWS_REGION = "us-east-1"
Write-Host "✅ AWS_REGION = $env:AWS_REGION" -ForegroundColor Green

# Note: OPENSEARCH_HOST is not set (memory agent will use fallback mode)
Write-Host "ℹ️  OPENSEARCH_HOST not set - memory agent will use fallback mode" -ForegroundColor Yellow

# Set other useful environment variables
$env:MIN_SCORE = "0.000001"
$env:MAX_RESULTS = "9"
$env:BYPASS_TOOL_CONSENT = "true"
Write-Host "✅ MIN_SCORE = $env:MIN_SCORE" -ForegroundColor Green
Write-Host "✅ MAX_RESULTS = $env:MAX_RESULTS" -ForegroundColor Green
Write-Host "✅ BYPASS_TOOL_CONSENT = $env:BYPASS_TOOL_CONSENT" -ForegroundColor Green

Write-Host ""
Write-Host "⚠️  IMPORTANT: You must set AWS credentials manually before running the application!" -ForegroundColor Yellow
Write-Host "   Copy and paste these commands with your actual credentials:" -ForegroundColor Yellow
Write-Host ""
Write-Host '   $Env:AWS_ACCESS_KEY_ID="your-access-key-here"' -ForegroundColor Cyan
Write-Host '   $Env:AWS_SECRET_ACCESS_KEY="your-secret-key-here"' -ForegroundColor Cyan
Write-Host '   $Env:AWS_SESSION_TOKEN="your-session-token-here"' -ForegroundColor Cyan
Write-Host ""
Write-Host "Then run: uv run streamlit run multi_agent_bedrock/app.py" -ForegroundColor Green
Write-Host ""
Write-Host "Note: These variables are only set for this PowerShell session." -ForegroundColor Yellow