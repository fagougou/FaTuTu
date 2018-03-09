FROM node:lastest

MAINTAINER kirito

# 设置时区
RUN sh -c "echo 'Asia/Shanghai' > /etc/timezone" && \
    dpkg-reconfigure -f noninteractive tzdata

ADD package.json /tmp/package.json
RUN npm config set registry https://registry.npm.taobao.org && \
    cd /tmp && \
    npm install
RUN mkdir -p /app && cp -a /tmp/node_modules /app/

WORKDIR /app

ADD . .

EXPOSE 9000 9443

CMD ["node", "bin/www"]