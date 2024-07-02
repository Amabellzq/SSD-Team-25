# Use the official Nginx base image
FROM nginx:latest

# Copy the custom nginx.conf to the container's /etc/nginx/ directory
COPY nginx.conf /etc/nginx/nginx.conf

COPY nginx-selfsigned.crt /etc/nginx/nginx.conf

COPY nginx-selfsigned.key /etc/nginx/nginx.conf

# Expose port 80 to the outside world
EXPOSE 80

# Start Nginx when the container launches
CMD ["nginx", "-g", "daemon off;"]
