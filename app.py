from flask import Flask, request, jsonify
import yaml
import logging, os, requests
import datetime

# Priority example: r = requests.get(f"{API_URL}{COMPANY}/LOGPART('{PARTNAME}')/PARTTEXT_SUBFORM", auth=(PRIORITY_API_USERNAME, PRIORITY_API_PASSWORD))

app = Flask(__name__)

config = yaml.safe_load(open("config.yml"))

#region Global variables
COMPANY = config["COMPANY"]
API_URL = config["API_URL"]
PRIORITY_API_USERNAME= config["PRI_API_USERNAME"]
PRIORITY_API_PASSWORD= config["PRI_API_PASSWORD"]
ONETRAIL_USERNAME= config["ONETRAIL_USERNAME"]
ONETRAIL_PASSWORD= config["ONETRAIL_PASSWORD"]
#endregion

# Set up error logger.
path = r"error.log"
assert os.path.isfile(path)
logging.basicConfig(filename=path, level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logging.info('Flask server started.')

#region Endpoint definitions
@app.route("/Onetrail/")
def home():
    return "This is the Onetrail App on IIS Server to handle Price & Availability within Priority."

@app.route("/Onetrail/GetProductData/", methods = ['POST'])
def get_product_data():
    PARTNAME = request.get_json()['ZOTR_PRICEANDSTOCK']['PARTNAME']
    r = requests.get(f"https://services.onetrail.net/pde/rest/v5/products/?&SellerVPN={PARTNAME}", auth=(ONETRAIL_USERNAME, ONETRAIL_PASSWORD), headers={'Accept': 'application/json'})
    data = r.json()
    product = data['productType']['product']
    seller_info = product[0]['sellerInfo']
    # print(seller_info)
    
    responses = []
    for item in seller_info:
        GLN = item['partnerId']
        price = item['priceInfo']['productPrices'][0]['price']['value']
        stock = item['stockInfo']['warehouses'][0]['stock']
        ATPDate = item['stockInfo']['warehouses'][0]['ATPDate']
        
        
        final_data = {
            'PARTNAME': str(PARTNAME),
            'GLN': str(GLN),
            'PRICE': float(price),
            'STOCK': float(stock),
            # 'ATPDATE': str(datetime.datetime.strptime(ATPDate, "%Y%m%dT%H%M%S").strftime('%Y-%m-%dT%H:%M:%S'))
            # 'ATPDATE': ATPDate
        }
        
        # post if doesnt exist, patch if exists
        # OR add date to composite key, and post every time. dangerous.
        r = requests.post(f"{API_URL}{COMPANY}/ZOTR_PRICEANDSTOCK", json=final_data, auth=(PRIORITY_API_USERNAME, PRIORITY_API_PASSWORD))
        responses.append(r.json())
    
    return jsonify(responses)
        


