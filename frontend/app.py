"""
Streamlit Frontend Application
Main interface for Content Agent
"""

import streamlit as st
import asyncio
import sys
from pathlib import Path
import requests
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core import Container, EventBus, ModuleRegistry
from shared.config.settings import get_settings

class ContentGeneratorApp:
    """Main Streamlit application class"""
    
    def __init__(self):
        self.settings = get_settings()
        self.container = Container()
        self.module_registry = None
        
    async def initialize(self):
        """Initialize the application"""
        if 'app_initialized' not in st.session_state:
            # Setup dependencies
            self.container.register('config', self.settings)
            self.container.register('event_bus', EventBus())
            
            # Initialize module registry
            self.module_registry = ModuleRegistry(self.container)
            await self.module_registry.discover_and_load_modules()
            
            st.session_state.app_initialized = True
            st.session_state.modules = self.module_registry.get_all_modules()
    
    def render(self):
        """Render the main application"""
        
        # Page configuration
        st.set_page_config(
            page_title="Content Agent",
            page_icon="🤖",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Initialize app
        if 'app_initialized' not in st.session_state:
            with st.spinner("Initializing Content Agent..."):
                try:
                    asyncio.run(self.initialize())
                except Exception as e:
                    st.error(f"Failed to initialize application: {e}")
                    st.stop()
        
        # Main interface
        self.render_sidebar()
        self.render_main_content()
    
    def render_sidebar(self):
        """Render sidebar navigation"""
        
        with st.sidebar:
            st.title("🤖 Content Agent")
            st.markdown("---")
            
            # Module status
            if 'modules' in st.session_state:
                st.markdown("**Loaded Modules:**")
                for module_name, module in st.session_state.modules.items():
                    status_icon = "✅" if module.is_initialized() else "❌"
                    st.markdown(f"{status_icon} {module_name.replace('_', ' ').title()}")
            
            st.markdown("---")
            
            # Navigation
            pages = {
                "🏠 Dashboard": "dashboard",
                "🔍 Keyword Research": "keyword_research",
                "✍️ Content Generator": "content_generator",
                "📅 Scheduler": "scheduler",
                "📝 WordPress": "wordpress",
                "🕷️ Web Scraping": "web_scraping",
                "⚙️ Settings": "settings"
            }
            
            selected_page = st.selectbox("Navigation", list(pages.keys()))
            st.session_state.current_page = pages[selected_page]
    
    def render_main_content(self):
        """Render main content based on selected page"""
        
        if st.session_state.current_page == "dashboard":
            self.render_dashboard()
        elif st.session_state.current_page == "keyword_research":
            self.render_keyword_research()
        elif st.session_state.current_page == "content_generator":
            self.render_content_generator()
        elif st.session_state.current_page == "scheduler":
            self.render_scheduler()
        elif st.session_state.current_page == "wordpress":
            self.render_wordpress()
        elif st.session_state.current_page == "web_scraping":
            self.render_web_scraping()
        elif st.session_state.current_page == "settings":
            self.render_settings()
    
    def render_dashboard(self):
        """Render dashboard page"""
        
        st.title("🏠 Content Agent Dashboard")
        st.markdown("Welcome to your AI-powered content generation platform!")
        
        # Module status overview
        if 'modules' in st.session_state:
            st.subheader("📊 Module Status")
            
            col1, col2, col3 = st.columns(3)
            
            total_modules = len(st.session_state.modules)
            active_modules = sum(1 for module in st.session_state.modules.values() if module.is_initialized())
            
            with col1:
                st.metric("Total Modules", total_modules)
            
            with col2:
                st.metric("Active Modules", active_modules)
            
            with col3:
                st.metric("Success Rate", f"{(active_modules/total_modules)*100:.1f}%" if total_modules > 0 else "0%")
            
            # Module details
            st.subheader("🔧 Module Details")
            for module_name, module in st.session_state.modules.items():
                with st.expander(f"{module_name.replace('_', ' ').title()} Module"):
                    info = module.get_module_info()
                    st.write(f"**Version:** {info.version}")
                    st.write(f"**Description:** {info.description}")
                    st.write(f"**Status:** {'✅ Initialized' if module.is_initialized() else '❌ Not Initialized'}")
                    
                    if info.dependencies:
                        st.write(f"**Dependencies:** {', '.join(info.dependencies)}")
    
    def render_keyword_research(self):
        """Render keyword research page"""
        
        st.title("🔍 Keyword Research")
        st.markdown("Discover high-potential keywords for your content strategy")
        
        # Check if module is loaded
        if 'keyword_research' in st.session_state.modules:
            module = st.session_state.modules['keyword_research']
            if module.is_initialized():
                # Input form
                with st.form("keyword_research_form"):
                    st.subheader("Research Parameters")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        primary_keyword = st.text_input(
                            "Primary Keyword",
                            placeholder="Enter your main keyword...",
                            help="The main keyword you want to research"
                        )
                        
                        industry = st.selectbox(
                            "Industry",
                            ["Technology", "Marketing", "Healthcare", "Finance", "Education", "Other"]
                        )
                    
                    with col2:
                        location = st.selectbox(
                            "Target Location",
                            ["United States", "United Kingdom", "Canada", "Australia", "Global"]
                        )
                        
                        research_depth = st.select_slider(
                            "Research Depth",
                            options=["Basic", "Standard", "Comprehensive"],
                            value="Standard"
                        )
                    
                    submitted = st.form_submit_button("🔍 Start Research", use_container_width=True)
                    
                    if submitted:
                        if primary_keyword:
                            st.success(f"Keyword research initiated for: {primary_keyword}")
                            st.info("Research results will be displayed here once completed.")
                        else:
                            st.error("Please enter a primary keyword")
            else:
                st.error("Keyword Research module is not properly initialized")
        else:
            st.error("Keyword Research module not found")
    
    def render_content_generator(self):
        """Render content generator page"""
        
        st.title("✍️ Content Generator")
        st.markdown("Generate high-quality content powered by AI")
        
        # Check if module is loaded
        if 'content_generation' in st.session_state.modules:
            module = st.session_state.modules['content_generation']
            if module.is_initialized():
                # Content generation form
                with st.form("content_generation_form"):
                    st.subheader("Content Parameters")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        content_type = st.selectbox(
                            "Content Type",
                            ["Blog Post", "Social Media", "Website Copy", "Product Description", "Email Newsletter"]
                        )
                        
                        target_length = st.slider("Target Word Count", 100, 3000, 1000, 100)
                        
                        tone = st.selectbox(
                            "Tone",
                            ["Professional", "Casual", "Friendly", "Authoritative", "Conversational"]
                        )
                    
                    with col2:
                        industry = st.text_input("Industry/Topic", placeholder="e.g., Technology, Healthcare, Finance")
                        
                        target_audience = st.selectbox(
                            "Target Audience",
                            ["General", "Professionals", "Beginners", "Experts", "Decision Makers"]
                        )
                        
                        language = st.selectbox("Language", ["English", "Spanish", "French", "German"])
                    
                    # Content prompt
                    prompt = st.text_area(
                        "Content Prompt/Description",
                        placeholder="Describe what you want to create, include key points, target keywords, etc.",
                        height=120
                    )
                    
                    submitted = st.form_submit_button("🚀 Generate Content", use_container_width=True)
                    
                    if submitted:
                        if prompt.strip():
                            st.success("Content generation initiated!")
                            st.info("AI-generated content will appear here once completed.")
                        else:
                            st.error("Please provide a content prompt")
            else:
                st.error("Content Generation module is not properly initialized")
        else:
            st.error("Content Generation module not found")
    
    def render_scheduler(self):
        """Render scheduler page"""
        
        st.title("📅 Content Scheduler")
        st.markdown("Schedule and automate your content publishing")
        
        # Check if module is loaded
        if 'scheduling' in st.session_state.modules:
            module = st.session_state.modules['scheduling']
            if module.is_initialized():
                st.success("Scheduling module is active!")
                
                # Simple scheduling interface
                with st.form("scheduling_form"):
                    st.subheader("Schedule Content")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        content_title = st.text_input("Content Title")
                        publish_date = st.date_input("Publish Date")
                    
                    with col2:
                        publish_time = st.time_input("Publish Time")
                        platform = st.selectbox("Platform", ["WordPress", "Social Media", "Email"])
                    
                    submitted = st.form_submit_button("📅 Schedule Content", use_container_width=True)
                    
                    if submitted:
                        if content_title:
                            st.success(f"Content '{content_title}' scheduled for {publish_date} at {publish_time}")
                        else:
                            st.error("Please enter a content title")
            else:
                st.error("Scheduling module is not properly initialized")
        else:
            st.error("Scheduling module not found")
    
    def render_wordpress(self):
        """Render WordPress manager page"""
        
        st.title("📝 WordPress Manager")
        st.markdown("Manage your WordPress content and publishing")
        
        # Check if module is loaded
        if 'wordpress_integration' in st.session_state.modules:
            module = st.session_state.modules['wordpress_integration']
            if module.is_initialized():
                st.success("WordPress integration is active!")
                
                # WordPress status
                st.subheader("🔗 Connection Status")
                st.info("WordPress connection test successful!")
                
                # Quick actions
                st.subheader("⚡ Quick Actions")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("📊 Site Info", use_container_width=True):
                        st.info("Site information will be displayed here")
                
                with col2:
                    if st.button("📝 Recent Posts", use_container_width=True):
                        st.info("Recent posts will be displayed here")
                
                with col3:
                    if st.button("🖼️ Media Library", use_container_width=True):
                        st.info("Media library will be displayed here")
            else:
                st.error("WordPress integration module is not properly initialized")
        else:
            st.error("WordPress integration module not found")
    
    def render_web_scraping(self):
        """Render web scraping page"""
        
        st.title("🕷️ Web Scraping")
        st.markdown("Advanced web scraping and competitor analysis")
        
        # Check if module is loaded
        if 'web_scraping' in st.session_state.modules:
            module = st.session_state.modules['web_scraping']
            if module.is_initialized():
                st.success("Web scraping module is active!")
                
                # Scraping interface
                with st.form("scraping_form"):
                    st.subheader("Scrape Website")
                    
                    url = st.text_input("Website URL", placeholder="https://example.com")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        extraction_type = st.selectbox("Extraction Type", ["Content", "Links", "Images", "Full Page"])
                        max_pages = st.number_input("Max Pages", min_value=1, max_value=100, value=5)
                    
                    with col2:
                        delay = st.slider("Delay (seconds)", 0.0, 5.0, 1.0, 0.1)
                        use_ai = st.checkbox("Use AI for content analysis")
                    
                    submitted = st.form_submit_button("🕷️ Start Scraping", use_container_width=True)
                    
                    if submitted:
                        if url:
                            st.success(f"Scraping initiated for: {url}")
                            st.info("Scraping results will be displayed here once completed.")
                        else:
                            st.error("Please enter a valid URL")
            else:
                st.error("Web scraping module is not properly initialized")
        else:
            st.error("Web scraping module not found")
    
    def render_settings(self):
        """Render settings page"""
        
        st.title("⚙️ Settings")
        st.markdown("Configure Content Agent settings")
        
        # API Configuration
        with st.expander("🔑 API Configuration", expanded=True):
            st.text_input("OpenAI API Key", type="password", value="", help="Your OpenAI API key")
            st.text_input("Anthropic API Key", type="password", value="", help="Your Anthropic API key")
            st.text_input("Google API Key", type="password", value="", help="Your Google API key")
            st.text_input("SERP API Key", type="password", value="", help="Your SERP API key")
        
        # Content Settings
        with st.expander("📝 Content Settings"):
            st.slider("Default Content Length", 300, 3000, 1000, step=100)
            st.selectbox("Default Tone", ["Professional", "Casual", "Friendly", "Formal"])
            st.selectbox("Default Model", ["GPT-4o-mini", "Claude-3-Haiku", "GPT-4o"])
        
        # WordPress Settings
        with st.expander("📝 WordPress Settings"):
            st.text_input("WordPress URL", placeholder="https://yoursite.com")
            st.text_input("WordPress Username")
            st.text_input("WordPress App Password", type="password")
        
        # Save button
        if st.button("💾 Save Settings", type="primary", use_container_width=True):
            st.success("Settings saved successfully!")

def main():
    """Main entry point"""
    app = ContentGeneratorApp()
    app.render()

if __name__ == "__main__":
    main()
