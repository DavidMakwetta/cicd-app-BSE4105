# cicd-app

## Contents

1. [Introduction](#introduction)
2. [Repository structure](#repository-structure)
3. [What the files do](#what-the-files-do)
4. [How to run it](#how-to-run-it)
5. [The CI/CD pipeline](#the-cicd-pipeline)
6. [Test guide (test2026)](#test-guide-test2026)

---

## Introduction
This session will demonstrate the use of GitLab CI/CD to build and deploy a simple web application. The application is a simple flask app that requires a database for operation. The CI/CD pipeline will build the application, run tests, and deploy the application to our VM server.


The app is a small Flask web service backed by PostgreSQL. It has two routes:

| Route | What it returns |
|---|---|
| `/` | A "Hello, World!" message |
| `/users` | The rows of the `users` table, as JSON |

---

## Repository structure

```text
cicd-app/
├── app/
│   ├── app.py              # Flask application
│   ├── test_app.py         # pytest tests
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # builds the app image
├── db_init/
│   └── init.sql            # creates and fills the users table
├── docker-compose.yml      # runs the app and the database together
├── .gitlab-ci.yml          # GitLab CI/CD pipeline (build, test, deploy)
└── README.md
```

---

## What the files do

### `app/app.py`
The Flask application. It reads the database settings from environment variables (`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_HOST`, `POSTGRES_PORT`), connects to PostgreSQL with `psycopg2`, and serves the `/` and `/users` routes on port 5000.

### `app/test_app.py`
pytest tests that check the `/` route, the `/users` route, and that the app can connect to the database.

### `app/requirements.txt`
The Python packages the app needs: Flask, Werkzeug, psycopg2-binary, pytest and pytest-flask.

### `app/Dockerfile`
Builds the app image from `python:3.9-slim`, installs the requirements, copies the code, exposes port 5000 and starts `app.py`.

### `db_init/init.sql`
Creates the `users` table (`id`, `name`, `email`) and inserts sample users. PostgreSQL runs it automatically the first time the database container starts.

### `docker-compose.yml`
Runs two services together:

- **`buyinza-web`**: the Flask app, built from `./app`, on host port `30134`.
- **`buyinza-db`**: PostgreSQL 15 on host port `31134`, with its data in `./db_data` and `db_init/` loaded on first start.

> Change both host port numbers to the ones your class gave you.

### `.gitlab-ci.yml`
The GitLab CI/CD pipeline. See [The CI/CD pipeline](#the-cicd-pipeline) below.

---

## How to run it

You need Docker with Docker Compose.

```bash
# start the app and the database
docker compose up -d --build

# check that it is running
curl localhost:30134/
curl localhost:30134/users

# stop everything
docker compose down
```

Replace `30134` with your own port if you changed it in `docker-compose.yml`.

To run the tests, the database must be running. Then:

```bash
docker compose exec buyinza-web pytest
```

---

## The CI/CD pipeline

The pipeline runs on pushes to `main` and has three stages:

| Stage | What it does |
|---|---|
| **build** | Builds the image from `./app` and pushes it to the GitLab container registry as `cicd-app:latest`. |
| **test** | Starts a PostgreSQL container, loads `db_init/init.sql`, starts the app linked to it, runs `pytest` inside the app container, then cleans up. |
| **deploy** | Connects to the server over SSH, pulls the latest image and runs `docker-compose up -d --build` in `$DEPLOY_HOME/microservices/cicd-app`. |

The deploy job needs these CI/CD variables (**Settings → CI/CD → Variables**):

| Variable | Meaning |
|---|---|
| `SSH_PRIVATE_KEY` | Private key used to log in to the server |
| `DEPLOY_HOST` | Server address |
| `DEPLOY_USER` | User to log in as |
| `DEPLOY_HOME` | Home folder on the server that contains `microservices/cicd-app` |

---

## Test guide (test2026)

Step-by-step notes for the 2026 test, kept as originally written.

> **Placeholders:** replace `<username>` with your username and `<PORT>` with the port shown in `INFO.txt`.

### Log in

```bash
ssh <username>@ldapgit.cranecloud.io
```

### Part A: Linux shell tasks

```bash
mkdir ~/test2026
chmod 700 ~/test2026
ls -ld ~/test2026          # should show drwx------
```

```bash
cp /opt/test2026/<username>/bundle.zip ~/test2026/
cd ~/test2026
unzip bundle.zip
ls -R
cat INFO.txt               # shows your port and project URL
```

```bash
cat count_lines.sh
./count_lines.sh data/access.log
```

edit `answers.sh` (use `nano answers.sh` or `vim answers.sh`)

Log fields: `$1` is the IP and `$9` is the status code. In `services.csv`, use `-F,` with `$1` as the name and `$6` as the status.

```bash
a3() {
  awk '$9 ~ /^5[0-9][0-9]$/ {c++} END {print c+0}' data/access.log
}
a4() {
  awk '{print $1}' data/access.log | sort | uniq -c | sort -rn | head -1 | awk '{print $2}'
}
a5() {
  tail -n +2 data/services.csv | awk -F, '$6=="down" {print $1}' | sort
}
a6() {
  awk '$9==404 {print $1}' data/access.log | sort -u | wc -l
}
```

Test them:

```bash
cat answers.sh             # see how the functions are called
bash answers.sh
```

#### `check_service.sh` (`nano check_service.sh`)

```bash
#!/bin/bash
if [ $# -lt 1 ]; then
  echo "Usage: $0 service_name" >&2
  exit 1
fi
name="$1"
result=$(awk -F, -v n="$name" 'NR>1 && $1==n {print $1 " is " $6 " on port " $3; exit}' data/services.csv)
if [ -z "$result" ]; then
  echo "$name not found" >&2
  exit 2
fi
echo "$result"
exit 0
```

```bash
chmod +x check_service.sh
./check_service.sh billing; echo $?     # prints "billing is up on port 8412", then 0
./check_service.sh; echo $?             # usage on stderr, then 1
./check_service.sh nosuch; echo $?      # "nosuch not found" on stderr, then 2
./check_service.sh cache                # must not match cache-proxy
```

---

### Part B: Git and GitLab

#### Git identity

```bash
git config --global user.name "Firstname Lastname"
git config --global user.email "your@email"
```

```bash
man ssh-keygen
ssh-keygen -t ed25519 -C "<username>-test2026"
cat ~/.ssh/id_ed25519.pub
```

Copy the output into GitLab under **Profile → Preferences → SSH Keys → Add key**, then check it:

```bash
ssh -T git@gitlab.cranecloud.io
```

#### B2: clone over SSH

```bash
cd ~/test2026
git clone git@gitlab.cranecloud.io:bse4105-test-2026/test-<username>.git repo
cd repo
git branch -a
```

#### B3: create the test-2026 branch

```bash
git checkout main
git checkout -b test-2026
git push -u origin test-2026
```

#### B4: merge hotfix and resolve the conflict

```bash
git merge origin/hotfix        # or: git merge hotfix
git status
nano config/settings.ini       # keep log_level = warning and ttl = 300, delete the <<<<<<< ======= >>>>>>> lines
grep -n '<<<<\|====\|>>>>' config/settings.ini    # should print nothing
git add config/settings.ini
git commit -m "Merge hotfix into test-2026"
git push
```

#### B5: STUDENT.md with a multi-line commit message

```bash
cd ~/test2026/repo
printf "Full name: Your Full Name\nStudent number: 0000000\n" > STUDENT.md
git add STUDENT.md
git commit -m "Add STUDENT.md" -m "Adds my full name and student number for the 2026 test."
git push
git log -1
```

#### B6: merge request (GitLab web UI, not a command)

1. Open your project, go to **Merge requests → New merge request**.
2. Set source `test-2026` and target `main`.
3. Title: `Test 2026 – <username>` (with the en dash).
4. Write a description of your changes, then click **Create merge request**.

> **Do not merge it, and do not delete any branch.**

---

### Part C: Docker and CI/CD

#### C1: fix the Dockerfile (typical correct form; compare with yours)

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

Check that `app.py` ends with `app.run(host="0.0.0.0", port=5000)`. Test it locally:

```bash
cd ~/test2026/repo
docker build -t test-local .
docker run -d --name tmp-test -p <PORT>:5000 test-local
curl localhost:<PORT>
docker rm -f tmp-test
```

#### C2: /health route and test

In `app.py`:

```python
@app.route("/health")
def health():
    return jsonify({"status": "ok", "user": "<username>"})
```

Check that `jsonify` is imported: `from flask import Flask, jsonify`.

In `test_app.py` (match the style of the existing tests):

```python
def test_health():
    client = app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"
```

Run it:

```bash
pip install -r requirements.txt pytest
pytest
```

#### C3–C5: .gitlab-ci.yml (a template; keep your existing DOCKER_HOST line and tags)

First create the variable in GitLab under **Settings → CI/CD → Variables → Add variable**, with key `APP_PORT` and value your port.

```yaml
stages:
  - build
  - test
  - deploy
variables:
  IMAGE_TAG: $CI_COMMIT_SHORT_SHA
  # keep the DOCKER_HOST line that was provided
build:
  stage: build
  tags: [test2026]
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker build -t $CI_REGISTRY_IMAGE:$IMAGE_TAG .
    - docker push $CI_REGISTRY_IMAGE:$IMAGE_TAG
test:
  stage: test
  tags: [test2026]
  script:
    - docker run --rm $CI_REGISTRY_IMAGE:$IMAGE_TAG sh -c "pip install pytest && pytest"
deploy:
  stage: deploy
  tags: [test2026]
  rules:
    - if: $CI_COMMIT_BRANCH == "test-2026"
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker pull $CI_REGISTRY_IMAGE:$IMAGE_TAG
    - docker rm -f $CI_PROJECT_NAME || true
    - docker run -d --name $CI_PROJECT_NAME -p $APP_PORT:5000 $CI_REGISTRY_IMAGE:$IMAGE_TAG
```

Commit, push and verify:

```bash
git add -A
git commit -m "Fix Dockerfile and CI, add /health and test"
git push
```

Then watch the pipeline under **Build → Pipelines**, and on ldapgit run:

```bash
docker ps
curl localhost:<PORT>/health
```

#### C6: show that a failing test blocks deploy

```bash
# Break the test, e.g. change 200 to 500 in test_health
nano test_app.py
git add -A
git commit -m "Break test on purpose"
git push
# In GitLab: test job fails, deploy job does not run
# Fix it
nano test_app.py
git add -A
git commit -m "Fix test"
git push
# In GitLab: whole pipeline passes
docker ps
curl localhost:<PORT>/health
```

Leave both pipelines in the history, and make sure the container is still running at 6:30 pm.

---

### Part D: quick answers

| Topic | Command or answer |
|---|---|
| Owner-only access | `chmod 700 test2026` |
| Both streams to a file | `> out.txt 2>&1` |
| Last exit status | `echo $?` (2 means the script failed with status 2) |
| Push rejected (remote has new commits) | `git pull` (or `git pull --rebase`), then `git push` |
| Undo a pushed commit safely | `git revert <commit>`, then `git push` |
| Conflict markers | The part above `=======` (HEAD) comes from the branch you were on |
| Port already allocated | `docker ps` shows which container holds the port |
| Publish a port | `docker run -p 33012:5000 ...` (`EXPOSE` alone doesn’t publish it) |
| `ls -ld` showing `drwxr-x---` | `750` |

Other answers: Dockerfile layer caching explains the `requirements.txt` order, Compose uses the service name `db` as the host name, a stuck pipeline is fixed by matching the runner’s tag (`test2026`), and secrets belong in masked CI/CD variables.

---

### Final checklist before time runs out

```bash
ls ~/test2026                   # answers.sh check_service.sh data repo INFO.txt
cd ~/test2026/repo && git status && git log --oneline -5
docker ps
curl localhost:<PORT>/health
```

### All commands in one place

```bash
# ---------- LOGIN / SETUP ----------
ssh <username>@ldapgit.cranecloud.io
cat ~/test2026/INFO.txt
git config --global user.name "Firstname Lastname"
git config --global user.email "your@email"

# ---------- PART A ----------
mkdir ~/test2026
chmod 700 ~/test2026
ls -ld ~/test2026
cp /opt/test2026/<username>/bundle.zip ~/test2026/
cd ~/test2026
unzip bundle.zip
ls -R
cat INFO.txt
cat count_lines.sh
./count_lines.sh data/access.log
nano answers.sh
cat answers.sh
bash answers.sh

# a3
awk '$9 ~ /^5[0-9][0-9]$/ {c++} END {print c+0}' data/access.log
# a4
awk '{print $1}' data/access.log | sort | uniq -c | sort -rn | head -1 | awk '{print $2}'
# a5
tail -n +2 data/services.csv | awk -F, '$6=="down" {print $1}' | sort
# a6
awk '$9==404 {print $1}' data/access.log | sort -u | wc -l

# a7
nano check_service.sh
awk -F, -v n="$name" 'NR>1 && $1==n {print $1 " is " $6 " on port " $3; exit}' data/services.csv
chmod +x check_service.sh
./check_service.sh billing; echo $?
./check_service.sh; echo $?
./check_service.sh nosuch; echo $?
./check_service.sh cache

# ---------- PART B ----------
man ssh-keygen
ssh-keygen -t ed25519 -C "<username>-test2026"
cat ~/.ssh/id_ed25519.pub
ssh -T git@gitlab.cranecloud.io

cd ~/test2026
git clone git@gitlab.cranecloud.io:bse4105-test-2026/test-<username>.git repo
cd repo
git branch -a

git checkout main
git checkout -b test-2026
git push -u origin test-2026

git merge origin/hotfix        # or: git merge hotfix
git status
nano config/settings.ini
grep -n '<<<<\|====\|>>>>' config/settings.ini
git add config/settings.ini
git commit -m "Merge hotfix into test-2026"
git push

cd ~/test2026/repo
printf "Full name: Your Full Name\nStudent number: 0000000\n" > STUDENT.md
git add STUDENT.md
git commit -m "Add STUDENT.md" -m "Adds my full name and student number for the 2026 test."
git push
git log -1

# ---------- PART C ----------
nano Dockerfile
docker build -t test-local .
docker run -d --name tmp-test -p <PORT>:5000 test-local
curl localhost:<PORT>
docker rm -f tmp-test

nano app.py
nano test_app.py
pip install -r requirements.txt pytest
pytest

nano .gitlab-ci.yml
# CI script commands used inside .gitlab-ci.yml:
docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
docker build -t $CI_REGISTRY_IMAGE:$IMAGE_TAG .
docker push $CI_REGISTRY_IMAGE:$IMAGE_TAG
docker run --rm $CI_REGISTRY_IMAGE:$IMAGE_TAG sh -c "pip install pytest && pytest"
docker pull $CI_REGISTRY_IMAGE:$IMAGE_TAG
docker rm -f $CI_PROJECT_NAME || true
docker run -d --name $CI_PROJECT_NAME -p $APP_PORT:5000 $CI_REGISTRY_IMAGE:$IMAGE_TAG

git add -A
git commit -m "Fix Dockerfile and CI, add /health and test"
git push
docker ps
curl localhost:<PORT>/health

# C6: break test, push, then fix and push
nano test_app.py
git add -A
git commit -m "Break test on purpose"
git push
nano test_app.py
git add -A
git commit -m "Fix test"
git push
docker ps
curl localhost:<PORT>/health

# ---------- PART D (commands referenced in questions) ----------
chmod 700 test2026
./check_service.sh billing > out.txt 2>&1
echo $?
git pull
git pull --rebase
git revert <commit>
git reset --hard HEAD~1
git push --force
git checkout <commit>
git merge hotfix
docker ps
docker images
docker run -p 33012:5000 ...
ls -ld test2026

# ---------- FINAL CHECK ----------
ls ~/test2026
cd ~/test2026/repo && git status && git log --oneline -5
docker ps
curl localhost:<PORT>/health

```

---

## Note: database name mismatch

In `docker-compose.yml`, the app (`buyinza-web`) connects to a database called `userdb` (`POSTGRES_DB: userdb`), but the database container (`buyinza-db`) creates one called `buyinzadb`. Because the names don't match, the app can't find its database and the `/users` route will probably fail.

This may be intentional, as part of the test. To fix it, make both `POSTGRES_DB` values the same in `docker-compose.yml`, for example:

```yaml
services:
  buyinza-web:
    environment:
      POSTGRES_DB: buyinzadb

  buyinza-db:
    environment:
      POSTGRES_DB: buyinzadb
```

If the database has already been created, run `docker compose down` and delete the `db_data` folder so that `db_init/init.sql` runs again on the next start.
