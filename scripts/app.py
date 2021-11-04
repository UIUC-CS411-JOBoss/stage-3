from faker import Faker
import pymysql
import pymysql.cursors
import os
from tenacity import retry, wait_fixed
import random
from datetime import datetime, timedelta
from time import time
import random
import csv

BASE_DATE = datetime(2021, 8, 1)

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

USER_CNT = 10000
USER_APPLY_MAX = 100

fake = Faker()

print ('[-] loading company csv...')
with open('companies.csv', newline='') as f:
    reader = csv.reader(f)
    company_list = list(reader)[1:]
    print ('[v] company csv loaded')

print ('[-] loading job csv...')
with open('jobs.csv', newline='') as f:
    reader = csv.reader(f)
    job_list_csv = list(reader)
    print ('[v] job csv loaded')
    
job_list = [[element if element != '' else None for element in line] for line in job_list_csv[1:]] 
print ('[v] job list loaded')

# status = ['applied', 'OA', 'behavior interview', 'technical interview', 'rejected', 'offered']
status_1 = ['applied']
status_2 = ['applied', 'OA', 'behavior interview', 'technical interview']
status_3 = ['rejected']
status_4 = ['offered']
status_5 = ['applied', 'OA', 'behavior interview', 'technical interview', 'offered']
status_6 = ['applied', 'OA', 'behavior interview', 'technical interview', 'rejected']
status_list = [status_1, status_2, status_4, status_5] + [status_3]*1000 + [status_6]*500


def random_apply(user_id):
  job_status_list = []
  for job_record in random.sample(job_list, random.randrange(0, USER_APPLY_MAX)):
    job_id = job_record[0]
    d = BASE_DATE + timedelta(days=random.randint(1, 30))
    for status in random.choice(status_list):
      d = d + timedelta(days=random.randint(1, 15))
      job_status_list.append((job_id, user_id, d, status))
  return job_status_list

@retry(wait=wait_fixed(2))
def get_db():
  print("get db")
  return pymysql.connect(host=DB_HOST,
                        user=DB_USER,
                        password=DB_PASSWORD,
                        database=DB_NAME,
                        cursorclass=pymysql.cursors.DictCursor)

def q(connection):
    query1 = "SELECT SQL_NO_CACHE company.id, company.name, COUNT(*) AS num_of_offer \
            FROM JOB_STATUS AS status JOIN JOB AS job ON status.job_id = job.id JOIN COMPANY AS company ON job.company_id = company.id \
            WHERE status.create_at LIKE '202%' AND status.application_status = 'offered' AND job.type = 'internship' \
            GROUP BY company.id, company.name \
            ORDER BY num_of_offer DESC LIMIT 15;"

    query2 = "SELECT SQL_NO_CACHE u.id, u.email, u.reverse_email \
                FROM USER AS u JOIN JOB_STATUS AS js ON u.id = js.user_id JOIN JOB AS j ON j.id = js.job_id \
                WHERE (DATE(js.create_at) >= CURDATE() - interval 1 week) AND u.reverse_email LIKE 'ude.sionilli@%' \
                GROUP BY u.id \
                HAVING COUNT(*) < 5 \
                ORDER BY u.email ASC LIMIT 15;"

    # uiuc 不活躍使用者 (7 天內 apply status 少於五筆)
    # thebjorn. (2015, Aug 14). MYSQL datetime rows from 7 days ago?. Stack Overflow. https://stackoverflow.com/a/32016131
    query3 = "SELECT SQL_NO_CACHE u.id, u.email, u.reverse_email \
                FROM USER AS u JOIN JOB_STATUS AS js ON u.id = js.user_id JOIN JOB AS j ON j.id = js.job_id \
                WHERE (DATE(js.create_at) >= CURDATE() - interval 1 week) AND u.email LIKE '%@illinois.edu' \
                GROUP BY u.id \
                HAVING COUNT(*) < 5 \
                ORDER BY u.email ASC LIMIT 15;"
    explain_1 = "EXPLAIN ANALYZE " + query1
    explain_2 = "EXPLAIN ANALYZE " + query2
    explain_3 = "EXPLAIN ANALYZE " + query3

    # QUERY 1
    with connection.cursor() as cursor:
        t = time()
        cursor.execute(query1)
        result = cursor.fetchall()
        print("==========QUERY 1============\n\n",)
        print('time:', time()-t, '\n\n')
        print('count:', len(result))
        for i in result:
            print(i)
        cursor.execute(explain_1)
        result = cursor.fetchone()
        print("=========== EXPLAIN ============\n\n")
        print(result['EXPLAIN'])
        print("==========END QUERY 1============\n\n")
    
    # QUERY 2
    with connection.cursor() as cursor:
        t = time()
        cursor.execute(query2)
        result = cursor.fetchall()
        print("==========QUERY 2============\n\n",)
        print('time:', time()-t, '\n\n')
        print('count:', len(result))
        for i in result:
            print(i)
        cursor.execute(explain_2)
        result = cursor.fetchone()
        print("=========== EXPLAIN ============\n\n")
        print(result['EXPLAIN'])
        print("==========END QUERY 2============\n\n")

    # QUERY 3
    with connection.cursor() as cursor:
        t = time()
        cursor.execute(query3)
        result = cursor.fetchall()
        print("==========QUERY 3============\n\n",)
        print('time:', time()-t, '\n\n')
        print('count:', len(result))
        for i in result:
            print(i)
        cursor.execute(explain_3)
        result = cursor.fetchone()
        print("=========== EXPLAIN ============\n\n")
        print(result['EXPLAIN'])
        print("==========END QUERY 3============\n\n")   

