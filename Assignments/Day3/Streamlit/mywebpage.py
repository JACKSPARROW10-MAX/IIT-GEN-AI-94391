import streamlit as st
st.title("My Portfolio")

st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Go to", ["Home", "Projects", "Skills", "Contact"])

if page == "Home":
    st.header("Welcome to My Portfolio")
    st.write("This is the home page of my portfolio website. Here you can find information about me and my work.")
elif page == "Projects":
    st.header("Projects")
    st.write("Here are some of the projects I have worked on:")
    st.markdown("- Project 1: Description of project 1")
    st.markdown("- Project 2: Description of project 2")
    st.markdown("- Project 3: Description of project 3")
elif page == "Skills":
    st.header("Skills")
    st.write("Here are some of my skills:")
    st.markdown("- Skill 1")
    st.markdown("- Skill 2")
    st.markdown("- Skill 3")
elif page == "Contact":
    st.header("Contact Me")
    st.write("You can reach me at:")
    st.markdown("- Email:prathamesh@gmail.com")
    st.markdown("- Phone: +1234567890")
    st.markdown("- LinkedIn: [linkedin.com/in/prathamesh](https://linkedin.com/in/prathamesh)")