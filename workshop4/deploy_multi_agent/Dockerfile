FROM --platform=linux/arm64 python:3.12
EXPOSE 8501
WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN  pip3 install --upgrade pip && pip3 install -r requirements.txt
COPY . .

# STRANDS_KNOWLEDGE_BASE_ID - Bedrock Knowledge Base identifier
# IMPORTANT: Replace "IMW46CITZE" with YOUR Bedrock Knowledge Base ID
# This is a placeholder value - students MUST update this with their own KB ID
# To find your KB ID: AWS Bedrock console > Knowledge bases > Your KB > Overview
# Example: ENV STRANDS_KNOWLEDGE_BASE_ID="ABC123XYZ"
ENV STRANDS_KNOWLEDGE_BASE_ID="IMW46CITZE"

# Command overriden by docker-compose
CMD streamlit run app.py
