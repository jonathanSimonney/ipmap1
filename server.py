# !/usr/bin/env python

# multiprocessing, threading
import argparse
import asyncio
import sys

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


async def handle(request):
    ip = request.match_info.get('ip', "")
    if ip == "":
        text = "Hello"
    else:
        # Gather uname and date commands

        print('nmap', '-sV', ip)

        commands = run_command('nmap', '-sV', ip)

        result = await commands

        text = str(format(result))
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


main()
