FROM node:12.2.0-alpine

WORKDIR /frontend

COPY package.json ./
COPY package-lock.json ./

RUN npm install -g -- --mode development

ENV NODE_ENV=development
ENV REACT_APP_VERSION=dev-in-docker
ENV PATH="/usr/lib/node-modules/.bin:${PATH}"

CMD ["npm","start"]


