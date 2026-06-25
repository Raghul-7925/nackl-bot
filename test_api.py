"""
Quick test: verify the GraphQL queries against the live Acki Nacki endpoint.
Run: python test_api.py
"""
import asyncio
import httpx
import json

GRAPHQL = "https://mainnet.ackinacki.org/graphql"

# raghul's MvMultifactor address (from the screenshot)
TEST_ACCOUNT = "8c478bedb9ffdb890f1e82de78d5edbb0f2af2d4162952a41a99ab9c22871ae7"
# raghul's Indexer address (from response.txt)
TEST_INDEXER = "a432f6f5c777d59c202033c16216d0c1b5569d1bebb9ffeaa8dc4dd3d9dd1718"

async def gql(client, query, variables):
    resp = await client.post(
        GRAPHQL,
        content=json.dumps({"query": query, "variables": variables}),
        headers={"Content-Type": "text/plain", "Origin": "https://acki.live"},
        timeout=15,
    )
    data = resp.json()
    if "errors" in data:
        raise ValueError(data["errors"][0]["message"])
    return data["data"]

async def main():
    async with httpx.AsyncClient() as client:

        print("=" * 60)
        print("Test 1: Get MvMultifactor account info")
        print("=" * 60)
        q1 = """
        query GetAccountInfo($accountId: String!, $dappId: String!) {
          blockchain {
            account(account_id: $accountId, dapp_id: $dappId) {
              info {
                balance(format: DEC)
                balance_other { currency value(format: DEC) }
                last_paid
                code_hash
                dapp_id
              }
            }
          }
        }
        """
        d1 = await gql(client, q1, {"accountId": TEST_ACCOUNT, "dappId": TEST_ACCOUNT})
        info = d1["blockchain"]["account"]["info"]
        print(f"SHELL balance: {int(info['balance']) / 1e9:.4f}")
        for bal in info.get("balance_other") or []:
            print(f"Currency {bal['currency']}: {int(bal['value']) / 1e9:.4f}")
        print(f"Code hash: {info['code_hash'][:16]}...")
        print(f"Dapp ID: {(info.get('dapp_id') or 'None')[:16]}...")

        print()
        print("=" * 60)
        print("Test 2: Get Indexer data (name resolution)")
        print("=" * 60)
        q2 = """
        query GetIndexerData($accountId: String!, $dappId: String!) {
          blockchain {
            account(account_id: $accountId, dapp_id: $dappId) {
              info { data code_hash }
            }
          }
        }
        """
        d2 = await gql(client, q2, {"accountId": TEST_INDEXER, "dappId": TEST_INDEXER})
        info2 = d2["blockchain"]["account"]["info"]
        print(f"Indexer code hash: {info2['code_hash'][:16]}...")
        print(f"Data length: {len(info2.get('data') or '')} chars (base64 BOC)")
        print("→ _wallet and _name decoded from BOC via TVM SDK")

        print()
        print("=" * 60)
        print("Test 3: Recent transactions for speed/taps")
        print("=" * 60)
        q3 = """
        query GetTxns($accountId: String!, $dappId: String!) {
          blockchain {
            account(account_id: $accountId, dapp_id: $dappId) {
              transactions(last: 10, allow_latest_inconsistent_data: true) {
                nodes {
                  id
                  now
                  balance_delta_other { currency value(format: DEC) }
                }
              }
            }
          }
        }
        """
        d3 = await gql(client, q3, {"accountId": TEST_ACCOUNT, "dappId": TEST_ACCOUNT})
        nodes = d3["blockchain"]["account"]["transactions"]["nodes"]
        print(f"Got {len(nodes)} transactions")
        nackl_sum = 0
        for tx in nodes:
            for d in tx.get("balance_delta_other") or []:
                if d["currency"] == 1 and int(d["value"]) > 0:
                    nackl_sum += int(d["value"])
        print(f"NACKL received in last 10 txns: {nackl_sum / 1e9:.4f}")

        print()
        print("✅ All queries working!")

asyncio.run(main())
