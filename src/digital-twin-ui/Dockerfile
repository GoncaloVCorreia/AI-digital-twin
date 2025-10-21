# ---------- Build stage ----------
FROM node:18-alpine AS build
WORKDIR /app

# Copy and install dependencies
COPY package*.json ./
RUN npm ci

# Copy project and build static assets
COPY . .
RUN npm run build

# ---------- Serve stage ----------
FROM nginx:alpine
# Copy built React app into Nginx's default static directory
COPY --from=build /app/build /usr/share/nginx/html

# Configure SPA routing fallback
RUN printf 'server {\n\
    listen 80;\n\
    root /usr/share/nginx/html;\n\
    index index.html;\n\
    location / {\n\
        try_files $uri /index.html;\n\
    }\n\
}\n' > /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
