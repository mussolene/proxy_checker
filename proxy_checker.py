import concurrent.futures
import json
import os

import requests

proxy_filtered = []

for file in os.listdir("./"):
    if file.find("proxy") != -1 or file.find("Proxy") != -1:
        with open(file, "r") as f:
            lines = f.readlines()
            proxy_filtered = proxy_filtered + [line.strip() for line in lines]

l = set(proxy_filtered)
b = list(l)

proxy_filtered = b

valid_proxy = []


def get_proxy(proxy_list):
    with concurrent.futures.ThreadPoolExecutor(max_workers=500) as executor:
        future_to_proxy = {
            executor.submit(is_valid_proxy, proxy, "http://httpbin.org/ip", 60): proxy
            for proxy in proxy_list
        }
        for future in concurrent.futures.as_completed(future_to_proxy):
            proxy = future_to_proxy[future]
            try:
                data = future.result()
                if data is not None:
                    valid_proxy.append(data)
            except Exception as exc:
                print("%r generated an exception: %s" % (proxy, exc))


def is_valid_proxy(proxy, url, timout=5):
    rp = proxy.split(":")
    ret = {"protocols": [], "country_code": "", "ip": rp[0], "port": rp[1]}

    protocols = ["http", "socks5", "socks4", "socks4a", "socks5h"]

    for protocol in protocols:
        try:
            if protocol == "http":
                proxy_dict = {
                    "http": proxy,
                    "https": proxy,
                }
            else:
                proxy_dict = {
                    "http": protocol + "://" + proxy,
                    "https": protocol + "://" + proxy,
                }
            response = requests.get(url, proxies=proxy_dict, timeout=timout)
            if response.status_code == 200:
                ret["protocols"].append(protocol)
        except Exception as e:
            pass

    if len(ret["protocols"]) > 0:
        return ret
    else:
        return None


if __name__ == "__main__":
    get_proxy(proxy_filtered)
    json.dump(
        valid_proxy,
        open("valid_proxy2.json", "w"),
        indent=4,
        sort_keys=True,
        default=str,
        ensure_ascii=False,
    )
