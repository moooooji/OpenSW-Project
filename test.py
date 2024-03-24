import ipinfo

access_token = "39bd4f67da2f8a"
handler = ipinfo.getHandler(access_token)
detail = handler.getDetails()
print(detail.all)