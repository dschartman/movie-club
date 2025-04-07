# Build stage
FROM node:lts-alpine as build

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci

# Copy source code
COPY . .

# Set the API URL to use the nginx proxy
ENV REACT_APP_API_URL=/api

# Build the app for production
RUN npm run build

# Production stage
FROM nginx:stable-alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

# This creates a runtime configurable file (will overwrite the one from build)
RUN echo 'window.MOVIE_CLUB_CONFIG = { API_URL: "/api" };' > /usr/share/nginx/html/config.js

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
