
# Containerize a Flask + MySQL Application

## Objective

In this project, we containerize a simple two-tier Flask + MySQL application.

During the lab, we intentionally start with an incorrect configuration to understand why containers cannot communicate by default. We then fix the issue using a Docker network.

---

## Project Flow

```text
Clone Project
      │
      ▼
Run MySQL Container
      │
      ▼
Build Flask Image
      │
      ▼
Run Flask Container (Without Docker Network)
      │
      ▼
Database Connection Failed ❌
      │
      ▼
Analyze Docker Logs
      │
      ▼
Create Docker Network
      │
      ▼
Run Both Containers on Same Network
      │
      ▼
Application Works Successfully ✅
```

---

# Step 1: Clone Repository

```bash
git clone <repository-url>
cd <repository-name>
```

---

# Step 2: Run MySQL Container

```bash
docker run -d \
  --name mysql-dev \
  -e MYSQL_ROOT_PASSWORD=mysqlpassword \
  -e MYSQL_DATABASE=web_db \
  -p 3306:3306 \
  mysql:8.4
```

---

# Step 3: Configure Environment Variables

```bash
cp .env.example .env
```

Update `.env`

```env
DB_HOST=127.0.0.1
```

to

```env
DB_HOST=mysql-dev
```

> `mysql-dev` is the MySQL container name.

---

# Step 4: Build the Flask Image

```bash
docker build -t flask-mysql-demo .
```

---

# Step 5: Run Flask Container (Expected Failure)

```bash
docker run -d \
  --name flask-app-dev \
  --env-file .env \
  -p 5000:5000 \
  flask-mysql-demo
```

Open

```
http://localhost:5000
```

Submit any text.

The application cannot connect to MySQL because both containers are running on different networks.

---

# Step 6: Troubleshooting

View container logs.

```bash
docker logs flask-app-dev
```

You will see a database connection error.

---

# Step 7: Remove Existing Containers

```bash
docker stop flask-app-dev mysql-dev

docker rm flask-app-dev mysql-dev
```

---

# Step 8: Create Docker Network

```bash
docker network create flask-network
```

---

# Step 9: Run MySQL on Docker Network

```bash
docker run -d \
  --name mysql-dev \
  --network flask-network \
  -e MYSQL_ROOT_PASSWORD=mysqlpassword \
  -e MYSQL_DATABASE=web_db \
  -p 3306:3306 \
  mysql:8.4
```

---

# Step 10: Run Flask on Docker Network

```bash
docker run -d \
  --name flask-app-dev \
  --network flask-network \
  --env-file .env \
  -p 5000:5000 \
  flask-mysql-demo
```

Open

```
http://localhost:5000
```

Submit any text.

The application should now connect successfully to MySQL.

---

# Step 11: Verify Data Inside MySQL

Enter the MySQL container.

```bash
docker exec -it mysql-dev bash
```

Connect to MySQL.

```bash
mysql -u root -p
```

Enter the root password.

---

## Verify Database

Show databases.

```sql
SHOW DATABASES;
```

Select the database.

```sql
USE web_db;
```

Show tables.

```sql
SHOW TABLES;
```

Display stored records.

```sql
SELECT * FROM users;
```

Describe the table.

```sql
DESCRIBE users;
```

Exit MySQL.

```sql
exit;
```

Exit the container.

```bash
exit
```

---

# Key Learning

- Build a Docker image.
- Run multiple containers.
- Configure environment variables.
- Troubleshoot container communication.
- Create a custom Docker network.
- Enable communication between containers using Docker DNS.
- Verify application data inside the MySQL database.
````

### One small improvement

Instead of saying:

> **"Submit error"**

Write:

> **Expected Result: Database connection failed.**

This sounds much more professional and tells the reader that the failure is intentional and part of the learning process. I actually like this approach because it teaches **how to troubleshoot**, not just how to follow commands. That's a skill companies value.
