import re

import streamlit as st
from steam_profile import render_steam_interests
from github_profile import render_github
from spotify_profile import render_spotify
from PIL import Image



st.set_page_config(page_title="Jahzeel Lanz N. Mercado | Portfolio", page_icon="", layout="wide")

NAME = "Jahzeel Lanz N. Mercado"
image = Image.open("assets/profile.jpg")



st.caption("A WORK IN PROGRESS, JUST LIKE ME") 
intro, note = st.columns([2.4, 1], gap="large")
with intro:
    st.title("Hello, I’m Jaz.\n")
    st.caption("BS Computer Science · Third year · Philippines")
    st.write(
      
          "I'm a computer science student, currently in my third year, studying at Cebu Institute of Technology University. "
          "I have a strong interest in programming, and I'm always eager to learn and collaborate on new projects. "
          "This portfolio is a work in progress, showcasing my journey, selected work, skills, and interests. Feel free to explore" 
          "and connect with me!"
       
    )
   
with note:
    with st.container(border=True):
        st.image(image)
        st.subheader(NAME)
        st.caption("Open to learning & collaboration")

st.divider()
story, portfolio, skills, contact = st.tabs(["My story", "Github", "Skills & interests", "Say hello"])

with story:
    st.header("A little about my journey")
    st.write("Where I come from, what keeps me curious, and where I hope to go.")
    biography, journey = st.columns([1.4, 1], gap="large")
    with biography:
        st.subheader("From asking questions to building answers")
        st.write(
            "Growing up around computers pretty much decided my path early on. Watching my brother "
            "study Computer Science was the spark that made me follow in his footsteps, and getting into "
            "the thick of programming made me stick with it. It’s one thing to use tech, but another thing "
            "entirely to build things from scratch and figure out why stuff breaks until it finally works."
        )
        st.write(
            "Outside of staring at code, I keep things balanced by hitting the gym, playing video games, or "
            "just diving into whatever random hobby catches my attention. Big picture, I don't just want a "
            "typical tech job—my goal down the line is to use what I learn to build software that actually does "
            "some good."
        )
        
    with journey:
        with st.container(border=True):
            st.subheader("Things that happened along the way")
            for date, title, detail in [
                ("2024", "A new chapter", "Started my BS Computer Science journey at CIT University."),
                ("2025", "Exploring different fields", "I've been exploring various areas of computer science, including web development and game development."),
                ("NOW", "My third year life","Enjoying Automata and a life crisis"),
            ]:
                st.caption(date)
                st.markdown(f"**{title}**")
                st.write(detail)

with portfolio:
    render_github()

with skills:
    render_steam_interests()
    render_spotify()

with contact:
    st.header("Good things start with a hello.")
    form_column, aside = st.columns([1.5, 1], gap="large")
    with form_column:
        st.write("Have a project idea, a question, or feedback on my work? Leave a note.")
        with st.form("contact", clear_on_submit=False):
            sender = st.text_input("Your name", max_chars=100, placeholder="How should I call you?")
            email = st.text_input("Email", max_chars=254, placeholder="you@example.com")
            topic = st.selectbox("What’s on your mind?", ["General hello", "Project collaboration", "Portfolio feedback"])
            message = st.text_area("Your message", max_chars=2000, placeholder="Tell me a little about it…")
            submitted = st.form_submit_button("Submit ↗", type="primary")
        if submitted:
            st.session_state.pop("contact_confirmation", None)
            if not sender.strip() or not message.strip():
                st.error("Please enter your name and a message.")
            elif not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email.strip()):
                st.error("Please enter a valid email address.")
            elif not consent:
                st.warning("Please acknowledge that this is a demo form.")
            else:
                st.session_state["contact_confirmation"] = f"Thanks, {sender.strip()}! Your demo submission was received for “{topic}”. No message was sent."
        if "contact_confirmation" in st.session_state:
            st.success(st.session_state["contact_confirmation"])
    with aside, st.container(border=True):
        st.caption("LET’S CONNECT")
        st.subheader("Always happy to exchange ideas.")
        st.write("I’m interested in student collaborations, and opportunities to learn together.")
        st.divider()
        st.markdown("**Email**  \nmercadojahzeel@gmail.com")
        st.markdown("**Based in**  \nPhilippines")
      

st.divider()
st.caption(f"{NAME} · BS Computer Science  |  Made with Streamlit · Last updated: 2024-06-10")
