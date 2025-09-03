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
        self.backend_url = "http://localhost:8000"
        
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
    
    def check_backend_status(self):
        """Check if backend is running"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
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
            
            # Backend status
            backend_status = self.check_backend_status()
            status_color = "🟢" if backend_status else "🔴"
            status_text = "Connected" if backend_status else "Disconnected"
            st.markdown(f"**Backend:** {status_color} {status_text}")
            
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
                "📅 Content Scheduler": "scheduler",
                "📝 WordPress Manager": "wordpress",
                "⚙️ Settings": "settings"
            }
            
            selected_page = st.selectbox(
                "Navigate to:",
                options=list(pages.keys()),
                key="navigation"
            )
            
            st.session_state.current_page = pages[selected_page]
    
    def render_main_content(self):
        """Render main content area"""
        
        current_page = st.session_state.get('current_page', 'dashboard')
        
        if current_page == "dashboard":
            self.render_dashboard()
        elif current_page == "keyword_research":
            self.render_keyword_research()
        elif current_page == "content_generator":
            self.render_content_generator()
        elif current_page == "scheduler":
            self.render_scheduler()
        elif current_page == "wordpress":
            self.render_wordpress()
        elif current_page == "settings":
            self.render_settings()
    
    def render_dashboard(self):
        """Render dashboard page"""
        
        st.title("🏠 Dashboard")
        st.markdown("Welcome to Content Agent - Your AI-Powered Content Generation Platform")
        
        # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Modules Loaded",
                value=len(st.session_state.get('modules', {})),
                delta=None
            )
        
        with col2:
            st.metric(
                label="Content Generated",
                value="0",
                delta=None
            )
        
        with col3:
            st.metric(
                label="Keywords Researched",
                value="0",
                delta=None
            )
        
        with col4:
            backend_status = self.check_backend_status()
            st.metric(
                label="API Status",
                value="Online" if backend_status else "Offline",
                delta=None
            )
        
        st.markdown("---")
        
        # Quick Actions
        st.subheader("🚀 Quick Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔍 Research Keywords", use_container_width=True):
                st.session_state.current_page = "keyword_research"
                st.rerun()
        
        with col2:
            if st.button("✍️ Generate Content", use_container_width=True):
                st.session_state.current_page = "content_generator"
                st.rerun()
        
        with col3:
            if st.button("📅 Schedule Content", use_container_width=True):
                st.session_state.current_page = "scheduler"
                st.rerun()
        
        # System Status
        st.markdown("---")
        st.subheader("📊 System Status")
        
        # Module details
        if 'modules' in st.session_state:
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
                    self.perform_keyword_research(primary_keyword, location, research_depth)
                else:
                    st.error("Please enter a primary keyword")
    
    def render_content_generator(self):
        """Render content generator page"""
        
        st.title("✍️ Content Generator")
        st.markdown("Generate high-quality content powered by AI")
        
        st.info("Content generation functionality will be implemented when the content_generation module is created.")
    
    def render_scheduler(self):
        """Render scheduler page"""
        
        st.title("📅 Content Scheduler")
        st.markdown("Schedule and automate your content publishing")
        
        st.info("Scheduling functionality will be implemented when the scheduling module is created.")
    
    def render_wordpress(self):
        """Render WordPress manager page"""
        
        st.title("📝 WordPress Manager")
        st.markdown("Manage your WordPress content and publishing")
        
        st.info("WordPress integration will be implemented when the wordpress_integration module is created.")
    
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
    
    def perform_keyword_research(self, keyword: str, location: str, depth: str):
        """Perform keyword research"""
        
        with st.spinner(f"Researching '{keyword}'..."):
            try:
                # Simulate research process
                import time
                import random
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Simulate research steps
                steps = [
                    "Analyzing search trends...",
                    "Gathering SERP data...",
                    "Finding related keywords...",
                    "Analyzing competition...",
                    "Generating insights..."
                ]
                
                for i, step in enumerate(steps):
                    status_text.text(step)
                    time.sleep(1)
                    progress_bar.progress((i + 1) / len(steps))
                
                status_text.text("Research complete!")
                
                # Display results
                st.success("✅ Keyword research completed!")
                
                # Mock results
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📊 Keyword Metrics")
                    st.metric("Search Volume", f"{random.randint(1000, 50000):,}")
                    st.metric("Competition", random.choice(["Low", "Medium", "High"]))
                    st.metric("Opportunity Score", f"{random.randint(60, 95)}/100")
                
                with col2:
                    st.subheader("🔗 Related Keywords")
                    related_keywords = [
                        f"best {keyword}",
                        f"how to {keyword}",
                        f"{keyword} guide",
                        f"{keyword} tips",
                        f"free {keyword}"
                    ]
                    
                    for kw in related_keywords:
                        st.write(f"• {kw}")
                
            except Exception as e:
                st.error(f"Research failed: {e}")

def main():
    """Main function to run the Streamlit app"""
    app = ContentGeneratorApp()
    app.render()

if __name__ == "__main__":
    main()
