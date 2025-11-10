import streamlit as st
import pandas as pd
from datetime import datetime
from search import search_court_cases

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
    
    date_filter = st.selectbox(
        "Date Filter",
        options=["all", "specific"],
        format_func=lambda x: "All Dates" if x == "all" else "Specific Date"
    )
    
    specific_date = None
    if date_filter == "specific":
        specific_date = st.date_input("Select Date")
    
    location_filter = st.text_input(
        "Location Filter",
        value="all",
        help="Enter 'all' for all locations or a specific court code"
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
                # Prepare date parameter
                date_param = "all"
                if date_filter == "specific" and specific_date:
                    date_param = specific_date.strftime("%Y-%m-%d")
                
                # Search for cases
                cases = search_court_cases(
                    search_type="a",
                    first_name=first_name.upper(),
                    last_name=last_name.upper(),
                    date=date_param,
                    location=location_filter
                )
                
                if not cases:
                    st.warning(f"No cases found for {first_name.upper()} {last_name.upper()}")
                else:
                    # Display summary
                    st.success(f"✅ Found {len(cases)} case(s) for **{first_name.upper()} {last_name.upper()}**")
                    
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
                            
                            # Links
                            st.markdown("---")
                            link_col1, link_col2 = st.columns(2)
                            
                            with link_col1:
                                if case.get('webex_url'):
                                    st.markdown(f"🎥 [Join WebEx Meeting]({case['webex_url']})")
                            
                            with link_col2:
                                if case.get('detail_url'):
                                    st.markdown(f"🔗 [View Case Details]({case['detail_url']})")
                    
                    # Export option
                    st.markdown("---")
                    st.subheader("📥 Export Data")
                    
                    # Create DataFrame for export
                    df = pd.DataFrame(cases)
                    csv = df.to_csv(index=False)
                    
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"court_cases_{first_name}_{last_name}_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                    
            except Exception as e:
                st.error(f"❌ Error searching cases: {str(e)}")
                st.exception(e)

else:
    # Welcome message when no search has been performed
    st.info("👈 Enter an attorney's name in the sidebar and click 'Search Cases' to begin")
    
    st.markdown("""
    ### How to Use:
    1. Enter the attorney's **first name** and **last name** in the sidebar
    2. Optionally select a specific date or location filter
    3. Click the **Search Cases** button
    4. View all cases for that attorney in an organized format
    5. Download results as CSV if needed
    
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
