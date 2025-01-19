import base64
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("api_key")


class ImageAccessibilityAnalyzer:
  

    def __init__(self, model="gemini-1.5-flash"):
       
        self.chat_model = ChatGoogleGenerativeAI(
            model=model, 
            api_key=api_key 
        )
        self.output_parser = StrOutputParser()
        

    def _create_analysis_chain(self, system_prompt):
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", [
                {
                    "type": "image_url", 
                    "image_url": {"url": "{image_base64}"}
                },
                {"type": "text", "text": "{analysis_prompt}"}
            ])
        ])
        
        return prompt | self.chat_model | self.output_parser

    def scene_understanding(self, image_base64):
        
        """Generate comprehensive scene description"""
        system_prompt = """
        You are an AI assistant helping visually impaired individuals understand visual scenes.
        Provide a comprehensive, detailed, and vivid description of the image.
        Focus on layout, colors, objects, people, and spatial relationships.
        provide in short and clear.
        """
        
        chain = self._create_analysis_chain(system_prompt)
        
        return chain.invoke({
            "image_base64": image_base64,
            "analysis_prompt": "Describe every significant detail in this scene, explaining layout, colors, and key elements."
        })

    def text_to_speech_ocr(self, image_base64):
        """Extract and prepare text for audio conversion"""
        system_prompt = """
        You are an advanced OCR and text extraction assistant for visually impaired users.
        Carefully extract ALL readable text from the image.
        Organize text hierarchically, maintaining reading order and context.
         provide in short and clear.
        """
        
        chain = self._create_analysis_chain(system_prompt)
        
        return chain.invoke({
            "image_base64": image_base64,
            "analysis_prompt": "Extract ALL readable text from this image. Organize text by sections, headings, and reading sequence."
        })

    def object_detection(self, image_base64):
        """Detect and describe objects for navigation safety"""
        system_prompt = """
        You are a safety-oriented object detection assistant for visually impaired navigation.
        Identify and locate objects in the image with precise spatial descriptions.
        Prioritize potential obstacles, hazards, and navigation challenges.
         provide in short and clear.
        """
        
        chain = self._create_analysis_chain(system_prompt)
        
        return chain.invoke({
            "image_base64": image_base64,
            "analysis_prompt": """
            Systematically identify objects in this scene. For each object, provide: 
            1. Object name 
            2. Location in image 
            3. Potential navigation impact 
            4. Safety considerations
            """
        })

    def task_specific_guidance(self, image_base64):
        """Provide context-specific task guidance"""
        system_prompt = """
        You are a contextual assistance AI for visually impaired users.
        Analyze the image and provide actionable, step-by-step guidance.
        Offer precise, helpful instructions based on the image's content.
         provide in short and clear.
        """
        
        chain = self._create_analysis_chain(system_prompt)
        
        return chain.invoke({
            "image_base64": image_base64,
            "analysis_prompt": """
            Analyze this image and provide detailed, step-by-step guidance. 
            Identify objects, their potential use, and offer practical instructions.
            """
        })

def process_uploaded_image(analyzer, uploaded_file, analysis_type):
    
    # Read the uploaded file
    image_bytes = uploaded_file.getvalue()
    
    # Base64 encode the image
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    image_base64 = f"data:image/jpeg;base64,{image_base64}"
    
    # Perform specific analysis
    analysis_methods = {
        "Scene Understanding": analyzer.scene_understanding,
        "Text to Speech": analyzer.text_to_speech_ocr,
        "Object Detection": analyzer.object_detection,
        "Task Guidance": analyzer.task_specific_guidance
    }
    
    try:
        response = analysis_methods[analysis_type](image_base64)
        return response
    except Exception as e:
        return f"Error processing image: {str(e)}"

