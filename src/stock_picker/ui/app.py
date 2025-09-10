#!/usr/bin/env python
# SQLite workaround for cloud environments
try:
    __import__('pysqlite3')
    import sys as _sys
    _sys.modules['sqlite3'] = _sys.modules.pop('pysqlite3')
except ImportError:
    pass

import streamlit as st
import json
import os
from datetime import datetime
import sys
from dotenv import load_dotenv, find_dotenv
import threading
import time

# Add the src directory to the path so we can import the stock_picker module
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Global variables for managing analysis process
analysis_thread = None
analysis_stop_event = threading.Event()



st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        :root {
            /* Primary Theme Colors */
            --bg-dark: #2d2621;          /* Background */
            --text-primary: #ece5d8;     /* Foreground */
            --accent-primary: #c0a080;   /* Primary */
            --accent-primary-hover: #a88c6f; /* Slightly darker than primary for hover effects */
            --accent-secondary: #59493e; /* Accent */
            
            /* UI Component Colors */
            --bg-card: #3a322c;          /* Card */
            --text-secondary: #c5bcac;   /* Muted Foreground */
            --border-color: #4a4039;     /* Border/Input */
            
            /* Status Colors */
            --success: #10b981;          /* Keeping original as it contrasts well */
            --warning: #f59e0b;          /* Keeping original as it contrasts well */
            --danger: #b54a35;           /* Destructive */
        }
        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-dark);
            color: var(--text-primary);
        }
        .stApp {
            background-color: var(--bg-dark);
            color: var(--text-primary);
        }
        .block-container {
            padding: 2rem 3rem;
            max-width: 1400px;
            margin: 0 auto;
        }
        .nav-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            padding: 1rem 3rem;
            background: rgba(45, 38, 33, 0.9); /* --bg-dark with opacity */
            backdrop-filter: blur(10px);
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 999;
        }
        .nav-title {
            font-size: 1.75rem;
            font-weight: 700;
            color: var(--accent-primary);
            background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .nav-links a {
            margin: 0 15px;
            color: var(--text-secondary);
            text-decoration: none;
            font-weight: 500;
            transition: all 0.3s ease;
            padding: 8px 16px;
            border-radius: 8px;
        }
        .nav-links a:hover {
            color: var(--accent-primary);
            background: rgba(192, 160, 128, 0.15); /* --accent-primary with opacity */
        }
        .main-content {
            margin-top: 80px;
        }
        .hero-section {
            text-align: center;
            padding: 3rem 1rem;
            margin-bottom: 2rem;
        }
        .hero-title {
            font-size: 3rem;
            font-weight: 800;
            margin-bottom: 1rem;
            background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.5px;
        }
        .hero-subtitle {
            font-size: 1.25rem;
            color: var(--text-secondary);
            max-width: 700px;
            margin: 0 auto 2rem;
            line-height: 1.6;
        }
        .section-title {
            font-size: 2rem;
            font-weight: 700;
            color: var(--text-primary);
            margin: 3rem 0 2rem 0;
            position: relative;
            padding-bottom: 15px;
        }
        .section-title:after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 60px;
            height: 4px;
            background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
            border-radius: 2px;
        }
        .card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0,0,0,0.3);
        }
        .feature-card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 30px;
            height: 100%;
            transition: all 0.3s ease;
        }
        .feature-card:hover {
            border-color: var(--accent-primary);
            transform: translateY(-5px);
        }
        .feature-icon {
            width: 60px;
            height: 60px;
            background: rgba(192, 160, 128, 0.15); /* --accent-primary with opacity */
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 20px;
        }
        .feature-icon svg {
            width: 32px;
            height: 32px;
            fill: var(--accent-primary);
        }
        .feature-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 15px;
        }
        .feature-desc {
            color: var(--text-secondary);
            line-height: 1.6;
            font-size: 1.05rem;
        }
        .stButton>button {
            background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
            color: white;
            border: none;
            border-radius: 10px;
            padding: 14px 28px;
            font-weight: 600;
            font-size: 1.1rem;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(192, 160, 128, 0.4); /* --accent-primary with opacity */
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(192, 160, 128, 0.6); /* --accent-primary with higher opacity */
        }
        .stButton>button:active {
            transform: translateY(0);
        }
        .stSelectbox, .stTextInput {
            background: var(--bg-card); /* Using card background instead of separate input color */
            border: 1px solid var(--border-color);
            border-radius: 10px;
            color: var(--text-primary);
            padding: 12px 16px;
            font-size: 1.1rem;
            margin-bottom: 20px;
        }
        .stSelectbox:focus, .stTextInput:focus {
            border-color: var(--accent-primary);
            box-shadow: 0 0 0 3px rgba(192, 160, 128, 0.3); /* --accent-primary with opacity */
        }
        .stSelectbox label, .stTextInput label {
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 8px;
            display: block;
        }
        .stSelectbox div, .stTextInput input {
            background: transparent;
            color: var(--text-primary);
            border: none;
            padding: 0;
        }
        .stSelectbox div:focus, .stTextInput input:focus {
            box-shadow: none;
        }
        .input-container {
            margin-bottom: 25px;
        }
        .input-label {
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 8px;
            display: block;
            font-size: 1.1rem;
        }
        .input-hint {
            color: var(--text-secondary);
            font-size: 0.9rem;
            margin-top: 5px;
            display: block;
        }
        .stExpander {
            border: 1px solid var(--border-color) !important;
            border-radius: 16px !important;
            background: var(--bg-card) !important;
        }
        .stExpander header {
            font-size: 1.2rem !important;
            font-weight: 600 !important;
            color: var(--accent-primary) !important;
        }
        .stExpander [data-testid="stExpanderDetails"] {
            padding: 1.5rem !important;
        }
        .footer {
            text-align: center;
            padding: 3rem 2rem;
            color: var(--text-secondary);
            font-size: 1rem;
            border-top: 1px solid var(--border-color);
            margin-top: 3rem;
        }
        .analysis-placeholder {
            background: var(--bg-card);
            border: 2px dashed var(--border-color);
            border-radius: 16px;
            padding: 40px;
            text-align: center;
            margin: 20px 0;
        }
        .placeholder-icon {
            font-size: 4rem;
            color: var(--accent-primary);
            margin-bottom: 20px;
        }
        .placeholder-text {
            color: var(--text-secondary);
            font-size: 1.2rem;
            max-width: 600px;
            margin: 0 auto;
            line-height: 1.6;
        }
        .metric-container {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin: 25px 0;
        }
        .metric-card {
            flex: 1;
            min-width: 220px;
            background: rgba(192, 160, 128, 0.1); /* --accent-primary with opacity */
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 25px;
            text-align: center;
            transition: all 0.3s ease;
        }
        .metric-card:hover {
            border-color: var(--accent-primary);
            background: rgba(192, 160, 128, 0.2); /* --accent-primary with higher opacity */
        }
        .metric-title {
            font-size: 1rem;
            color: var(--text-secondary);
            margin-bottom: 12px;
            font-weight: 500;
        }
        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            color: var(--accent-primary);
        }
        .company-card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 25px;
            margin-bottom: 20px;
            transition: all 0.3s ease;
        }
        .company-card:hover {
            border-color: var(--accent-primary);
        }
        .company-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 15px;
            border-bottom: 1px solid var(--border-color);
        }
        .company-name {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--text-primary);
            margin: 0;
        }
        .company-ticker {
            background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
            color: white;
            padding: 6px 14px;
            border-radius: 20px;
            font-weight: 700;
            font-size: 0.9rem;
        }
        .company-reason {
            font-size: 1.05rem;
            line-height: 1.7;
            color: var(--text-secondary);
        }
        .decision-card {
            background: linear-gradient(135deg, var(--bg-card) 0%, #2d2621 100%); /* Using --bg-dark */
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 40px;
            margin: 25px 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.25);
        }
        .decision-header {
            text-align: center;
            margin-bottom: 30px;
        }
        .decision-title {
            font-size: 2.2rem;
            font-weight: 800;
            color: var(--accent-primary);
            margin-bottom: 15px;
        }
        .decision-subtitle {
            font-size: 1.3rem;
            color: var(--text-secondary);
        }
        @media (max-width: 768px) {
            .block-container {
                padding: 1.5rem;
            }
            .hero-title {
                font-size: 2.2rem;
            }
            .section-title {
                font-size: 1.7rem;
            }
            .card, .feature-card {
                padding: 20px;
            }
        }
    </style>
    <div class="nav-container">
        <div class="nav-title">StockIntel Analytics</div>
        <div class="nav-links">
            <a href="#how-it-works">How It Works</a>
            <a href="#run-analysis">Run Analysis</a>
            <a href="#results">Results</a>
        </div>
    </div>
    <div class="main-content">
