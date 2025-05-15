import requests
import re

DEBANK_API_KEY = " -- "  # API Key

def is_valid_eth_address(address: str) -> bool:
    return bool(re.match(r"^0x[a-fA-F0-9]{40}$", address))

def fetch_portfolio(wallet_address: str) -> list:
    url = "https://pro-openapi.debank.com/v1/user/all_complex_protocol_list"
    headers = {
        "accept": "application/json",
        "AccessKey": DEBANK_API_KEY
    }
    params = {
        "id": wallet_address
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"API request failed: {e}")
        return []

def extract_positions(protocols: list):
    staking = []
    all_positions = []

    for protocol in protocols:
        protocol_name = protocol.get("name", "Unknown Protocol")
        items = protocol.get("portfolio_item_list", [])

        for item in items:
            item_name = item.get("name", "").lower()
            detail_types = [t.lower() for t in item.get("detail_types", [])]

            # Extract supply tokens (positions)
            supply_tokens = item.get("detail", {}).get("supply_token_list", [])
            for token in supply_tokens:
                position = {
                    "protocol": protocol_name,
                    "category": item.get("name", "Other"),
                    "token": token.get("symbol"),
                    "amount": token.get("amount", 0),
                    "usd_value": token.get("amount", 0) * token.get("price", 0)
                }
                all_positions.append(position)

                # If staking, also include in separate list
                if "staked" in item_name or "staked" in detail_types:
                    staking.append(position)

    return staking, all_positions

def main():
    print("🔍 DeBank DeFi Position Viewer\n")
    wallet_address = input("Enter your wallet address (0x...): ").strip()

    if not is_valid_eth_address(wallet_address):
        print("❌ Invalid wallet address.")
        return

    print("\n📡 Fetching data from DeBank...")
    data = fetch_portfolio(wallet_address)
    staking, all_positions = extract_positions(data)

    print("\n🔒 Staking Positions:")
    if staking:
        for pos in staking:
            print(f"  {pos['protocol']} | {pos['token']}: {pos['amount']:.4f} (${pos['usd_value']:.2f})")
    else:
        print("  None found.")

    print("\n🌐 All DeFi Positions:")
    if all_positions:
        for pos in all_positions:
            print(f"  {pos['protocol']} [{pos['category']}] | {pos['token']}: {pos['amount']:.4f} (${pos['usd_value']:.2f})")
    else:
        print("  No DeFi positions found.")

if __name__ == "__main__":
    main()
