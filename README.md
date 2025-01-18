# ITSP Project

This project is designed to work with a Docker-based PostgreSQL database and a Python application. Follow the steps below to set up the environment and run the project.

---

## **Prerequisites**
Before you begin, ensure you have the following installed on your system:
- **Docker**: Required to run the shared database container.
- **Python 3.11**: Ensure Python 3.11 is installed and available in your PATH.
- **Git**: To clone the project repository.

---

## **Setup Instructions**

### **Step 1: Download and Load the Docker Database**
1. Download the Docker image tar file:
   [Download Here](https://drive.google.com/file/d/1d2-lh50M3GrngsGER_N4RGX8ovc2fELv/view?usp=sharing)
   
2. Load the Docker image:
   ```bash
   docker load < shared_postgis.tar
   ```

3. Verify the image is loaded:
   ```bash
   docker images
   ```

4. Run the container:
   ```bash
   docker run -d -p 4321:5432 --name itsp_database shared_postgis
   ```

5. Confirm the database is running:
   ```bash
   docker ps
   ```

---

### **Step 2: Clone the Project Repository**
Clone the GitHub repository to your local machine:
```bash
git clone https://github.com/denkmoritz/itsp-project.git
cd itsp-project
```

---

### **Step 3: Set Up a Virtual Environment**

#### **Mac/Linux Users**:
1. Create a virtual environment:
   ```bash
   python3.11 -m venv venv
   ```

2. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

#### **Windows Users**:
1. Create a virtual environment:
   ```powershell
   python3.11 -m venv venv
   ```

2. Activate the virtual environment:
   ```powershell
   .\venv\Scripts\activate
   ```

---

### **Step 4: Install Required Python Packages**
With the virtual environment activated, install the project dependencies:
```bash
pip3 install -r requirements.txt
```

---

### **Step 5: Run the Application**
Run the main application script:
```bash
python3 main.py
```

---

## **Notes**
- Ensure Docker is running before executing the application, as it relies on the PostgreSQL database.
- The database can be accessed locally on `localhost:4321` using a database client if needed.

---

## **Troubleshooting**
- **Database Connection Issues**:
  - Ensure the Docker container is running and properly mapped to port `4321`.
  - Check if your firewall or antivirus is blocking Docker.

- **Python Version Issues**:
  - Verify that Python 3.11 is being used:
    ```bash
    python3.11 --version
    ```

- **Dependency Installation Errors**:
  - Ensure the virtual environment is activated before running `pip3 install`.

---