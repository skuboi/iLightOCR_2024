import streamlit as st
import pandas as pd
import time

st.write("Hello World")

# st.write() is Streamlit's "Swiss Army knife". You can pass almost anything to st.write(): text, data, Matplotlib figures, Altair charts, and more. 


#Widgets can also be accessed by key, if you choose to specify a string to use as the unique key for the widget:
st.text_input("Your name", key="name")
    # You can access the value at any point with:
st.session_state.name

#Use st.selectbox to choose from a series. You can write in the options you want, or pass through an array or data frame column.
df = pd.DataFrame({
    'first column': [1, 2, 3, 4],
    'second column': [10, 20, 30, 40]
    })

option = st.selectbox(
    'Which number do you like best?',
     df['first column'])

'You selected: ', option

#Progress Bars
# Add a placeholder
latest_iteration = st.empty()
bar = st.progress(0)

for i in range(100):
  # Update the progress bar with each iteration.
  latest_iteration.text(f'Iteration {i+1}')
  bar.progress(i + 1)
  time.sleep(0.1)

'...and now we\'re done!'

#Caching
#The basic idea behind caching is to store the results of expensive function calls and return the cached result when the same inputs occur again
#To cache a function in Streamlit, you need to apply a caching decorator to it.:
    #st.cache_data is the recommended way to cache computations that return data. Use st.cache_data when you use a function that returns a serializable data object (e.g. str, int, float, DataFrame, dict, list). It creates a new copy of the data at each function call, 
        #anything you can store in a database– python primitives, dataframes, API calls
    #st.cache_resource is the recommended way to cache global resources like ML models or database connections. Use st.cache_resource when your function returns unserializable objects that you don’t want to load multiple times. It returns the cached object itself, which is shared across all reruns and sessions without copying or duplication.
        #anything you can't store in a db

# Session State
# Session State provides a dictionary-like interface where you can save information that is preserved between script reruns
    # A session is a single instance of viewing an app. If you view an app from two different tabs in your browser, each tab will have its own session. So each viewer of an app will have a Session State tied to their specific view. Streamlit maintains this session as the user interacts with the app. 
# Use st.session_state with key or attribute notation to store and recall values.

# Static File Serving
#However, if you want a direct URL to an image or file you'll need to host it. This requires setting the correct configuration and placing your hosted files in a directory named static. 