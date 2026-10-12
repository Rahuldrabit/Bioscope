FROM node:24-bookworm-slim AS dependencies
WORKDIR /app
RUN corepack enable
COPY pnpm-workspace.yaml pnpm-lock.yaml ./
COPY apps/web/package.json ./apps/web/package.json
RUN pnpm --dir apps/web install --frozen-lockfile

FROM node:24-bookworm-slim AS build
WORKDIR /app
RUN corepack enable
COPY --from=dependencies /app/node_modules ./node_modules
COPY --from=dependencies /app/apps/web/node_modules ./apps/web/node_modules
COPY pnpm-workspace.yaml pnpm-lock.yaml ./
COPY apps/web ./apps/web
RUN pnpm --dir apps/web build

FROM node:24-bookworm-slim AS runtime
WORKDIR /app/apps/web
ENV NODE_ENV=production \
    HOSTNAME=0.0.0.0
COPY --from=build /app/node_modules /app/node_modules
COPY --from=build /app/apps/web/node_modules ./node_modules
COPY --from=build /app/apps/web/package.json ./package.json
COPY --from=build /app/apps/web/public ./public
COPY --from=build /app/apps/web/.next ./.next
EXPOSE 3000
CMD ["node", "node_modules/next/dist/bin/next", "start"]
