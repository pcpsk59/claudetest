# Claude Test Project

A project with automated Git and GitHub workflow setup for safe version control.

## Features

- ✅ Automated CI/CD pipeline
- ✅ Branch protection with PR requirements
- ✅ Automated dependency updates
- ✅ Pre-commit hooks for code quality
- ✅ Security scanning
- ✅ Automated backups

## Workflow

This repository uses an automated workflow that:

1. **Protects your code**: Main branch requires pull request reviews
2. **Maintains quality**: Automated linting, testing, and formatting
3. **Keeps dependencies updated**: Dependabot automatically creates PRs for updates
4. **Provides security**: Automated security scanning on every commit
5. **Enables rollbacks**: Tagged releases for easy version management

## Getting Started

1. Clone the repository
2. Install dependencies (if applicable)
3. Create a feature branch: `git checkout -b feature/your-feature`
4. Make your changes
5. Push and create a pull request

## Branch Strategy

- `main`: Production-ready code, protected
- `feature/*`: New features and bug fixes
- `hotfix/*`: Emergency fixes

The automated workflow ensures all code is tested and reviewed before reaching main.