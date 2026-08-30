import streamlit as st
import yt_dlp
import os
from pathlib import Path

st.set_page_config(page_title="SocialDown Pro", page_icon="📥", layout="centered")

st.title("📥 SocialDown Pro")
st.write("Aap yahan se YouTube aur social media videos asani se download kar sakte hain!")

# URL input
url = st.text_input("Enter Video URL:", placeholder="https://www.youtube.com/watch?v=...")

# Quality option
quality = st.selectbox("Select Format:", ["Video (Best)", "Audio (MP3)"])

if st.button("Start Download", type="primary"):
    if not url:
        st.error("Please enter a valid URL!")
    else:
        with st.spinner("Downloading... Barah-e-karam intezaar karein..."):
            try:
                DOWNLOAD_DIR = os.path.join(str(Path.home()), "Downloads", "SocialDown_Pro")
                os.makedirs(DOWNLOAD_DIR, exist_ok=True)

                if "Audio" in quality:
                    ydl_opts = {
                        'format': 'bestaudio/best',
                        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
                        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}],
                    }
                else:
                    ydl_opts = {
                        'format': 'best',
                        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
                    }

                # Cookie support agar file mojood ho
                if os.path.exists('cookies.txt'):
                    ydl_opts['cookiefile'] = 'cookies.txt'

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    title = info.get('title', 'Media File')

                st.success(f"Successfully Downloaded: {title}")
            except Exception as e:
                st.error(f"Error aa gaya: {str(e)}")