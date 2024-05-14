# Ali Express webscraper

## Description
This script allows fetching n number of trending products in a specific category from Aliexpress

## Tools and Libraries
- Selenium
- Pandas

## Usage
- Create a virtual environment
```sh
python3 -m venv .venv  # Unix/macOS
py -m venv .venv       # Windows
```

- Activate the virtual environment
```sh
source .venv/bin/activate  # Unix/macOS
.venv\Scripts\activate       # Windows
```

- Install dependencies
```sh
pip install -r requirements.txt
```

- Run script to fetch products
```sh
python ali_express.py <category-name> <number-of-products> # example python ali_express.py Shoes 60  
```

- A new file called trending_products.csv is generated or updated