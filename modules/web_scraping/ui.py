"""
Web Scraping Module UI
Streamlit interface for web scraping, competitor analysis, and content discovery
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from typing import Dict, List, Any, Optional

def render_web_scraping_ui():
    """Render the main web scraping interface"""
    
    st.title("🕷️ Web Scraping & Content Intelligence")
    st.markdown("Advanced web scraping, competitor analysis, and content opportunity discovery using AI")
    
    # Sidebar navigation
    page = st.sidebar.selectbox(
        "Choose a tool:",
        ["📊 Dashboard", "🔍 URL Scraping", "🏢 Competitor Analysis", "💡 Content Discovery", "📈 Trending Topics", "🕳️ Content Gaps"]
    )
    
    if page == "📊 Dashboard":
        render_scraping_dashboard()
    elif page == "🔍 URL Scraping":
        render_url_scraping()
    elif page == "🏢 Competitor Analysis":
        render_competitor_analysis()
    elif page == "💡 Content Discovery":
        render_content_discovery()
    elif page == "📈 Trending Topics":
        render_trending_topics()
    elif page == "🕳️ Content Gaps":
        render_content_gaps()

def render_scraping_dashboard():
    """Render the scraping dashboard with overview metrics"""
    
    st.header("📊 Scraping Dashboard")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Pages Scraped", "1,250", "+45 today")
    
    with col2:
        st.metric("Success Rate", "94.4%", "+2.1%")
    
    with col3:
        st.metric("Avg. Scraping Time", "2.3s", "-0.5s")
    
    with col4:
        st.metric("Active Sessions", "3", "2 running")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Scraping Performance (Last 7 Days)")
        
        # Mock data for performance chart
        dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(6, -1, -1)]
        scraped = [45, 52, 38, 61, 47, 55, 48]
        successful = [42, 49, 36, 58, 44, 52, 45]
        
        df_performance = pd.DataFrame({
            'Date': dates,
            'Scraped': scraped,
            'Successful': successful
        })
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_performance['Date'], y=df_performance['Scraped'], 
                                name='Total Scraped', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=df_performance['Date'], y=df_performance['Successful'], 
                                name='Successful', line=dict(color='green')))
        
        fig.update_layout(height=300, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Content Types Distribution")
        
        # Mock data for content types
        content_types = ['Blog Posts', 'Articles', 'Product Pages', 'Landing Pages', 'News']
        counts = [450, 380, 200, 120, 100]
        
        fig = px.pie(values=counts, names=content_types, height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent activity
    st.subheader("Recent Scraping Activity")
    
    # Mock recent activity data
    recent_activity = [
        {"time": "2 minutes ago", "action": "Scraped", "url": "https://example.com/article1", "status": "✅ Success"},
        {"time": "5 minutes ago", "action": "Analyzed", "url": "https://competitor.com/blog", "status": "✅ Success"},
        {"time": "12 minutes ago", "action": "Discovered", "url": "https://trending.com/news", "status": "✅ Success"},
        {"time": "18 minutes ago", "action": "Scraped", "url": "https://example.com/product", "status": "❌ Failed"},
        {"time": "25 minutes ago", "action": "Analyzed", "url": "https://competitor.com/guide", "status": "✅ Success"}
    ]
    
    df_activity = pd.DataFrame(recent_activity)
    st.dataframe(df_activity, use_container_width=True)

def render_url_scraping():
    """Render the URL scraping interface"""
    
    st.header("🔍 URL Scraping")
    st.markdown("Extract content from individual URLs or batch scrape multiple URLs")
    
    # Single URL scraping
    st.subheader("Single URL Scraping")
    
    with st.form("single_scraping_form"):
        url = st.text_input("URL to scrape", placeholder="https://example.com/article")
        
        col1, col2 = st.columns(2)
        with col1:
            extraction_strategy = st.selectbox(
                "Extraction Strategy",
                ["basic", "css", "llm", "hybrid"],
                help="Basic: Simple text extraction, CSS: CSS selector-based, LLM: AI-powered, Hybrid: Combination"
            )
            
            content_type = st.selectbox(
                "Content Type",
                ["article", "product", "job_listing", "news", "blog_post"]
            )
        
        with col2:
            use_llm = st.checkbox("Use LLM for analysis", help="Enable AI-powered content analysis")
            
            custom_schema = st.text_area(
                "Custom Extraction Schema (JSON)",
                placeholder='{"title": {"selector": "h1", "type": "text"}}',
                help="Optional custom extraction rules"
            )
        
        submitted = st.form_submit_button("🚀 Start Scraping")
        
        if submitted and url:
            if not url.startswith(('http://', 'https://')):
                st.error("Please enter a valid URL starting with http:// or https://")
            else:
                with st.spinner("Scraping in progress..."):
                    # Simulate scraping
                    import time
                    time.sleep(2)
                    
                    # Mock results
                    st.success("✅ Scraping completed successfully!")
                    
                    # Display results
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("📊 Content Metrics")
                        metrics_data = {
                            "Word Count": 1250,
                            "Reading Time": "6 minutes",
                            "Headings": 8,
                            "Paragraphs": 15,
                            "Images": 3,
                            "Links": 12
                        }
                        
                        for metric, value in metrics_data.items():
                            st.metric(metric, value)
                    
                    with col2:
                        st.subheader("🔍 SEO Analysis")
                        seo_data = {
                            "Title Length": "58 characters ✅",
                            "Meta Description": "145 characters ✅",
                            "H1 Tags": "1 ✅",
                            "Structured Data": "Present ✅",
                            "Canonical URL": "Set ✅"
                        }
                        
                        for seo_item, status in seo_data.items():
                            st.write(f"**{seo_item}:** {status}")
                    
                    # Extracted content preview
                    st.subheader("📝 Extracted Content Preview")
                    content_preview = f"""
                    # Sample Article Title
                    
                    This is a sample article extracted from {url} using the {extraction_strategy} strategy.
                    
                    ## Key Points
                    
                    - Content extraction completed successfully
                    - Used {content_type} content type
                    - LLM analysis: {'enabled' if use_llm else 'disabled'}
                    
                    ## Main Content
                    
                    The article discusses various topics related to content marketing and SEO optimization.
                    It provides practical insights and actionable strategies for improving online presence.
                    
                    ### Subsection 1
                    
                    Detailed explanation of the first main point with examples and case studies.
                    
                    ### Subsection 2
                    
                    Further elaboration on the second key concept with practical applications.
                    """
                    
                    st.markdown(content_preview)
                    
                    # Download options
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.download_button(
                            "📥 Download HTML",
                            content_preview,
                            file_name="scraped_content.html",
                            mime="text/html"
                        )
                    
                    with col2:
                        st.download_button(
                            "📥 Download Markdown",
                            content_preview,
                            file_name="scraped_content.md",
                            mime="text/markdown"
                        )
                    
                    with col3:
                        st.download_button(
                            "📥 Download JSON",
                            json.dumps({"url": url, "content": content_preview, "metrics": metrics_data}, indent=2),
                            file_name="scraped_content.json",
                            mime="application/json"
                        )
    
    # Batch URL scraping
    st.subheader("Batch URL Scraping")
    
    with st.form("batch_scraping_form"):
        urls_input = st.text_area(
            "URLs to scrape (one per line)",
            placeholder="https://example1.com/article1\nhttps://example2.com/article2\nhttps://example3.com/article3",
            help="Enter multiple URLs, one per line"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            batch_strategy = st.selectbox("Extraction Strategy", ["basic", "css", "llm", "hybrid"])
            batch_content_type = st.selectbox("Content Type", ["article", "product", "job_listing", "news", "blog_post"])
        
        with col2:
            max_concurrent = st.slider("Max Concurrent", min_value=1, max_value=10, value=5)
            batch_use_llm = st.checkbox("Use LLM for analysis")
        
        batch_submitted = st.form_submit_button("🚀 Start Batch Scraping")
        
        if batch_submitted and urls_input:
            urls = [url.strip() for url in urls_input.split('\n') if url.strip()]
            
            if not urls:
                st.error("Please enter at least one valid URL")
            else:
                with st.spinner(f"Batch scraping {len(urls)} URLs..."):
                    # Simulate batch scraping
                    import time
                    time.sleep(3)
                    
                    st.success(f"✅ Batch scraping completed! Processed {len(urls)} URLs")
                    
                    # Mock batch results
                    batch_results = []
                    for i, url in enumerate(urls):
                        batch_results.append({
                            "URL": url,
                            "Status": "✅ Success" if i < len(urls) - 1 else "❌ Failed",
                            "Word Count": 1200 + (i * 50),
                            "Processing Time": f"{1.5 + (i * 0.2):.1f}s",
                            "Content Type": batch_content_type
                        })
                    
                    df_batch = pd.DataFrame(batch_results)
                    st.dataframe(df_batch, use_container_width=True)
                    
                    # Batch statistics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total URLs", len(urls))
                    with col2:
                        st.metric("Successful", len([r for r in batch_results if "Success" in r["Status"]]))
                    with col3:
                        st.metric("Failed", len([r for r in batch_results if "Failed" in r["Status"]]))

def render_competitor_analysis():
    """Render the competitor analysis interface"""
    
    st.header("🏢 Competitor Analysis")
    st.markdown("Analyze competitor content strategies and identify opportunities")
    
    with st.form("competitor_analysis_form"):
        competitor_url = st.text_input(
            "Competitor URL",
            placeholder="https://competitor.com",
            help="Enter the main URL of the competitor to analyze"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            analysis_depth = st.selectbox(
                "Analysis Depth",
                ["basic", "standard", "comprehensive"],
                help="Basic: Quick overview, Standard: Detailed analysis, Comprehensive: Full deep dive"
            )
            
            pages_to_analyze = st.slider(
                "Pages to Analyze",
                min_value=10,
                max_value=200,
                value=50,
                help="Number of pages to discover and analyze"
            )
        
        with col2:
            include_ai_insights = st.checkbox("Include AI Insights", value=True, help="Enable AI-powered analysis")
            
            analysis_focus = st.multiselect(
                "Analysis Focus Areas",
                ["Content Strategy", "SEO Analysis", "Competitive Gaps", "Market Positioning", "Performance Metrics"],
                default=["Content Strategy", "SEO Analysis", "Competitive Gaps"]
            )
        
        analyze_submitted = st.form_submit_button("🔍 Analyze Competitor")
        
        if analyze_submitted and competitor_url:
            if not competitor_url.startswith(('http://', 'https://')):
                st.error("Please enter a valid URL starting with http:// or https://")
            else:
                with st.spinner("Analyzing competitor content..."):
                    # Simulate analysis
                    import time
                    time.sleep(5)
                    
                    st.success("✅ Competitor analysis completed!")
                    
                    # Analysis results
                    st.subheader("📊 Analysis Results")
                    
                    # Content strategy analysis
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("📝 Content Strategy")
                        strategy_data = {
                            "Content Types": ["Blog Posts", "Case Studies", "Whitepapers"],
                            "Content Themes": ["AI/ML", "Digital Transformation", "Innovation"],
                            "Writing Style": "Professional & Advanced",
                            "Content Depth": "Comprehensive",
                            "Target Audience": "Executives & Professionals"
                        }
                        
                        for key, value in strategy_data.items():
                            if isinstance(value, list):
                                st.write(f"**{key}:** {', '.join(value)}")
                            else:
                                st.write(f"**{key}:** {value}")
                    
                    with col2:
                        st.subheader("🔍 SEO Strategy")
                        seo_data = {
                            "Title Optimization": "Excellent (avg: 58 chars)",
                            "Meta Descriptions": "95% usage rate",
                            "Heading Structure": "High quality",
                            "Keyword Targeting": "Optimal density",
                            "Technical SEO": "Structured data present"
                        }
                        
                        for key, value in seo_data.items():
                            st.write(f"**{key}:** {value}")
                    
                    # Competitive gaps
                    st.subheader("🕳️ Competitive Gaps Identified")
                    
                    gaps_data = {
                        "Content Gaps": ["Limited video content", "No interactive tools"],
                        "Format Gaps": ["Missing podcast content", "No webinars"],
                        "Quality Gaps": ["Some content could be more actionable"],
                        "Topic Gaps": ["Limited coverage of emerging trends"]
                    }
                    
                    for gap_type, gaps in gaps_data.items():
                        st.write(f"**{gap_type}:**")
                        for gap in gaps:
                            st.write(f"  • {gap}")
                    
                    # Strategic recommendations
                    st.subheader("💡 Strategic Recommendations")
                    
                    recommendations = [
                        "Focus on video content creation to fill format gaps",
                        "Develop interactive tools and calculators for engagement",
                        "Create more actionable, step-by-step content",
                        "Cover emerging industry trends quickly",
                        "Develop podcast content for audio audience",
                        "Create webinar series for thought leadership"
                    ]
                    
                    for i, rec in enumerate(recommendations, 1):
                        st.write(f"{i}. {rec}")
                    
                    # Performance metrics
                    st.subheader("📈 Performance Metrics")
                    
                    metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
                    
                    with metrics_col1:
                        st.metric("Content Quality", "8.7/10", "+0.3")
                    
                    with metrics_col2:
                        st.metric("SEO Effectiveness", "9.2/10", "+0.5")
                    
                    with metrics_col3:
                        st.metric("Audience Engagement", "8.5/10", "+0.2")
                    
                    with metrics_col4:
                        st.metric("Competitive Position", "8.9/10", "+0.4")
                    
                    # Market positioning chart
                    st.subheader("🎯 Market Positioning")
                    
                    # Mock positioning data
                    positioning_data = {
                        "Thought Leadership": 85,
                        "Content Quality": 87,
                        "SEO Performance": 92,
                        "Audience Reach": 78,
                        "Innovation": 82
                    }
                    
                    fig = px.bar(
                        x=list(positioning_data.keys()),
                        y=list(positioning_data.values()),
                        title="Competitive Positioning Scores",
                        height=400
                    )
                    fig.update_layout(yaxis_title="Score (0-100)")
                    st.plotly_chart(fig, use_container_width=True)

def render_content_discovery():
    """Render the content discovery interface"""
    
    st.header("💡 Content Discovery")
    st.markdown("Discover content opportunities and identify content gaps")
    
    with st.form("content_discovery_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            keywords = st.text_input(
                "Target Keywords",
                placeholder="AI, content marketing, SEO",
                help="Enter keywords separated by commas"
            )
            
            industry = st.selectbox(
                "Industry Focus",
                ["", "technology", "marketing", "healthcare", "finance", "education", "retail", "manufacturing"],
                help="Select your target industry"
            )
        
        with col2:
            content_type = st.selectbox(
                "Content Type",
                ["blog_post", "social_media", "newsletter", "whitepaper", "case_study", "video"],
                help="Type of content you want to create"
            )
            
            max_opportunities = st.slider(
                "Max Opportunities",
                min_value=5,
                max_value=100,
                value=20,
                help="Maximum number of opportunities to discover"
            )
        
        auto_analyze = st.checkbox("Auto-analyze discovered content", value=True)
        
        discover_submitted = st.form_submit_button("🔍 Discover Opportunities")
        
        if discover_submitted:
            with st.spinner("Discovering content opportunities..."):
                # Simulate discovery
                import time
                time.sleep(3)
                
                st.success("✅ Content discovery completed!")
                
                # Discovery results
                st.subheader("📊 Discovery Results")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Opportunities Found", "15")
                    st.metric("Content Gaps", "8")
                    st.metric("Trending Topics", "5")
                
                with col2:
                    st.metric("High Priority", "6")
                    st.metric("Medium Priority", "7")
                    st.metric("Low Priority", "2")
                
                # Top opportunities
                st.subheader("🎯 Top Content Opportunities")
                
                opportunities_data = [
                    {
                        "Topic": "AI Implementation Guide",
                        "Opportunity Score": 8.5,
                        "Priority": "High",
                        "Estimated Impact": "High",
                        "Difficulty": "Medium"
                    },
                    {
                        "Topic": "Industry Trend Analysis",
                        "Opportunity Score": 8.2,
                        "Priority": "High",
                        "Estimated Impact": "High",
                        "Difficulty": "Low"
                    },
                    {
                        "Topic": "Best Practices Guide",
                        "Opportunity Score": 7.8,
                        "Priority": "Medium",
                        "Estimated Impact": "Medium",
                        "Difficulty": "Low"
                    }
                ]
                
                df_opportunities = pd.DataFrame(opportunities_data)
                st.dataframe(df_opportunities, use_container_width=True)
                
                # Content gaps analysis
                st.subheader("🕳️ Content Gap Analysis")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Topic Coverage:**")
                    topic_coverage = {
                        "AI": {"score": 7.5, "count": 3},
                        "Content Marketing": {"score": 8.2, "count": 5},
                        "SEO": {"score": 6.8, "count": 2}
                    }
                    
                    for topic, data in topic_coverage.items():
                        score_color = "🟢" if data["score"] >= 8 else "🟡" if data["score"] >= 6 else "🔴"
                        st.write(f"{score_color} {topic}: {data['score']}/10 ({data['count']} articles)")
                
                with col2:
                    st.write("**Content Depth:**")
                    depth_data = {"Shallow": 2, "Medium": 5, "Deep": 3}
                    
                    fig = px.pie(values=list(depth_data.values()), names=list(depth_data.keys()), height=200)
                    st.plotly_chart(fig, use_container_width=True)
                
                # Recommendations
                st.subheader("💡 Strategic Recommendations")
                
                recommendations = [
                    "Create content about 'AI implementation' with opportunity score 8.5",
                    "Develop content covering: Case studies and expert interviews",
                    "Focus on AI trends and sustainability practices",
                    "Create comprehensive industry guides and tutorials",
                    "Develop industry case studies and success stories",
                    "Focus on improving content quality and depth",
                    "Consider adding video content to your strategy"
                ]
                
                for i, rec in enumerate(recommendations, 1):
                    st.write(f"{i}. {rec}")

def render_trending_topics():
    """Render the trending topics interface"""
    
    st.header("📈 Trending Topics")
    st.markdown("Discover trending topics and emerging trends in your industry")
    
    with st.form("trending_topics_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            industry = st.selectbox(
                "Industry Focus",
                ["", "technology", "marketing", "healthcare", "finance", "education", "retail", "manufacturing"]
            )
            
            time_period = st.selectbox(
                "Time Period",
                ["7d", "30d", "90d"],
                help="7d: This week, 30d: This month, 90d: This quarter"
            )
        
        with col2:
            max_topics = st.slider(
                "Max Topics",
                min_value=5,
                max_value=50,
                value=15
            )
            
            include_velocity = st.checkbox("Include trend velocity analysis", value=True)
        
        trending_submitted = st.form_submit_button("📈 Discover Trending Topics")
        
        if trending_submitted:
            with st.spinner("Analyzing trending topics..."):
                # Simulate analysis
                import time
                time.sleep(2)
                
                st.success("✅ Trending topics analysis completed!")
                
                # Trending topics
                st.subheader("🔥 Top Trending Topics")
                
                trending_data = [
                    {"Topic": "AI in Content Marketing", "Growth Rate": 7.2, "Confidence": 8.5, "Status": "Rising"},
                    {"Topic": "Sustainable Business Practices", "Growth Rate": 6.8, "Confidence": 8.1, "Status": "Rising"},
                    {"Topic": "Remote Work Optimization", "Growth Rate": 5.9, "Confidence": 7.8, "Status": "Stable"},
                    {"Topic": "Digital Transformation", "Growth Rate": 6.5, "Confidence": 8.3, "Status": "Rising"},
                    {"Topic": "Customer Experience Innovation", "Growth Rate": 6.1, "Confidence": 7.9, "Status": "Stable"}
                ]
                
                df_trending = pd.DataFrame(trending_data)
                st.dataframe(df_trending, use_container_width=True)
                
                # Trend velocity chart
                if include_velocity:
                    st.subheader("📊 Trend Velocity Analysis")
                    
                    velocity_data = {
                        "Fast Growing": ["AI", "Sustainability"],
                        "Stable": ["SEO", "Content Marketing"],
                        "Declining": ["Traditional Marketing", "Print Advertising"]
                    }
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write("**🚀 Fast Growing**")
                        for topic in velocity_data["Fast Growing"]:
                            st.write(f"• {topic}")
                    
                    with col2:
                        st.write("**➡️ Stable**")
                        for topic in velocity_data["Stable"]:
                            st.write(f"• {topic}")
                    
                    with col3:
                        st.write("**📉 Declining**")
                        for topic in velocity_data["Declining"]:
                            st.write(f"• {topic}")
                
                # Emerging trends
                st.subheader("🌱 Emerging Trends")
                
                emerging_data = [
                    {
                        "Topic": "AI in Content Marketing",
                        "Confidence": 8.5,
                        "Growth Rate": 7.2,
                        "Evidence": ["Recent mentions", "Growing search volume"],
                        "Trajectory": "Rapid growth expected",
                        "Action": "Create comprehensive content immediately"
                    }
                ]
                
                for trend in emerging_data:
                    with st.expander(f"🌱 {trend['Topic']} (Confidence: {trend['Confidence']})"):
                        st.write(f"**Growth Rate:** {trend['Growth Rate']}/10")
                        st.write(f"**Evidence:** {', '.join(trend['Evidence'])}")
                        st.write(f"**Predicted Trajectory:** {trend['Trajectory']}")
                        st.write(f"**Recommended Action:** {trend['Action']}")
                
                # Recommendations
                st.subheader("💡 Recommendations")
                
                recommendations = [
                    "Create content about trending topic: AI in Content Marketing",
                    "Early adoption opportunity: AI in Content Marketing (confidence: 8.5)",
                    "Focus on fast-growing topics: AI, Sustainability",
                    "Monitor technology trends for content opportunities",
                    "Create technology-focused trending content",
                    "Stay updated with industry news and developments",
                    "Monitor social media for viral content opportunities",
                    "Create content that capitalizes on trending topics quickly"
                ]
                
                for i, rec in enumerate(recommendations, 1):
                    st.write(f"{i}. {rec}")

def render_content_gaps():
    """Render the content gaps interface"""
    
    st.header("🕳️ Content Gap Analysis")
    st.markdown("Identify content gaps by analyzing competitor content and market needs")
    
    with st.form("content_gaps_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            competitor_urls = st.text_area(
                "Competitor URLs (one per line)",
                placeholder="https://competitor1.com\nhttps://competitor2.com",
                help="Enter competitor URLs to analyze for gaps"
            )
            
            industry = st.selectbox(
                "Industry Focus",
                ["", "technology", "marketing", "healthcare", "finance", "education", "retail", "manufacturing"]
            )
        
        with col2:
            target_keywords = st.text_input(
                "Target Keywords",
                placeholder="AI, automation, digital transformation",
                help="Keywords to analyze for content gaps"
            )
            
            analysis_focus = st.multiselect(
                "Focus Areas",
                ["Topic Gaps", "Format Gaps", "Quality Gaps", "Audience Gaps", "Timing Gaps"],
                default=["Topic Gaps", "Format Gaps", "Quality Gaps"]
            )
        
        gaps_submitted = st.form_submit_button("🔍 Analyze Content Gaps")
        
        if gaps_submitted:
            with st.spinner("Analyzing content gaps..."):
                # Simulate analysis
                import time
                time.sleep(3)
                
                st.success("✅ Content gap analysis completed!")
                
                # Gap analysis results
                st.subheader("📊 Gap Analysis Results")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Competitors Analyzed", len([u for u in competitor_urls.split('\n') if u.strip()]) if competitor_urls else 0)
                    st.metric("Keywords Analyzed", len([k for k in target_keywords.split(',') if k.strip()]) if target_keywords else 0)
                    st.metric("Total Gaps Found", "12")
                
                with col2:
                    st.metric("High Priority Gaps", "5")
                    st.metric("Medium Priority Gaps", "4")
                    st.metric("Low Priority Gaps", "3")
                    st.metric("Opportunity Score", "7.8/10")
                
                # Detailed gap analysis
                st.subheader("🕳️ Detailed Gap Analysis")
                
                gaps_data = {
                    "Topic Gaps": [
                        "Limited coverage of 'AI implementation'",
                        "Missing content about 'sustainability practices'"
                    ],
                    "Format Gaps": [
                        "Limited video content",
                        "No infographic content"
                    ],
                    "Quality Gaps": [
                        "Content quality could be improved"
                    ],
                    "Audience Gaps": [
                        "Limited advanced content for professionals"
                    ],
                    "Timing Gaps": [
                        "Delayed coverage of breaking news"
                    ]
                }
                
                for gap_type, gaps in gaps_data.items():
                    if gap_type in analysis_focus or not analysis_focus:
                        with st.expander(f"📋 {gap_type} ({len(gaps)} gaps)"):
                            for gap in gaps:
                                st.write(f"• {gap}")
                
                # Prioritized gaps
                st.subheader("🎯 Prioritized Content Gaps")
                
                prioritized_gaps = [
                    {
                        "Gap": "Limited coverage of 'AI implementation'",
                        "Type": "Topic Gaps",
                        "Priority Score": 8.5,
                        "Estimated Effort": "Medium - Requires research and writing",
                        "Potential Impact": "High - Directly addresses audience needs"
                    },
                    {
                        "Gap": "Limited video content",
                        "Type": "Format Gaps",
                        "Priority Score": 7.0,
                        "Estimated Effort": "High - Requires new skills and tools",
                        "Potential Impact": "Medium - Improves content variety"
                    },
                    {
                        "Gap": "Content quality could be improved",
                        "Type": "Quality Gaps",
                        "Priority Score": 8.8,
                        "Estimated Effort": "Medium - Requires improved processes",
                        "Potential Impact": "Very High - Improves overall content performance"
                    }
                ]
                
                df_gaps = pd.DataFrame(prioritized_gaps)
                st.dataframe(df_gaps, use_container_width=True)
                
                # Gap-filling recommendations
                st.subheader("💡 Gap-Filling Recommendations")
                
                recommendations = [
                    "Create content to address: Limited coverage of 'AI implementation'",
                    "Develop limited video content to diversify content",
                    "Focus on improving content depth and research quality",
                    "Create comprehensive technology guides and tutorials",
                    "Develop technology case studies and success stories",
                    "Conduct audience research to identify unmet needs",
                    "Analyze competitor content for improvement opportunities",
                    "Create content that addresses common pain points"
                ]
                
                for i, rec in enumerate(recommendations, 1):
                    st.write(f"{i}. {rec}")
                
                # Opportunity score breakdown
                st.subheader("📈 Opportunity Score Breakdown")
                
                score_breakdown = {
                    "Topic Coverage": 7.5,
                    "Content Depth": 6.8,
                    "Format Diversity": 5.2,
                    "Content Quality": 7.8,
                    "Audience Targeting": 8.1
                }
                
                fig = px.bar(
                    x=list(score_breakdown.keys()),
                    y=list(score_breakdown.values()),
                    title="Content Gap Opportunity Scores",
                    height=400
                )
                fig.update_layout(yaxis_title="Score (0-10)")
                st.plotly_chart(fig, use_container_width=True)
