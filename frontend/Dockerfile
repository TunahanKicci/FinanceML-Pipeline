FROM node:18-alpine AS build
WORKDIR /app

COPY package*.json ./

# NPM registry ve timeout ayarlarını yap
RUN npm config set registry https://registry.npmjs.org/ && \
    npm config set fetch-retries 5 && \
    npm config set fetch-retry-mintimeout 60000 && \
    npm config set fetch-retry-maxtimeout 300000

# NPM install with cache and retry
RUN npm install --legacy-peer-deps --network-timeout=300000

COPY . .
RUN npm run build

FROM nginx:alpine

# Install curl for healthchecks
RUN apk add --no-cache curl

COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]