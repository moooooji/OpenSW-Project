import re

log_data = """
Mar 25 16:42:09 parkvm sshd[3794]: Accepted password for park from 192.168.149.1 port 53194 ssh2
Mar 25 16:42:09 parkvm sshd[3794]: pam_unix(sshd:session): session opened for user park(uid=1000) by (uid=0)
Mar 25 16:42:09 parkvm systemd-logind[838]: New session 7 of user park.
"""

# IP 주소 추출을 위한 정규 표현식
ip_pattern = r'from (\d+\.\d+\.\d+\.\d+)'

# 사용자 이름 추출을 위한 정규 표현식
user_pattern = r'session opened for user (\w+)'

# 세션 번호 추출을 위한 정규 표현식
session_pattern = r'New session (\d+) of user (\w+)'

# 각 정규 표현식을 사용하여 데이터 추출
ip_match = re.search(ip_pattern, log_data)
user_match = re.search(user_pattern, log_data)
session_match = re.search(session_pattern, log_data)

# 추출한 데이터 출력
if ip_match:
    print("ip_adress:", ip_match.group(1))
else:
    print("IP 주소를 찾을 수 없습니다.")

if user_match:
    print("user_name:", user_match.group(1))
else:
    print("사용자 이름을 찾을 수 없습니다.")

if session_match:
    print("session_number:", session_match.group(1))
    print("user_name:", session_match.group(2))
else:
    print("세션 정보를 찾을 수 없습니다.")
