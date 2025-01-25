import os
import streamlit as st
from deepgram import DeepgramClient, SpeakOptions
import uuid
from utils import ImageAccessibilityAnalyzer, process_uploaded_image
from dotenv import load_dotenv
import time

## will work
load_dotenv()

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

def apply_custom_css():
    st.markdown("""
        <style>
        /* Main container styling */
        .main {
            padding: 2rem;
        }
        
        /* Custom title styling */
        .custom-title {
            background: linear-gradient(90deg, #3a7bd5, #00d2ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 2rem;
            text-align: center;
        }
        
        /* Card-like container for sections */
        .stCard {
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 1rem;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        /* Custom file uploader */
        .uploadedFile {
            border: 2px dashed rgba(255, 255, 255, 0.2);
            border-radius: 0.5rem;
            padding: 1rem;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .uploadedFile:hover {
            border-color: #00d2ff;
            background: rgba(58, 123, 213, 0.1);
        }
        
        /* Custom button styling */
        .stButton>button {
            background: linear-gradient(90deg, #3a7bd5, #00d2ff);
            color: white;
            border: none;
            border-radius: 0.5rem;
            padding: 0.5rem 2rem;
            font-weight: 600;
            transition: all 0.3s ease;
            width: 100%;
            margin: 0.5rem 0;
        }
        
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 210, 255, 0.3);
        }
        
        /* Radio button styling */
        .stRadio>label {
            background: rgba(255, 255, 255, 0.05);
            padding: 0.5rem 1rem;
            border-radius: 0.5rem;
            margin: 0.25rem;
            transition: all 0.3s ease;
        }
        
        .stRadio>label:hover {
            background: rgba(58, 123, 213, 0.2);
        }

        /* Custom radio options with icons */
        .custom-radio-options {
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
            gap: 1rem;
            margin: 1rem 0;
        }

        .radio-option {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 1rem;
        }

        .radio-option i {
            font-size: 1.2rem;
            color: #00d2ff;
        }
        
        /* Progress bar styling */
        .stProgress>div>div {
            background: linear-gradient(90deg, #3a7bd5, #00d2ff);
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
        }
        
        /* Custom info box */
        .custom-info-box {
            background: rgba(58, 123, 213, 0.1);
            border-left: 4px solid #3a7bd5;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 1rem 0;
        }
        
        /* Animation for loading spinner */
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }
        
        .stSpinner>div {
            animation: pulse 1s infinite;
        }
        </style>
    """, unsafe_allow_html=True)

