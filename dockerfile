# frontend build stage
FROM node:latest AS frontend_builder

WORKDIR /bamboo_builder/frontend
COPY ./frontend ./

# install pnpm
RUN npm install -g pnpm

# install frontend dependencies
RUN pnpm install

# build frontend static files
RUN pnpm run build

FROM python:3.12.1

WORKDIR /bamboo

# copy bamboo backend files
COPY ./backend ./

# copy frontend static files to APIFlask static folder
COPY --from=frontend_builder /bamboo/frontend/dist /bamboo/backend/static
# install requirements
RUN pip install -r requirements.txt
# install gunicorn
RUN pip install gunicorn

CMD [ "gunicorn", "app:app" ]
