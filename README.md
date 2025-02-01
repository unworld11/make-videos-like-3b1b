# make-videos-like-3b1b
using ai generated code to generate manim aninations in the style of 3 Blue 1 Brown.


## How It Works?

Well, The pipeline is simple,
we use llama3.3:70b to generate manim code in the style of 3B1B
this code is stored in a file and then rendered 
i ensure the errors if occur, can be easily pinpointed
rendering does take a little time so be patient
using streamlit as frontend because why not


## How to install
clone the repository
you will need to install manim or manimlib, i use ubuntu so using manimlib, change the system prompt as well
install all the required libraries - streamlit,groq
get a groq api key from groq playground - it's free

```
streamlit run app.py
```
