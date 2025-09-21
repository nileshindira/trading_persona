"""
Dhan Data Extractor
Extract trading data from Dhan API
"""

import requests
import pandas as pd
from typing import Optional
from datetime import datetime

class DhanExtractor:
    """Extract trading data from Dhan"""
    
    def __init__(self, access_token: str, client_id: Optional[str] = None):
        self.access_token = access_token
        self.client_id = client_id
        self.base_url = "https://api.dhan.co"
        
    def extract_trades(self, 
                      from_date: str, 
                      to_date: str, 
                      output_file: Optional[str] = None) -> pd.DataFrame:
        """Extract all trades between dates"""
        
        trades = []
        page = 0
        
        while True:
            response = requests.post(
                f"{self.base_url}/v2/trades/historical",
                headers={
                    "access-token": self.access_token,
                    "Content-Type": "application/json"
                },
                json={
                    "from_date": from_date,
                    "to_date": to_date,
                    "page": page
                }
            )
            
            if response.status_code != 200:
                break
            
            data = response.json()
            if not data.get('data'):
                break
            
            trades.extend(data['data'])
            page += 1
            
            print(f"Fetched page {page}, total trades: {len(trades)}")
        
        # Convert to DataFrame
        df = pd.DataFrame(trades)
        
        # Rename columns to standard format
        df = df.rename(columns={
            'tradeDate': 'trade_date',
            'tradingSymbol': 'symbol',
            'transactionType': 'transaction_type',
            'tradedPrice': 'price',
            'tradedQuantity': 'quantity'
        })
        
        # Save to CSV if output file specified
        if output_file:
            df.to_csv(output_file, index=False)
            print(f"Saved {len(df)} trades to {output_file}")
        
        return df
