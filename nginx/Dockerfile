# Use the official Nginx base image
FROM nginx:latest

# Copy the custom nginx.conf to the container's /etc/nginx/ directory
COPY nginx.conf /etc/nginx/nginx.conf

COPY nginx-selfsigned.crt /etc/ssl/certs/nginx-selfsigned.crt

COPY nginx-selfsigned.key /etc/ssl/private/nginx-selfsigned.key

# Expose port 80 to the outside world
EXPOSE 80

# Start Nginx when the container launches
CMD ["nginx", "-g", "daemon off;"]
