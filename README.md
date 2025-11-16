# akshar Documentation

This branch contains the built Sphinx documentation for GitHub Pages.

**Do not edit files in this branch directly.**

Documentation source files are in the `docs/source/` directory on the `main` branch.

## Updating Documentation

### Automated Method

From the `main` branch, run:
```bash
./docs/deploy_docs.sh
```

This will:
1. Build the documentation
2. Switch to `docs` branch
3. Copy built files
4. Commit changes
5. Optionally switch back to `main`

Then push:
```bash
git push origin docs
```

### Manual Method

```bash
# On main branch
git checkout main
cd docs && ./build_docs.sh

# Switch to docs branch
git checkout docs

# Copy built files
cp -r docs/build/html/* .

# Commit and push
git add .
git commit -m "Update documentation"
git push origin docs

# Switch back to main
git checkout main
```

## GitHub Pages Setup

1. Go to repository Settings > Pages
2. Under "Source", select:
   - Branch: `docs`
   - Folder: `/ (root)`
3. Save

Your documentation will be available at:
`https://<username>.github.io/<repository-name>/`

## Note

The `.nojekyll` file is required for GitHub Pages to serve Sphinx documentation correctly.

