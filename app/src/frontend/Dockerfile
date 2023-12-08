FROM node:20.9.0-buster-slim as build

WORKDIR /app
ENV PATH /app/node_modules/.bin:$PATH
ENV PUBLIC_URL /

COPY package.json ./
COPY yarn.lock ./
RUN npm install

COPY . ./
RUN npm run build

# Nginx wrapper to serve static files
FROM nginx:stable
ENV NODE_ENV production
# remove existing files from nginx directory
RUN rm -rf /usr/share/nginx/html/*
# copy built assets from 'build' stage
COPY --from=build /app/out /usr/share/nginx/html
# add nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]