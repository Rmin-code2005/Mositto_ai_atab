import cv2
from huggingface_hub import hf_hub_download
from ultralytics import YOLO
from supervision import Detections
from PIL import Image
from deepface import DeepFace
import numpy as np
import concurrent.futures
from time import time
import os
import tkinter as tk
from tkinter import ttk
#model_path = hf_hub_download(repo_id="arnabdhar/YOLOv8-Face-Detection", filename="model.pt")
model_path='../model.pt'
print(model_path)
model = YOLO(model_path)
faces=[]
path_of_students_dataset=os.getcwd()+'/students'
path_of_teachers_dataset=os.getcwd()+'/teachers'
students_images=os.listdir(path_of_students_dataset+'/images')
teachers_images=os.listdir(path_of_teachers_dataset+'/images')
manager_face_check_list=[]
manager_input_value = None
manager_selected_item = None
atab_stu={'present': []}
def check_faces(x):
    global faces
    for i in range(len(faces)):
        result=DeepFace.verify(img1_path=faces[i] , img2_path=x)
        if result['verified']:
            return 0
    faces.append(x)
    return 1
def face_detector(mode):
    from design import frame_start
    from tkinter import Label
    l = Label(master=frame_start)
    l.place(x=resizer(100, 'x'), y=resizer(500, 'y'))
    global faces
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
    faces = []

    cap=cv2.VideoCapture(0)
    if not cap.isOpened():
        print("eror")
    else:
       start=time();
       while(time()-start<=2 ):
            ret, frame = cap.read()
            if ret:
                frame=cv2.flip(frame,1)
                output=model(frame)
                result = Detections.from_ultralytics(output[0])
                alpha_frame=frame.copy()
                if len(result.xyxy) > 0:  # Assuming result.xyxy contains detected bounding boxes
                    face_crop = []
                    for i in result.xyxy:
                        x1, y1, x2, y2 = map(int, i)  # Extract bounding box coordinates
                        start_point = (x1, y1)
                        end_point = (x2, y2)

                        # Draw rectangle around the face
                        cv2.rectangle(alpha_frame, start_point, end_point, (255, 0, 0), 2)

                        # Crop the face region (without excessive padding)
                        face_crop.append(frame[y1-100:y2+100, x1-100:x2+100].copy())  # Crop directly within bounds

                        for crop in face_crop:
                            executor.submit(check_faces, crop)

                cv2.imshow("AI", alpha_frame)
            if cv2.getWindowProperty("AI", cv2.WND_PROP_VISIBLE) < 1:
                break  # Exit the loop when the window is closed


            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
       
       cap.release()
       cv2.destroyAllWindows()
       l.config(text='please wait . . .')  # Update text
       executor.shutdown(wait=True)
       l.destroy()

    print(len(faces))
    for idx, crop in enumerate(faces):
        if crop.size != 0:  
            cv2.imshow(f"Crop {idx}", crop)
            key = cv2.waitKey(0)  
            if key == ord('q'):   
                break
    cv2.destroyAllWindows()
    if mode=='students':
        student_atab()
    elif mode == 'teachers':
        teacher_atab()
    elif mode=='managers':
        sitch=manager_add_person()
        if sitch[0]:
            add_image(manager_selected_item,sitch[1])
#cv2.cvtColor(main_image, cv2.COLOR_BGR2RGB)
def manager_add_person():
    global manager_face_check_list
    if manager_selected_item=='students':
        manager_face_check_list=students_images
        manager_face_check_list = [
            cv2.cvtColor(cv2.imread(path_of_students_dataset + f'/images/{i}'),cv2.COLOR_BGR2RGB) if i.split(sep='.')[0] != manager_input_value else 'bug'
            for i in manager_face_check_list
        ]
    else:
        manager_face_check_list=teachers_images
        manager_face_check_list = [
            cv2.cvtColor(cv2.imread(path_of_teachers_dataset + f'/images/{i}'),cv2.COLOR_BGR2RGB) if i.split(sep='.')[0] != manager_input_value else 'bug'
            for i in manager_face_check_list
        ]
    if 'bug' in manager_face_check_list:
        return [0]
    else:
        for i in faces:
            for j in manager_face_check_list:
                result=DeepFace.verify(img1_path=i , img2_path=j)
                if result['verified']:
                    return [0]
            return[1,i]
            
def add_image(mode , sitch):
    global students_images
    global teachers_images
    if mode == 'students':
        cv2.imwrite(path_of_students_dataset + f'/images/{manager_input_value}.jpg', sitch)
        students_images=os.listdir(path_of_students_dataset+'/images')
    else:
        cv2.imwrite(path_of_teachers_dataset + f'/images/{manager_input_value}.jpg', sitch)
        teachers_images=os.listdir(path_of_teachers_dataset+'/images')
    

    
    

