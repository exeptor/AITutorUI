FROM python:3.9-slim
WORKDIR /Users/tsvm/Projects/AITutorUI
COPY . .
RUN pip install Flask
EXPOSE 5000
CMD [ "python", "./run.py" ]