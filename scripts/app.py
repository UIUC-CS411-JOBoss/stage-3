from faker import Faker
import pymysql
import pymysql.cursors
import os
from tenacity import retry, wait_fixed
import random
from datetime import datetime, timedelta
from time import time

BASE_DATE = datetime(2021, 8, 1)

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

USER_CNT = 10000

fake = Faker()

company_list = [
  ('Facebook', 'https://www.facebook.com/careers/'),
  ('Apple', 'https://www.apple.com/careers/us/'),
  ('Netflix', 'https://jobs.netflix.com/jobs/'),
  ('Microsoft', 'https://careers.microsoft.com/us/en'),
  ('Google', 'https://careers.google.com/'),
  ('Gusto', 'https://gusto.com/about/careers'),
  ('Hudson River Trading', 'https://www.hudsonrivertrading.com/')
]

job_list = [
  # `company_id`, `url`, `archived_url`, `active`, `location`, `type`, `title`, `description`, `accept_opt_cpt`, `visa_sponsorship`
  (1, "https://www.facebook.com/careers/v2/jobs/946116176191468/", "", True, "", "internship", "Software Engineer, Intern/Co-op", "", "yes", "yes"),
  (2, "https://jobs.apple.com/en-us/details/200253195/software-engineering-internship?team=STDNT", "", True, "", "internship", "Software Engineering Internship", "", "yes", "yes"),
  (3, "https://jobs.netflix.com/jobs/119544498", "", True, "", "internship", "Machine Learning Intern", "", "yes", "yes"),
  (4, "https://careers.microsoft.com/students/us/en/job/1085294/Software-Engineering-Intern-Opportunities", "", True, "", "internship", "Software Engineering: Intern Opportunities", "", "yes", "yes"),
  (5, "https://careers.google.com/jobs/results/122335392432038598-software-engineering-intern-masters-summer-2022/?employment_type=INTERN", "", True, "", "internship", "Software Engineering Intern, Master's, Summer 2022", "", "yes", "yes"),
  (6, 'https://boards.greenhouse.io/gusto/jobs/3499036', "", True, "", "internship", "Software Engineering Intern (Summer 2022)", "", "yes", "yes"),
  (7, 'https://www.hudsonrivertrading.com/careers/job/?gh_jid=3015374', "", True, "", "internship", "Software Engineering Internship - Summer 2022", "", "yes", "yes"),
]

# status = ['applied', 'OA', 'behavior interview', 'technical interview', 'rejected', 'offered']
status_1 = ['applied']
status_2 = ['applied', 'OA', 'behavior interview', 'technical interview']
status_3 = ['rejected']
status_4 = ['offered']
status_5 = ['applied', 'OA', 'behavior interview', 'technical interview', 'offered']
status_6 = ['applied', 'OA', 'behavior interview', 'technical interview', 'rejected']
status_list = [status_1, status_2, status_4, status_5] + [status_3]*1000 + [status_6]*500

job_ids = list(range(1, len(job_list)))

def random_apply(user_id):
  job_status_list = []
  for job_id in random.sample(job_ids, random.randrange(1, len(job_list))):
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

connection = get_db()

with connection:
    with connection.cursor() as cursor:
        users = [(fake.email(), '') for _ in range(USER_CNT)]
        query = "INSERT INTO `USER` (`email`, `token`) VALUES (%s, %s)"
        cursor.executemany(query, users)
    connection.commit()
    with connection.cursor() as cursor:
        query = "SELECT COUNT(1) FROM USER;"
        cursor.execute(query)
        result = cursor.fetchone()
        print('USER COUNT', result)
    with connection.cursor() as cursor:
        query = "INSERT INTO `COMPANY` (`name`, `website`) VALUES (%s, %s)"
        cursor.executemany(query, company_list)
    connection.commit()
    with connection.cursor() as cursor:
        query = "SELECT COUNT(1) FROM COMPANY;"
        cursor.execute(query)
        result = cursor.fetchone()
        print('COMPANY COUNT', result)
    with connection.cursor() as cursor:
        query = "INSERT INTO `JOB` (`company_id`, `url`, `archived_url`, `active`, `location`, `type`, `title`, `description`, `accept_opt_cpt`, `visa_sponsorship`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.executemany(query, job_list)
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
    
    query1 = "SELECT SQL_NO_CACHE company.id, company.name, COUNT(*) AS num_of_offer \
                FROM JOB_STATUS AS status JOIN JOB AS job ON status.job_id = job.id JOIN COMPANY AS company ON job.company_id = company.id \
                WHERE status.create_at LIKE '2021%' AND status.application_status = 'offered' \
                GROUP BY company.id, company.name \
                ORDER BY num_of_offer DESC;"
    query2 = "SELECT SQL_NO_CACHE u.id \
                FROM USER AS u JOIN JOB_STATUS AS js ON u.id = js.user_id \
                WHERE date(js.create_at) = CURDATE() - interval 7 day \
                GROUP BY u.id \
                HAVING COUNT(*) < 5;"
    explain_1 = "EXPLAIN " + query1
    explain_2 = "EXPLAIN " + query2

    # QUERY 1
    with connection.cursor() as cursor:
        t = time()
        cursor.execute(query1)
        result = cursor.fetchall()
        print("==========QUERY 1============",)
        print(time()-t, query1)
        print('#'*50)
        print(result)
        cursor.execute(explain_1)
        result = cursor.fetchall()
        print("$$$$$$$$$$ EXPLAIN $$$$$$$$$$$")
        print(result)
        print("==========END QUERY 1============")
    
    # QUERY 2
    with connection.cursor() as cursor:
        t = time()
        cursor.execute(query2)
        result = cursor.fetchall()
        print("==========QUERY 2============")
        print(time()-t, query2)
        print('#'*50)
        print(result)
        cursor.execute(explain_2)
        result = cursor.fetchall()
        print("$$$$$$$$$$ EXPLAIN $$$$$$$$$$$")
        print(result)
        print("==========END QUERY 1============")
      
    # ADD INDEX
    with connection.cursor() as cursor:
        sql = "CREATE INDEX application_status_index ON JOB_STATUS (application_status, create_at);"
        cursor.execute(sql)

    # QUERY 1
    with connection.cursor() as cursor:
        t = time()
        cursor.execute(query1)
        result = cursor.fetchall()
        print("==========QUERY 1============",)
        print(time()-t, query1)
        print('#'*50)
        print(result)
        print('#'*50)
        cursor.execute(explain_1)
        result = cursor.fetchall()
        print("$$$$$$$$$$ EXPLAIN $$$$$$$$$$$")
        print(result)
        print("==========END QUERY 1============")
    
    # QUERY 2
    with connection.cursor() as cursor:
        t = time()
        cursor.execute(query2)
        result = cursor.fetchall()
        print("==========QUERY 2============")
        print(time()-t, query2)
        print('#'*50)
        print(result)
        print('#'*50)
        cursor.execute(explain_2)
        result = cursor.fetchall()
        print("$$$$$$$$$$ EXPLAIN $$$$$$$$$$$")
        print(result)
        print("==========END QUERY 1============")
