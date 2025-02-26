# **Student Information System**

A simple student information system built using Python, PyQt6, and CSV files. This application allows users to manage student, college, and program data with features like adding, editing, deleting, searching, and sorting.

## **Features**

Load student, college, and program data from CSV files
- Delete records dynamically
- Search functionality
- Sort functionality
- Data consistency (removes dependent data when a college is deleted)

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

### **3. Run the Application**
```bash
python main.py
```

---

## **Project Structure**
```
/my-project
│── main.py             # Entry point of the application
│── MainWindow.py       # Handles main UI logic
│── CustomTable.py      # Custom QTableWidget with options menu
│── functions/
│   ├── edit.py         # Handles editing logic
│   ├── delete.py       # Handles deletion logic
│   ├── load.py         # Loads CSV data into the UI
│   ├── csv_operations.py  # CSV handling functions
│── ui/                 # Qt Designer UI files
│   ├── mainWindow.ui
│   ├── editStudent.ui
│   ├── editCollege.ui
│   ├── editProgram.ui
│── data/               # CSV files (students, colleges, programs)
│── requirements.txt    # Required dependencies
│── README.md           # Project documentation
│── .gitignore          # Files to ignore in Git
```

---

## **Usage**
1. **Run the app**: Open the terminal and run `python main.py`.  
2. **Navigate through tabs**: The app has tabs for students, colleges, and programs.  
3. **Add/Edit/Delete records**: Use the options menu in the table.  
4. **Search and sort**: Use the search bar and combo sort bar to find records and sort data.

---

## **Future Improvements**
- Improve UI design
- Add search by fields
- Improve search function to handle big data
- Improve "Add" function to add data in any file regardless of current tab
- Improve "Edit" function to edit data dynamically
- Add export/import CSV functionality  
- Implement a database instead of CSV files  

---

