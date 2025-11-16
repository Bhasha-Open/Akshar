#!/bin/bash
# Deploy built documentation to docs branch for GitHub Pages

set -e

echo "Deploying documentation to docs branch..."
echo ""

# make sure we're on main
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "Warning: Not on main branch (currently on $CURRENT_BRANCH)"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# build docs first
echo "Building documentation..."
cd docs
./build_docs.sh
cd ..

# stash any uncommitted changes
git stash

# switch to docs branch
echo "Switching to docs branch..."
git checkout docs

# copy built files
echo "Copying built HTML files..."
rm -rf *.html *.js *.inv _* api/ features/ installation.html quickstart.html tutorials/ cli.html genindex.html search.html objects.inv searchindex.js
cp -r docs/build/html/* .

# add .nojekyll if missing
touch .nojekyll

# commit and push
echo "Committing changes..."
git add .
git commit -m "Update documentation [auto-deploy]" || echo "No changes to commit"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ Documentation deployed!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "To push to GitHub:"
echo "  git push origin docs"
echo ""
echo "Then configure GitHub Pages:"
echo "  Settings > Pages > Source: docs branch"
echo ""

# switch back to main
read -p "Switch back to main branch? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git checkout main
    git stash pop || true
fi

