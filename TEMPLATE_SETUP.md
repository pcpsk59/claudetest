# Project Template Setup Guide

## Method 1: GitHub Template Repository (Recommended)

### One-Time Setup:
1. **Create Template Repository**:
   ```bash
   # Push current setup to GitHub
   git remote add origin https://github.com/del19/project-template
   git push -u origin main
   ```
   
2. **Mark as Template**:
   - Go to GitHub repository settings
   - Check "Template repository" checkbox
   - Save settings

### For Each New Project:
1. **Use Template**: Click "Use this template" on GitHub
2. **Clone & Customize**: 
   ```bash
   git clone https://github.com/del19/new-project-name
   cd new-project-name
   ./setup-project.sh "New Project Name"
   ```

## Method 2: Local Template + Script

### One-Time Setup:
Create a local template directory with automated setup script.

### For Each New Project:
```bash
# Copy template
cp -r ~/templates/project-template ./new-project
cd new-project
./init-project.sh "Project Name" "description"
```

## Method 3: CLI Tool (Most Efficient)

### Install once:
```bash
npm install -g create-project-template
```

### Use for every project:
```bash
create-project my-new-project
cd my-new-project
# Everything is already set up!
```

## Recommended Workflow for Starting Any Project

### Before Writing Code:
1. **Initialize from template** (5 seconds)
2. **Run setup script** (30 seconds)
3. **Push to GitHub** (1 minute)
4. **Start coding** with full protection

### Template Includes:
- ✅ Git repository with main branch
- ✅ Complete .gitignore for all languages
- ✅ GitHub Actions CI/CD pipeline
- ✅ Dependabot configuration
- ✅ Pre-commit hooks
- ✅ PR templates
- ✅ Branch protection ready
- ✅ Security scanning
- ✅ Automated backups

This reduces setup time from 15-20 minutes to under 2 minutes!