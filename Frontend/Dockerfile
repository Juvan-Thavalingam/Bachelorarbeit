FROM ghcr.io/cirruslabs/flutter:stable AS build

WORKDIR /app
COPY . .

# Dependencies & Build
RUN flutter pub get
RUN flutter build web

# 🌐 Serve-Stage mit NGINX
FROM nginx:alpine AS serve
COPY --from=build /app/build/web /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
