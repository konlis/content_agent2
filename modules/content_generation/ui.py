"""
Content Generation UI Components - Continued
"""

            # Save button
            if st.button("💾 Save Changes", use_container_width=True, type="primary"):
                st.session_state.generated_content.update({
                    'title': new_title,
                    'content': new_content,
                    'seo_title': seo_title,
                    'meta_description': meta_description,
                    'word_count': len(new_content.split())
                })
                st.success("✅ Content saved successfully!")
                st.rerun()
        
        with tab2:
            # Preview tab
            st.markdown("### 📄 Content Preview")
            st.markdown(content_data.get('content', ''))
            
            # SEO preview
            st.markdown("---")
            st.markdown("### 🔍 SEO Preview")
            
            seo_title = content_data.get('seo_title', content_data.get('title', ''))
            meta_desc = content_data.get('meta_description', '')
            
            st.markdown(f"""
            <div style="border: 1px solid #ddd; padding: 15px; border-radius: 5px;">
                <h3 style="color: #1a0dab; margin: 0; font-size: 18px;">{seo_title}</h3>
                <p style="color: #006621; margin: 5px 0; font-size: 14px;">yoursite.com/{content_data.get('title', '').lower().replace(' ', '-')}</p>
                <p style="color: #545454; margin: 0; font-size: 13px;">{meta_desc}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with tab3:
            # Analytics tab
            st.markdown("### 📊 Content Analytics")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Word Count", f"{content_data.get('word_count', 0):,}")
                st.metric("Reading Time", f"{max(1, content_data.get('word_count', 0) // 200)} min")
            
            with col2:
                st.metric("SEO Score", f"{content_data.get('seo_score', 0):.1f}/100")
                st.metric("Readability", f"{content_data.get('readability_score', 0):.1f}")
            
            with col3:
                st.metric("Generation Cost", f"${content_data.get('cost', 0):.3f}")
                st.metric("Quality Level", content_data.get('parameters', {}).get('quality_level', 'standard').title())
    
    @staticmethod
    def template_manager():
        """Template management interface"""
        
        st.title("📋 Template Manager")
        st.markdown("Manage your content templates and create custom ones")
        
        # Template tabs
        tab1, tab2, tab3 = st.tabs(["📋 Available Templates", "➕ Create Template", "📊 Template Stats"])
        
        with tab1:
            # Available templates
            st.subheader("Available Templates")
            
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
                },
                {
                    "name": "Product Description",
                    "description": "E-commerce product descriptions",
                    "word_count": "200-400",
                    "sections": ["Headline", "Features", "Benefits", "Specs"],
                    "use_cases": ["E-commerce", "Product catalogs", "Sales pages"]
                }
            ]
            
            for template in templates:
                with st.expander(f"📋 {template['name']}", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Description:** {template['description']}")
                        st.write(f"**Word Count:** {template['word_count']}")
                        st.write(f"**Sections:** {', '.join(template['sections'])}")
                    
                    with col2:
                        st.write("**Use Cases:**")
                        for use_case in template['use_cases']:
                            st.write(f"• {use_case}")
                        
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button(f"Use Template", key=f"use_{template['name']}"):
                                st.session_state.selected_template = template['name'].lower().replace(' ', '_')
                                st.info(f"Template '{template['name']}' selected!")
                        
                        with col_b:
                            if st.button(f"Preview", key=f"preview_{template['name']}"):
                                st.session_state.preview_template = template['name']
        
        with tab2:
            # Create custom template
            st.subheader("Create Custom Template")
            
            with st.form("create_template_form"):
                template_name = st.text_input("Template Name")
                template_description = st.text_area("Description")
                
                st.write("**Template Structure:**")
                
                # Dynamic section builder
                if 'template_sections' not in st.session_state:
                    st.session_state.template_sections = [
                        {"name": "Introduction", "word_count": 150, "purpose": "Hook and overview"}
                    ]
                
                for i, section in enumerate(st.session_state.template_sections):
                    col1, col2, col3, col4 = st.columns([2, 1, 2, 1])
                    
                    with col1:
                        section['name'] = st.text_input(f"Section {i+1} Name", value=section['name'], key=f"section_name_{i}")
                    
                    with col2:
                        section['word_count'] = st.number_input(f"Words", value=section['word_count'], key=f"section_words_{i}")
                    
                    with col3:
                        section['purpose'] = st.text_input(f"Purpose", value=section['purpose'], key=f"section_purpose_{i}")
                    
                    with col4:
                        if st.button("🗑️", key=f"remove_section_{i}") and len(st.session_state.template_sections) > 1:
                            st.session_state.template_sections.pop(i)
                            st.rerun()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.form_submit_button("➕ Add Section"):
                        st.session_state.template_sections.append({
                            "name": f"Section {len(st.session_state.template_sections) + 1}",
                            "word_count": 200,
                            "purpose": "Purpose description"
                        })
                        st.rerun()
                
                with col2:
                    if st.form_submit_button("💾 Save Template", type="primary"):
                        if template_name:
                            # Save template logic would go here
                            st.success(f"✅ Template '{template_name}' created successfully!")
                        else:
                            st.error("Please enter a template name")
        
        with tab3:
            # Template statistics
            st.subheader("Template Statistics")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Templates", "4", delta="+1 this month")
            
            with col2:
                st.metric("Most Used", "Blog Post", delta="78% usage")
            
            with col3:
                st.metric("Custom Templates", "0", delta="Create your first!")
            
            # Usage chart
            st.subheader("Template Usage")
            
            usage_data = {
                "Template": ["Blog Post", "Social Media", "Website Copy", "Product Description"],
                "Usage Count": [45, 32, 28, 15],
                "Success Rate": [92, 88, 85, 90]
            }
            
            df = pd.DataFrame(usage_data)
            
            fig = px.bar(df, x="Template", y="Usage Count", title="Template Usage Statistics")
            st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def content_history():
        """Content history and library"""
        
        st.title("📚 Content History")
        st.markdown("View and manage your generated content")
        
        # Filters
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            content_type_filter = st.selectbox(
                "Content Type",
                ["All", "Blog Post", "Social Media", "Website Copy", "Product Description"]
            )
        
        with col2:
            date_filter = st.selectbox(
                "Time Period", 
                ["All Time", "Last 7 days", "Last 30 days", "Last 3 months"]
            )
        
        with col3:
            quality_filter = st.selectbox(
                "Quality Score",
                ["All", "90-100", "80-89", "70-79", "Below 70"]
            )
        
        with col4:
            sort_by = st.selectbox(
                "Sort By",
                ["Most Recent", "Highest Quality", "Word Count", "Lowest Cost"]
            )
        
        # Mock content history
        history_data = []
        for i in range(10):
            history_data.append({
                "Title": f"Content Title {i+1}",
                "Type": ["Blog Post", "Social Media", "Website Copy"][i % 3],
                "Word Count": 800 + i * 100,
                "SEO Score": 75 + (i * 2),
                "Generated": f"2024-01-{15 + i:02d}",
                "Cost": f"${0.02 + (i * 0.01):.2f}",
                "Status": ["Published", "Draft", "Scheduled"][i % 3]
            })
        
        df = pd.DataFrame(history_data)
        
        # Content grid
        st.subheader(f"📄 Content Library ({len(df)} items)")
        
        # Display as cards
        for i, row in df.iterrows():
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 2])
                
                with col1:
                    st.write(f"**{row['Title']}**")
                    st.write(f"*{row['Type']}* • {row['Generated']}")
                
                with col2:
                    st.metric("Words", f"{row['Word Count']:,}")
                
                with col3:
                    st.metric("SEO", f"{row['SEO Score']}")
                
                with col4:
                    st.metric("Cost", row['Cost'])
                
                with col5:
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        if st.button("👀", key=f"view_{i}", help="View"):
                            st.session_state.view_content_id = i
                    
                    with col_b:
                        if st.button("✏️", key=f"edit_{i}", help="Edit"):
                            st.session_state.edit_content_id = i
                    
                    with col_c:
                        if st.button("🗑️", key=f"delete_{i}", help="Delete"):
                            st.warning(f"Delete '{row['Title']}'?")
                
                # Status badge
                status_color = {"Published": "🟢", "Draft": "🟡", "Scheduled": "🔵"}[row['Status']]
                st.write(f"{status_color} {row['Status']}")
                
                st.divider()
        
        # Bulk actions
        st.subheader("🔧 Bulk Actions")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📥 Export All"):
                st.info("Exporting all content...")
        
        with col2:
            if st.button("🗑️ Delete Selected"):
                st.warning("Delete selected content?")
        
        with col3:
            if st.button("📊 Generate Report"):
                ContentGenerationUI._show_content_report(df)
        
        with col4:
            if st.button("🔄 Refresh"):
                st.rerun()
    
    @staticmethod
    def _show_content_report(df):
        """Show content analytics report"""
        
        st.subheader("📊 Content Analytics Report")
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Content", len(df))
        
        with col2:
            avg_words = df['Word Count'].mean()
            st.metric("Avg. Word Count", f"{avg_words:,.0f}")
        
        with col3:
            avg_seo = df['SEO Score'].mean()
            st.metric("Avg. SEO Score", f"{avg_seo:.1f}")
        
        with col4:
            total_cost = sum([float(cost.replace('$', '')) for cost in df['Cost']])
            st.metric("Total Cost", f"${total_cost:.2f}")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Content type distribution
            type_counts = df['Type'].value_counts()
            fig = px.pie(values=type_counts.values, names=type_counts.index, 
                        title="Content Type Distribution")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # SEO score distribution
            fig = px.histogram(df, x="SEO Score", nbins=10, 
                             title="SEO Score Distribution")
            st.plotly_chart(fig, use_container_width=True)
        
        # Performance over time
        df['Generated'] = pd.to_datetime(df['Generated'])
        daily_content = df.groupby('Generated').size().reset_index(name='Count')
        
        fig = px.line(daily_content, x='Generated', y='Count', 
                     title="Content Generation Over Time")
        st.plotly_chart(fig, use_container_width=True)


# Initialize session state
if 'template_sections' not in st.session_state:
    st.session_state.template_sections = []

if 'show_editor' not in st.session_state:
    st.session_state.show_editor = False
