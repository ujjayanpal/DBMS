import logging

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Log to console
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

# Also log to a file
file_handler = logging.FileHandler("mysql-A4A-errors.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


import tkinter as tk

import time
import mysql.connector

# Function to connect to MySQL database
def connect_to_mysql(config, attempts=3, delay=2):
    attempt = 1

    # Implement a reconnection routine
    while attempt <= attempts:
        try:
            return mysql.connector.connect(**config)
        
        except (mysql.connector.Error, IOError) as err: 
            if (attempts is attempt):
                # Attempts to reconnect failed; returning None
                logger.error("Failed to connect, exiting without a connection: %s", err)
                return None

            logger.error("Connection failed: %s. Retrying (%d/%d)...", err, attempt, attempts-1)

            # progressive reconnect delay
            time.sleep(delay ** attempt)
            attempt += 1

    return None


config = {
    "host": "localhost",
    "user": "root",
    "password": "*********",
    "database": "academic_insti",
}
cnx = connect_to_mysql(config)
cursor = cnx.cursor()


"""
Returns 0 if the course exists and is offered by the department
Returns 1 if the course does not exist
Returns 2 if the course exists but is not offered by the department
"""
def check_if_course_exists(courseID, deptID):
    check_course_existence = (
        "SELECT * "
        "FROM course "
        "WHERE courseId=%s"
    )
    cursor.execute(check_course_existence, (courseID,))
    rows = cursor.fetchall()
    if cursor.rowcount == 0:
        logger.error("Course with ID %s does not exist.", courseID)
        return 1
    # It's now guaranteed that the course exists, so exactly one row will be returned
    if rows[0][3] != deptID:
        logger.error("Course with ID %s is offered by department %s, not by department %s.", courseID, rows[0][3], deptID)
        return 2
    return 0





"""
Returns 0 if the teacher exists
Returns 1 if the teacher does not exist
"""
def check_if_teacher_exists(teacherID):
    check_teacher_existence = (
        "SELECT * "
        "FROM professor "
        "WHERE empId=%s"
    )
    cursor.execute(check_teacher_existence, (teacherID,))
    cursor.fetchall()
    if cursor.rowcount == 0:
        logger.error("Teacher with ID %s does not exist.", teacherID)
        return 1
    return 0





"""
Returns 0 if the input teaching tuple is a new one
Returns 1 if the same teaching tuple already exists
Returns 2 if the teaching tuple exists but in a different classroom
"""
def check_if_teaching_tuple_exists(courseID, teacherID, classroom):
    check_teaching_tuple_existence = (
        "SELECT * "
        "FROM teaching "
        "WHERE empId=%s AND courseId=%s AND sem='Even' AND year=2006"
    )
    cursor.execute(check_teaching_tuple_existence, (teacherID, courseID,))
    rows = cursor.fetchall()
    if cursor.rowcount > 0:
        if rows[0][4]==classroom:
            logger.error("Teaching tuple already exists.")
            return 1
        else:
            logger.error("Teaching tuple exists but with a different classroom.")
            return 2
    return 0





"""
Adds a new teaching tuple to the database, no questions asked
"""
def add_teaching_tuple(courseID, teacherID, classroom):
    add_teaching_tuple = (
        "INSERT INTO teaching "
        "VALUES (%s, %s, 'Even', 2006, %s)"
    )
    cursor.execute(add_teaching_tuple, (teacherID, courseID, classroom))
    cursor.fetchall()
    cnx.commit()





"""
Updates the classroom of an existing teaching tuple, no questions asked
"""
def update_teaching_tuple(courseID, teacherID, classroom):
    update_teaching_tuple = (
        "UPDATE teaching "
        "SET classroom=%s "
        "WHERE empId=%s AND courseId=%s AND sem='Even' AND year=2006"
    )
    cursor.execute(update_teaching_tuple, (classroom, teacherID, courseID))
    cursor.fetchall()
    cnx.commit()



"""
Returns 0 if the student exists
Returns 1 if the student does not exist
"""
def check_if_rollNo_exists(rollNo):
    check_rollNo_existence = (
        "SELECT * "
        "FROM student "
        "WHERE rollNo=%s"
    )
    cursor.execute(check_rollNo_existence, (rollNo,))
    cursor.fetchall()
    if cursor.rowcount == 0:
        logger.error("Student with roll number %s does not exist.", rollNo)
        return 1
    return 0





"""
Returns 0 if the course exists
Returns 1 if the course does not exist
"""
def check_if_courseID_exists(courseID):
    check_courseID_existence = (
        "SELECT * "
        "FROM course "
        "WHERE courseId=%s"
    )
    cursor.execute(check_courseID_existence, (courseID,))
    cursor.fetchall()
    if cursor.rowcount == 0:
        logger.error("Course with ID %s does not exist.", courseID)
        return 1
    return 0





"""
Returns 0 if the student is not already enrolled in the course
Returns 1 if the student is already enrolled in the course
"""
def check_if_student_enrolled(rollNo, courseID):
    check_enrollment = (
        "SELECT * "
        "FROM enrollment "
        "WHERE rollNo=%s AND courseId=%s AND sem='Even' AND year=2006"
    )
    cursor.execute(check_enrollment, (rollNo, courseID,))
    cursor.fetchall()
    if cursor.rowcount > 0:
        logger.error("Student with roll number %s is already enrolled in course with ID %s.", rollNo, courseID)
        return 1
    return 0





"""
Check if a student is eligible to enroll in a course, based on prerequisites
Returns 0 if the student is eligible
Returns 1 if the student is not eligible
"""
def check_prerequisites(rollNo, courseID):
    check_prerequisites = (
        "SELECT * "
        "FROM prerequisite "
        "WHERE courseId=%s"
    )
    cursor.execute(check_prerequisites, (courseID,))
    prereqs = cursor.fetchall()
    if cursor.rowcount == 0:
        return (0, "OK")
    for prereq in prereqs:
        check_enrollment = (
            "SELECT * "
            "FROM enrollment "
            "WHERE rollNo=%s AND courseId=%s AND year<2006"
        )
        cursor.execute(check_enrollment, (rollNo, prereq[0],))
        grades = cursor.fetchall()
        if cursor.rowcount == 0:
            logger.error("Student with roll number %s is not eligible to enroll in course with ID %s.", rollNo, courseID)
            return (1, f"Student has not taken the prereq course {prereq[0]}.")
        passed = False
        for grade in grades:
            if grade[4] not in ['U', 'I', 'W']:
                passed = True
                break
        if not passed:
            logger.error("Student with roll number %s is not eligible to enroll in course with ID %s.", rollNo, courseID)
            return (1, f"Student has not passed the prereq course {prereq[0]}.")
    return (0, "OK")





"""
Enroll a student in a course, no questions asked
"""
def enroll_student(rollNo, courseID):
    enroll = (
        "INSERT INTO enrollment "
        "VALUES (%s, %s, 'Even', 2006, NULL)"
    )
    cursor.execute(enroll, (rollNo, courseID,))
    cursor.fetchall()
    cnx.commit()





window = tk.Tk()
window.title("Academic Insti Database Upadate Sytem")

lbl_greeting = tk.Label(text="Welcome to the Academic Institute Database Update System.\nYou are adding details for AY 2006, Even Semester.\n", pady=20)
lbl_greeting.pack()




frm_A = tk.Frame(master=window, relief=tk.GROOVE, borderwidth=4, height=80, width=120)

lbl_heading_A = tk.Label(master=frm_A, text="Add new teaching tuple", fg="Blue", pady=15)
lbl_heading_A.grid(row=0, column=0, columnspan=2)

lbl_courseId_A = tk.Label(master=frm_A, text="Course ID:")
lbl_courseId_A.grid(row=1, column=0)

ent_courseId_A = tk.Entry(master=frm_A, width=10)
ent_courseId_A.grid(row=1, column=1)

lbl_deptId = tk.Label(master=frm_A, text="Department ID:")
lbl_deptId.grid(row=2, column=0)

ent_deptId = tk.Entry(master=frm_A, width=10)
ent_deptId.grid(row=2, column=1)

lbl_profId = tk.Label(master=frm_A, text="Professor ID:")
lbl_profId.grid(row=3, column=0)

ent_profId = tk.Entry(master=frm_A, width=10)
ent_profId.grid(row=3, column=1)

lbl_classroom = tk.Label(master=frm_A, text="Classroom:")
lbl_classroom.grid(row=4, column=0)

ent_classroom = tk.Entry(master=frm_A, width=10)
ent_classroom.grid(row=4, column=1)


def insert_button():
    courseID = ent_courseId_A.get()
    deptID = ent_deptId.get()
    teacherID = ent_profId.get()
    classroom = ent_classroom.get()

    flag1 = check_if_course_exists(courseID, deptID)
    if flag1 == 0:
        if check_if_teacher_exists(teacherID) == 0:
            flag2 = check_if_teaching_tuple_exists(courseID, teacherID, classroom)
            if flag2 == 0:
                add_teaching_tuple(courseID, teacherID, classroom)
                lbl_msg_A.config(text="Teaching tuple added successfully.", fg='green')
            elif flag2 == 1:
                lbl_msg_A.config(text="Teaching tuple already exists.", fg='red')
            elif flag2 == 2:
                update_teaching_tuple(courseID, teacherID, classroom)
                lbl_msg_A.config(text="Teaching tuple classroom updated successfully.", fg='green')
        else:
            lbl_msg_A.config(text=f"Teacher with ID {teacherID} does not exist.", fg='red')
    elif flag1 == 1:
        lbl_msg_A.config(text=f"Course with ID {courseID} does not exist.", fg='red')
    elif flag1 == 2:
        lbl_msg_A.config(text=f"Course with ID {courseID} is not offered by department {deptID}.", fg='red')


btn_insert = tk.Button(master=frm_A, text="Add", command=insert_button, height=1, width=6)
btn_insert.grid(row=5, column=0, columnspan=2)

lbl_msg_A = tk.Label(master=frm_A, text="Any warnings will appear here.", fg='#8c8c8b', height=2, width=50)
lbl_msg_A.grid(row=6, column=0, columnspan=2)





frm_B = tk.Frame(master=window, relief=tk.GROOVE, borderwidth=4, height=80, width=120)

lbl_heading_B = tk.Label(master=frm_B, text="Enroll a student in a course", fg="Blue", pady=15)
lbl_heading_B.grid(row=0, column=0, columnspan=2)

lbl_studentId = tk.Label(master=frm_B, text="Roll No:")
lbl_studentId.grid(row=1, column=0)

ent_studentId = tk.Entry(master=frm_B, width=10)
ent_studentId.grid(row=1, column=1)

lbl_courseId_B = tk.Label(master=frm_B, text="Course ID:")
lbl_courseId_B.grid(row=2, column=0)

ent_courseId_B = tk.Entry(master=frm_B, width=10)
ent_courseId_B.grid(row=2, column=1)

def enroll_button():
    rollNo = ent_studentId.get()
    courseID = ent_courseId_B.get()

    flag1 = check_if_rollNo_exists(rollNo)
    if flag1 == 0:
        flag2 = check_if_courseID_exists(courseID)
        if flag2 == 0:
            flag3 = check_if_student_enrolled(rollNo, courseID)
            if flag3 == 0:
                flag4, msg = check_prerequisites(rollNo, courseID)
                if flag4 == 0:
                    enroll_student(rollNo, courseID)
                    lbl_msg_B.config(text="Student enrolled successfully.", fg='green')
                else:
                    lbl_msg_B.config(text=f"{msg}", fg='red')
            else:
                lbl_msg_B.config(text="Student is already enrolled in this course.", fg='red')
        else:
            lbl_msg_B.config(text=f"Course with ID {courseID} does not exist.", fg='red')
    else:
        lbl_msg_B.config(text=f"Student with roll number {rollNo} does not exist.", fg='red')

btn_enroll = tk.Button(master=frm_B, text="Enroll", command=enroll_button, height=1, width=6)
btn_enroll.grid(row=3, column=0, columnspan=2)

lbl_msg_B = tk.Label(master=frm_B, text="Any warnings will appear here.", fg='#8c8c8b', height=2, width=50)
lbl_msg_B.grid(row=4, column=0, columnspan=2)




frm_A.pack(fill=tk.BOTH, expand=True)
frm_B.pack(fill=tk.BOTH, expand=True)



window.mainloop()


cursor.close()
cnx.close()