# ITSP Project

This project is designed to detect the color of Google Street View cars by using the Google Static Street View API.

---

## **Prerequisites**
Before you begin, ensure you have the following installed on your system:
- **Docker**: Required to run the shared database container.
- **Python 3.11**: Ensure Python 3.11 is installed and available in your PATH.
- **Git**: To clone the project repository.

---

## **Setup Instructions**

### **Step 1: Download and Load the Docker Database**
1. Pull the Docker image:
   ```bash
   docker pull moritzdenk/itsp-image:latest
   ```
   
2. Run the Docker container
   ```bash
   docker run -d \
    -e POSTGRES_USER=postgres \
    -e POSTGRES_PASSWORD=3004 \
    -e POSTGRES_DB=itsp \
    -p 24321:5432 \
    --name itsp-container \
    moritzdenk/itsp-image:latest

   ```

3. Start the container after reboot or shutdown
   ```bash
   docker start itsp-container
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
- The database can be accessed locally on `localhost:24321` using a database client if needed.

---

## **Troubleshooting**
- **Database Connection Issues**:
  - Ensure the Docker container is running and properly mapped to port `24321`.
  - Check if your firewall or antivirus is blocking Docker.

- **Python Version Issues**:
  - Verify that Python 3.11 is being used:
    ```bash
    python3.11 --version
    ```

- **Dependency Installation Errors**:
  - Ensure the virtual environment is activated before running `pip3 install`.

---