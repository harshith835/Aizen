import google.generativeai as genai
from pathlib import Path
import streamlit as st
from streamlit_option_menu import option_menu
from PIL import Image

#api initialize
genai.configure(api_key=st.secrets["API_KEY"])
generation_config = {
"temperature": 0,
"top_p": 1,
"top_k": 32,
"max_output_tokens": 4096,
}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    }
]

#ocr model
model = genai.GenerativeModel(model_name = "gemini-1.5-pro",
generation_config = generation_config,
safety_settings = safety_settings)

## fronted part
col1, col2 = st.columns(2)
with st.sidebar:
    select_op = option_menu('Home', ["OCR",'ChatBot','About Us'],icons = ['house','chat','person'] ,default_index=0)
if select_op == "OCR":

    imageQuestion = st.text_input("What to extract from image?")

    question = st.text_input("Ask question:")

    userImage = st.file_uploader("Photo de bhai (PNG, JPEG, JPG):", type=["png", "jpeg", "jpg"])
    outcome = ""
    if userImage is not None:
        st.image(userImage, caption='Uploaded Image')
        byteimage = userImage.read()
        
    if st.button("Send"):
        problem_picture = {
        'mime_type': 'image/png',
        'data':  byteimage
        }
        # OCR_prompt = "extract the equation from the image output: just the equation no text"

        ocr = model.generate_content(
            contents=[imageQuestion,problem_picture]
        )
        outcome = ocr.text
        st.write(outcome)
        prompt=f'{question}:{ocr.text}'

        text_model=genai.GenerativeModel(model_name = "gemini-1.0-pro")
        response=text_model.generate_content(prompt)

        st.write(response.text)

#################### chatBot #####################
#
if "conversation_started" not in st.session_state:
    st.session_state.conversation_started = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "user_persona" not in st.session_state:
    st.session_state.user_persona = None
#

#code for personas

def generate_persona_prompt(persona, user_input):
    persona_prompts = {
        "kid": "You are talking to a kid. Answer in a simple and fun way.",
        "student": "You are talking to a student. Provide clear and informative answers.",
        "working professional": "You are talking to a working professional. Provide detailed and professional answers.",
        "researcher": "You are talking to a researcher. Provide in-depth and analytical answers."
    }
    prompt = f"{persona_prompts.get(persona, '')} {user_input} "
    return prompt

#

#newest shit 11:56

if select_op == "ChatBot":
    if not st.session_state.conversation_started:
        # Select persona
        persona_options = ["kid", "student", "working professional", "researcher"]
        persona = st.selectbox("Who are you?", persona_options)
        # Language_options = ['English','Hindi','Japanese']
        # lan = st.selectbox("Which Language do you prefer",Language_options)
        user_input = st.text_input("You:")
        
        if st.button("Talk"):
            st.session_state.conversation_started = True
            st.session_state.user_persona = persona
            st.session_state.chat_model = genai.GenerativeModel(model_name="gemini-1.0-pro")
            prompt = generate_persona_prompt(persona, user_input)
            ai = st.session_state.chat_model.generate_content(prompt)
            st.session_state.chat_history.append(('🧑', user_input))
            st.session_state.chat_history.append(('🤖', ai.text))
            st.experimental_rerun()
    else:
        for speaker, message in st.session_state.chat_history:
            st.write(f"{speaker}: {message}")

        user_input = st.text_input("You:", key="new_input")
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("Send"):
                if user_input:
                    prompt = generate_persona_prompt(st.session_state.user_persona, user_input)
                    ai = st.session_state.chat_model.generate_content(prompt)
                    st.session_state.chat_history.append(('🧑', user_input))
                    st.session_state.chat_history.append(('🤖', ai.text))
                    st.experimental_rerun()
        
        with col2:
            if st.button("Clear"):
                st.session_state.conversation_started = False
                st.session_state.chat_history = []
                st.session_state.user_persona = None
                st.experimental_rerun()
