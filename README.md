# Daily Expenses Sharing Application - Convin Assignment

This backend application allows users to manage their daily expenses and split them with others using different methods: equal, exact amounts, or percentages. The system provides a downloadable balance sheet summarizing the expenses.

## Steps to Run the Project

1. Clone the repository:
    ```bash
    git clone https://github.com/PankajJaisu/Convin-AI-Assignment.git
    ```

2. Navigate to the Project Folder:
    ```bash
    cd Convin-AI-Assigment
    ```

3. Ensure Python is installed by checking the version:
    ```bash
    python --version
    ```

4. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

5. Apply migrations to set up the database:
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```


6. Run the project:
    ```bash
    python manage.py runserver
    ```



### Postman API Documentation
```
https://documenter.getpostman.com/view/26432004/2sAXxY3oYP
```

## Additional Information

The application supports the following expense splitting methods:

- **Equal Split**: Expenses are divided equally among all participants.
- **Exact Amounts**: Users specify the exact amount each participant owes.
- **Percentage Split**: Users specify the percentage each participant owes, with the total percentage summing to 100%.


## .env Content

- **CLOUDNARY_API_SECRET**= ""
- **CLOUDNARY_API_KEY**=""
- **CLOUDNARY_CLOUD_NAME** =""



