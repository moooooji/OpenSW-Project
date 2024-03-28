import time
import re
import subprocess
import ipinfo
import pprint
import pymysql

conn = pymysql.connect(host='127.0.0.1', user='root', db='s2r', charset='utf8')
cur = conn.cursor()

access_token = "39bd4f67da2f8a"
handler = ipinfo.getHandler(access_token)

filterd_ip = ""
# 유튜브 강의 코드

# 정규표현식 패턴 (로그에서 실패한 ssh 로그인 메시지를 찾기 위해 사용)
failed_ssh_pattern = "Failed password for (invalid user)?(\w+) from (\d+\.\d+\.\d+\.\d+)"

# 실패 횟수와 차단 시간 설정
max_failures = 3
ban_time_minutes = 5

# 차단된 사용자와 차단 시작 시간을 저장할 딕셔너리
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
    subprocess.run(["iptables", "-I", "INPUT", "-s", ip_adress, "-j", "DROP"])


def unban_user(username, ip_adress):
    # iptables에서 해당 IP 주소를 차단 해제
    subprocess.run(["iptables", "-D", "INPUT", "-s", ip_adress, "-j", "DROP"])
    print(f"Unblocking {username} from {ip_adress}.")


def check_log():
    with open("/var/log/auth.log", "r") as auth_log:
        for line in auth_log:
            # 로그에서 실패한 ssh 로그인을 찾음
            match = re.search(failed_ssh_pattern, line)
            if match:
                username = match.group(2)
                ip = match.group(3)
                result = sql_select(f"select * from ipInfo where ip='{ip}'")
                print(result)
                if not result:
                    failed_users[ip] = failed_users.get(ip, 0) # failed_users 딕셔너리에 로그에서 나온 ip가 없으면 0으로 초기화
                    failed_users[ip] += 1 # 비번 틀릴 때마다 1회씩 증가

                    if (failed_users[ip] >= max_failures): # 3회이상 실패할 경우 DB에서 관리
                        del failed_users[ip] # DB에 관리할 경우 딕셔너리 키 삭제
                        ban_start_time = time.time()
                        result = sql_insert("INSERT INTO `ipInfo` (ip, start_time) VALUES (%s, %s)", (ip, ban_start_time)) # 로그인 실패가 3회 이상일 경우 DB에 저장하여 관리
                        ban_user(ip)
                else:        
                    banned_ip = result[0][1]
                    banned_start_time = result[0][2]
                    
                    if float(banned_start_time) - time.time() > 60: # ban 시간 1분 이상이면 언밴
                            unban_user(banned_ip)


                # ip = match.group().split(" ")[5]
                # failed_user[id] = (time.time())
                # detail = handler.getDetails(filtered_ip)
                # print(detail.all) # ip에 대한 모든 정보 출력

                # timestamp = time.mktime(time.strptime(line[:15], "%b %d %H:%M:%S"))

                # 1분 이내의 로그인만 처리
                # if timestamp >= start_time - 60:
                #     username = match.group(2)
                #     ip_adress = match.group(3)

                #     if username in banned_users:
                #         banned_users[username] += 1
                #         if banned_users[username] >= max_failures:
                #             if (
                #                 username not in banned_users
                #                 or banned_users[username] >= max_failures
                #             ):
                #                 print(
                #                     f"Blocking {username} from {ip_adress} for {ban_time_minutes} minutes"
                #                 )
                #                 ban_user(ip_adress)
                #                 banned_users[username] = (
                #                     time.time()   
                #                 )  # 차단 시작 시간 기록
                #     else:
                #         banned_users[username] = 1

        # 차단된 사용자 중 시간이 지난 사용자 차단 해제
        # for username, ban_start_time in list(banned_users.items()):
        #     if time.time() - ban_start_time >= ban_time_minutes * 60:
        #         del banned_users[username]
        #         unban_user(username, ip_adress)

if __name__ == "__main__":
    while True:
        check_log()
        time.sleep(60)
          # 1분마다 로그 확인