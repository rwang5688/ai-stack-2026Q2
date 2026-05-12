FROM --platform=linux/arm64 python:3.12
EXPOSE 8501
WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt
COPY . .
ENV BYPASS_TOOL_CONSENT=true
ENV OTEL_SDK_DISABLED=true
CMD streamlit run streamlit_app/app.py --server.port 8501 --server.address 0.0.0.0
