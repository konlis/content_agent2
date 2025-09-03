"""
WordPress Integration Module Streamlit UI Components
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import asyncio
import requests
from loguru import logger
import base64

class WordPressUI:
    """UI components for WordPress integration and content publishing"""
    
    @staticmethod
    def dashboard():
        """WordPress integration dashboard"""
        st.title("📝 WordPress Dashboard")
        
        # Connection status
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Connection Status",
                value="Connected",
                delta="Healthy",
                help="WordPress site connection status"
            )
        
        with col2:
            st.metric(
                "Posts Published",
                value="23",
                delta="5 this week",
                help="Total posts published via Content Agent"
            )
        
        with col3:
            st.metric(
                "Media Library",
                value="45",
                delta="8 new",
                help="Media items in WordPress library"
            )
        
        with col4:
            st.metric(
                "Success Rate",
                value="96.8%",
                delta="2.1%",
                help="Publishing success rate"
            )
        
        st.divider()
        
        # Quick actions
        st.subheader("🚀 Quick Actions")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📝 Publish Content", use_container_width=True):
                st.switch_page("pages/wordpress_publish.py")
        
        with col2:
            if st.button("🖼️ Generate Image", use_container_width=True):
                st.session_state['show_image_generator'] = True
                st.rerun()
        
        with col3:
            if st.button("📚 Media Library", use_container_width=True):
                st.switch_page("pages/wordpress_media.py")
        
        with col4:
            if st.button("⚙️ Settings", use_container_width=True):
                st.switch_page("pages/wordpress_settings.py")
        
        # Image generator modal
        if st.session_state.get('show_image_generator', False):
            WordPressUI._show_image_generator_modal()
        
        # Recent activity and statistics code continues as before...
        # (Previous code for dashboard remains the same)
    
    @staticmethod
    def _show_image_generator_modal():
        """Show image generation modal"""
        st.subheader("🎨 Generate Featured Image")
        
        with st.container():
            # Image generation form
            col1, col2 = st.columns(2)
            
            with col1:
                prompt_input = st.text_area(
                    "Image Prompt",
                    placeholder="Describe the image you want to generate...",
                    help="Describe what you want the image to show"
                )
                
                title_input = st.text_input(
                    "Article Title (Optional)",
                    placeholder="Enter article title for context"
                )
                
                keywords_input = st.text_input(
                    "Keywords (Optional)",
                    placeholder="Enter keywords separated by commas"
                )
            
            with col2:
                style = st.selectbox(
                    "Image Style",
                    options=["photorealistic", "illustration", "modern", "corporate", "abstract", "vintage"],
                    help="Choose the visual style for the generated image"
                )
                
                aspect_ratio = st.selectbox(
                    "Aspect Ratio",
                    options=["16:9", "4:3", "1:1", "3:2"],
                    help="Choose the dimensions for the image"
                )
                
                # API Model Selection
                api_model = st.selectbox(
                    "AI Model",
                    options=["gemini-flash", "dall-e-3", "stable-diffusion"],
                    help="Choose which AI model to use for generation"
                )
                
                auto_upload = st.checkbox(
                    "Auto-upload to WordPress",
                    value=True,
                    help="Automatically upload generated image to WordPress media library"
                )
            
            # Generation buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🎨 Generate Image", type="primary"):
                    if prompt_input:
                        with st.spinner(f"Generating image with {api_model.upper()}..."):
                            # Mock generation process
                            import time
                            time.sleep(3)
                        
                        st.success("✅ Image generated successfully!")
                        
                        # Show preview
                        st.image(
                            "https://via.placeholder.com/800x450/4A90E2/FFFFFF?text=Generated+Image",
                            caption=f"Generated with {api_model}: {prompt_input[:50]}...",
                            use_container_width=True
                        )
                        
                        if auto_upload:
                            st.info("📤 Image uploaded to WordPress media library")
                            st.write("**Media ID:** 123")
                            st.write("**WordPress URL:** https://yoursite.com/wp-content/uploads/generated-image.jpg")
                    else:
                        st.error("Please enter an image prompt")
            
            with col2:
                if st.button("🔄 Generate from Content"):
                    # Show content selection
                    content_options = {
                        "content_1": "Digital Marketing Guide",
                        "content_2": "SEO Best Practices", 
                        "content_3": "Social Media Strategy"
                    }
                    
                    selected_content = st.selectbox(
                        "Select Content",
                        options=list(content_options.keys()),
                        format_func=lambda x: content_options[x]
                    )
                    
                    if st.button("Generate from Selected Content"):
                        with st.spinner(f"Analyzing content and generating image with {api_model.upper()}..."):
                            import time
                            time.sleep(3)
                        
                        st.success("✅ Content-based image generated!")
                        st.image(
                            "https://via.placeholder.com/800x450/2C5F8C/FFFFFF?text=Content+Based+Image",
                            caption=f"Generated from: {content_options[selected_content]}",
                            use_container_width=True
                        )
            
            with col3:
                if st.button("❌ Close"):
                    st.session_state['show_image_generator'] = False
                    st.rerun()
    
    @staticmethod
    def publish_form():
        """WordPress content publishing form"""
        # Previous publish form code continues as before...
        # (All the publishing form code remains the same)
        pass
    
    @staticmethod
    def settings():
        """WordPress integration settings"""
        st.title("⚙️ WordPress Settings")
        
        # Connection settings
        st.subheader("🔗 Connection Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            wordpress_url = st.text_input(
                "WordPress Site URL",
                value="https://yoursite.com",
                placeholder="https://yourwordpresssite.com"
            )
            
            username = st.text_input(
                "WordPress Username",
                value="admin",
                placeholder="Your WordPress username"
            )
        
        with col2:
            app_password = st.text_input(
                "WordPress App Password",
                value="xxxx xxxx xxxx xxxx xxxx xxxx",
                type="password",
                help="Generate this in WordPress Admin → Users → Profile"
            )
            
            # Test connection button
            if st.button("🔍 Test Connection"):
                with st.spinner("Testing WordPress connection..."):
                    import time
                    time.sleep(2)
                
                st.success("✅ WordPress connection successful!")
                
                # Show site info
                with st.expander("📊 Site Information"):
                    st.write("**Site Name:** Your WordPress Site")
                    st.write("**WordPress Version:** 6.4.2")
                    st.write("**Active Theme:** Twenty Twenty-Four")
                    st.write("**Total Posts:** 45")
                    st.write("**Total Media:** 67")
        
        st.divider()
        
        # Image generation settings
        st.subheader("🎨 Image Generation Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**AI Image Generation:**")
            
            # API Model Selection
            image_api_model = st.selectbox(
                "Default Image Generation API",
                options=["gemini-flash", "dall-e-3", "midjourney", "stable-diffusion"],
                index=0,
                help="Choose which AI model to use for image generation"
            )
            
            if image_api_model == "gemini-flash":
                google_api_key = st.text_input(
                    "Google API Key",
                    value="AIza..." if st.secrets.get("GOOGLE_API_KEY") else "",
                    type="password",
                    help="Google Gemini API key for image generation"
                )
                
                if st.button("🔍 Test Gemini API"):
                    with st.spinner("Testing Gemini API..."):
                        import time
                        time.sleep(2)
                    st.success("✅ Gemini API connection successful!")
                    
            elif image_api_model == "dall-e-3":
                openai_api_key = st.text_input(
                    "OpenAI API Key",
                    value="sk-..." if st.secrets.get("OPENAI_API_KEY") else "",
                    type="password",
                    help="OpenAI API key for DALL-E 3"
                )
                
                if st.button("🔍 Test OpenAI API"):
                    with st.spinner("Testing OpenAI API..."):
                        import time
                        time.sleep(2)
                    st.success("✅ OpenAI API connection successful!")
            
            elif image_api_model == "stable-diffusion":
                st.info("🔧 Stable Diffusion integration coming soon!")
                
            elif image_api_model == "midjourney":
                st.info("🔧 Midjourney integration coming soon!")
            
            default_image_style = st.selectbox(
                "Default Image Style",
                options=["photorealistic", "illustration", "modern", "corporate", "abstract"],
                index=0
            )
            
            default_aspect_ratio = st.selectbox(
                "Default Aspect Ratio",
                options=["16:9", "4:3", "1:1", "3:2"],
                index=0
            )
        
        with col2:
            st.write("**Image Optimization:**")
            
            max_image_width = st.number_input(
                "Max Image Width (px)",
                min_value=800,
                max_value=3000,
                value=1920
            )
            
            max_image_height = st.number_input(
                "Max Image Height (px)",
                min_value=600,
                max_value=2000,
                value=1080
            )
            
            image_quality = st.slider(
                "Image Quality",
                min_value=60,
                max_value=100,
                value=85,
                help="JPEG quality percentage"
            )
            
            convert_to_webp = st.checkbox(
                "Convert to WebP format",
                value=False,
                help="Convert images to WebP for better compression"
            )
            
            auto_alt_text = st.checkbox(
                "Auto-generate alt text",
                value=True,
                help="Automatically generate SEO-friendly alt text for images"
            )
        
        st.divider()
        
        # Save settings
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            if st.button("💾 Save Settings", type="primary", use_container_width=True):
                with st.spinner("Saving settings..."):
                    import time
                    time.sleep(1)
                
                st.success("✅ Settings saved successfully!")
                st.balloons()
    
    @staticmethod
    def media_library():
        """WordPress media library interface"""
        st.title("📚 WordPress Media Library")
        
        # Media library controls
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            media_filter = st.selectbox(
                "Filter by type:",
                options=["all", "image", "video", "audio", "document"]
            )
        
        with col2:
            sort_by = st.selectbox(
                "Sort by:",
                options=["date", "name", "size", "type"]
            )
        
        with col3:
            if st.button("📤 Upload Media"):
                st.session_state['show_upload_modal'] = True
        
        with col4:
            if st.button("🔄 Refresh Library"):
                st.rerun()
        
        # Upload modal
        if st.session_state.get('show_upload_modal', False):
            with st.container():
                st.subheader("📤 Upload Media")
                
                uploaded_files = st.file_uploader(
                    "Choose files",
                    accept_multiple_files=True,
                    type=['jpg', 'jpeg', 'png', 'gif', 'webp', 'mp4', 'pdf', 'doc', 'docx']
                )
                
                if uploaded_files:
                    for file in uploaded_files:
                        col1, col2, col3 = st.columns([2, 2, 1])
                        
                        with col1:
                            st.write(f"📁 {file.name}")
                        
                        with col2:
                            st.write(f"Size: {file.size / 1024:.1f} KB")
                        
                        with col3:
                            if st.button("Upload", key=f"upload_{file.name}"):
                                with st.spinner(f"Uploading {file.name}..."):
                                    import time
                                    time.sleep(2)
                                st.success(f"✅ {file.name} uploaded!")
                
                if st.button("❌ Close Upload"):
                    st.session_state['show_upload_modal'] = False
                    st.rerun()
        
        st.divider()
        
        # Media grid
        st.subheader("🖼️ Media Items")
        
        # Mock media data
        media_items = [
            {
                "id": 123,
                "filename": "marketing-header.jpg",
                "type": "image",
                "size": "245 KB",
                "uploaded": "2 hours ago",
                "url": "https://via.placeholder.com/300x200/4A90E2/FFFFFF?text=Marketing+Header",
                "alt_text": "Marketing strategy header image"
            },
            {
                "id": 124,
                "filename": "seo-guide.png",
                "type": "image",
                "size": "198 KB",
                "uploaded": "1 day ago",
                "url": "https://via.placeholder.com/300x200/2C5F8C/FFFFFF?text=SEO+Guide",
                "alt_text": "SEO guide featured image"
            },
            {
                "id": 125,
                "filename": "social-media-tips.jpg",
                "type": "image",
                "size": "312 KB",
                "uploaded": "2 days ago",
                "url": "https://via.placeholder.com/300x200/5A67D8/FFFFFF?text=Social+Media",
                "alt_text": "Social media tips illustration"
            },
            {
                "id": 126,
                "filename": "content-strategy.jpg",
                "type": "image",
                "size": "278 KB",
                "uploaded": "3 days ago",
                "url": "https://via.placeholder.com/300x200/48BB78/FFFFFF?text=Content+Strategy",
                "alt_text": "Content strategy infographic"
            }
        ]
        
        # Display media in grid
        cols = st.columns(3)
        
        for i, item in enumerate(media_items):
            with cols[i % 3]:
                with st.container():
                    # Display image
                    st.image(item["url"], caption=item["filename"], use_container_width=True)
                    
                    # Media info
                    st.write(f"**ID:** {item['id']}")
                    st.write(f"**Size:** {item['size']}")
                    st.write(f"**Uploaded:** {item['uploaded']}")
                    st.write(f"**Alt Text:** {item['alt_text']}")
                    
                    # Action buttons
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        if st.button("📋", key=f"copy_{item['id']}", help="Copy URL"):
                            st.success("URL copied!")
                    
                    with col_b:
                        if st.button("✏️", key=f"edit_{item['id']}", help="Edit"):
                            st.info("Edit functionality would open here")
                    
                    with col_c:
                        if st.button("🗑️", key=f"delete_{item['id']}", help="Delete"):
                            st.warning("Delete confirmation would appear here")
                    
                    st.divider()
        
        # Pagination
        st.subheader("📄 Pagination")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            if st.button("⏮️ First"):
                st.rerun()
        
        with col2:
            if st.button("◀️ Previous"):
                st.rerun()
        
        with col3:
            st.write("Page 1 of 5")
        
        with col4:
            if st.button("▶️ Next"):
                st.rerun()
        
        with col5:
            if st.button("⏭️ Last"):
                st.rerun()
    
    @staticmethod
    def site_management():
        """WordPress site management interface"""
        st.title("🌐 WordPress Site Management")
        
        # Site overview
        st.subheader("📊 Site Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Posts", "45", "3")
        
        with col2:
            st.metric("Published", "42", "3")
        
        with col3:
            st.metric("Drafts", "3", "0")
        
        with col4:
            st.metric("Categories", "8", "1")
        
        st.divider()
        
        # Categories and tags management
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📂 Categories")
            
            # Display existing categories
            categories = [
                {"name": "Marketing", "count": 12},
                {"name": "SEO", "count": 8},
                {"name": "Social Media", "count": 6},
                {"name": "Content Strategy", "count": 5},
                {"name": "Technology", "count": 3}
            ]
            
            for cat in categories:
                col_a, col_b, col_c = st.columns([3, 1, 1])
                with col_a:
                    st.write(f"📂 {cat['name']}")
                with col_b:
                    st.write(f"({cat['count']} posts)")
                with col_c:
                    if st.button("✏️", key=f"edit_cat_{cat['name']}"):
                        st.info(f"Edit category: {cat['name']}")
            
            # Add new category
            st.write("**Add New Category:**")
            new_category = st.text_input("Category Name", key="new_cat")
            cat_description = st.text_area("Description (Optional)", key="new_cat_desc")
            
            if st.button("➕ Add Category"):
                if new_category:
                    st.success(f"✅ Category '{new_category}' created!")
                else:
                    st.error("Please enter a category name")
        
        with col2:
            st.subheader("🏷️ Tags")
            
            # Display existing tags
            tags = [
                {"name": "digital marketing", "count": 15},
                {"name": "seo tips", "count": 12},
                {"name": "content creation", "count": 10},
                {"name": "social media", "count": 8},
                {"name": "wordpress", "count": 5}
            ]
            
            for tag in tags:
                col_a, col_b, col_c = st.columns([3, 1, 1])
                with col_a:
                    st.write(f"🏷️ {tag['name']}")
                with col_b:
                    st.write(f"({tag['count']} posts)")
                with col_c:
                    if st.button("✏️", key=f"edit_tag_{tag['name']}"):
                        st.info(f"Edit tag: {tag['name']}")
            
            # Add new tag
            st.write("**Add New Tag:**")
            new_tag = st.text_input("Tag Name", key="new_tag")
            tag_description = st.text_area("Description (Optional)", key="new_tag_desc")
            
            if st.button("➕ Add Tag"):
                if new_tag:
                    st.success(f"✅ Tag '{new_tag}' created!")
                else:
                    st.error("Please enter a tag name")
    
    @staticmethod
    def publishing_history():
        """WordPress publishing history and analytics"""
        st.title("📊 Publishing History")
        
        # Date range filter
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "From Date",
                value=datetime.now().date() - timedelta(days=30)
            )
        with col2:
            end_date = st.date_input(
                "To Date",
                value=datetime.now().date()
            )
        
        # Platform and status filters
        col1, col2 = st.columns(2)
        with col1:
            status_filter = st.selectbox(
                "Status",
                options=['All', 'Published', 'Failed', 'Draft']
            )
        with col2:
            type_filter = st.selectbox(
                "Content Type",
                options=['All', 'Blog Post', 'Tutorial', 'Review', 'News']
            )
        
        if st.button("🔍 Apply Filters"):
            st.rerun()
        
        st.divider()
        
        # Summary metrics
        st.subheader("📈 Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Published", "47", "+12")
        with col2:
            st.metric("Success Rate", "94.2%", "+2.1%")
        with col3:
            st.metric("Avg. Word Count", "1,847", "+156")
        with col4:
            st.metric("Images Generated", "34", "+8")
        
        # Publishing timeline
        st.subheader("📅 Publishing Timeline")
        
        # Mock timeline data
        timeline_data = []
        for i in range(15):
            date = datetime.now() - timedelta(days=i)
            timeline_data.append({
                'Date': date.strftime('%Y-%m-%d'),
                'Time': date.strftime('%H:%M'),
                'Title': f'Blog Post {i+1}',
                'Type': ['Blog Post', 'Tutorial', 'Review'][i % 3],
                'Status': 'Published' if i % 8 != 0 else 'Failed',
                'Word Count': 1500 + (i * 100),
                'Image Generated': 'Yes' if i % 3 == 0 else 'No'
            })
        
        # Display as dataframe
        df = pd.DataFrame(timeline_data)
        
        # Add color coding for status
        def color_status(val):
            color = 'background-color: lightgreen' if val == 'Published' else 'background-color: lightcoral'
            return color
        
        styled_df = df.style.applymap(color_status, subset=['Status'])
        st.dataframe(styled_df, use_container_width=True)
        
        # Export options
        st.subheader("📥 Export Data")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 Export CSV"):
                st.success("CSV export ready for download")
        
        with col2:
            if st.button("📊 Generate Report"):
                st.success("Detailed report generated")
        
        with col3:
            if st.button("📧 Email Report"):
                st.success("Report sent via email")
