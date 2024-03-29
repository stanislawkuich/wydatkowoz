# Wydatkowoz

<p align="center">
  <img width="460" height="300" src="https://raw.githubusercontent.com/stanislawkuich/wydatkowoz/main/web/templates/static/logo.png">
</p>


## Description

Simply application to manage home budget.

**Dashboard page**

![Dashboard](png/dashboard_1.png "Wydatkowoz - dashboard")
![Dashboard](png/dashboard_2.png "Wydatkowoz - dashboard")

**Incomes page**

![Income](png/income_tab.png "Wydatkowoz - tab to manage incomes")

**Expenses page**

![Expenses](png/expenses_tab.png "Wydatkowoz - tab to manage expenses")

## How to run

> docker build -f Dockerfile -t wydatkowoz:latest .

> docker run --rm -d  -p 5000:5000/tcp -p 8025:8025/tcp wydatkowoz:latest

### Podman

1. Build image

> podman build -t wydatkowoz:latest -f Dockerfile

Be careful for SElinux policies

```
ausearch -m avc -ts recent | audit2allow -a -M custom_container_app

******************** IMPORTANT ***********************
To make this policy package active, execute:

semodule -i custom_container_app.pp

```

2. Run container

> podman run -p 8080:5000 localhost/wydatkowoz:latest

If you want mount volume for persitance:

Example:

> podman run -d -p 8080:5000 -p 8025:8025/tcp -v /home/user:/app/data:Z localhost/wydatkowoz:latest

Remember to assign good permissions

> podman unshare chown 1999:1999 -R /home/user

3. Create systemd service

> podman generate systemd CONTAINER_NAME > /usr/lib/systemd/user/wydatkowoz.service

4. Reload services

> systemctl --user daemon-reload

5. Start service

> systemctl --user start wydatkowoz.service

> systemctl --user enable wydatkowoz.service

## API documentation

1. Get expenses

```
curl -k -H "Content-Type: application/json" http://127.0.0.1:8080/api/v1/expenses

```

2. Get incomes

```
curl -k -H "Content-Type: application/json" http://127.0.0.1:8080/api/v1/incomes

```

3. New expenses

```
curl -k -X POST -H "Content-Type: application/json" --data '{"date":"2022-08-02","value":2000,"name":"test2","category":2,"waspayed":false}' http://127.0.0.1:8080/api/v1/expenses

```

4. New income

```
curl -k -X POST -H "Content-Type: application/json" --data '{"id":1,"date":"2022-08-02","value":2000,"name":"test2"}' http://127.0.0.1:8080/api/v1/incomes

```

5. Update expenses

```
curl -k -X POST -H "Content-Type: application/json" --data '{"id":8,"date":"2022-08-02","value":2000,"name":"test2","category":2,"waspayed":false}' http://127.0.0.1:8080/api/v1/expenses/update

```

6. Update income

```
curl -k -X POST -H "Content-Type: application/json" --data '{"id":1,"date":"2022-08-02","value":2000,"name":"test2"}' http://127.0.0.1:8080/api/v1/incomes/update

```

7. Delete expenses

```
curl -k -X DELETE -H "Content-Type: application/json" http://127.0.0.1:8080/api/v1/expenses/delete/2

```

8. Delete income

```
curl -k -X DELETE -H "Content-Type: application/json" http://127.0.0.1:8080/api/v1/incomes/delete/2

```