FROM node:18

WORKDIR /app

COPY package.json yarn.lock ./

RUN yarn install --frozen-lockfile

COPY . .

RUN yarn build

CMD ["yarn", "serve", "--host", "0.0.0.0"]
