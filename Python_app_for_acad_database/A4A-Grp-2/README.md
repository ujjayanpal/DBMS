# DBMS (CS3700) Assignment 4A
Group No. 2

Group Members:
1. CS21B016 - BAPAN MANDAL
2. CS21B019 - AMAN BHOGE
3. CS21B006 - ANWAAY BADWAIK
4. CS21B084 - UJJAYAN PAL
5. CS21B044 - KUMAR KSHITIZ SINGH

Link to assignment: [Click here](https://drive.google.com/file/d/15WtgeLSVnkRqQ6u-G5x0iXibWtjdeafY/view?usp=sharing)

## Requirements

### Task 1 - Addition of Courses
- Assumption: Year - 2006, Semester - even
- Take input from user: courseID, DeptId, TeacherID, Classroom
- Check if the courseID, DeptId, TeacherID already exists: If not, then raise some warning to user
- Check if the input courseID is actually offered by the input DeptId: If not, then raise some warning to user
- TeacherID can be from other dept as well, so no need to check if TeacherID is from the input DeptId
- Update teaching table with the new input

### Task 2 - Enroll Students
- Take input from user: rollNo, courseID
- Check if the rollNo, courseID already exists: If not, then raise some warning to user
- Verify if the student has passed in the prerequisites of the course that he/she wants to enroll in.


## How to run the code

The following steps assume you already have a MySQL server installed and running on your local machine, which has an Ubuntu OS.

### Step 1: Install the required packages
```bash
pip install mysql-connector-python
sudo apt-get install python3-tk
```
You must download and load the academic_insti MySQL file (provided in moodle) in your MySQL server.
Now, you need to login as the root user to MySQL. For this, change the password in the `final_code.py` (or in the 4th cell of the `Assignment-4A.ipynb` notebook) file to your MySQL root password.

### Step 2: Run the code
You can either run the code from the Jupyter notebook or from the python file. To run the code from the python file, run the following command:
```bash
python3 final_code.py
```
This will trigger a GUI window where you can input the required details for the tasks. It will give you proper warnings if you enter any wrong details and will update the database accordingly.