def configure_page():
    """Configure Streamlit page settings"""
    st.set_page_config(
        page_title="Accessibility Image Analyzer",
        page_icon="👁️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    apply_custom_css()

def create_custom_container(title, content):
    """Create a custom styled container"""
    st.markdown(f"""
        <div class="stCard">
            <h3 style="color: #00d2ff; margin-bottom: 1rem;">{title}</h3>
            <div>{content}</div>
        </div>
    """, unsafe_allow_html=True)

def text_to_speech(text, model="aura-zeus-en"):
    """Convert text to speech using Deepgram"""
    try:
        os.makedirs('temp', exist_ok=True)
        filename = f'temp/description_{uuid.uuid4()}.mp3'
        
        deepgram = DeepgramClient(DEEPGRAM_API_KEY)
        options = SpeakOptions(model=model)
        deepgram.speak.rest.v("1").save(filename, {"text": text}, options)
        
        return filename
    except Exception as e:
        st.error(f"Text-to-Speech conversion error: {e}")
        return None

def cleanup_temp_files():
    """Clean up temporary audio files only"""
    try:
        if 'audio_file' in st.session_state and st.session_state.audio_file:
            if os.path.exists(st.session_state.audio_file):
                os.remove(st.session_state.audio_file)
            st.session_state.audio_file = None
            
        if os.path.exists('temp'):
            for file in os.listdir('temp'):
                if file.endswith('.mp3'):
                    os.remove(os.path.join('temp', file))
    except Exception as e:
        st.error(f"Error cleaning up temp files: {e}")

def reset_states():
    """Reset session states when uploading new image"""
    st.session_state.description = None
    cleanup_temp_files()

def create_analysis_options():
    """Create radio options with icons"""
    analysis_options = {
        "🔍 Scene Understanding": "Scene Understanding",
        "🗣️ Text to Speech": "Text to Speech",
        "👁️ Object Detection": "Object Detection",
        "📝 Task Guidance": "Task Guidance"
    }
    
    selected = st.radio(
        "Choose Analysis Type",
        options=list(analysis_options.keys()),
        horizontal=True,
        format_func=lambda x: analysis_options[x]
    )
    
    return analysis_options[selected]

def main():
    """Main Streamlit application entry point"""
    configure_page()
    
    # Initialize session states
    if 'description' not in st.session_state:
        st.session_state.description = None
    if 'audio_file' not in st.session_state:
        st.session_state.audio_file = None
    if 'previous_upload' not in st.session_state:
        st.session_state.previous_upload = None
    
    # Custom title with gradient
    st.markdown('<h1 class="custom-title">Visionary AI: Empowering the Visually Impaired</h1>', unsafe_allow_html=True)
    
    # Enhanced sidebar
    with st.sidebar:
        st.markdown("""
            <div class="custom-info-box">
                <h2 style="color: #00d2ff;">About This Tool</h2>
                <p>This application provides multiple accessibility-focused image analysis techniques:</p>
                <ul>
                    <li>🔍 <strong>Scene Understanding:</strong> Detailed visual scene descriptions</li>
                    <li>🗣️ <strong>Text to Speech:</strong> OCR and text extraction</li>
                    <li>👁️ <strong>Object Detection:</strong> Safety and navigation insights</li>
                    <li>📝 <strong>Task Guidance:</strong> Context-specific instructions</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    analyzer = ImageAccessibilityAnalyzer()
    
    # Analysis options with icons
    selected_analysis = create_analysis_options()
    
    # Enhanced file uploader at the top
    uploaded_file = st.file_uploader(
        "Upload an image for detailed analysis", 
        type=["jpg", "jpeg", "png", "webp"],
        help="Supports JPG, JPEG, PNG, and WEBP formats",
        on_change=reset_states
    )
    
    # Main content area with two columns
    if uploaded_file is not None:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="stCard">', unsafe_allow_html=True)
            st.markdown('<h3 style="color: #00d2ff; margin-bottom: 1rem;">Uploaded Image</h3>', unsafe_allow_html=True)
            st.image(uploaded_file, use_container_width=True, caption="Uploaded Image")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            if st.button(f"🔍 Analyze for {selected_analysis}", type="primary"):
                cleanup_temp_files()
                
                with st.spinner(f"🕒 Performing {selected_analysis} Analysis..."):
                    try:
                        st.session_state.description = process_uploaded_image(
                            analyzer, 
                            uploaded_file,
                            selected_analysis
                        )
                        st.success("✨ Analysis Complete!")
                    except Exception as e:
                        st.error(f"❌ An error occurred: {e}")
            
            # Show description in right column if it exists
            if st.session_state.description:
                create_custom_container("Analysis Results", st.session_state.description)
                
                if st.button("🔊 Listen to Description", key="audio_button"):
                    if 'audio_file' in st.session_state and st.session_state.audio_file:
                        cleanup_temp_files()
                    
                    with st.spinner("🎵 Generating audio..."):
                        audio_path = text_to_speech(st.session_state.description)
                        if audio_path and os.path.exists(audio_path):
                            st.session_state.audio_file = audio_path
                
                if st.session_state.audio_file and os.path.exists(st.session_state.audio_file):
                    progress_bar = st.progress(0)
                    
                    with st.expander("🎧 Audio Description", expanded=True):
                        try:
                            st.audio(st.session_state.audio_file, format='audio/mp3')
                            
                            for percent_complete in range(100 + 1):
                                progress_bar.progress(percent_complete)
                                time.sleep(0.05)
                            
                            progress_bar.progress(0)
                        except Exception as e:
                            st.error(f"❌ Error playing audio: {e}")
                            cleanup_temp_files()

if __name__ == "__main__":
    main()