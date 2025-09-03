# Content Agent - AI-Powered Content Generation Platform

**Content Agent** is a modular, AI-powered content generation platform that combines keyword research, content creation, SEO optimization, and automated publishing into one comprehensive solution.

## 🚀 Features

### Core Features
- **🔍 Keyword Research** - Multi-source keyword analysis with Google Trends, SERP API, and web scraping
- **✍️ Content Generation** - AI-powered content creation using OpenAI and Anthropic models
- **📊 SEO Optimization** - Real-time SEO scoring and optimization suggestions
- **📅 Content Scheduling** - Automated content scheduling and publishing
- **📝 WordPress Integration** - Direct publishing to WordPress sites
- **💰 Cost Management** - Smart model selection and usage tracking

### Advanced Features
- **🔧 Modular Architecture** - Easy to extend with new features
- **⚡ Real-time Processing** - Streaming content generation with progress tracking
- **📈 Analytics Dashboard** - Comprehensive performance tracking
- **🌐 Multi-language Support** - Content generation in multiple languages
- **🎯 Template System** - Pre-built content templates for different industries
- **🤖 Automation** - Fully automated content pipelines

## 🏗️ Architecture

Content Agent uses a modular architecture with the following components:

```
content_agent/
├── core/                    # Core framework (DI, Events, Module Registry)
├── shared/                  # Shared utilities and database models
├── modules/                 # Feature modules (plug & play)
│   ├── keyword_research/    # Keyword research and analysis
│   ├── content_generation/  # AI content generation
│   ├── scheduling/          # Content scheduling
│   ├── wordpress_integration/ # WordPress publishing
│   └── seo_optimization/    # SEO analysis and optimization
├── backend/                 # FastAPI REST API
├── frontend/               # Streamlit web interface
└── main.py                 # Application entry point
```

## 📋 Prerequisites

- Python 3.11 or higher
- PostgreSQL (optional, SQLite works for development)
- Redis (optional, for caching and task queues)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd content_agent
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux  
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys and settings
```

### 5. Setup Database (Optional)
```bash
# For PostgreSQL (recommended for production)
createdb content_agent

# Update DATABASE_URL in .env
# DATABASE_URL=postgresql://username:password@localhost:5432/content_agent
```

## ⚙️ Configuration

### Required API Keys

Add these to your `.env` file:

```env
# AI Models
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# SEO & Research
GOOGLE_API_KEY=your_google_api_key_here
SERPAPI_KEY=your_serpapi_key_here

# WordPress Integration
WORDPRESS_URL=https://yoursite.com
WORDPRESS_USERNAME=your_username
WORDPRESS_APP_PASSWORD=your_app_password

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/content_agent
REDIS_URL=redis://localhost:6379/0
```

### Optional Configuration

```env
# Rate Limits & Cost Control
DAILY_USER_LIMIT=50
COST_PER_USER_LIMIT=10.0
DEFAULT_MODEL_TIER=research

# Application Settings
DEBUG=true
LOG_LEVEL=INFO
SECRET_KEY=your-secret-key-here
```

## 🚀 Quick Start

### Method 1: Streamlit Frontend (Recommended for beginners)
```bash
python main.py --mode frontend
```
Then open http://localhost:8501 in your browser.

### Method 2: FastAPI Backend Only
```bash
python main.py --mode backend
```
API documentation available at http://localhost:8000/docs

### Method 3: Both Frontend and Backend
```bash
python main.py --mode both
```

## 📖 Usage Guide

### 1. Keyword Research

1. Navigate to **🔍 Keyword Research** in the sidebar
2. Enter your primary keyword
3. Select your target location and research depth
4. Click **🔍 Start Research**
5. Review results: metrics, related keywords, competitors, trends

### 2. Content Generation

1. Go to **✍️ Content Generator**
2. Input your keyword research results
3. Configure content parameters:
   - Content type (blog post, social media, etc.)
   - Tone and style
   - Target word count
   - Company information
4. Click **🚀 Generate Content**
5. Review and edit the generated content

### 3. Content Scheduling

1. Visit **📅 Content Scheduler**
2. Select generated content
3. Choose publishing platforms
4. Set schedule (one-time or recurring)
5. Configure automation settings

### 4. WordPress Publishing

1. Configure WordPress settings in **⚙️ Settings**
2. Test connection
3. Publish content directly or schedule for later

## 🔧 Development

### Adding New Modules

1. Create module directory in `modules/`
2. Implement module class extending `BaseModule`
3. Add services, routes, and UI components
4. The module will be auto-discovered and loaded

Example module structure:
```python
# modules/my_module/module.py
from core.base_module import BaseModule, ModuleInfo

