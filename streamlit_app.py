import streamlit as st
from openai import OpenAI
import os
import time
import csv

# Get the current working directory
cwd = os.getcwd()
st.title("📄 AI Software Manager")

models = [
    "deepseek/deepseek-r1:free",
    "nvidia/llama-3.1-nemotron-ultra-253b-v1:free",
    "mistralai/mistral-small-3.1-24b-instruct:free",
    "qwen/qwen-2.5-7b-instruct:free",
    "open-r1/olympiccoder-32b:free",
    "deepseek/deepseek-r1-distill-llama-70b:free",
    "thudm/glm-z1-9b:free",
    "thudm/glm-z1-32b:free",
    "deepseek/deepseek-r1-distill-qwen-32b:free"
]

selected_models = st.multiselect("Choose models to compare:", models)

system_instruction = (
    "Modify the given Python code based on the user's instruction. Ensure that all necessary changes are made and provide appropriate comments on the modified lines. Return the entire modified code as plain text without any additional explanations or omissions."
)

openai_api_key = "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"
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=openai_api_key)

file_path = f"{cwd}/test.py"
with open(file_path, "r") as file:
    document = file.read()

with st.form(key='prompt_form', clear_on_submit=True):
    prompt = st.text_input(
        "What can I assist you with?",
        placeholder="Change the font color to....",
        disabled=not document,
    )
    submit_button = st.form_submit_button(label='Submit', use_container_width=True)
    if submit_button:
        messages = [
            {
                "role": "system",
                "content": system_instruction
            },
            {
                "role": "user",
                "content": f"Original Code: {document} \n\n---\n\n User Request:{prompt}"
            }
        ]

        csv_file = "model_response_times.csv"
        file_exists = os.path.isfile(csv_file)
        with open(csv_file, mode="a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            if not file_exists:
                writer.writerow(["model", "response_time_seconds"])
            for model in selected_models:
                start_time = time.time()
                stream = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    stream=True,
                )
                # Collect the full response
                response = "".join([chunk.choices[0].delta.content or "" for chunk in stream])
                elapsed = time.time() - start_time
                writer.writerow([model, f"{elapsed:.2f}"])
                # Write the response to test2.py (overwrites for each model, last one remains)
                with open(f"{cwd}/test2.py", "w") as test_file:
                    test_file.write(response)
        st.success("Response times and responses written to files.")