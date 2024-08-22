<p align="center">
  <img src="https://cdn-icons-png.flaticon.com/512/6295/6295417.png" width="100" />
</p>
<p align="center">
    <h1 align="center">E-MART</h1>
</p>
<p align="center">
    <em>HTTP error 401 for prompt `slogan`</em>
</p>
<p align="center">
	<img src="https://img.shields.io/github/license/techdev59/e-mart.git?style=flat&color=0080ff" alt="license">
	<img src="https://img.shields.io/github/last-commit/techdev59/e-mart.git?style=flat&logo=git&logoColor=white&color=0080ff" alt="last-commit">
	<img src="https://img.shields.io/github/languages/top/techdev59/e-mart.git?style=flat&color=0080ff" alt="repo-top-language">
	<img src="https://img.shields.io/github/languages/count/techdev59/e-mart.git?style=flat&color=0080ff" alt="repo-language-count">
<p>
<p align="center">
		<em>Developed with the software and tools below.</em>
</p>
<p align="center">
	<img src="https://img.shields.io/badge/Python-3776AB.svg?style=flat&logo=Python&logoColor=white" alt="Python">
	<img src="https://img.shields.io/badge/Django%20REST%20Framework-FF1709.svg?style=flat&logo=Django&logoColor=white" alt="Django REST Framework">
	<img src="https://img.shields.io/badge/GraphQL-E10098.svg?style=flat&logo=GraphQL&logoColor=white" alt="GraphQL">
	<img src="https://img.shields.io/badge/SQLite-003B57.svg?style=flat&logo=SQLite&logoColor=white" alt="SQLite">
</p>
<hr>

##  Quick Links

