# Use the official Nginx base image
FROM nginx:latest

# Copy the custom nginx.conf to the container's /etc/nginx/ directory
COPY nginx.conf /etc/nginx/nginx.conf

COPY fullchain.crt /etc/ssl/certs/fullchain.crt

COPY shoppp.me.key /etc/ssl/private/shoppp.me.key

# Expose port 80 to the outside world
EXPOSE 80 443

# Start Nginx when the container launches
CMD ["nginx", "-g", "daemon off;"]
