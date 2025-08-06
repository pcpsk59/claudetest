# New Project Setup Checklist

## ⚡ Quick Start (2 minutes)

### Option 1: Use GitHub Template (Fastest)
- [ ] Go to https://github.com/del19/project-template
- [ ] Click "Use this template" → "Create a new repository"
- [ ] Name your repository and clone it
- [ ] Run: `./setup-project.sh "Project Name" "Description" "language"`
- [ ] Push: `git push -u origin main`

### Option 2: Copy Template Locally
```bash
# Copy template
cp -r ~/project-template ./my-new-project
cd my-new-project
./setup-project.sh "My New Project" "Project description" "javascript"
```

## 📋 Pre-Development Checklist

### Repository Setup (Required)
- [ ] **Initialize Git**: Repository created with main branch
- [ ] **Add .gitignore**: Comprehensive exclusions for your language
- [ ] **Create README**: Project description and setup instructions
- [ ] **First commit**: Initial project structure committed

### GitHub Setup (Recommended)
- [ ] **Push to GitHub**: Repository created and pushed
- [ ] **Branch Protection**: 
  - [ ] Protect main branch
  - [ ] Require PR reviews (at least 1)
  - [ ] Require status checks to pass
  - [ ] Restrict pushes to main
- [ ] **Enable Discussions**: For team communication
- [ ] **Add Topics**: For repository discovery

### Automation Setup (Essential)
- [ ] **GitHub Actions**: CI/CD pipeline configured
  - [ ] Code quality checks
  - [ ] Security scanning
  - [ ] Automated testing
  - [ ] Daily backups
- [ ] **Dependabot**: Dependency updates configured
- [ ] **Pre-commit hooks**: Local quality checks installed
  ```bash
  pip install pre-commit
  pre-commit install
  ```

### Development Environment
- [ ] **IDE Setup**: VS Code/IntelliJ with relevant extensions
- [ ] **Linting**: ESLint, Flake8, or language-specific linters
- [ ] **Formatting**: Prettier, Black, or auto-formatters
- [ ] **Testing**: Jest, pytest, or testing framework
- [ ] **Package Manager**: npm, pip, cargo, etc. initialized

### Documentation
- [ ] **API Documentation**: If building APIs
- [ ] **Contributing Guidelines**: For team projects
- [ ] **License**: Choose appropriate license
- [ ] **Changelog**: For tracking versions

### Security
- [ ] **Secrets Management**: No hardcoded secrets
- [ ] **Environment Variables**: .env template created
- [ ] **Security Scanning**: CodeQL or similar enabled
- [ ] **Dependency Audit**: Regular security updates

## 🚨 Before First Code Commit

### Final Verification
- [ ] All automated checks pass
- [ ] Pre-commit hooks work locally
- [ ] GitHub Actions workflow validates
- [ ] Branch protection rules active
- [ ] Team has access (if applicable)

### First Development Cycle Test
1. [ ] Create feature branch: `git checkout -b feature/test-setup`
2. [ ] Make small change and commit
3. [ ] Push and create PR
4. [ ] Verify all checks pass
5. [ ] Merge PR to test full workflow

## ⚙️ Language-Specific Additions

### JavaScript/Node.js
- [ ] `package.json` configured
- [ ] ESLint + Prettier setup
- [ ] Jest or testing framework
- [ ] TypeScript (if applicable)

### Python
- [ ] `requirements.txt` or `pyproject.toml`
- [ ] Virtual environment setup
- [ ] Flake8 + Black configured
- [ ] pytest setup

### Java
- [ ] Maven or Gradle configured
- [ ] JUnit setup
- [ ] CheckStyle configured

### Go
- [ ] `go.mod` initialized
- [ ] `go fmt` and `go vet` in CI
- [ ] Testing setup

---

## 🎯 Success Criteria

✅ **Your project is properly set up when:**
- New team members can clone and start contributing in under 5 minutes
- All code changes go through automated quality checks
- Main branch is always deployable
- Dependencies stay updated automatically
- Security vulnerabilities are caught early
- You can rollback to any previous version easily