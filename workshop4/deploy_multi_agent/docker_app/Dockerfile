FROM --platform=linux/arm64 python:3.12
EXPOSE 8501
WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN  pip3 install --upgrade pip && pip3 install -r requirements.txt
COPY . .

# STRANDS_KNOWLEDGE_BASE_ID - Bedrock Knowledge Base identifier
# IMPORTANT: Replace "IMW46CITZE" with your own Knowledge Base ID
# This value is from the workshop setup - builders must use their own KB ID
# To find your KB ID: Check AWS Bedrock console > Knowledge bases > Your KB > Overview
ENV STRANDS_KNOWLEDGE_BASE_ID="IMW46CITZE"

# Command overriden by docker-compose
CMD streamlit run app.py