> - [ Overview](#-overview)
> - [ Features](#-features)
> - [ Repository Structure](#-repository-structure)
> - [ Getting Started](#-getting-started)
>   - [ Installation](#-installation)
>   - [ Running e-mart](#-running-e-mart)
> - [ Project Roadmap](#-project-roadmap)
> - [ Contributing](#-contributing)
> - [ License](#-license)
> - [ Acknowledgments](#-acknowledgments)

---

##  Overview


The **E-Mart Project** is an online marketplace platform developed using Django, GraphQL, and Django Rest Framework (DRF). This platform allows users to manage stores and list a wide range of products across various categories, manage their accounts, and track their orders. E-Mart is designed to offer a seamless and user-friendly  store management, integrating modern web technologies for optimal performance and scalability.

---

##  Features


- **User Authentication and Profiles**
  - Secure user registration and login with Django's built-in authentication system.
  - Profile management with options to update personal details and view order history.

- **Store Management**
  - Store management for verious locations
  - it has store manager, admin and location manger users

- **Product Management**
  - Comprehensive product catalog with detailed descriptions, images, and prices.
  - Categories and subcategories for easy product navigation.
  - Stock management to keep track of available inventory.

- **GraphQL API**
  - Efficient querying of data with GraphQL endpoints.
  - Flexible API for retrieving specific data required by frontend applications.

- **RESTful API with DRF**
  - Robust RESTful API for product and order management.
  - Authentication and permission handling for secure API access.

- **Admin Dashboard**
  - Django admin interface for managing products, stores, prices, locations, and other resources.
  - Custom admin actions for bulk operations.

---

##  Repository Structure

```sh
└── e-mart/
    ├── README.md
    ├── accounts
    │   ├── __init__.py
    │   ├── admin.py
    │   ├── apps.py
    │   ├── models.py
    │   ├── schemas
    │   │   └── user.py
    │   ├── tests.py
    │   └── views.py
    ├── emart
    │   ├── __init__.py
    │   ├── asgi.py
    │   ├── schema.py
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    ├── manage.py
    ├── products
    │   ├── __init__.py
    │   ├── admin.py
    │   ├── apps.py
    │   ├── models.py
    │   ├── schemas
    │   │   ├── categories.py
    │   │   ├── countries.py
    │   │   ├── departments.py
    │   │   ├── locations.py
    │   │   ├── price_list.py
    │   │   ├── price_list_details.py
    │   │   ├── products.py
    │   │   ├── states.py
    │   │   ├── store.py
    │   │   ├── unit_of_measure.py
    │   │   └── vendors.py
    │   ├── tests.py
    │   ├── utils.py
    │   └── views.py
    ├── requirements.txt
    └── utils
        ├── blob.py
        ├── funct.py
        └── graph.py
```

---

##  Getting Started

***Requirements***

Ensure you have the following dependencies installed on your system:

* **Python**: `version x.y.z`

###  Installation

1. Clone the salon-management repository:

```sh
git clone https://github.com/techdev59/e-mart.git
```

2. Change to the project directory:

```sh
cd e-mart
```

3. Create virtual environment:

```sh
python -m venv venv
```

3. Activate virtual environment:

for wundows
```sh
venv\Scripts\activate
```
for linux
```sh
Source venv/bin/activate
```


4. Install the dependencies:

```sh
pip install -r requirements.txt
```

###  Running salon-management

Use the following command to run salon-management:

```sh
python manage.py runserver
```


## To apply migrations 

first use this command

```sh
python manage.py makemigrations
```
then apply all the migrations
```sh
python manage.py migrate
```

---

##  Contributing

Contributions are welcome! Here are several ways you can contribute:

- **[Submit Pull Requests](https://github.com/techdev59/e-mart.git/blob/main/CONTRIBUTING.md)**: Review open PRs, and submit your own PRs.
- **[Join the Discussions](https://github.com/techdev59/e-mart.git/discussions)**: Share your insights, provide feedback, or ask questions.
- **[Report Issues](https://github.com/techdev59/e-mart.git/issues)**: Submit bugs found or log feature requests for E-mart.

<details closed>
    <summary>Contributing Guidelines</summary>

1. **Fork the Repository**: Start by forking the project repository to your GitHub account.
2. **Clone Locally**: Clone the forked repository to your local machine using a Git client.
   ```sh
   git clone https://github.com/techdev59/e-mart.git
   ```
3. **Create a New Branch**: Always work on a new branch, giving it a descriptive name.
   ```sh
   git checkout -b new-feature-x
   ```
4. **Make Your Changes**: Develop and test your changes locally.
5. **Commit Your Changes**: Commit with a clear message describing your updates.
   ```sh
   git commit -m 'Implemented new feature x.'
   ```
6. **Push to GitHub**: Push the changes to your forked repository.
   ```sh
   git push origin new-feature-x
   ```
7. **Submit a Pull Request**: Create a PR against the original project repository. Clearly describe the changes and their motivations.

Once your PR is reviewed and approved, it will be merged into the main branch.

</details>

---

##  License

This project is protected under the [SELECT-A-LICENSE](https://choosealicense.com/licenses) License. For more details, refer to the [LICENSE](https://choosealicense.com/licenses/) file.

---

##  Acknowledgments


We would like to express our gratitude to the following communities and individuals:

- **Django Community**: For providing a powerful, flexible, and well-documented web framework that makes developing complex applications manageable and enjoyable.
- **Django Rest Framework (DRF)**: For enabling the creation of robust and flexible RESTful APIs, making integration with frontend applications seamless.
- **Open Source Contributors**: To all the developers and maintainers of the open-source packages that this project relies on. Your contributions make the software ecosystem thrive.
- **Stack Overflow and Online Communities**: For offering a wealth of knowledge, troubleshooting tips, and support that make overcoming development challenges easier.
- **GraphQL**: A query language for your API, providing a more efficient, powerful, and flexible alternative to REST.
- **Contributors to This Project**: To everyone who has contributed their time and skills to improve this project, from developers to testers and designers. Your contributions are invaluable.

[**Return**](#-quick-links)

---
