import urllib.request
import json

def get_ip_location(ip_address):
    # ipinfo.io에서 제공하는 무료 API URL 구성
    url = f"http://ipinfo.io/{ip_address}/json"

    # urllib을 사용하여 HTTP 요청 수행
    with urllib.request.urlopen(url) as response:
        # 응답 데이터를 읽고 JSON으로 파싱
        data = json.loads(response.read().decode())

    return data

# 테스트 IP 주소로 함수 호출
ip_address = '8.8.8.8'  # Google의 공개 DNS 서버 IP
location_info = get_ip_location(ip_address)

print(location_info)