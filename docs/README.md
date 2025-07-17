# Liberation System Documentation

This directory contains the source files for the Liberation System GitHub Pages site.

## Files

- `index.md` - Main landing page
- `architecture.md` - System architecture documentation
- `_config.yml` - Jekyll configuration
- `_layouts/default.html` - Custom dark neon theme layout
- `_data/navigation.yml` - Navigation configuration

## Local Development

To run the site locally:

```bash
# Install Jekyll
gem install bundler jekyll

# Create Gemfile
echo "source 'https://rubygems.org'" > Gemfile
echo "gem 'github-pages', group: :jekyll_plugins" >> Gemfile

# Install dependencies
bundle install

# Run local server
bundle exec jekyll serve
```

The site will be available at `http://localhost:4000`.

## GitHub Pages

The site is automatically deployed to GitHub Pages when changes are pushed to the `main` branch.

Live site: https://tiation.github.io/liberation-system
