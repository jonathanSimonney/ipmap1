# !/usr/bin/env python

# multiprocessing, threading
import argparse
import asyncio
import sys
import xmltodict
import json

from my_lru_cache import lru_cache
from aiohttp import web
if sys.platform == 'win32':
    loop = asyncio.ProactorEventLoop()
    asyncio.set_event_loop(loop)


@lru_cache(maxsize=32)
async def run_command(*args):
    # Create subprocess
    process = await asyncio.create_subprocess_exec(
        *args,
        # stdout must a pipe to be accessible as process.stdout
        stdout=asyncio.subprocess.PIPE)
    # Wait for the subprocess to finish
    stdout, stderr = await process.communicate()
    # Return stdout
    return stdout.decode().strip()


async def scan_single_port(future, port_scanned):
    commands = run_command('nmap', '-sV', '-oX', '-', port_scanned)

    result = await commands

    xml_text = str(format(result))
    scan_result = xmltodict.parse(xml_text)

    if 'host' in scan_result['nmaprun']:
        future_result = scan_result['nmaprun']['host']
    else:
        future_result = None
    future.set_result(future_result)


async def handle(request):
    global dict_scanned_ip # shared across coroutines!!!

    ip = request.match_info.get('ip', "")
    if ip == "":
        text = "Hello"
    else:
        # Gather uname and date commands
        ip_array = ip.split('-')

        try:
            first_part_ip = ip_array[0]
            splitted_ip = first_part_ip.split('.')
            min_port = int(splitted_ip[len(splitted_ip) - 1])
            scanned_ip = '.'.join(splitted_ip[:len(splitted_ip) - 1])

            print(min_port, scanned_ip)

            max_port = int(ip_array[1])

            elem_to_scan = []
            for port_number in range(min_port, max_port + 1):
                elem_to_scan.append(scanned_ip + '.' + str(port_number))
        except IndexError:
            elem_to_scan = ip_array

        scan_result = []

        for scanned_ip in elem_to_scan:
            if scanned_ip not in dict_scanned_ip:
                future = asyncio.Future()
                asyncio.ensure_future(scan_single_port(future, scanned_ip))
                dict_scanned_ip[scanned_ip] = future
            scan_result.append(dict_scanned_ip[scanned_ip])

        list_to_parse = []
        await asyncio.wait(scan_result)
        for future in scan_result:
            list_to_parse.append(future.result())

        json_text = str(json.dumps(list_to_parse))
        text = json_text
    return web.Response(text=text)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port")

    parser.add_argument("--host")
    args = parser.parse_args()

    print(int(args.port), args.host)
    app = web.Application()
    app.router.add_get('/{ip}', handle)

    web.run_app(app, host=args.host, port=int(args.port))


dict_scanned_ip = dict()  # shared across coroutines!!!
main()
