#!/bin/bash

# Project Setup Script - Automates new project initialization
# Usage: ./setup-project.sh "Project Name" "Project Description" [language]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required parameters are provided
if [ $# -lt 1 ]; then
    print_error "Usage: $0 \"Project Name\" [\"Description\"] [language]"
    print_error "Example: $0 \"My Web App\" \"A cool web application\" \"javascript\""
    exit 1
fi

PROJECT_NAME="$1"
PROJECT_DESC="${2:-A new project with automated version control}"
LANGUAGE="${3:-general}"
REPO_NAME=$(echo "$PROJECT_NAME" | tr '[:upper:]' '[:lower:]' | sed 's/ /-/g')

print_status "Setting up project: $PROJECT_NAME"
print_status "Description: $PROJECT_DESC"
print_status "Language: $LANGUAGE"

# Update README with project details
print_status "Updating README.md..."
cat > README.md << EOF
# $PROJECT_NAME

$PROJECT_DESC

## Features

- ✅ Automated CI/CD pipeline
- ✅ Branch protection with PR requirements
- ✅ Automated dependency updates
- ✅ Pre-commit hooks for code quality
- ✅ Security scanning
- ✅ Automated backups

## Quick Start

1. Clone the repository
2. Install dependencies: \`npm install\` (or appropriate for your language)
3. Start development: \`npm run dev\` (or appropriate command)

## Development Workflow

1. Create feature branch: \`git checkout -b feature/your-feature\`
2. Make changes and commit (pre-commit hooks will run automatically)
3. Push and create pull request
4. After review and tests pass, merge to main

## Project Structure

\`\`\`
.
├── .github/              # GitHub workflows and templates
├── src/                  # Source code
├── tests/                # Test files
└── docs/                 # Documentation
\`\`\`

Generated with automated project template.
EOF

# Update dependabot.yml with correct username
if [ -f .github/dependabot.yml ]; then
    print_status "Updating Dependabot configuration..."
    # Get current git user
    GIT_USER=$(git config user.name || echo "owner")
    sed -i.bak "s/del19/$GIT_USER/g" .github/dependabot.yml && rm .github/dependabot.yml.bak
fi

# Language-specific setup
case $LANGUAGE in
    "javascript"|"js"|"node")
        print_status "Setting up JavaScript/Node.js project..."
        if [ ! -f package.json ]; then
            npm init -y
            sed -i.bak "s/\"name\": \".*\"/\"name\": \"$REPO_NAME\"/" package.json
            sed -i.bak "s/\"description\": \".*\"/\"description\": \"$PROJECT_DESC\"/" package.json && rm package.json.bak
        fi
        mkdir -p src tests
        echo "console.log('Hello from $PROJECT_NAME!');" > src/index.js
        ;;
    
    "python"|"py")
        print_status "Setting up Python project..."
        if [ ! -f requirements.txt ]; then
            touch requirements.txt
        fi
        mkdir -p src tests
        cat > src/main.py << EOF
#!/usr/bin/env python3
"""
$PROJECT_NAME
$PROJECT_DESC
"""

def main():
    print("Hello from $PROJECT_NAME!")

if __name__ == "__main__":
    main()
EOF
        ;;
    
    "java")
        print_status "Setting up Java project..."
        mkdir -p src/main/java src/test/java
        ;;
    
    *)
        print_status "Setting up general project..."
        mkdir -p src tests docs
        ;;
esac

# Commit all changes
print_status "Committing initial setup..."
git add .
git commit -m "chore: customize project setup for '$PROJECT_NAME'

- Update README with project details
- Configure language-specific structure for $LANGUAGE
- Set up initial project files" || print_warning "No changes to commit"

print_success "Project setup complete!"
print_status "Next steps:"
echo "  1. Push to GitHub: git remote add origin https://github.com/username/$REPO_NAME"
echo "  2. Push: git push -u origin main"
echo "  3. Enable branch protection in GitHub settings"
echo "  4. Start coding in the src/ directory"
echo ""
print_success "Your project '$PROJECT_NAME' is ready for development!"