connection = get_db()

with connection:
    with connection.cursor() as cursor:
        # illinois.edu
        emails = [fake.user_name()+'@illinois.edu' for _ in range(200)] + [fake.free_email() for _ in range(USER_CNT)]
        users = [(email, email[::-1], '',) for email in emails]
        random.shuffle(users)
        query = "INSERT INTO `USER` (`email`, `reverse_email`, `token`) VALUES (%s, %s, %s)"
        cursor.executemany(query, users)
    connection.commit()
    with connection.cursor() as cursor:
        query = "SELECT COUNT(1) FROM USER;"
        cursor.execute(query)
        result = cursor.fetchone()
        print('USER COUNT', result)
    with connection.cursor() as cursor:
        query = "INSERT INTO `COMPANY` (`id`, `name`, `employer_industry_id`, `employer_logo_url`) VALUES (%s, %s, %s, %s)"
        cursor.executemany(query, company_list)
    connection.commit()
    with connection.cursor() as cursor:
        query = "SELECT COUNT(1) FROM COMPANY;"
        cursor.execute(query)
        result = cursor.fetchone()
        print('COMPANY COUNT', result)
    with connection.cursor() as cursor:
        query = "INSERT INTO `JOB` (`id`,`company_id`,`duration`,`job_type_id`,`job_type_name`,`location_cities`,`location_countries`,`location_states`,`location_names`,`salary_type_id`,`salary_type_name`,`text_description`,`title`,`remote`,`cumulative_gpa_required`,`cumulative_gpa`,`located_in_us`,`accepts_opt_cpt_candidates`,`willing_to_sponsor_candidate`,`graduation_date_minimum`,`graduation_date_maximum`,`work_auth_required`,`school_year_or_graduation_date_required`,`us_authorization_optional`,`work_authorization_requirements`,`apply_start`,`updated_at`,`expiration_date`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        cursor.executemany(query, job_list)
    connection.commit()
    
    with connection.cursor() as cursor:
        query = "SELECT COUNT(1) FROM JOB;"
        cursor.execute(query)
        result = cursor.fetchone()
        print('JOB COUNT', result)
    
    job_apply_list = []
    for i in range(1, USER_CNT):
      job_apply_list += random_apply(i)
    
    with connection.cursor() as cursor:
        query = "INSERT INTO `JOB_STATUS` (`job_id`, `user_id`, `create_at`, `application_status`) VALUES (%s, %s, %s, %s)"
        cursor.executemany(query, job_apply_list)
    connection.commit()
    with connection.cursor() as cursor:
        query = "SELECT COUNT(1) FROM JOB_STATUS;"
        cursor.execute(query)
        result = cursor.fetchone()
        print('JOB_STATUS COUNT', result)
    

    # ADD INDEX
    with connection.cursor() as cursor:
        sql = "CREATE INDEX create_at_index ON JOB_STATUS (create_at);"
        cursor.execute(sql)

    print("=======with index 0 & 5======\n\n")
    q(connection)

    # Remove INDEX
    with connection.cursor() as cursor:
        sql = "DROP INDEX create_at_index on JOB_STATUS;"
        cursor.execute(sql)

    q(connection)

    # ADD INDEX
    with connection.cursor() as cursor:
        sql = "CREATE INDEX application_status_index ON JOB_STATUS (application_status);"
        cursor.execute(sql)

    print("=======with index 1======\n\n")
    q(connection)

    # Remove INDEX
    with connection.cursor() as cursor:
        sql = "DROP INDEX application_status_index on JOB_STATUS;"
        cursor.execute(sql)


    # ADD INDEX
    with connection.cursor() as cursor:
        sql = "CREATE INDEX application_status_index2 ON JOB_STATUS (application_status, create_at);"
        cursor.execute(sql)

    print("=======with index 2======\n\n")
    q(connection)

    # Remove INDEX
    with connection.cursor() as cursor:
        sql = "DROP INDEX application_status_index2 on JOB_STATUS;"
        cursor.execute(sql)


    # ADD INDEX
    with connection.cursor() as cursor:
        sql = "CREATE INDEX user_email_index ON USER (email);"
        cursor.execute(sql)

    print("=======with index 3======\n\n")
    q(connection)

    # Remove INDEX
    with connection.cursor() as cursor:
        sql = "DROP INDEX user_email_index on USER;"
        cursor.execute(sql)


    # ADD INDEX
    with connection.cursor() as cursor:
        sql = "CREATE INDEX r_user_email_index ON USER (reverse_email);"
        cursor.execute(sql)

    print("=======with index 4======\n\n")
    q(connection)

    # Remove INDEX
    with connection.cursor() as cursor:
        sql = "DROP INDEX r_user_email_index on USER;"
        cursor.execute(sql)
