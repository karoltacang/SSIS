# **Student Information System (v2)**

A student information system built using **Python**, **PyQt6**, and **MySQL**. This application allows users to manage **student**, **college**, and **program** data with features like **adding**, **editing**, **deleting**, **searching**, **sorting**, and **pagination**.

## **New in v2**
- 🔄 **Migrated from CSV to MySQL** for more reliable, persistent data storage
- 📄 **Pagination** support for smooth navigation through large tables

---

## **Features**

- View, add, edit, and delete students, colleges, and programs  
- Search and sort functionality  
- Pagination for large datasets  
- **Referential integrity**: dependent records (e.g., students) are retained, with foreign keys set to `NULL` when a college/program is deleted  

---

## **Installation**

### **1. Clone the Repository**
```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

### **2. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **3. Set Up MySQL Database**
- Create a database and run your schema script
- Update `functions/connection.py` with your database credentials

### **4. Run the Application**
```bash
python main.py
```

---

## **Project Structure**
```
/SSIS
│── main.py                   # Entry point
│── MainWindow.py             # Main UI logic
│── CustomTable.py            # Adds options menu
│
├── controllers/              # Controller logic for each entity
│   ├── college_controller.py
│   ├── program_controller.py
│   └── student_controller.py
│
├── functions/                # DB connection and operations
│   ├── connection.py         # MySQL database connection
│   ├── db_operations.py      # Insert, update, delete, search
│   └── load.py               # Loads data into the UI
│
├── ui/                       # Qt Designer UI files + converted Python modules
│   ├── mainWindow.ui
│   ├── editStudent.ui
│   ├── editCollege.ui
│   ├── editProgram.ui
│   ├── editStudent.py
│   ├── editCollege.py
│   ├── editProgram.py
│   └── mainWindow.py
│
├── requirements.txt          # Dependencies
├── README.md                 # This documentation
├── .gitignore
└── LICENSE
```

---

## **Usage**
1. **Run the app**: `python main.py`  
2. **Browse data** via tabs for students, colleges, and programs  
3. **Add/Edit/Delete**: Use table context menus  
4. **Search/Sort**: Use toolbar inputs  
5. **Pagination**: Navigate data pages easily with controls at the bottom

---

## **Future Improvements**
- Export/import to Excel or CSV
- UI improvements

---
