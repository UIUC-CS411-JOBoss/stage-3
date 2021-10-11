from faker import Faker
import pymysql
import pymysql.cursors
import os
from tenacity import retry, wait_fixed
import random


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
  ('Google', 'https://careers.google.com/')
]

job_list = [
  # `company_id`, `url`, `archived_url`, `active`, `location`, `type`, `title`, `description`, `accept_opt_cpt`, `visa_sponsorship`
  (1, "https://www.facebook.com/careers/v2/jobs/946116176191468/", "", True, "", "internship", "Software Engineer, Intern/Co-op", "", "yes", "yes"),
  (2, "https://jobs.apple.com/en-us/details/200253195/software-engineering-internship?team=STDNT", "", True, "", "internship", "Software Engineering Internship", "", "yes", "yes"),
  (3, "https://jobs.netflix.com/jobs/119544498", "", True, "", "internship", "Machine Learning Intern", "", "yes", "yes"),
  (4, "https://careers.microsoft.com/students/us/en/job/1085294/Software-Engineering-Intern-Opportunities", "", True, "", "internship", "Software Engineering: Intern Opportunities", "", "yes", "yes"),
  (5, "https://careers.google.com/jobs/results/122335392432038598-software-engineering-intern-masters-summer-2022/?employment_type=INTERN", "", True, "", "internship", "Software Engineering Intern, Master's, Summer 2022", "", "yes", "yes"),
]

status = ['applied', 'OA', 'behavior interview', 'technical interview', 'rejected', 'offered']
status_1 = ['applied']
status_2 = ['applied', 'OA', 'behavior interview', 'technical interview']
status_3 = ['rejected']
status_4 = ['offered']
status_5 = ['applied', 'OA', 'behavior interview', 'technical interview', 'offered']

job_ids = list(range(1, 6))

def random_apply(user_id):
  job_status_list = []
  job_applied = random.sample(job_ids, random.randrange(1, 5))
  # job_id` 
  # `user_id`
  # `create_at`
  # `application_status

@retry(wait=wait_fixed(2))
def get_db():
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
    for i in range(USER_CNT):
      random_apply(i)
