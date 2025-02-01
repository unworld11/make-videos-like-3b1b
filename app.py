import streamlit as st
import subprocess
from groq import Groq

def better_clean_generated_code(code: str) -> str:
    """
    Cleans the generated code by:
    1. Removing Markdown fences like ``` and any lines that look like disclaimers.
    2. Locating the first line that starts with common Python code syntax to trim leading text.
    3. Returning only the valid Python code segment.
    """
    lines = code.splitlines()

    cleaned_lines = []
    for line in lines:
        lower_stripped = line.strip().lower()
        if lower_stripped.startswith("```"):
            continue
        if any(
            phrase in lower_stripped
            for phrase in ["sure", "certainly", "here is", "here's", "assistant"]
        ):
            continue
        cleaned_lines.append(line)

    code_keywords = ("from ", "import ", "class ", "def ")
    first_code_line = 0
    for idx, line in enumerate(cleaned_lines):
        # Check if the line starts with a common Python code token
        if any(line.lstrip().startswith(k) for k in code_keywords):
            first_code_line = idx
            break

    return "\n".join(cleaned_lines[first_code_line:])


def get_scene_from_groq(prompt: str) -> str:
    """
    Uses the Groq SDK to stream-generate Manim scene code based on the given prompt.
    
    The generated code will explain the provided topic in the style of 3Blue1Brown,
    with multiple Scenes as if it were a cohesive video.
    The code should be fully self-contained and executable with Manim.
    """
    # TODO - add groq api key
    client = Groq(api_key="[key]")

    messages = [
        {
            "role": "user",
            "content": (
                "Generate an extensive ManimLib code in the style of 3Blue1Brown that explains the "
                "following topic as if it were a multi-Scene video: \n\n"
                f"{prompt}\n\n"
                "The code must be fully self-contained and executable with Manim, and it should "
                "include multiple Scenes or classes to illustrate the concept step by step. "
                "Please output only valid Python code using ' from manimlib.imports import *' (no markdown fences, no disclaimers)."
            )
        }
    ]
    
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=1,
        max_completion_tokens=32768,
        top_p=1,
        stream=True,
        stop=None,
    )
    
    scene_code = ""
    for chunk in completion:
        scene_code += chunk.choices[0].delta.content or ""
    return scene_code

# ------------------ Streamlit UI Setup ------------------
st.title("AI Video Generator: 3Blue1Brown Style")
st.write("Enter a topic or concept to explain (as if you're creating a multi-Scene Manim video):")

# Multi-line text area for user input
prompt = st.text_area("Topic/Concept", height=150)

if st.button("Generate Video"):
    if not prompt.strip():
        st.error("Please enter a topic or description to explain.")
    else:
        st.info("Generating scene code using the Groq API...")
        
        try:
            raw_scene_code = get_scene_from_groq(prompt)
            # Clean the generated code to remove any extraneous non-code text
            scene_code = better_clean_generated_code(raw_scene_code)
            st.success("Scene code generated successfully!")
        except Exception as e:
            st.error(f"Error generating scene code: {e}")
            st.stop()

        # Optionally display the generated scene code for review
        with st.expander("View Generated Scene Code"):
            st.code(scene_code, language="python")
        
        # Save the generated code to a file that Manim can execute
        filename = "generated_scene.py"
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(scene_code)
            st.success("Scene code written to file successfully!")
        except Exception as e:
            st.error(f"Error writing the scene file: {e}")
            st.stop()

        st.info("Rendering video with Manim (this may take a moment)...")
        
        # Assume that the generated code defines a scene class named "GeneratedScene".
        # If the class name(s) differ, you can change them here or run multiple scenes.
        manim_command = ["manim", "-pql", filename, "GeneratedScene"]
        try:
            # Capture both stdout and stderr for detailed logging
            result = subprocess.run(
                manim_command,
                check=True,
                capture_output=True,
                text=True
            )
            st.success("Video rendered successfully!")
            st.text("Manim output:\n" + result.stdout)
        except subprocess.CalledProcessError as e:
            st.error("Error during video rendering:")
            st.text("STDOUT:\n" + e.stdout)
            st.text("STDERR:\n" + e.stderr)
