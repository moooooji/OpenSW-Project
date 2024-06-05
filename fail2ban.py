import time
import re
import subprocess
import pprint
from init import *

conn, cur = db_connect()
handler = ipinfo_connect()

filterd_ip = ""
# 유튜브 강의 코드

# 정규표현식 패턴 (로그에서 실패한 ssh 로그인 메시지를 찾기 위해 사용)
failed_ssh_pattern = r"Failed password for (invalid user )?(\w+) from (\d+\.\d+\.\d+\.\d+)"
success_ssh_pattern = r"Accepted password for (invalid user )?(\w+) from (\d+\.\d+\.\d+\.\d+)"
# 실패 횟수와 차단 시간 설정
max_failures = 3
ban_time_minutes = 15

# 차ong 사용자와 차단 시작 시간을 저장할 딕셔너리
failed_users = {}

# 프로그램 시작 시간 기록
start_time = time.time()

def sql_select(query):
    cur.execute(query)
    result = cur.fetchall()

    return result

def sql_insert(query, data):
    cur.execute(query, data)
    result = conn.commit()

    return result


def ban_user(ip_adress):
    # iptabels를 사용하여 해당 IP 주소를 차단
    print(11)
    subprocess.run(["iptables", "-I", "INPUT", "-s", ip_adress, "-j", "DROP"])
    


def unban_user(username, ip_adress):
    # iptables에서 해당 IP 주소를 차단 해제
    print(22)
    subprocess.run(["iptables", "-D", "INPUT", "-s", ip_adress, "-j", "DROP"])
    print(f"Unblocking {username} from {ip_adress}.")


def check_log():
    with open("/var/log/auth.log", "r") as auth_log:
        for line in auth_log:
            # 로그에서 실패한 ssh 로그인을 찾음
            match = re.search(failed_ssh_pattern, line)
            if match:
                date = ' '.join(line.split(' ')[:3]) # ssh 접속 시간 가져오기
                username = match.group(2) # 접속 계정 가져오기
                ip = match.group(3) # 접속 ip 가져오기

                ip_info = handler.getDetails('14.7.125.196')
                city = ip_info.city
                latitude = ip_info.latitude
                longitude = ip_info.longitude
                region = ip_info.region
                postal = ip_info.postal
                country_name = ip_info.country_name
                access_time = date

                result = sql_select(f"select * from ipInfo where ip='{ip}' and success = 0 and access_time = '{access_time}'") # 이미 벤 된 ip는 제외

                if not result: # 이미 벤 되어진 ip가 아닌 경우에만
                    failed_users[ip] = failed_users.get(ip, 0) # failed_users 딕셔너리에 로그에서 나온 ip가 없으면 0으로 초기화
                    failed_users[ip] += 1 # 비번 틀릴 때마다 1회씩 증가

                    if (failed_users[ip] >= max_failures): # 3회이상 실패할 경우 DB에서 관리, 블랙리스트
                        del failed_users[ip] # DB에 관리할 경우 딕셔너리 키 삭제
                        ban_start_time = time.time()
                        result = sql_insert("INSERT INTO `ipInfo` (ip, country_name, region, city, postal, latitude, longitude, ban_start_time, access_time, success) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (ip, country_name, region, city, postal, latitude, longitude, ban_start_time, access_time, 0)) # 로그인 실패가 3회 이상일 경우 DB에 저장하여 관리
                        ban_user(ip)
                else:        
                    banned_ip = result[0][1]
                    banned_start_time = result[0][2]
                    
            match = re.search(success_ssh_pattern, line)

            if match:
                date = ' '.join(line.split(' ')[:3])
                username = match.group(2)
                ip = match.group(3)
                ip_info = handler.getDetails('14.7.125.196')
                city = ip_info.city
                latitude = ip_info.latitude
                longitude = ip_info.longitude
                region = ip_info.region
                postal = ip_info.postal
                country_name = ip_info.country_name
                access_time = date
                ban_start_time = '0'
                result = sql_select(f"select * from ipInfo where ip = '{ip}' and success = 1 and access_time = '{access_time}'")
                if not result:
                    print(2)
                    result = sql_insert("INSERT INTO `ipInfo` (ip, country_name, region, city, postal, latitude, longitude, ban_start_time, access_time, success) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (ip, country_name, region, city, postal, latitude, longitude, ban_start_time, access_time, 1)) # 로그인 실패가 3회 이상일 경우 DB에 저장하여 관리
                    print('success')
               


    result = sql_select(f"select ban_start_time from ipInfo where ip = '{ip}' and success = 0")
    if result:
        ban_start_time = float(result[0][0])
        if time.time() - ban_start_time >= ban_time_minutes * 60:
            unban_user(username, ip)

if __name__ == "__main__":
    while True:
        check_log()
        time.sleep(60)