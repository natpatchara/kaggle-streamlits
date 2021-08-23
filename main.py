import streamlit as st
import os
import pydicom
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib.animation as animation
import streamlit.components.v1 as components

PAGE_CONFIG = {"page_title":"DICOM-imageviewer","page_icon":":smiley:","layout":"centered"}
st.set_page_config(**PAGE_CONFIG)
path = "dicom-flair/dicom-flair"
train_label = pd.read_csv("data.csv")

def show_animation(images, figsize = (6,6), fps = 5):
    fig = plt.figure(figsize = figsize)
    plt.axis("off")
    im = plt.imshow(images[0], cmap = "gray", vmin=0., vmax=255.)
    
    def animate_func(i):
        im.set_array(images[i])
        return [im]
    
    return animation.FuncAnimation(fig, animate_func, frames=len(images), interval = 1000//fps)

def load_slice(path):
    #load dicom file
    data = pydicom.read_file(path)
    #read pixel value
    data = data.pixel_array
    
    #normalize pixel value to (0,255)
    data = data - np.min(data)
    if(np.max(data) != 0):
        data = data / np.max(data)
    data = (data * 255).astype(np.uint8)
    
    return data

def load_image(patient_id, path):
    
    patient_folder = os.path.join(path,patient_id)
    datas = []
    
    for dirname,_,filenames in os.walk(patient_folder):
        for filename in sorted(filenames,key=lambda x: int(x[:-4].split("-")[-1])):
            slice_path = os.path.join(dirname,filename)
            data = load_slice(slice_path)
            datas.append(data)
            
    return datas

def main():
    st.title("DICOM-imageviewer")

    with st.form(key='Model_form') :
        id = st.selectbox("Select pateint ID:", os.listdir(path))
        submitted = st.form_submit_button('Submit')
        

    if (submitted):
        datas = load_image(id,path)
        label = train_label[train_label["FolderID"] == id]
        ani = show_animation(datas)
        submitted = False
        
    components.html(ani.to_jshtml(), height=1000)
    show_label = st.checkbox("Show label")
    if(show_label):
      st.write("Label:", label["Diagnosis"].values[0].split("-")[0])    

if __name__ == '__main__':
	main()