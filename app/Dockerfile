FROM python:3.9

WORKDIR /app
ENV FLASK_APP=app
ENV SHOGI_ENGINE=/opt/YaneuraOu/YaneuraOu-mate-debian
COPY ./flaskapp/requirements.txt .
RUN apt-get update && apt-get install -y libgl1-mesa-dev clang && pip install --upgrade pip && pip install -r requirements.txt
RUN cd /opt && git clone https://github.com/yaneurao/YaneuraOu.git && cd /opt/YaneuraOu/source && make clean normal TARGET_CPU=AVX2 YANEURAOU_EDITION=YANEURAOU_MATE_ENGINE && mv /opt/YaneuraOu/source/YaneuraOu-by-gcc /opt/YaneuraOu/YaneuraOu-mate-debian && cd /app
