FROM ruby:3.2-slim

# Install system build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /srv/jekyll

# Install Bundler
RUN gem install bundler

# Copy Gemfile and install dependencies (cached in Docker layer)
COPY Gemfile* ./
RUN bundle install

EXPOSE 4000

CMD ["bundle", "exec", "jekyll", "serve", "--host", "0.0.0.0", "--port", "4000", "--livereload"]
