# AttendanceSystem
Below is a clean, structured, professional **README.md** suitable for GitHub.
It explains the project, the tech stack, features, setup instructions, and how everything works.

You can copy-paste it directly into your repository.



Face Recognition Attendance System

A Python-based biometric attendance tracking system using face recognition, OpenCV, and SQLite. The project captures real-time video, detects faces, recognizes registered students, and marks attendance automatically.

---

📌 Project Overview

This system replaces traditional manual attendance methods with a smart computer-vision-based solution.
Using a webcam feed, the program identifies students based on their facial features and logs their attendance with a timestamp into a local SQLite database.

It is designed to be fast, accurate, and easy to use in classrooms and laboratories.



✨ Key Features

* **Real-time face detection** using OpenCV
* **Face recognition** using encodings (HOG/CNN models)
* **Automatic attendance marking** with timestamps
* **SQLite database storage** (`attendance_system.db`)
* **Student registration and training support**
* **Modular Python architecture**
* **Lightweight—no internet connection required**


🧠 Technologies & Libraries Used

Programming Languages

* Python 3.x

Python Libraries

| Library              | Purpose                                            |
| -------------------- | -------------------------------------------------- |
| **OpenCV (cv2)**     | Captures video frames & detects faces in real time |
| **face_recognition** | Generates encodings & performs facial recognition  |
| **numpy**            | Handles image arrays & mathematical operations     |
| **sqlite3**          | Stores and retrieves attendance records            |
| **datetime**         | Generates timestamps for attendance logs           |
| **pickle**           | Saves and loads trained face encodings             |

### **Database**

* **SQLite** (lightweight, file-based database)
  File included: `attendance_system.db`

---

## **📁 Project Structure**

```
AttendanceSystem/
│
├── attendance_app.py         # Main application script
├── attendance_system.db      # SQLite database for attendance
├── README.md                 # Documentation file


🚀 How the System Works

1. Face Registration

* The system captures multiple images of each student.
* Face encodings are generated using `face_recognition`.
* Encodings are stored using `pickle` or as part of a dataset.

2. Recognition Phase

* Webcam stream processed using OpenCV.
* Faces detected using HOG/CNN models.
* Extracted encodings are compared with stored encodings.

3. Attendance Marking

When a match is found:

* Student name/ID is retrieved.
* A new attendance record is inserted into the SQLite database.
* Timestamp stored using Python’s `datetime`.

4. Data Storage

* SQLite database stores:

  * Student name or ID
  * Time of attendance
  * Date
  * Additional optional metadata

🗄️ Database Details

The SQLite file `attendance_system.db` stores:

| Field     | Description                |
| --------- | -------------------------- |
| id        | Auto-generated primary key |
| name      | Student name               |
| timestamp | Entry time                 |
| date      | Attendance date            |

You can inspect it using:

* DB Browser for SQLite
* VS Code SQLite extension

🛠️ Future Improvements

* Web-based dashboard for attendance viewing
* CSV export for attendance reports
* Admin panel for managing students
* Cloud database support (Firebase/MySQL)
* Mobile app version



📜 License

This project is open-source under the MIT License.


💬 Author

**Qutbuddin Mohammed**
GitHub: [https://github.com/Mohammedqutbuddin](https://github.com/Mohammedqutbuddin)

