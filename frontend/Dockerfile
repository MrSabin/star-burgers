FROM node:16.16.0-buster-slim
WORKDIR /opt/star-burgers
COPY package.json package-lock.json ./
RUN npm ci --include=dev
COPY bundles-src bundles-src/
RUN /opt/star-burgers/node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"