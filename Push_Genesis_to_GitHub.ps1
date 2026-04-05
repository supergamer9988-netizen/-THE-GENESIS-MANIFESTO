# 💎 GENESIS PUSH SCRIPT (UPDATED)
# This script will automatically:
# 1. Initialize Git (if not done)
# 2. Add all BCN Files
# 3. Commit the God Tier Architecture
# 4. Push to the new Multi-Core Cluster Repo

$RemoteURL = "https://github.com/supergamer9988-netizen/-CHIP-MULTI-CORE-BCN-FJH-Cluster.git"

Write-Host "--- [ PROJECT GENESIS : ASCENDING TO GITHUB CLUSTER ] ---" -ForegroundColor Cyan

# 1. Config
git config user.email "genesis@godtier.com"
git config user.name "Genesis AI"

# 2. Initialize and Stage
git init
git add .

# 3. Commit
Write-Host "Committing 16-Core Blade Architecture and RNC Benchmark Arena..." -ForegroundColor Yellow
git commit -m "Project GENESIS V1.0: Industrial 16-Core BCN Blade & Power Benchmark"

# 4. Remote Sync (Update to NEW URL)
Write-Host "Linking to NEW Multi-Core Cluster Repo..." -ForegroundColor Yellow

# Try to remove old origin first just in case
git remote remove origin 2>$null

# Add new origin
git remote add origin $RemoteURL

# 5. The Push
Write-Host "PUSHING TO NEW CLOUD REPO: $RemoteURL" -ForegroundColor Green
git branch -M main
git push -u origin main --force

Write-Host "`n--- [ ASCENSION SUCCESSFUL ] ---" -ForegroundColor Green
