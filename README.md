# Online Phenotyping Platform  

## Project Overview  
Our increasing usage of smartphones and the Internet (particularly social media/networking) over the last couple of decades has increased what can be termed our ‘digital footprint’ or our ‘digital exhaust’. An individual’s digital footprint is basically the data records they create resulting from their interactions with the Internet and personal digital devices such as smartphones. The fact that an individual’s digital footprint could be used to infer their behaviours, preferences and mental states opens the possibility of using such a process to gain insights into their mental health, insights of clinical value that could be used to anticipate mental ill-health and also inform treatment. At the intersection of the computing, data and behavioural sciences, this process of learning about an individual’s psychology from their digital footprint has been termed ‘digital phenotyping’.including members from the School of Computing and Information Systems at The University of Melbourne. Data collected by AWARE is stored in a MySQL database and information that it tracks includes GPS/geolocation, accelerometer, application usage, amount and daily periods of smartphone use, call and SMS quantities, and screen touch patterns.

The platform developed in this project will be used in digital phenotyping research being conducted at The University of Melbourne (for an example see  [https://cis.unimelb.edu.au/hci/projects/personal-sensing/](https://cis.unimelb.edu.au/hci/projects/personal-sensing/)). This work could also lead to such a platform being used one day by psychologists/psychiatrists in a clinical setting, so that clinicians can gain patient insights that inform their treatment.


## People  
***Client***  
**Simon D'Alfonso**  
Research Fellow, School of Computing and Information Systems, Melbourne School of Engineering, University of Melbourne

***Supervisor***  
**Wei Wang**  
Experienced developer in both China and Australia, she has supervised student project since 2021, and is in the later stages of completing her PhD.

***Student Developers***  
**Mengran Hou**  
Product Owner menhou@student.unimelb.edu.au  
**Liping Meng**  
Scrum Master lipingm@student.unimelb.edu.au  
**Ziqi Wang**  
Deployment Lead wangzw10@student.unimelb.edu.au  
**Yuning Qi**  
Development Environment Lead yuningq1@student.unimelb.edu.au  
**Xiaojiang Zheng**  
Architecture Lead xiaojiangz@student.unimelb.edu.au  
**Wenyao Wang**  
Quality Assurance Lead WENYAOW1@student.unimelb.edu.au  




## How to Set Up the Environment
1. Install python with minimum version 3.8  
3. Navigate to `/SenPsi_Koalas` directory  
2. Create virtual environment directory with  
    `python -m venv venv`  
3. Start virtual environment  
    Mac: `source venv/bin/activate`  
    Windows: `venv\Scripts\Activate`  
4. Set GITHUB_TOKEN environment variable
    ```
    $ export GITHUB_TOKEN="replace with token"  # for Linux, Mac      !!! Don't share it or save it on GitHub !!!
    $ set GITHUB_TOKEN="replace with token"     # Windows CMD         !!! Don't share it or save it on GitHub !!!
    $ $env:GITHUB_TOKEN = "replace with token"  # Windows powerShell  !!! Don't share it or save it on GitHub !!!
    ```
5. Install admin_volt_pro with pip  
    Mac: `pip install git+https://${GITHUB_TOKEN}@github.com/app-generator/priv-django-admin-volt-pro.git`
    Windows: `pip install git+https://%GITHUB_TOKEN%@github.com/app-generator/priv-django-admin-volt-pro.git`
6. Install requirement packages  
    `pip install -r requirements.txt`  
7. Create a .env file in `/SenPsi_Koalas/.env`, edit the file with  
    ```
    DB_ENGINE="mysql"
    DB_NAME="aware database name"
    DB_USERNAME="database admin name"
    DB_PASS="admin password"
    DB_HOST="127.0.0.1"
    DB_PORT=3306
    RENDER_EXTERNAL_HOSTNAME="koala.senpsi.net"
    ```
8. Deploy
    1. `git clone https://github.com/SWEN90014-2023/PP-Platypus.git`  
    2. python3.10 or above  
    3. `export GITHUB_TOKEN=secret_key`  
    5. create virtual environment `python -m venv venv`  
    4. activate virtual environment  `source venv/bin/activate`  
    5. `pip install -r requirements.txt`  
    6. Setup MySQL Database  
    7. Setup .env configuration  
    8. `ifconfig` find out local `ip_address`
    9. use screen to create a shell session `screen -S senpsi`  
        * `screen -ls` show all sessions  
        * `screen -r [session]` reattach to a session  
        * `screen -R` reattach when possible, otherwise starts a new session  
        * `screen -S [sockname]` create a session with name=sockname  
    9. `venv/bin/python3 manage.py runserver <ip_address>:80`  
    

## Directory Structure Overview
1. `/SenPsi_Koalas/home/templates/components`: Contains public component templates, such as dashboard and reusable tables.  
2. `/SenPsi_Koalas/home/templates/layout`: Contains layout templates.  
3. `/SenPsi_Koalas/home/templates/views`: Contains page templates, edit index.html inside each directory.  
4. `/SenPsi_Koalas/home/urls.py` and `/SenPsi_Koalas/home/views.py`: Page routing configuration.  
5. For running the program, please refer to the [Readme](https://github.com/bingx1/digital-phenotyping/blob/main/README.md) file from SenPsi sample project.  
