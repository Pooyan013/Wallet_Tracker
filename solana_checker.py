import time
import requests
from datetime import datetime
from config import HELIUS_KEY, ADMIN_ID, TELEGRAM_TOKEN
from db import get_wallets, get_last_signature, update_signature
import telebot

bot = telebot.TeleBot(TELEGRAM_TOKEN)
HELIUS = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_KEY}"

def get_signatures(address, before_signature=None):
    params = {"limit": 5}
    if before_signature:
        params["before"] = before_signature
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [address, params]
    }
    r = requests.post(HELIUS, json=payload)
    return r.json().get("result", [])

def get_transaction(signature):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [signature, {"encoding": "jsonParsed"}]
    }
    r = requests.post(HELIUS, json=payload)
    return r.json().get("result")

def format_spl_tx(tx):
    try:
        ts = tx["blockTime"]
        dt = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S') if ts else "نامشخص"
        meta = tx.get("meta", {})
        pre_token_balances = meta.get("preTokenBalances", [])
        post_token_balances = meta.get("postTokenBalances", [])
        tokens_moved = []

        for pre, post in zip(pre_token_balances, post_token_balances):
            pre_amount = pre["uiTokenAmount"].get("uiAmount") or 0
            post_amount = post["uiTokenAmount"].get("uiAmount") or 0
            diff = post_amount - pre_amount
            if diff != 0:
                mint = post["mint"]
                tokens_moved.append((mint, diff))

        if not tokens_moved:
            return None  

        msg = f"🕐 زمان تراکنش: {dt}\n"
        for mint, diff in tokens_moved:
            direction = "دریافت" if diff > 0 else "ارسال"
            msg += f"{abs(diff):.5f} توکن با mint: {mint} ({direction})\n"
        return msg

    except Exception as e:
        return f"خطا در پردازش تراکنش SPL: {e}"

def check_wallets():
    wallets = get_wallets()
    for address, name in wallets:
        last_sig = get_last_signature(address)
        signatures = get_signatures(address, before_signature=None)
        new_sigs = []
        for sig in signatures:
            if sig["signature"] == last_sig:
                break
            new_sigs.append(sig)
        new_sigs.reverse()

        for sig in new_sigs:
            tx = get_transaction(sig["signature"])
            if not tx:
                continue
            msg = format_spl_tx(tx)
            if msg:
                bot.send_message(ADMIN_ID, f"تراکنش جدید برای {name}:\n{msg}")
            update_signature(address, sig["signature"])

if __name__ == "__main__":
    while True:
        try:
            check_wallets()
            time.sleep(60) 
        except Exception as e:
            print("خطا در حلقه بررسی تراکنش‌ها:", e)
            time.sleep(30)
