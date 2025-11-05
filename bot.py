import os, sys, time
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from web3 import Web3
from eth_account import Account

try:
    from termcolor import colored
except Exception:
    def colored(x, *_args, **_kwargs): return x
try:
    import pyfiglet 
except Exception:
    pass
try:
    import colorama; colorama.init()
except Exception:
    pass

GREEN='green'; RED='red'; YELLOW='yellow'; CYAN='cyan'; MAGENTA='magenta'

def get_time_str():
    return colored(f"[{datetime.now().strftime('%H:%M:%S')}]", CYAN, attrs=['bold'])

def LG(msg,color=YELLOW): print(f"{get_time_str()} {colored(msg, color, attrs=['bold'])}")
def OK(msg): print(f"{get_time_str()} {colored(msg, GREEN, attrs=['bold'])}")
def ERR(msg): print(f"{get_time_str()} {colored(msg, RED, attrs=['bold'])}")
def WARN(msg): print(f"{get_time_str()} {colored(msg, YELLOW, attrs=['bold'])}")

def banner():
    print(colored(f"Asseto Subscribe Script", CYAN, attrs=['bold']))
    print(colored(f"Waktu Saat Ini: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\n", YELLOW))

def set_title():
    try:
        sys.stdout.write('\x1b]2;Asseto Subscribe Script\x1b\\'); sys.stdout.flush()
    except Exception:
        pass

def get_raw_tx(signed_tx):
    return getattr(signed_tx, 'rawTransaction', None) or getattr(signed_tx, 'raw_transaction')

RPC_URL='https://atlantic.dplabs-internal.com'
CHAIN_ID=688689
USDT_ADDRESS=Web3.to_checksum_address('0xe7e84b8b4f39c507499c40b4ac199b050e2882d5')
SUBSCRIBE_CONTRACT=Web3.to_checksum_address('0x56f4add11d723412d27a9e9433315401b351d6e3')

USDT_DECIMALS=6
SUBSCRIBE_AMOUNT_DEC='0.0001'
GAS_LIMIT_SUBSCRIBE=200000
SLEEP_BETWEEN_TX=1.0

