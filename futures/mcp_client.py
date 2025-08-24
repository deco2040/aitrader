
# mcp_client.py - 선물 거래 전용
import subprocess
import json
import asyncio
import logging


class FuturesMCPClient:

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
        """잔고 조회 (선물 계정)"""
        cmd = f'echo \'{{"method": "ccxt_fetch_balance", "params": {{}}}}\' | npx @lazydino/ccxt-mcp'
        result = await self._run_cmd(cmd)

        if result:
            self.cache['balance'] = result
            return result
        return self.cache.get('balance', {})

    async def fetch_positions(self, symbol=None):
        """포지션 조회 (선물 전용)"""
        params = {"symbol": symbol} if symbol else {}
        cmd = f'echo \'{{"method": "ccxt_fetch_positions", "params": {json.dumps(params)}}}\' | npx @lazydino/ccxt-mcp'
        result = await self._run_cmd(cmd)

        if result:
            self.cache['positions'] = result
            return result
        return self.cache.get('positions', [])

    async def create_market_order(self, symbol, side, amount, leverage=None):
        """시장가 주문 (선물)"""
        params = {
            "symbol": symbol,
            "type": "market",
            "side": side,
            "amount": amount
        }
        
        if leverage:
            params["leverage"] = leverage

        cmd = f'echo \'{{"method": "ccxt_create_order", "params": {json.dumps(params)}}}\' | npx @lazydino/ccxt-mcp'
        return await self._run_cmd(cmd)

    async def create_limit_order(self, symbol, side, amount, price, leverage=None):
        """지정가 주문 (선물)"""
        params = {
            "symbol": symbol,
            "type": "limit",
            "side": side,
            "amount": amount,
            "price": price
        }
        
        if leverage:
            params["leverage"] = leverage

        cmd = f'echo \'{{"method": "ccxt_create_order", "params": {json.dumps(params)}}}\' | npx @lazydino/ccxt-mcp'
        return await self._run_cmd(cmd)

    async def create_stop_order(self, symbol, side, amount, stop_price, leverage=None):
        """스탑 주문 (선물)"""
        params = {
            "symbol": symbol,
            "type": "stop_market",
            "side": side,
            "amount": amount,
            "stopPrice": stop_price
        }
        
        if leverage:
            params["leverage"] = leverage

        cmd = f'echo \'{{"method": "ccxt_create_order", "params": {json.dumps(params)}}}\' | npx @lazydino/ccxt-mcp'
        return await self._run_cmd(cmd)

    async def set_leverage(self, symbol, leverage):
        """레버리지 설정"""
        params = {
            "symbol": symbol,
            "leverage": leverage
        }

        cmd = f'echo \'{{"method": "ccxt_set_leverage", "params": {json.dumps(params)}}}\' | npx @lazydino/ccxt-mcp'
        return await self._run_cmd(cmd)

    async def set_margin_mode(self, symbol, margin_mode):
        """마진 모드 설정 (isolated/cross)"""
        params = {
            "symbol": symbol,
            "marginMode": margin_mode
        }

        cmd = f'echo \'{{"method": "ccxt_set_margin_mode", "params": {json.dumps(params)}}}\' | npx @lazydino/ccxt-mcp'
        return await self._run_cmd(cmd)

    async def cancel_order(self, order_id, symbol):
        """주문 취소"""
        params = {
            "id": order_id,
            "symbol": symbol
        }

        cmd = f'echo \'{{"method": "ccxt_cancel_order", "params": {json.dumps(params)}}}\' | npx @lazydino/ccxt-mcp'
        return await self._run_cmd(cmd)

    async def cancel_all_orders(self, symbol):
        """모든 주문 취소"""
        params = {"symbol": symbol}

        cmd = f'echo \'{{"method": "ccxt_cancel_all_orders", "params": {json.dumps(params)}}}\' | npx @lazydino/ccxt-mcp'
        return await self._run_cmd(cmd)

    async def fetch_funding_rate(self, symbol):
        """펀딩 비율 조회"""
        params = {"symbol": symbol}

        cmd = f'echo \'{{"method": "ccxt_fetch_funding_rate", "params": {json.dumps(params)}}}\' | npx @lazydino/ccxt-mcp'
        return await self._run_cmd(cmd)

    async def fetch_open_orders(self, symbol=None):
        """미체결 주문 조회"""
        params = {"symbol": symbol} if symbol else {}

        cmd = f'echo \'{{"method": "ccxt_fetch_open_orders", "params": {json.dumps(params)}}}\' | npx @lazydino/ccxt-mcp'
        return await self._run_cmd(cmd)

    async def close_position(self, symbol, side=None, amount=None):
        """포지션 청산"""
        # 현재 포지션 확인
        positions = await self.fetch_positions(symbol)
        
        if not positions:
            return None

        # 해당 심볼의 포지션 찾기
        position = next((p for p in positions if p['symbol'] == symbol and p['size'] != 0), None)
        
        if not position:
            return None

        # 반대 방향으로 시장가 주문
        close_side = 'sell' if position['side'] == 'long' else 'buy'
        close_amount = amount or abs(position['size'])

        return await self.create_market_order(symbol, close_side, close_amount)

    async def get_account_info(self):
        """계정 정보 조회 (마진 비율 등)"""
        cmd = f'echo \'{{"method": "ccxt_fetch_account", "params": {{}}}}\' | npx @lazydino/ccxt-mcp'
        result = await self._run_cmd(cmd)

        if result:
            self.cache['account'] = result
            return result
        return self.cache.get('account', {})

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

    # 편의 메서드들
    async def long_market(self, symbol, usdt_amount, leverage=None):
        """롱 포지션 진입 (시장가)"""
        ticker = await self.fetch_ticker(symbol)
        if not ticker:
            return None
            
        price = ticker['last']
        amount = usdt_amount / price
        
        return await self.create_market_order(symbol, 'buy', amount, leverage)

    async def short_market(self, symbol, usdt_amount, leverage=None):
        """숏 포지션 진입 (시장가)"""
        ticker = await self.fetch_ticker(symbol)
        if not ticker:
            return None
            
        price = ticker['last']
        amount = usdt_amount / price
        
        return await self.create_market_order(symbol, 'sell', amount, leverage)

    async def get_position_info(self, symbol):
        """특정 심볼 포지션 정보"""
        positions = await self.fetch_positions(symbol)
        
        if not positions:
            return None
            
        position = next((p for p in positions if p['symbol'] == symbol and p['size'] != 0), None)
        
        if not position:
            return {
                'symbol': symbol,
                'size': 0,
                'side': None,
                'unrealized_pnl': 0,
                'unrealized_pnl_percentage': 0,
                'liquidation_price': 0,
                'margin_ratio': 1.0
            }
            
        return position
