
Setup the [pwncollege](https://github.com/pwncollege/pwncollege)
# Handle the challenges

Information includes challenges, user accounts, etc. will be inserted into the MariaDB database.

## Insert challenges via database

1. Prepare the challenges: folder `xxx/challenges/xxx`

2. Check the docker images we use

```shell
$ docker images
REPOSITORY                               TAG               IMAGE ID       CREATED         SIZE
xxx/xxx_challenge                  latest            f43aaf8cb9d4   2 minutes ago   6.83GB
xxx/xxx_kernel_challenge           latest            bbe55489eb00   2 minutes ago   10.3GB
...
```

3. Modify the `xxx/challenges/generate_sql.sh`

```python
#!/usr/bin/env bash

CATEGORIES=("xxx")

# challenges start from id 1, before inserting challenges, check ctfd.challenges table to make sure the id will not conflict with exist ones
id=1
for category in ${CATEGORIES[@]}; do
    for challenge in $(ls -v $category | grep -v '.*\.c'); do
        path="$category/$challenge"
        if [ -d "$path" ]; then
            docker_image="bbe55489eb00" # change the value to xxx/xxx_kernel_challenge image id
        elif echo $path | grep -q '.*\.ko'; then
            docker_image="bbe55489eb00" # change the value to xxx/xxx_kernel_challenge image id
        else
            docker_image="f43aaf8cb9d4" # change the value to xxx/xxx_challenge image id
        fi
        echo "insert into challenges (id, name, description, max_attempts, value, category, type, state) values (${id}, '${challenge}', '', 0, 1, '${category}', 'docker', 'visible');"
        echo "insert into docker_challenges (id, docker_image_name) values (${id}, '${docker_image}');"
        echo "insert into flags (id, challenge_id, type, content, data) values (${id}, ${id}, 'user', '', 'cheater');"
        id=$((id+1))
    done
done
```
4. Copy challenges and script to `.data` 

```shell
cp generate_sql.sh ../.data/challenges/global/
cp -r xxx/ ../.data/challenges/global
```

5. Insert the challenges to database

```shell
./generate_sql.sh | docker exec -i xxx_db mysql -uctfd -pctfd -Dctfd
```

This command will influence three tables in `ctfd` database: challenges, docker_challenges, and flags.
 I will explain it later.

6. Connect to the database

```shell
docker exec -it xxx_db mysql -u root -p'ctfd'
```

7. Check the database
```shell
MariaDB [ctfd]> show databases;
+--------------------+
| Database           |
+--------------------+
| ctfd               |
| information_schema |
| mysql              |
| performance_schema |
+--------------------+
4 rows in set (0.001 sec)

MariaDB [none]> use ctfd;
MariaDB [ctfd]> show tables;
...
MariaDB [ctfd]> select * from challenges;
+----+------+-------------+--------------+-------+----------+--------+---------+--------------+
| id | name | description | max_attempts | value | category | type   | state   | requirements |
+----+------+-------------+--------------+-------+----------+--------+---------+--------------+
|  1 | arm1 |             |            0 |     1 | xxx   | docker | visible | NULL         |
|  2 | arm2 |             |            0 |     1 | xxx   | docker | visible | NULL         |
+----+------+-------------+--------------+-------+----------+--------+---------+--------------+
2 rows in set (0.001 sec)

MariaDB [ctfd]> select * from docker_challenges;
+----+-------------------+
| id | docker_image_name |
+----+-------------------+
|  1 | f43aaf8cb9d4      |
|  2 | f43aaf8cb9d4      |
+----+-------------------+
2 rows in set (0.000 sec)

MariaDB [ctfd]> select * from flags;
+----+--------------+------+---------+---------+
| id | challenge_id | type | content | data    |
+----+--------------+------+---------+---------+
|  1 |            1 | user |         | cheater |
|  2 |            2 | user |         | cheater |
+----+--------------+------+---------+---------+
2 rows in set (0.001 sec)
```

> `challenges` table stores the basic information of challenges, `docker_challenges` table stores the docker image used to run challenges. **ATTENTION**, this docker image can be changed whenever build new   `xxx_challenge` image I mentioned before.

## Delete challenges via database

```shell
MariaDB [ctfd]> delete from docker_challenges where id=263;
MariaDB [ctfd]> delete from docker_challenges where id>0 AND id<260;
MariaDB [ctfd]> delete from challenges where id=0;

error: Cannot delete or update a parent row: a foreign key constraint fails
MariaDB [ctfd]> show VARIABLES like "foreign%";
+--------------------+-------+
| Variable_name      | Value |
+--------------------+-------+
| foreign_key_checks | ON    |
+--------------------+-------+
1 row in set (0.001 sec)
MariaDB [ctfd]> SET foreign_key_checks = 0;  // if the value if on 
// > drop table table1 or delete
MariaDB [ctfd]> SET foreign_key_checks = 1; // after finishing deleting, turn on the key check
```

# Handle the system

## Clean and restart the whole system:

```shell
service nginx stop
service apache2 stop
docker kill $(docker ps -q)
docker container prune
./run.sh xxx
```

# Update docker images

`xxx_challenge` run normal applications, `xxx_kernel_challenge` run `.ko` or other linux kernel modules [maybe].

## Modify the dockerfile to support ARM:

```dockerfile
# xxx_challenge/Dockerfile
FROM pwncollege/pwncollege_challenge

RUN apt-get update && apt-get install -y gcc-aarch64-linux-gnu
RUN wget https://ughe.github.io/data/2018/ld-linux-aarch64.so.1 -P /lib/
RUN wget https://ughe.github.io/data/2018/libc.so.6 -P /lib64/


# xxx_kernel_challenge/Dockerfile
FROM pwncollege/pwncollege_kernel_challenge

RUN apt-get update && apt-get install -y gcc-aarch64-linux-gnu
RUN wget https://ughe.github.io/data/2018/ld-linux-aarch64.so.1 -P /lib/
RUN wget https://ughe.github.io/data/2018/libc.so.6 -P /lib64/
```

## Build new images with ARM support:

```shell
docker build -f /opt/xxx/containers/xxx_challenge/Dockerfile -t xxx/xxx_challenge:latest .
docker build -f /opt/xxx/containers/xxx_kernel_challenge/Dockerfile -t xxx/xxx_kernel_challenge:latest .
```

## Test the image

```shell
docker run -t -i xxx/xxx_challenge:latest /bin/bash
```

# Other tips

- Copy from host to docker container: `docker cp src [image_id]:dst`
- Build dynamic Arm program: `aarch64-linux-gnu-gcc -o arm1 arm.c`
- Update `docker_challenges`: `update docker_challenges set docker_image_name = 'xx' where id < xx`

## Set caddy
1. install caddy: `conf/caddy.sh`
2. setup caddy conf: 

```shell
xxx.xxx.academy {
    reverse_proxy / 127.0.0.1:8000
}
```
3. stop `nginx-proxy` container.
4. change port

```shell
           --publish 80:80 \
           --publish 443:443 \
```
5. run caddy: `caddy run -adapter caddyfile -config caddy.conf`
