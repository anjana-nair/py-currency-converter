#!/usr/bin/env python3
"""
Currency Converter Script
Converts amounts between different currencies using live exchange rates.
"""

import requests
import json
from typing import Optional, Dict, List
import argparse
from datetime import datetime


class CurrencyConverter:
    """A class to handle currency conversion operations."""
    
    # Free API endpoint (no API key required)
    BASE_URL = "https://api.exchangerate-api.com/v4/latest"
    
    def __init__(self):
        """Initialize the converter with exchange rate cache."""
        self.cache: Dict[str, Dict] = {}
    
    def get_exchange_rates(self, base_currency: str) -> Optional[Dict]:
        """
        Fetch exchange rates for a given base currency.
        
        Args:
            base_currency: The base currency code (e.g., 'USD', 'EUR')
            
        Returns:
            Dictionary with exchange rates or None if request fails
        """
        base_currency = base_currency.upper()
        
        # Return cached result if available
        if base_currency in self.cache:
            return self.cache[base_currency]
        
        try:
            response = requests.get(f"{self.BASE_URL}/{base_currency}", timeout=5)
            response.raise_for_status()
            data = response.json()
            self.cache[base_currency] = data
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error fetching exchange rates: {e}")
            return None
    
    def convert(self, amount: float, from_currency: str, to_currency: str) -> Optional[float]:
        """
        Convert an amount from one currency to another.
        
        Args:
            amount: The amount to convert
            from_currency: Source currency code
            to_currency: Target currency code
            
        Returns:
            Converted amount or None if conversion fails
        """
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        
        if amount < 0:
            print("Error: Amount cannot be negative")
            return None
        
        rates_data = self.get_exchange_rates(from_currency)
        if not rates_data:
            return None
        
        rates = rates_data.get('rates', {})
        
        if to_currency not in rates:
            print(f"Error: Currency '{to_currency}' not found")
            return None
        
        conversion_rate = rates[to_currency]
        converted_amount = amount * conversion_rate
        return converted_amount
    
    def get_supported_currencies(self, base_currency: str = "USD") -> Optional[List[str]]:
        """
        Get list of all supported currencies.
        
        Args:
            base_currency: Reference currency for fetching the list
            
        Returns:
            List of supported currency codes or None if request fails
        """
        rates_data = self.get_exchange_rates(base_currency)
        if not rates_data:
            return None
        
        currencies = list(rates_data.get('rates', {}).keys())
        currencies.insert(0, base_currency)  # Add base currency to the list
        return sorted(currencies)


def main():
    """Main function to run the currency converter from command line."""
    parser = argparse.ArgumentParser(
        description="Convert currencies using live exchange rates"
    )
    parser.add_argument(
        "amount",
        type=float,
        help="Amount to convert"
    )
    parser.add_argument(
        "from_currency",
        help="Source currency code (e.g., USD, EUR, GBP)"
    )
    parser.add_argument(
        "to_currency",
        help="Target currency code (e.g., USD, EUR, GBP)"
    )
    parser.add_argument(
        "--list-currencies",
        action="store_true",
        help="List all supported currencies"
    )
    
    args = parser.parse_args()
    
    converter = CurrencyConverter()
    
    # List currencies if requested
    if args.list_currencies:
        print("Fetching supported currencies...")
        currencies = converter.get_supported_currencies()
        if currencies:
            print(f"\nSupported currencies ({len(currencies)}):")
            # Print in columns
            for i, currency in enumerate(currencies, 1):
                print(f"  {currency}", end="  " if i % 5 != 0 else "\n")
            print()
        return
    
    # Perform conversion
    result = converter.convert(args.amount, args.from_currency, args.to_currency)
    
    if result is not None:
        print(f"\n{args.amount} {args.from_currency.upper()} = {result:.2f} {args.to_currency.upper()}")
        print(f"Conversion timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    else:
        print("Conversion failed. Please check your input.\n")


if __name__ == "__main__":
    main()
