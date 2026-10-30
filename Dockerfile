# Build
FROM node:24.4.1-alpine3.21 AS build
WORKDIR /app
RUN npm install -g pnpm@12.16.1
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile
COPY . .
RUN pnpm build

# Production Dependencies
FROM node:24.4.1-alpine3.21 AS dependencies
WORKDIR /app
COPY ./package.json ./
COPY ./pnpm-lock.yaml ./pnpm-workspace.yaml ./
RUN npm install -g pnpm@12.16.1
RUN pnpm i --prod --frozen-lockfile

# Runtime
FROM node:24.4.1-alpine3.21 AS runtime
USER node:node
WORKDIR /app
COPY --from=dependencies --chown=node:node /app/node_modules ./node_modules
COPY --from=build --chown=node:node /app/package.json /app/build ./
EXPOSE 3000
CMD ["node", "index.js"]