import time
import re
import subprocess

# 유튜브 강의 코드

# 정규표현식 패턴 (로그에서 실패한 ssh 로그인 메시지를 찾기 위해 사용)
failed_ssh_pattern = (
    r"Failed password for (invalid user )?(\w+) from (\d+\.\d+\.\d+\.\d+)"
)

# 실패 횟수와 차단 시간 설정
max_failures = 5
ban_time_minutes = 5

# 차단된 사용자와 차단 시작 시간을 저장할 딕셔너리
banned_users = {}

# 프로그램 시작 시간 기록
start_time = time.time()


def ban_user(ip_adress):
    # iptabels를 사용하여 해당 IP 주소를 차단
    subprocess.run(["iptables", "-I", "INPUT", "-s", ip_adress, "-j", "DROP"])


def unban_user(username, ip_adress):
    # iptables에서 해당 IP 주소를 차단 해제
    subprocess.run(["iptables", "-D", "INPUT", "-s", ip_adress, "-j", "DROP"])
    print(f"Unblocking {username} from {ip_adress}.")


def check_log():
    with open("../var/log/auth_log", "r") as auth_log:
        for line in auth_log:
            # 로그에서 실패한 ssh 로그인을 찾음
            match = re.search(failed_ssh_pattern, line)
            if match:
                timestamp = time.mktime(time.strptime(line[:15], "%b %d %H:%M:%S"))

                # 1분 이내의 로그인만 처리
                if timestamp >= start_time - 60:
                    username = match.group(2)
                    ip_adress = match.group(3)

                    if username in banned_users:
                        banned_users[username] += 1
                        if banned_users[username] >= max_failures:
                            if (
                                username not in banned_users
                                or banned_users[username] >= max_failures
                            ):
                                print(
                                    f"Blocking {username} from {ip_adress} for {ban_time_minutes} minutes"
                                )
                                ban_user(ip_adress)
                                banned_users[username] = (
                                    time.time()
                                )  # 차단 시작 시간 기록
                    else:
                        banned_users[username] = 1

        # 차단된 사용자 중 시간이 지난 사용자 차단 해제
        for username, ban_start_time in list(banned_users.items()):
            if time.time() - ban_start_time >= ban_time_minutes * 60:
                del banned_users[username]
                unban_user(username, ip_adress)

if __name__ == "__main__":
    while True:
        check_log()
        time.sleep(60)  # 1분마다 로그 확인