""", unsafe_allow_html=True)

@st.cache_data(ttl=30)
def load_json_file(file_path):
    """Load JSON data from a file"""
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return None

@st.cache_data(ttl=30)
def load_markdown_file(file_path):
    """Load markdown content from a file"""
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    return None

def main():
    st.set_page_config(
        page_title="StockIntel Analytics",
        page_icon="📊",
        layout="wide"
    )
    
    # Clear old temporary data on app start
    clear_old_temp_data()
    
    # Load .env for local runs (Streamlit Cloud will use secrets)
    try:
        # Load the .env file from the project root
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        dotenv_path = os.path.join(project_root, '.env')
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path=dotenv_path, override=True)
    except Exception:
        pass
    
    # Prefer Streamlit Cloud secrets, fall back to OS env
    google_key = None
    serper_key = None
    try:
        if hasattr(st, "secrets"):
            google_key = st.secrets.get("GOOGLE_API_KEY")
            serper_key = st.secrets.get("SERPER_API_KEY")
    except Exception:
        pass
    
    # Set environment variables if they exist in secrets but not in env
    if google_key and str(google_key).strip():
        os.environ["GOOGLE_API_KEY"] = str(google_key).strip()
    if serper_key and str(serper_key).strip():
        os.environ["SERPER_API_KEY"] = str(serper_key).strip()
    
    # Debug information for API keys (remove in production)
    # st.write(f"GOOGLE_API_KEY exists: {bool(os.getenv('GOOGLE_API_KEY'))}")
    # st.write(f"SERPER_API_KEY exists: {bool(os.getenv('SERPER_API_KEY'))}")
    
    # Hero Section
    st.markdown('''
        <div class="hero-section">
            <div class="hero-title">Intelligent Stock Analysis Platform</div>
            <div class="hero-subtitle">Leverage AI-powered insights to uncover market trends, analyze company fundamentals, and identify top-performing investment opportunities in real-time.</div>
        </div>
    ''', unsafe_allow_html=True)

    # "How It Works" Section
    st.markdown('<a name="how-it-works"></a>', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">How It Works</h2>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('''
        <div class="feature-card">
            <div class="feature-icon">
                <svg viewBox="0 0 24 24">
                    <path d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,4A8,8 0 0,1 20,12A8,8 0 0,1 12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4M12,6A6,6 0 0,0 6,12A6,6 0 0,0 12,18A6,6 0 0,0 18,12A6,6 0 0,0 12,6M12,8A4,4 0 0,1 16,12A4,4 0 0,1 12,16A4,4 0 0,1 8,12A4,4 0 0,1 12,8Z" />
                    <path d="M12,10A2,2 0 0,0 10,12A2,2 0 0,0 12,14A2,2 0 0,0 14,12A2,2 0 0,0 12,10Z" />
                </svg>
            </div>
            <h3 class="feature-title">Trend Analysis</h3>
            <p class="feature-desc">Our AI scans real-time financial news, market reports, and industry insights to identify emerging sectors and trending companies with high growth potential.</p>
        </div>
        ''', unsafe_allow_html=True)
    with c2:
        st.markdown('''
        <div class="feature-card">
            <div class="feature-icon">
                <svg viewBox="0 0 24 24">
                    <path d="M12,3C7.58,3 4,4.79 4,7C4,9.21 7.58,11 12,11C16.42,11 20,9.21 20,7C20,4.79 16.42,3 12,3M4,9V12C4,14.21 7.58,16 12,16C16.42,16 20,14.21 20,12V9C20,11.21 16.42,13 12,13C7.58,13 4,11.21 4,9M4,14V17C4,19.21 7.58,21 12,21C16.42,21 20,19.21 20,17V14C20,16.21 16.42,18 12,18C7.58,18 4,16.21 4,14Z" />
                </svg>
            </div>
            <h3 class="feature-title">In-Depth Research</h3>
            <p class="feature-desc">We conduct comprehensive financial analysis on identified companies, examining fundamentals, market sentiment</p>
        </div>
        ''', unsafe_allow_html=True)
    with c3:
        st.markdown('''
        <div class="feature-card">
            <div class="feature-icon">
                <svg viewBox="0 0 24 24">
                    <path d="M12,2L1,21H23M12,6L19.53,19H4.47M11,10V14H13V10M11,16V18H13V16" />
                </svg>
            </div>
            <h3 class="feature-title">Actionable Insights</h3>
            <p class="feature-desc">Receive clear, data-driven investment recommendations with detailed analysis on the top stock picks and risk assessment metrics.</p>
        </div>
        ''', unsafe_allow_html=True)

    # Main application layout
    st.markdown('<a name="run-stock-analysis"></a>', unsafe_allow_html=True)
    show_analysis_page()

    # GitHub link section
    st.markdown('''
        <div style="text-align: center; margin: 30px 0;">
            <a href="https://github.com/akshaykarthicks" target="_blank" style="color: var(--accent-primary); text-decoration: none; font-weight: 600; display: inline-flex; align-items: center; gap: 8px;">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path>
                </svg>
                View project on GitHub
            </a>
        </div>
    ''', unsafe_allow_html=True)

    st.markdown('<a name="results"></a>', unsafe_allow_html=True)
    show_results_page()

    # Agents section
    st.markdown('<h2 class="section-title">Our Agents</h2>', unsafe_allow_html=True)
    a1, a2, a3 = st.columns(3)
    with a1:
        st.markdown('''
        <div class="feature-card">
            <div class="feature-icon">
                <svg viewBox="0 0 24 24">
                    <path d="M3,5H21V7H3V5M3,11H21V13H3V11M3,17H15V19H3V17Z" />
                </svg>
            </div>
            <h3 class="feature-title">📰 Financial News Analyst</h3>
            <p class="feature-desc">Scans real-time financial news to identify 2–3 trending companies in the selected sector.</p>
        </div>
        ''', unsafe_allow_html=True)
    with a2:
        st.markdown('''
        <div class="feature-card">
            <div class="feature-icon">
                <svg viewBox="0 0 24 24">
                    <path d="M9,2A7,7 0 0,1 16,9C16,10.73 15.41,12.3 14.41,13.53L21.19,20.31L19.78,21.72L13,14.94C11.77,15.94 10.2,16.53 8.47,16.53A7,7 0 0,1 1.47,9.53A7,7 0 0,1 8.47,2.53M8.47,4.53A5,5 0 0,0 3.47,9.53A5,5 0 0,0 8.47,14.53A5,5 0 0,0 13.47,9.53A5,5 0 0,0 8.47,4.53Z" />
                </svg>
            </div>
            <h3 class="feature-title">🔍 Senior  Researcher</h3>
            <p class="feature-desc">Performs deep-dive research on fundamentals, sentiment, and competitive positioning.</p>
        </div>
        ''', unsafe_allow_html=True)
    with a3:
        st.markdown('''
        <div class="feature-card">
            <div class="feature-icon">
                <svg viewBox="0 0 24 24">
                    <path d="M11 17L6 12L7.41 10.59L11 14.17L16.59 8.58L18 10L11 17Z" />
                </svg>
            </div>
            <h3 class="feature-title">📊 Stock Picker</h3>
            <p class="feature-desc">Synthesizes findings to select the best opportunity and produce a clear recommendation.</p>
        </div>
        ''', unsafe_allow_html=True)

    # Footer
    st.markdown('''
        <div class="footer">
            <p>
                <a href="https://github.com/akshaykarthicks" target="_blank" style="color: var(--text-secondary); text-decoration: none;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 8px;">
                        <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path>
                    </svg>
                    akshaykarthicks on GitHub
                </a>
            </p>
        </div>
    </div>
    ''', unsafe_allow_html=True)

def show_analysis_page():
    st.markdown('<a name="run-analysis"></a>', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">Run Stock Analysis</h2>', unsafe_allow_html=True)
    
    # Input for sector with predefined options
    sectors = [
        "AI and Machine Learning",
        "Healthcare Technology",
        "Renewable Energy",
        "Fintech",
        "E-commerce",
        "Cybersecurity",
        "Electric Vehicles",
        "Biotechnology",
        "Semiconductors",
        "Cloud Computing"
    ]
    
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    st.markdown('<div class="input-label">Select Sector for Analysis</div>', unsafe_allow_html=True)
    selected_sector = st.selectbox(
        "Select Sector for Analysis:",
        options=sectors,
        index=0,
        help="Choose a sector to analyze for trending companies",
        label_visibility="collapsed"
    )
    st.markdown('<span class="input-hint">Choose from predefined sectors or enter a custom sector below</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    st.markdown('<div class="input-label">Or Enter a Custom Sector</div>', unsafe_allow_html=True)
    custom_sector = st.text_input(
        "Or enter a custom sector:",
        value="",
        placeholder="e.g., Consumer Electronics, Green Energy, etc.",
        help="Specify a custom sector you want to analyze",
        label_visibility="collapsed"
    )
    st.markdown('<span class="input-hint">Enter your own sector if not listed above</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Determine which sector to use
    sector = custom_sector if custom_sector else selected_sector
    
    # Run analysis button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Always enable the button; show errors dynamically if keys are missing
        run_disabled = False
        run_clicked = st.button("🚀 Run Analysis", use_container_width=True, disabled=run_disabled, key="run_analysis")
        cancel_clicked = st.button("⏹️ Cancel Analysis", use_container_width=True, key="cancel_analysis")
        
        if run_clicked:
            if sector:
                if not os.getenv("GOOGLE_API_KEY"):
                    st.error("GOOGLE_API_KEY not found. Please add your API keys:")
                    st.info("1. For local development: Create a `.env` file in the project root with your keys\n"
                           "2. For Streamlit Cloud: Add your keys in Settings > Secrets\n"
                           "3. As environment variables: Set GOOGLE_API_KEY and SERPER_API_KEY in your system")
                    st.code("""