class MyModule(BaseModule):
    def get_module_info(self) -> ModuleInfo:
        return ModuleInfo(
            name="my_module",
            version="1.0.0", 
            description="My custom module",
            dependencies=[]
        )
    
    async def initialize(self) -> bool:
        # Initialize your module
        return True
    
    def register_routes(self, app):
        # Register FastAPI routes
        pass
    
    def register_ui_components(self):
        # Register Streamlit components
        return {}
```

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black content_agent/
flake8 content_agent/
```

## 📊 API Documentation

### Keyword Research Endpoints

```
POST /api/keyword-research/research
GET  /api/keyword-research/suggestions/{keyword}
GET  /api/keyword-research/trending
GET  /api/keyword-research/history
```

### Content Generation Endpoints

```
POST /api/content/generate
GET  /api/content/templates
POST /api/content/optimize
GET  /api/content/history
```

### Scheduling Endpoints

```
POST /api/scheduling/schedule
GET  /api/scheduling/calendar
PUT  /api/scheduling/{schedule_id}
DELETE /api/scheduling/{schedule_id}
```

## 🎯 Model Usage & Costs

Content Agent uses a tiered model approach to optimize costs:

- **Research Tier** (Cheap): GPT-4o-mini for keyword research and analysis
- **Draft Tier** (Medium): Claude-3-Haiku for initial content drafts
- **Final Tier** (Expensive): GPT-4o for final content polishing

Estimated costs:
- Keyword research: ~$0.01 per query
- Content generation: ~$0.10-0.50 per article
- SEO optimization: ~$0.05 per analysis

## 🔒 Security

- API keys stored securely in environment variables
- Rate limiting to prevent abuse
- Input validation and sanitization
- WordPress app passwords (not regular passwords)

## 📈 Performance

- Async processing for concurrent operations
- Redis caching for frequently accessed data
- Background tasks for long-running operations
- Database connection pooling
- Optimized model selection based on task complexity

## 🐛 Troubleshooting

### Common Issues

**Module loading fails:**
```bash
# Check Python path and dependencies
pip install -r requirements.txt
python -c "import sys; print(sys.path)"
```

**API connection errors:**
- Verify API keys in `.env`
- Check network connectivity
- Ensure rate limits aren't exceeded

**Database connection issues:**
- Verify DATABASE_URL format
- Check PostgreSQL/SQLite permissions
- Run database migrations

**Frontend not loading:**
- Check if port 8501 is available
- Verify Streamlit installation
- Check browser console for errors

### Debug Mode
```bash
# Enable debug logging
export DEBUG=true
export LOG_LEVEL=DEBUG
python main.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure code passes linting
6. Submit a pull request

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
pytest
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI and Anthropic for AI models
- Google for Trends and Search APIs
- SerpAPI for SERP data
- Streamlit for the amazing UI framework
- FastAPI for the high-performance backend

## 📞 Support

- 📧 Email: support@contentagent.ai
- 💬 Discord: [Join our community](https://discord.gg/contentagent)
- 📖 Documentation: [docs.contentagent.ai](https://docs.contentagent.ai)
- 🐛 Issues: [GitHub Issues](https://github.com/contentagent/issues)

---

**Content Agent** - Empowering content creators with AI-driven automation 🚀
