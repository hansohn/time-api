# -*- coding: utf-8 -*-
# MIT License
#
# Copyright (c) 2020 Ryan Hansohn
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Queries url X times per second and records success/failure and Time to last byte

"""

import argparse
import aiohttp
import asyncio
import os
import statistics
import time
import typing


class SimpleLoadTest():
    """
    Simple load test using async to query url X times per second and return
    basic metrics.
    """

    def time_delta(self, stime=0.0) -> float:
        """Returns time delta since initial def call"""
        return time.monotonic() - stime

    async def fetch(self, session: aiohttp.ClientSession, url: str, req_num: int, verbose: bool) -> typing.Tuple:
        """Fetch url and compute metrics"""
        req_start = self.time_delta()
        try:
            response = await session.get(url)
        except asyncio.TimeoutError:
            return 500, 0.0
        except aiohttp.ClientConnectionError:
            return 500, 0.0
        status_code = response.status
        time_to_last_byte = self.time_delta(req_start)
        response.close()
        if verbose:
            if status_code == 200:
                status = 'PASS'
            else:
                status = 'FAIL'
            print(f'req={req_num} status={status} url=\'{url}\' status_code={status_code} ttlb={time_to_last_byte:.3f} secs')
        return status_code, time_to_last_byte

    async def bound_fetch(self,
                          sem: asyncio.BoundedSemaphore,
                          session: aiohttp.ClientSession,
                          url: str,
                          req_num: int,
                          verbose: bool) -> typing.Tuple:
        """Initiate fetch concurrency up to Semaphore limit"""
        async with sem:
            sc, ttlb = await self.fetch(session, url, req_num, verbose)
        return sc, ttlb

    async def run(self,
                  url: str,
                  count: int,
                  rate: int,
                  threads: int,
                  verbose: bool = False) -> typing.Tuple:
        """Initiate Client Session and trigger fetch with Semaphore"""
        tasks = []
        sem = asyncio.BoundedSemaphore(threads)
        connector = aiohttp.TCPConnector(limit=0)
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            for i in range(count):
                req_num = i+1
                task = asyncio.ensure_future(self.bound_fetch(sem, session, url, req_num, verbose))
                tasks.append(task)
                await asyncio.sleep(1/rate)
            responses = asyncio.gather(*tasks)
            await responses
            return responses.result()


if __name__ == "__main__":
    # help
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", type=str, default=os.environ.get('SIMPLE_TARGET', 'https://www.google.com/'), help="target url to load test")
    parser.add_argument("-c", "--count", type=int, default=os.environ.get('SIMPLE_COUNT', 1000), help="total requests to send in load test")
    parser.add_argument("-r", "--rate", type=int, default=os.environ.get('SIMPLE_RATE', 100), help="target requests per sec")
    parser.add_argument("-t", "--threads", type=int, default=os.environ.get('SIMPLE_THREADS', 100), help="max allowed concurrent request")
    parser.add_argument("-v", "--verbose", default=os.environ.get('SIMPLE_VERBOSE', False), help="enable detailed fetch logging", action="store_true")
    args = parser.parse_args()

    # begin test
    obj = SimpleLoadTest()
    h = (f'[-- SIMPLE LOAD TEST --]\n'
         f'\n'
         f'[params]\n'
         f'target url: \'{args.url}\'\n'
         f'request count: {args.count}\n'
         f'requests per sec: {args.rate}\n'
         f'max threads: {args.threads}\n'
         f'\n'
         f'test in progress ...')
    print(h)
    loop = asyncio.get_event_loop()
    try:
        start = obj.time_delta()
        responses = loop.run_until_complete(obj.run(args.url, args.count, args.rate, args.threads, args.verbose))
        end = obj.time_delta(start)
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()

    print(f'test complete! please wait while we gather metrics ...')

    # compute metrics
    status_codes = [t[0] for t in responses]
    reqs_per_sec = len(status_codes) / end
    passed = status_codes.count(200)
    failed = len(status_codes) - passed
    ttlbs = [t[1] for t in responses]
    avg_ttlb = sum(ttlbs) / len(ttlbs)
    ttlb_avg_mean = statistics.mean(ttlbs)
    ttlb_avg_median = statistics.median(ttlbs)

    # msg
    m = (f'\n'
         f'[results]\n'
         f'total requests sent: {len(status_codes)}\n'
         f'requests per sec: {reqs_per_sec:.1f}\n'
         f'passed: {passed}, failed: {failed}\n'
         f'ttlb mean avg: {ttlb_avg_mean:.3f} seconds\n'
         f'ttlb median avg: {ttlb_avg_median:.3f} seconds\n'
         f'\n'
         f'Load test completed in {end:.3f} seconds')
    print(m)
