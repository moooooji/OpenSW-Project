import socket
import struct
import sys

# test1

def traceroute(destination):
    # 호스트명을 IP 주소로 변환
    dest_addr = socket.gethostbyname(destination)

    # ICMP 소켓 생성
    icmp = socket.getprotobyname('icmp')
    udp = socket.getprotobyname('udp')

    # 최대 TTL 값 설정
    max_hops = 30

    # 각 TTL 값에 대한 루프
    for ttl in range(1, max_hops + 1):
        # TTL 값을 IP 헤더에 포함시키기 위해 패킷 생성
        icmp_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
        icmp_sock.setsockopt(socket.SOL_IP, socket.IP_TTL, struct.pack('I', ttl))

        # ICMP 소켓 바인딩
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_sock.bind(('', 33434))

        # ICMP 소켓에 대한 주소 정보 가져오기
        icmp_sock.settimeout(3)
        try:
            icmp_sock.sendto(b"", (destination, 0))
            recv_packet, addr = icmp_sock.recvfrom(512)
            addr = addr[0]
            host = socket.gethostbyaddr(addr)[0]
        except socket.timeout:
            host = "*"
            addr = "*"
        finally:
            icmp_sock.close()
            udp_sock.close()

        # 결과 출력
        print(f"{ttl}\t{addr}\t{host}")

        # 목적지에 도달하면 종료
        if addr == dest_addr:
            break

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python traceroute.py <destination>")
        sys.exit(1)

    destination = sys.argv[1]
    traceroute(destination)
