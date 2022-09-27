FROM node:lts-alpine

WORKDIR /code

COPY package*.json ./

RUN npm install

RUN chmod a+rw ./node_modules

EXPOSE 8080

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.9.0/wait /wait
RUN chmod +x /wait

# Development mode
CMD /wait && npm run serve

# Production mode
# RUN npm install -g http-server
# CMD npm run build && /wait && http-server -P http://0.0.0.0:8080? dist
