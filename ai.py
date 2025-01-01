import streamlit as st
import os
from fpdf import FPDF
from groq import Groq  # Ensure this is properly imported

# Streamlit page configuration
st.set_page_config(
    page_title="TechPulse AI Chatbot",
    page_icon="\U0001F4BB",
    layout="centered"
)

# Retrieve and set API key from config
GROQ_API_KEY = "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"

# Validate the API key if it exists
if not GROQ_API_KEY:
    st.error("API key is missing.")
    st.stop()

# Save the API key to the environment variable
os.environ["GROQ_API_KEY"] = GROQ_API_KEY

# Initialize the Groq client with API key
try:
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
except Exception as e:
    st.error(f"Failed to initialize Groq client: {e}")
    st.stop()

# Initialize the chat history in Streamlit session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Streamlit page title
st.title("\U0001F4BB TechPulse AI Chatbot")

# Function to validate user prompt
def is_valid_prompt(prompt):
    keywords = [
        "technology", "AI", "machine learning", "software", "hardware", "innovation", "disruptive", 
        "robotics", "data science", "cloud computing", "quantum computing", "blockchain", "5G", 
        "cybersecurity", "IoT", "smart tech", "virtual reality", "augmented reality", "smart devices", 
        "AI models", "tech news", "programming", "coding", "digital transformation", "tech industry", 
        "AI ethics", "AI development", "tech startups", "computing", "ml","space technology"," automobile technology"," software",
    ]
    return any(keyword.lower() in prompt.lower() for keyword in keywords) or "your name" in prompt.lower()

# Function to create PDF
def create_pdf(content):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", size=12)
        encoded_content = content.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 10, encoded_content)
        return pdf.output(dest='S').encode('latin-1')
    except Exception as e:
        st.error(f"Error creating PDF: {e}")
        return None

# Display the chat history
for i, message in enumerate(st.session_state.chat_history):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            response_text = message["content"]
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="Download as Text",
                    data=response_text,
                    file_name=f"response_{i+1}.txt",
                    mime="text/plain"
                )
            with col2:
                pdf_bytes = create_pdf(response_text)
                if pdf_bytes:
                    st.download_button(
                        label="Download as PDF",
                        data=pdf_bytes,
                        file_name=f"response_{i+1}.pdf",
                        mime="application/pdf"
                    )

# Input field for user message
user_prompt = st.chat_input("Ask about technology or technical topics...")

if user_prompt:
    st.write("User Prompt being validated:", user_prompt)  # Debugging user input
    if is_valid_prompt(user_prompt):
        st.chat_message("user").markdown(user_prompt)
        st.session_state.chat_history.append({"role": "user", "content": user_prompt})

        # Prepare messages for the LLM
        messages = [
            {"role": "system", "content": "You are TechPulse AI, a chatbot designed to provide accurate information about technology, AI, machine learning, software, hardware, programming, tech news, and innovations. Do not respond to any queries unrelated to these topics."},
            *st.session_state.chat_history
        ]

        try:
            # Call the Groq API
            response = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=messages
            )

            # Debugging the assistant response
            assistant_response = response.choices[0].message.content
            st.write("Assistant Response:", assistant_response)  # Debugging the response

            st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})

            # Display the LLM response
            with st.chat_message("assistant"):
                st.markdown(assistant_response)

                col1, col2 = st.columns(2)

                # Text download in column 1
                with col1:
                    st.download_button(
                        label="Download as Text",
                        data=assistant_response,
                        file_name="response_latest.txt",
                        mime="text/plain"
                    )

                # PDF download in column 2
                with col2:
                    pdf_bytes = create_pdf(assistant_response)
                    if pdf_bytes:
                        st.download_button(
                            label="Download as PDF",
                            data=pdf_bytes,
                            file_name="response_latest.pdf",
                            mime="application/pdf"
                        )

        except Exception as e:
            st.error(f"Error while fetching the response from GROQ: {e}")
            st.write("Error Details:", e)
    else:
        if "your name" in user_prompt.lower():
            response = "My name is TechPulse AI, your technical assistant."
            st.chat_message("assistant").markdown(response)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
        else:
            st.error("This is not a technical-related question. Please ask about technology or technical topics.")
