# frontend build stage
FROM node:latest AS frontend_builder

# install pnpm
RUN npm install -g pnpm

COPY ./frontend /bamboo-frontend

WORKDIR /bamboo-frontend
# install frontend dependencies
RUN pwd && ls -l && pnpm install && pnpm run build

FROM python:3.12-slim-bookworm

WORKDIR /bamboo

# copy bamboo backend files
COPY ./backend ./
COPY ./requirements.txt ./
# install requirements
RUN pip install -r requirements.txt && pip install gunicorn
# copy frontend static files to APIFlask static folder
COPY --from=frontend_builder /bamboo-frontend/dist ./static
COPY ./scripts/entrypoint.sh /entrypoint.sh
# set data directory
ENV DATA_DIR /data
ENV FRONTEND_DIR /bamboo/static
ENV FLASK_APP app.py
VOLUME [ "/data" ]

EXPOSE 8000
ENTRYPOINT [ "/entrypoint.sh" ]
CMD [ "start" ]
