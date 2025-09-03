"""
Content Generation UI Components
Streamlit interface for content generation module
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, List
import json

class ContentGenerationUI:
    """UI components for content generation module"""
    
    @staticmethod
    def main_interface():
        """Main content generation interface"""
        st.title("✍️ Content Generator")
        st.markdown("Generate high-quality content using AI-powered tools")
        
        # Main tabs
        tab1, tab2, tab3 = st.tabs(["🚀 Generate Content", "📋 Templates", "📊 Analytics"])
        
        with tab1:
            ContentGenerationUI.content_generator()
        
        with tab2:
            ContentGenerationUI.template_manager()
        
        with tab3:
            ContentGenerationUI.analytics_dashboard()
    
    @staticmethod
    def content_generator():
        """Content generation interface"""
        st.subheader("Generate New Content")
        
        # Content parameters
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
        
        # Generate button
        if st.button("🚀 Generate Content", type="primary", use_container_width=True):
            if prompt.strip():
                with st.spinner("Generating content..."):
                    # Simulate content generation
                    st.success("Content generated successfully!")
                    
                    # Display generated content
                    st.subheader("Generated Content")
                    st.markdown("### Sample Title")
                    st.write("This is a sample generated title based on your prompt.")
                    
                    st.markdown("### Sample Content")
                    st.write("This is sample generated content. In a real implementation, this would be AI-generated content based on your parameters and prompt.")
                    
                    st.markdown("### SEO Meta Description")
                    st.write("This is a sample SEO meta description for your content.")
            else:
                st.error("Please provide a content prompt to generate content.")
    
    @staticmethod
    def template_manager():
        """Template management interface"""
        st.subheader("Content Templates")
        st.markdown("Manage your content templates and create custom ones")
        
        # Available templates
        templates = [
            {
                "name": "Blog Post",
                "description": "Comprehensive blog post with SEO optimization",
                "word_count": "1000-1500",
                "sections": ["Introduction", "Main Content", "Conclusion"],
                "use_cases": ["Thought leadership", "How-to guides", "Industry insights"]
            },
            {
                "name": "Social Media Post",
                "description": "Engaging social media content",
                "word_count": "100-300",
                "sections": ["Hook", "Value", "Call-to-Action"],
                "use_cases": ["LinkedIn posts", "Twitter threads", "Facebook updates"]
            },
            {
                "name": "Website Copy",
                "description": "Conversion-focused website content",
                "word_count": "300-800",
                "sections": ["Headline", "Problem", "Solution", "CTA"],
                "use_cases": ["Landing pages", "Service pages", "About pages"]
            }
        ]
        
        for template in templates:
            with st.expander(f"📋 {template['name']}"):
                st.write(f"**Description:** {template['description']}")
                st.write(f"**Word Count:** {template['word_count']}")
                st.write(f"**Sections:** {', '.join(template['sections'])}")
                st.write(f"**Use Cases:** {', '.join(template['use_cases'])}")
                
                if st.button(f"Use {template['name']} Template", key=f"use_{template['name']}"):
                    st.success(f"Template '{template['name']}' selected!")
    
    @staticmethod
    def analytics_dashboard():
        """Analytics dashboard"""
        st.subheader("Content Analytics")
        st.markdown("Track your content performance and generation metrics")
        
        # Sample metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Content", "47")
            st.metric("This Month", "12")
        
        with col2:
            st.metric("Avg. Word Count", "1,247")
            st.metric("Avg. Generation Time", "2.3 min")
        
        with col3:
            st.metric("Success Rate", "94%")
            st.metric("User Satisfaction", "4.8/5")
        
        with col4:
            st.metric("Cost This Month", "$23.45")
            st.metric("Tokens Used", "45.2K")
        
        # Sample chart
        st.subheader("Content Generation Trends")
        chart_data = pd.DataFrame({
            'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'Content Generated': [8, 12, 15, 11, 18, 22],
            'Cost': [12.50, 18.75, 23.45, 17.20, 28.10, 34.50]
        })
        
        st.line_chart(chart_data.set_index('Month')['Content Generated'])
        
        # Recent activity
        st.subheader("Recent Activity")
        activities = [
            "Generated blog post: 'AI in Healthcare' (1,200 words)",
            "Created social media template for Q2 campaign",
            "Updated product description for new service",
            "Generated email newsletter for March"
        ]
        
        for activity in activities:
            st.write(f"• {activity}")