ERC20_ABI=[
    {"constant":True,"inputs":[{"name":"owner","type":"address"},{"name":"spender","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"type":"function"},
    {"constant":False,"inputs":[{"name":"spender","type":"address"},{"name":"value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"type":"function"},
    {"constant":True,"inputs":[{"name":"owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"type":"function"},
    {"constant":True,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"type":"function"},
]

SUBSCRIBE_ABI=[
    {"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"subscribe","outputs":[],"stateMutability":"nonpayable","type":"function"}
]

def load_private_keys_from_env():
    items=[]
    for k,v in os.environ.items():
        if k.upper().startswith('PRIVATEKEY_') and v.strip():
            try:
                order=int(k.split('_',1)[1])
            except Exception:
                order=999999
            items.append((order,v.strip()))
    items.sort(key=lambda x:x[0])
    keys=[]
    for _,val in items:
        pk=val.strip()
        if pk.startswith('0X'):
            pk='0x'+pk[2:]
        if not pk.startswith('0x'):
            pk='0x'+pk
        keys.append(pk)
    return keys

def usdt_units(amount_dec_str):
    from decimal import Decimal,ROUND_DOWN,getcontext
    getcontext().prec=50
    return int((Decimal(amount_dec_str)*(Decimal(10)**USDT_DECIMALS)).to_integral_exact(rounding=ROUND_DOWN))

def approve_usdt_if_needed(w3,account,required_units):
    address=account.address
    erc20=w3.eth.contract(address=USDT_ADDRESS,abi=ERC20_ABI)
    try:
        current=erc20.functions.allowance(address,SUBSCRIBE_CONTRACT).call()
        if current>=required_units:
            return True
        if current>0:
            tx=erc20.functions.approve(SUBSCRIBE_CONTRACT,0).build_transaction({
                'from':address,
                'nonce':w3.eth.get_transaction_count(address),
                'gas':60000,
                'gasPrice':w3.eth.gas_price,
                'chainId':CHAIN_ID
            })
            signed=account.sign_transaction(tx)
            txh=w3.eth.send_raw_transaction(get_raw_tx(signed))
            OK(f"Reset allowance to 0 | TX: {txh.hex()}")
            w3.eth.wait_for_transaction_receipt(txh)
        MAX_UINT256=(1<<256)-1
        tx=erc20.functions.approve(SUBSCRIBE_CONTRACT,MAX_UINT256).build_transaction({
            'from':address,
            'nonce':w3.eth.get_transaction_count(address),
            'gas':80000,
            'gasPrice':w3.eth.gas_price,
            'chainId':CHAIN_ID
        })
        signed=account.sign_transaction(tx)
        txh=w3.eth.send_raw_transaction(get_raw_tx(signed))
        OK(f"Approve unlimited | TX: {txh.hex()}")
        w3.eth.wait_for_transaction_receipt(txh)
        OK("USDT approval completed.")
        return True
    except Exception as e:
        ERR(f"Approval error: {e}")
        return False

def do_assetto_subscribe_like_js(w3, account, subscribe_count):
    address=account.address
    LG(f"Starting Assetto for wallet {address}")
    erc20=w3.eth.contract(address=USDT_ADDRESS,abi=ERC20_ABI)
    subscribe=w3.eth.contract(address=SUBSCRIBE_CONTRACT,abi=SUBSCRIBE_ABI)
    try:
        bal=erc20.functions.balanceOf(address).call()
        OK(f"USDT balance (base units): {bal}")
        if bal==0:
            WARN("No USDT detected. Skipping this wallet.")
            return
    except Exception as e:
        ERR(f"Balance check failed: {e}")
        return
    need_per_call=usdt_units(SUBSCRIBE_AMOUNT_DEC)
    total_required=need_per_call * subscribe_count
    if not approve_usdt_if_needed(w3,account,total_required):
        return
    nonce=w3.eth.get_transaction_count(address)
    gas_price=w3.eth.gas_price
    
    OK(f"Executing {subscribe_count}x subscribe | amount={SUBSCRIBE_AMOUNT_DEC} USDT | gasLimit={GAS_LIMIT_SUBSCRIBE}")
    succ=0; fail=0
    for i in range(1, subscribe_count + 1):
        try:
            tx=subscribe.functions.subscribe(USDT_ADDRESS,need_per_call).build_transaction({
                'from':address,
                'nonce':nonce,
                'gas':GAS_LIMIT_SUBSCRIBE,
                'gasPrice':gas_price,
                'chainId':CHAIN_ID,
                'value':0
            })
            signed=account.sign_transaction(tx)
            txh=w3.eth.send_raw_transaction(get_raw_tx(signed))
            LG(f"[{i}/{subscribe_count}] Sent: {txh.hex()}", MAGENTA)
            rc=w3.eth.wait_for_transaction_receipt(txh)
            if rc and rc.get('status',0)==1:
                succ+=1
                OK(f"[{i}/{subscribe_count}] Subscribe succeeded")
            else:
                fail+=1
                WARN(f"[{i}/{subscribe_count}] Subscribe reverted (status != 1)")
            nonce+=1
            time.sleep(SLEEP_BETWEEN_TX)
        except Exception as e:
            fail+=1
            ERR(f"[{i}/{subscribe_count}] Subscribe failed: {e}")
            try:
                nonce = w3.eth.get_transaction_count(address)
            except Exception as e_nonce:
                ERR(f"Gagal mendapatkan nonce baru: {e_nonce}")
                nonce += 1
            time.sleep(SLEEP_BETWEEN_TX)
    OK(f"Finished subscribe loop: success {succ}, failed {fail}")

def main():
    set_title()
    banner()
    
    SUBSCRIBE_COUNT = 0
    try:
        sub_count_str = input(colored(f"> Masukkan jumlah subscribe (1-1000): ", CYAN, attrs=['bold']))
        SUBSCRIBE_COUNT = int(sub_count_str)
        if not (1 <= SUBSCRIBE_COUNT <= 1000):
            raise ValueError("Jumlah harus antara 1 dan 1000")
    except ValueError as e:
        ERR(f"Input tidak valid: {e}")
        sys.exit(1)
    
    OK(f"Akan menjalankan {SUBSCRIBE_COUNT} subscribe per wallet.\n")

    w3=Web3(Web3.HTTPProvider(RPC_URL,request_kwargs={'timeout':60}))
    if not w3.is_connected():
        ERR("RPC connection failed. Check your endpoint/connectivity.")
        sys.exit(1)
    keys=load_private_keys_from_env()
    if not keys:
        ERR("No PRIVATEKEY_1 / PRIVATEKEY_2 / ... found in .env")
        sys.exit(1)
    OK(f"{len(keys)} private key(s) loaded. Running Assetto for each wallet...")
    for idx,pk in enumerate(keys,start=1):
        try:
            account=Account.from_key(pk)
        except Exception as e:
            ERR(f"[Wallet #{idx}] Invalid private key: {e}")
            continue
        OK(f"[Wallet #{idx}] Address: {colored(account.address, MAGENTA)}")
        do_assetto_subscribe_like_js(w3, account, SUBSCRIBE_COUNT)
    OK("All done. Have fun!")

if __name__=='__main__':
    main()
