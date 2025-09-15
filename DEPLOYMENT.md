# 🚀 Deployment Guide

This guide covers multiple deployment options for your SOP & Manual RAG Agent.

## 📋 Pre-Deployment Checklist

- [ ] OpenAI API key ready
- [ ] App tested locally with `streamlit run streamlit_app.py`
- [ ] Git repository created (for cloud deployments)

---

## 🌩️ Option 1: Streamlit Cloud (Recommended - FREE)

**Best for**: Quick deployment, no server management needed

### Steps:

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/sop-agent.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Set main file path: `streamlit_app.py`
   - Click "Deploy!"

3. **Configure Secrets**:
   - In Streamlit Cloud app settings, go to "Secrets"
   - Add your environment variables:
   ```toml
   OPENAI_API_KEY = "your_openai_api_key_here"
   MODEL_NAME = "gpt-3.5-turbo"
   EMBEDDING_MODEL = "text-embedding-ada-002"
   ```

### ✅ Pros:
- Free hosting
- Automatic HTTPS
- Easy updates via Git
- No server management

### ❌ Cons:
- Limited to 1GB RAM
- Public repository required (or Streamlit for Teams)

---

## 🐳 Option 2: Docker Deployment

**Best for**: Self-hosting, more control, private repositories

### Local Docker:

```bash
# Build and run
docker build -t sop-agent .
docker run -p 8501:8501 --env-file .env sop-agent
```

### Docker Compose:

```bash
# Create .env file with your API key
echo "OPENAI_API_KEY=your_key_here" > .env

# Run with docker-compose
docker-compose up -d
```

### Deploy to Cloud Provider:

#### **Digital Ocean App Platform**:
1. Connect your GitHub repo
2. Choose "Docker" as source
3. Set environment variables
4. Deploy

#### **AWS ECS/Fargate**:
```bash
# Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com
docker tag sop-agent:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/sop-agent:latest
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/sop-agent:latest
```

#### **Google Cloud Run**:
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT-ID/sop-agent
gcloud run deploy --image gcr.io/PROJECT-ID/sop-agent --platform managed
```

---

## ☁️ Option 3: Traditional Cloud Hosting

**Best for**: Full control, custom domains, high performance

### Heroku:

1. **Create Heroku app**:
   ```bash
   heroku create your-sop-agent
   heroku config:set OPENAI_API_KEY=your_key_here
   ```

2. **Add Procfile**:
   ```
   web: streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0
   ```

3. **Deploy**:
   ```bash
   git push heroku main
   ```

### AWS EC2:

1. **Launch EC2 instance** (t3.medium recommended)
2. **Install dependencies**:
   ```bash
   sudo apt update
   sudo apt install python3-pip nginx
   pip3 install -r requirements.txt
   ```

3. **Run with systemd**:
   ```bash
   sudo nano /etc/systemd/system/sop-agent.service
   ```
   ```ini
   [Unit]
   Description=SOP Agent
   After=network.target

   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/home/ubuntu/sop-agent
   Environment=OPENAI_API_KEY=your_key_here
   ExecStart=/usr/bin/python3 -m streamlit run streamlit_app.py --server.port=8501
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

4. **Enable and start**:
   ```bash
   sudo systemctl enable sop-agent
   sudo systemctl start sop-agent
   ```

---

## 🔧 Environment Variables

Set these in your deployment platform:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | ✅ Yes | - | Your OpenAI API key |
| `MODEL_NAME` | ❌ No | `gpt-3.5-turbo` | OpenAI model to use |
| `EMBEDDING_MODEL` | ❌ No | `text-embedding-ada-002` | Embedding model |

---

## 📊 Performance Considerations

### Memory Requirements:
- **Minimum**: 1GB RAM
- **Recommended**: 2GB+ RAM
- **High-volume**: 4GB+ RAM

### Storage:
- **Vector database**: ~100MB per 1000 document chunks
- **Uploaded files**: Temporary storage only
- **Recommended**: 10GB+ storage

### Scaling:
- Use load balancer for multiple instances
- Consider Redis for session state
- Implement file cleanup for uploads

---

## 🔒 Security Best Practices

1. **Environment Variables**:
   - Never commit API keys to Git
   - Use secrets management in production

2. **HTTPS**:
   - Always use HTTPS in production
   - Most cloud platforms provide this automatically

3. **Access Control**:
   - Consider adding authentication for sensitive documents
   - Implement IP whitelisting if needed

4. **Data Privacy**:
   - Documents are processed locally
   - OpenAI API calls use your content for responses only

---

## 🚨 Troubleshooting

### Common Issues:

1. **Memory errors**:
   - Reduce chunk size in `document_processor.py`
   - Process fewer documents at once

2. **OpenAI API errors**:
   - Check API key validity
   - Verify API credits
   - App falls back to local embeddings

3. **File upload issues**:
   - Check file size limits (200MB default)
   - Ensure PDF files are not corrupted

4. **Vector store issues**:
   - Clear vector store if corrupted
   - Ensure write permissions

### Monitoring:

Add basic monitoring to your deployment:
```python
# Add to streamlit_app.py
import logging
logging.basicConfig(level=logging.INFO)
```

---

## 📈 Recommended Deployment Path

1. **Start**: Streamlit Cloud (free, easy)
2. **Scale**: Docker on DigitalOcean/AWS
3. **Enterprise**: Custom infrastructure with load balancing

Choose based on your needs:
- **Personal/Demo**: Streamlit Cloud
- **Business**: Docker deployment
- **Enterprise**: Full cloud infrastructure