def student_atab():
    from design import frame_start
    from tkinter import ttk
    progress = ttk.Progressbar(master=frame_start, length=500, mode='determinate')
    progress.place(x=resizer(100, 'x'), y=resizer(550, 'y'))  # You can adjust (x, y) as needed

    total_tasks = len(faces) * len(students_images)
    current_task = 0
    for i in range(len(faces)):
        if faces[i] is None or faces[i].size == 0:
            print(f"Face {i} is invalid, skipping...")
            continue

        for j in students_images:
            main_image = cv2.imread(path_of_students_dataset + f'/images/{j}')
            if main_image is None:
                print(f"Failed to load image {j}, skipping...")
                continue
            main_image = cv2.cvtColor(main_image, cv2.COLOR_BGR2RGB)
            if faces[i] is not None and faces[i].size > 0:
                if len(faces[i].shape) == 3 and faces[i].shape[2] == 3:  # check it's color image
                    faces_rgb = cv2.cvtColor(faces[i], cv2.COLOR_BGR2RGB)
                else:
                    faces_rgb = faces[i]
            else:
                    print(f"Face {i} is invalid after loading, skipping...")
                    continue
            try:
                result = DeepFace.verify(main_image, faces[i])
                if result['verified']:
                    atab_stu['present'].append(j.split(sep='.')[0])
            except Exception as e:
                print(f"Error verifying face {i} and image {j}: {e}")
                continue  # Just skip this pair, don't restart!
            current_task += 1
            progress['value'] = (current_task / total_tasks) * 100  # Update as percent
            progress.update()


    progress.destroy() 

            
def teacher_atab():
    from design import frame_start
    from tkinter import ttk
    progress = ttk.Progressbar(master=frame_start, length=500, mode='determinate')
    progress.place(x=resizer(100, 'x'), y=resizer(550, 'y'))  # You can adjust (x, y) as needed

    total_tasks = len(faces) * len(teachers_images)
    current_task = 0
    for i in range(len(faces)):
        if faces[i] is None or faces[i].size == 0:
            print(f"Face {i} is invalid, skipping...")
            continue

        for j in teachers_images:
            main_image = cv2.imread(path_of_teachers_dataset + f'/images/{j}')
            if main_image is None:
                print(f"Failed to load image {j}, skipping...")
                continue
            main_image = cv2.cvtColor(main_image, cv2.COLOR_BGR2RGB)
            if faces[i] is not None and faces[i].size > 0:
                if len(faces[i].shape) == 3 and faces[i].shape[2] == 3:  # check it's color image
                    faces_rgb = cv2.cvtColor(faces[i], cv2.COLOR_BGR2RGB)
                else:
                    faces_rgb = faces[i]
            else:
                    print(f"Face {i} is invalid after loading, skipping...")
                    continue
            try:
                result = DeepFace.verify(main_image, faces[i])
                if result['verified']:
                    atab_stu['present'].append(j.split(sep='.')[0])
            except Exception as e:
                print(f"Error verifying face {i} and image {j}: {e}")
                continue  # Just skip this pair, don't restart!
            current_task += 1
            progress['value'] = (current_task / total_tasks) * 100  # Update as percent
            progress.update()

def student_menue():
    global faces
    global atab_stu
    atab_stu['present']=[]
    faces=[]
    face_detector('students')

def teacher_menu():
    global faces
    global atab_stu
    atab_stu['present']=[]
    faces=[]
    face_detector('teachers')

def manager_menu():
    import tkinter as tk
    from design import window

    def select_teachers():
        global manager_selected_item
        manager_selected_item = "teachers"

    def select_students():
        global manager_selected_item
        manager_selected_item = "students"

    def on_submit():
        global manager_input_value
        manager_input_value = entry.get()
        entry_window.destroy() 
        face_detector('managers') 

    entry_window = tk.Toplevel(window)
    entry_window.title("manager menu")
    entry_window.geometry("300x300")

    label = tk.Label(entry_window, text="Please enter your input:")
    label.pack(pady=5)

    entry = tk.Entry(entry_window, width=40)
    entry.pack(pady=5)
    entry.focus_set()

    # Button for "teachers"
    teachers_button = tk.Button(entry_window, text="Teachers", command=select_teachers, width=20)
    teachers_button.pack(pady=10)

    # Button for "students"
    students_button = tk.Button(entry_window, text="Students", command=select_students, width=20)
    students_button.pack(pady=10)

    # Submit button
    submit_button = tk.Button(entry_window, text="Submit", command=on_submit, width=20)
    submit_button.pack(pady=10)

    entry_window.wait_window()
def resizer(x,mode):
    from design import window_size
    if mode=='x':
        return (x*window_size['x'])/1000
    else:
        return (x*window_size['y'])/1000
def paths(x):
    return os.path.join(os.getcwd(),x)

