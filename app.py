import streamlit as st
import pandas as pd
from datetime import datetime
from search import search_court_cases
from to_ics import cases_to_ics, sanitize_filename

# Page configuration
st.set_page_config(
    page_title="Utah Court Calendar Search",
    page_icon="⚖️",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .case-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 5px solid #1f77b4;
    }
    .case-header {
        font-size: 1.2em;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 10px;
    }
    .webex-link {
        background-color: #28a745;
        color: white;
        padding: 5px 10px;
        border-radius: 5px;
        text-decoration: none;
        display: inline-block;
        margin-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'cases' not in st.session_state:
    st.session_state.cases = None
if 'search_info' not in st.session_state:
    st.session_state.search_info = None

# Header
st.title("⚖️ Utah Court Calendar Search")
st.markdown("Search for court cases by attorney name")

# Sidebar for search inputs
with st.sidebar:
    st.header("🔍 Search Options")
    
    first_name = st.text_input(
        "Attorney First Name",
        value="",
        help="Enter the attorney's first name (minimum 2 characters)"
    )
    
    last_name = st.text_input(
        "Attorney Last Name", 
        value="",
        help="Enter the attorney's last name (minimum 2 characters)"
    )
    
    st.markdown("---")
    search_button = st.button("🔎 Search Cases", type="primary", use_container_width=True)

# Main content area
if search_button:
    if not first_name or not last_name:
        st.error("⚠️ Please enter both first and last name")
    elif len(first_name) < 2 or len(last_name) < 2:
        st.error("⚠️ First and last name must be at least 2 characters")
    else:
        with st.spinner("🔄 Searching court cases..."):
            try:
                # Search for cases
                cases = search_court_cases(
                    search_type="a",
                    first_name=first_name.upper(),
                    last_name=last_name.upper(),
                    date="all",
                    location="all"
                )
                
                # Store in session state
                st.session_state.cases = cases
                st.session_state.search_info = {
                    'first_name': first_name.upper(),
                    'last_name': last_name.upper()
                }
                
            except Exception as e:
                st.error(f"❌ Error searching cases: {str(e)}")
                st.exception(e)

# Display results if they exist in session state
if st.session_state.cases is not None and st.session_state.search_info is not None:
    cases = st.session_state.cases
    search_info = st.session_state.search_info
    
    if not cases:
        st.warning(f"No cases found for {search_info['first_name']} {search_info['last_name']}")
    else:
        # Display summary
        st.success(f"✅ Found {len(cases)} case(s) for **{search_info['first_name']} {search_info['last_name']}**")
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Cases", len(cases))
        with col2:
            webex_count = sum(1 for c in cases if c.get('webex_url'))
            st.metric("Virtual Hearings", webex_count)
        with col3:
            district_count = sum(1 for c in cases if 'District Court' in c.get('court_type', ''))
            st.metric("District Court", district_count)
        with col4:
            justice_count = sum(1 for c in cases if 'Justice Court' in c.get('court_type', ''))
            st.metric("Justice Court", justice_count)
        
        st.markdown("---")
        
        # Export options at the top
        st.subheader("📥 Export Data")
        
        col_export1, col_export2 = st.columns(2)
        
        with col_export1:
            # CSV export
            df = pd.DataFrame(cases)
            csv = df.to_csv(index=False)
            
            st.download_button(
                label="📊 Download CSV",
                data=csv,
                file_name=f"court_cases_{search_info['first_name']}_{search_info['last_name']}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col_export2:
            # ICS calendar export (all cases)
            with st.popover("📅 Download All as Calendar", use_container_width=True):
                st.write("**Enter details for all calendar events:**")
                combined_filevine_link = st.text_input(
                    "FileVine Link",
                    placeholder="https://filevine.com/...",
                    key="combined_filevine"
                )
                combined_attorney_name = st.text_input(
                    "Attorney Name",
                    placeholder="attorney",
                    key="combined_email",
                    help="Enter just the name (e.g., 'chris' for chris@dexterlaw.com)"
                )
                # Auto-append @dexterlaw.com
                if combined_attorney_name and combined_attorney_name.strip():
                    combined_attorney_email = f"{combined_attorney_name.strip()}@dexterlaw.com"
                    st.caption(f"📧 Will use: {combined_attorney_email}")
                else:
                    combined_attorney_email = ""
                    st.caption("📧 Will use: attorney@dexterlaw.com (default)")
                
                all_ics_content = cases_to_ics(cases, filevine_link=combined_filevine_link, attorney_email=combined_attorney_email)
                ics_filename = f"calendar_{search_info['first_name']}_{search_info['last_name']}_{datetime.now().strftime('%Y%m%d')}.ics"
                
                st.download_button(
                    label="💾 Generate & Download All",
                    data=all_ics_content,
                    file_name=ics_filename,
                    mime="text/calendar",
                    use_container_width=True,
                    key="combined_ics_download"
                )
        
        st.markdown("---")
        
        # Display each case
        for idx, case in enumerate(cases, 1):
                        with st.expander(
                            f"📋 Case #{idx}: {case.get('case_number', 'N/A')} - {case.get('date', 'N/A')} at {case.get('time', 'N/A')}",
                            expanded=True
                        ):
                            col_left, col_right = st.columns([2, 1])
                            
                            with col_left:
                                st.markdown(f"**Case Number:** {case.get('case_number', 'N/A')}")
                                st.markdown(f"**Case Type:** {case.get('case_type', 'N/A')}")
                                st.markdown(f"**Court:** {case.get('court', 'N/A')}")
                                if case.get('court_type'):
                                    st.markdown(f"**Court Type:** {case.get('court_type')}")
                                
                                st.markdown("---")
                                
                                st.markdown(f"**📅 Date:** {case.get('date', 'N/A')}")
                                st.markdown(f"**🕐 Time:** {case.get('time', 'N/A')}")
                                st.markdown(f"**👨‍⚖️ Judge:** {case.get('judge', 'N/A')}")
                                st.markdown(f"**🚪 Room:** {case.get('room', 'N/A')}")
                                
                                if case.get('hearing_type'):
                                    st.markdown(f"**📞 Hearing Type:** {case.get('hearing_type')}")
                                if case.get('hearing_purpose'):
                                    st.markdown(f"**📝 Purpose:** {case.get('hearing_purpose')}")
                            
                            with col_right:
                                st.markdown("### Parties")
                                st.markdown(f"**Plaintiff:**  \n{case.get('plaintiff', 'N/A')}")
                                st.markdown(f"**Defendant:**  \n{case.get('defendant', 'N/A')}")
                                
                                if case.get('attorney'):
                                    st.markdown(f"**Attorney:**  \n{case.get('attorney')}")
                            
                            # Links and Downloads
                            st.markdown("---")
                            link_col1, link_col2, link_col3 = st.columns(3)
                            
                            with link_col1:
                                if case.get('webex_url'):
                                    st.markdown(f"🎥 [Join WebEx Meeting]({case['webex_url']})")
                            
                            with link_col2:
                                if case.get('detail_url'):
                                    st.markdown(f"🔗 [View Case Details]({case['detail_url']})")
                            
                            with link_col3:
                                # ICS download with FileVine and email inputs
                                with st.popover("📅 Download .ics", use_container_width=True):
                                    st.write("**Enter details for calendar event:**")
                                    filevine_link = st.text_input(
                                        "FileVine Link",
                                        placeholder="https://filevine.com/...",
                                        key=f"filevine_{idx}"
                                    )
                                    attorney_name = st.text_input(
                                        "Attorney Name",
                                        placeholder="attorney",
                                        key=f"email_{idx}",
                                        help="Enter just the name (e.g., 'chris' for chris@dexterlaw.com)"
                                    )
                                    # Auto-append @dexterlaw.com
                                    if attorney_name and attorney_name.strip():
                                        attorney_email = f"{attorney_name.strip()}@dexterlaw.com"
                                        st.caption(f"📧 Will use: {attorney_email}")
                                    else:
                                        attorney_email = ""
                                        st.caption("📧 Will use: attorney@dexterlaw.com (default)")
                                    
                                    # Generate ICS file with the provided details
                                    ics_content = cases_to_ics([case], filevine_link=filevine_link, attorney_email=attorney_email)
                                    case_number = case.get('case_number', 'unknown')
                                    defendant = case.get('defendant', 'event').split()[0] if case.get('defendant') else 'event'
                                    defendant = sanitize_filename(defendant.upper())
                                    # Get plaintiff name parts for filename
                                    plaintiff = case.get('plaintiff', '')
                                    plaintiff_parts = plaintiff.split() if plaintiff else []
                                    first_name = plaintiff_parts[0] if len(plaintiff_parts) > 0 else 'Unknown'
                                    last_name = plaintiff_parts[-1] if len(plaintiff_parts) > 1 else ''
                                    first_name = sanitize_filename(first_name)
                                    last_name = sanitize_filename(last_name)
                                    name_part = f"{first_name}_{last_name}" if last_name else first_name
                                    ics_filename = f"{case_number}_{name_part}_{defendant}.ics"
                                    
                                    st.download_button(
                                        label="💾 Generate & Download",
                                        data=ics_content,
                                        file_name=ics_filename,
                                        mime="text/calendar",
                                        key=f"ics_download_{idx}",
                                        use_container_width=True
                                    )

else:
    # Welcome message when no search has been performed
    st.info("👈 Enter an attorney's name in the sidebar and click 'Search Cases' to begin")
    
    st.markdown("""
    ### How to Use:
    1. Enter the attorney's **first name** and **last name** in the sidebar
    2. Click the **Search Cases** button
    3. View all cases for that attorney in an organized format
    4. Download results as CSV if needed
    
    ### Features:
    - 📊 Summary metrics showing total cases, virtual hearings, and court types
    - 🎥 Direct links to WebEx meetings for virtual hearings
    - 📋 Detailed case information including parties, judge, and hearing purpose
    - 💾 Export results to CSV for further analysis
    """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>Utah Court Calendar Search | Data from legacy.utcourts.gov</div>",
    unsafe_allow_html=True
)