# Example .env file content:
GOOGLE_API_KEY=your_gemini_api_key_here
SERPER_API_KEY=your_serper_api_key_here
                    """, language="bash")
                    return
                progress = st.progress(0, text=f"Analyzing trending companies in {sector}…")
                status = st.empty()
                progress.progress(10, text="Initializing AI agents…")
                try:
                    # Lazy import heavy modules here to speed page load
                    from stock_picker.crew import StockPicker
                    inputs = {'sector': sector}
                    progress.progress(35, text="Searching financial news and gathering companies…")
                    status.info("Analyzing latest sector developments…")
                    result = StockPicker().crew().kickoff(inputs=inputs)
                    progress.progress(85, text="Generating reports and investment insights…")
                    
                    # Display success message
                    st.success("Analysis completed successfully!")
                    st.balloons()
                    
                    # Save timestamp for reference
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.info(f"Analysis completed at: {timestamp}")
                    
                    # Show raw result in an expander
                    with st.expander("View Detailed Analysis"):
                        st.text_area("Raw Result", result.raw, height=300)
                    progress.progress(100, text="Done")
                except Exception as e:
                    progress.empty()
                    status.empty()
                    st.error(f"An error occurred during analysis: {str(e)}")
                    st.info("Please check your API keys and network connection.")
            else:
                # Commenting out the sector warning
                # st.warning("Please enter a sector to analyze.")
                pass
        
        if cancel_clicked:
            # Commenting out the cancellation warning
            # st.warning("Analysis cancelled by user.")
            # Clear any existing results
            if os.path.exists("output/trending_companies.json"):
                os.remove("output/trending_companies.json")
            if os.path.exists("output/research_report.json"):
                os.remove("output/research_report.json")
            if os.path.exists("output/decision.md"):
                os.remove("output/decision.md")
    
    

def show_results_page():
    st.markdown('<a name="results"></a>', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">Analysis Results</h2>', unsafe_allow_html=True)
    
    # Results
    trending_file = "output/trending_companies.json"
    research_file = "output/research_report.json"
    decision_file = "output/decision.md"
    
    files_exist = any(os.path.exists(f) for f in [trending_file, research_file, decision_file])
    
    # Only show results if files exist (meaning analysis was completed)
    if not files_exist:
        st.markdown('''
            <div class="analysis-placeholder">
                <div class="placeholder-icon">📊</div>
                <h3>Analysis Results Will Appear Here</h3>
                <p class="placeholder-text">Run a stock analysis to generate comprehensive reports, financial insights, and investment recommendations. Your results will be displayed in this section once the analysis is complete.</p>
            </div>
        ''', unsafe_allow_html=True)
        return
    
    # Check if this is a new session (files exist but might be from previous run)
    # We'll show a warning if files are older than 1 hour
    file_times = []
    for f in [trending_file, research_file, decision_file]:
        if os.path.exists(f):
            file_times.append(os.path.getmtime(f))
    
    if file_times:
        latest_file_time = max(file_times)
        current_time = time.time()
        time_diff_hours = (current_time - latest_file_time) / 3600
        
        # Commenting out the warning for older files
        # if time_diff_hours > 1:
        #     st.warning("⚠️ Displaying results from a previous analysis. Run a new analysis to get updated results.")
    
    # Create tabs for better organization
    tab1, tab2, tab3 = st.tabs(["📈 Trending Companies", "🔍 Research Report", "📊 Investment Decision"])
    
    # Trending Companies Tab
    with tab1:
        show_trending_companies(trending_file)
        if os.path.exists(trending_file):
            with open(trending_file, 'rb') as f:
                st.download_button("📥 Download Trending Companies JSON", f, file_name="trending_companies.json", mime="application/json")

    # Research Report Tab
    with tab2:
        show_research_report(research_file)
        if os.path.exists(research_file):
            with open(research_file, 'rb') as f:
                st.download_button("📥 Download Research Report JSON", f, file_name="research_report.json", mime="application/json")

    # Investment Decision Tab
    with tab3:
        show_investment_decision(decision_file)
        if os.path.exists(decision_file):
            with open(decision_file, 'rb') as f:
                st.download_button("📥 Download Investment Decision MD", f, file_name="decision.md", mime="text/markdown")

def show_trending_companies(file_path):
    st.markdown('<h3>Trending Companies in the Sector</h3>', unsafe_allow_html=True)
    trending_data = load_json_file(file_path)
    if trending_data and "companies" in trending_data:
        for i, company in enumerate(trending_data["companies"], 1):
            st.markdown(f'''
                <div class="company-card">
                    <div class="company-header">
                        <h3 class="company-name">{i}. {company.get('name', 'N/A')}</h3>
                        <div class="company-ticker">{company.get('ticker', 'N/A') if company.get('ticker') else 'Private'}</div>
                    </div>
                    <div class="company-reason">{company.get('reason', 'N/A')}</div>
                </div>
            ''', unsafe_allow_html=True)
    else:
        st.info("No trending companies data available.")

def show_research_report(file_path):
    st.markdown('<h3>Comprehensive Research Analysis</h3>', unsafe_allow_html=True)
    research_data = load_json_file(file_path)
    if research_data:
        if "companies" in research_data:
            for i, company in enumerate(research_data["companies"], 1):
                st.markdown(f'''
                    <div class="company-card">
                        <div class="company-header">
                            <h3 class="company-name">{i}. {company.get('name', 'N/A')}</h3>
                            <div class="company-ticker">{company.get('ticker', 'N/A') if company.get('ticker') else 'Private'}</div>
                        </div>
                        <div class="company-reason">{company.get('reason', 'N/A')}</div>
                    </div>
                ''', unsafe_allow_html=True)

        # Market analysis section with improved UI
        st.markdown('<h3 style="margin: 30px 0 20px 0;">Market Analysis Metrics</h3>', unsafe_allow_html=True)
        
        # Display metrics in a more visually appealing way
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        
        # Market Position
        st.markdown(f'''
            <div class="metric-card">
                <div class="metric-title">Market Position</div>
                <div class="metric-value">{research_data.get('market_postion', 'N/A')}</div>
            </div>
        ''', unsafe_allow_html=True)
        
        # Future Growth
        st.markdown(f'''
            <div class="metric-card">
                <div class="metric-title">Future Growth Potential</div>
                <div class="metric-value">{research_data.get('future_growth', 'N/A')}</div>
            </div>
        ''', unsafe_allow_html=True)
        
        # Investment Potential
        st.markdown(f'''
            <div class="metric-card">
                <div class="metric-title">Investment Potential</div>
                <div class="metric-value">{research_data.get('investment_potential', 'N/A')}</div>
            </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
    else:
        st.info("No research report data available.")

def show_investment_decision(file_path):
    st.markdown('<h3>Investment Recommendation</h3>', unsafe_allow_html=True)
    decision_content = load_markdown_file(file_path)
    if decision_content:
        # Display the content directly without parsing
        st.markdown(f'''
            <div class="decision-card">
                <div class="decision-header">
                    <h2 class="decision-title">Recommended Investment</h2>
                </div>
                <div class="company-reason">
        ''', unsafe_allow_html=True)
        
        # Display the markdown content directly
        st.markdown(decision_content)
        
        st.markdown('''
                </div>
            </div>
        ''', unsafe_allow_html=True)
    else:
        st.info("No investment decision data available.")


def clear_old_temp_data():
    """Clear temporary data files that are older than 1 hour"""
    import time
    output_files = [
        "output/trending_companies.json",
        "output/research_report.json", 
        "output/decision.md"
    ]
    
    current_time = time.time()
    for file_path in output_files:
        if os.path.exists(file_path):
            file_mod_time = os.path.getmtime(file_path)
            # If file is older than 1 hour (3600 seconds), delete it
            if (current_time - file_mod_time) > 3600:
                try:
                    os.remove(file_path)
                except Exception:
                    pass  # Ignore errors in deletion


if __name__ == "__main__":
    main()