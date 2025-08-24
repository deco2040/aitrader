# mcp_client.py - 핵심만
import subprocess
import json
import asyncio
import logging


class MCPClient:

    def __init__(self):
        self.cache = {}

    async def fetch_ticker(self, symbol):
        """티커 조회"""
        cmd = f'echo \'{{"method": "ccxt_fetch_ticker", "params": {{"symbol": "{symbol}"}}}}\' | npx @lazydino/ccxt-mcp'
        result = await self._run_cmd(cmd)

        if result:
            self.cache['ticker'] = result
            return result
        return self.cache.get('ticker', {})

    async def fetch_balance(self):
        """잔고 조회"""
        cmd = f'echo \'{{"method": "ccxt_fetch_balance", "params": {{}}}}\' | npx @lazydino/ccxt-mcp'
        result = await self._run_cmd(cmd)

        if result:
            self.cache['balance'] = result
            return result
        return self.cache.get('balance', {})

    async def create_order(self, symbol, type, side, amount, price=None):
        """주문 생성"""
        params = {
            "symbol": symbol,
            "type": type,
            "side": side,
            "amount": amount
        }
        if price:
            params["price"] = price

        cmd = f'echo \'{{"method": "ccxt_create_order", "params": {json.dumps(params)}}}\' | npx @lazydino/ccxt-mcp'
        return await self._run_cmd(cmd)

    async def _run_cmd(self, cmd):
        """명령 실행"""
        try:
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE)
            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                return json.loads(stdout.decode())
            else:
                logging.error(f"MCP 오류: {stderr.decode()}")
                return None

        except Exception as e:
            logging.error(f"MCP 실행 실패: {e}")
            return None
