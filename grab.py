# Shopee Product Scrapper v1.0
# heryandp

import requests as req
import os,glob, json
import csv
from json_excel_converter import Converter 
from json_excel_converter.xlsx import Writer

#UA
base_url = "https://shopee.co.id"
header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}

# grab detil seller
def grab_d_seller(sellername):
    url_seller = base_url+"/api/v4/shop/get_shop_detail?username="+sellername
    grab_seller = req.get(url_seller,headers=header).json()
    # print(grab_seller)
    data_seller = {
        "name" : grab_seller["data"]["name"],
        "userid" : grab_seller["data"]["userid"],
        "shopid" : grab_seller["data"]["shopid"],
        "shopid" : grab_seller["data"]["shopid"],
        "rating" : grab_seller["data"]["rating_star"],
        "follower" : grab_seller["data"]["follower_count"],
        # "total_item" : grab_seller["data"]["item_count"],
        "shop_location" : grab_seller["data"]["shop_location"],
        "country" : grab_seller["data"]["country"]
    }
    print(data_seller)

# grab detil seller (id)
def grab_id_seller(sellername):
    url_seller = base_url+"/api/v4/shop/get_shop_detail?username="+sellername
    grab_seller = req.get(url_seller,headers=header).json()
    return str(grab_seller["data"]["shopid"])

def grab_produk(seller_id):
    url_total = base_url+"/api/v4/shop/search_items?limit=1&offset=0&shopid="+seller_id
    cek_total = req.get(url_total,headers=header).json()
    print("[+] Total Produk : "+str(cek_total["total_count"]))
    
    print("[+] Hapus file lama ...")
    for filename in glob.glob("data/"+seller_id+"*.json"):
        os.remove(filename)
    for filename in glob.glob(seller_id+".csv"):
        os.remove(filename)

    print("[+] Mulai download produk ...")
    a = 0
    b = 0
    while (True):
        print("-> download halaman "+ str(b))
        url_produk = base_url+"/api/v4/shop/search_items?limit=100&offset="+str(a)+"&shopid="+seller_id
        cek_produk = req.get(url_produk,headers=header).json()
        if (cek_produk["total_count"]==0):
            break
        else:
            # for product in cek_produk['items']:
            #     print(product['item_basic']['name'])
            with open("data/"+seller_id+"_"+str(b)+'.json', 'w') as json_file:
                json.dump(cek_produk["items"], json_file)
            a = a + 100
            b = b + 1

    # merging json
    print("[+] Merging data produk ...")
    data = []
    for f in glob.glob("data/"+seller_id+"*.json"):
        with open(f,) as infile:
            data.extend(json.load(infile))
    with open("data/"+seller_id+"_all.json",'w') as outfile:
        json.dump(data, outfile)
    # create csv
    print("[+] Membuat csv data produk ...")
    f_data = []
    f = open("data/"+seller_id+"_all.json")
    f_read = json.load(f)
    for i in f_read:
        if(i['item_basic']['price_min_before_discount']==-1):
            pminbd = 0
        else:
            pminbd = i['item_basic']['price_min_before_discount']/100000
        if(i['item_basic']['price_max_before_discount']==-1):
            pmaxbd = 0
        else:
            pmaxbd = i['item_basic']['price_max_before_discount']/100000
        f_data.append([
            i['item_basic']['shopid'],
            i['item_basic']['itemid'],
            i['item_basic']['name'],
            i['item_basic']['stock'],
            i['item_basic']['sold'],
            i['item_basic']['historical_sold'],
            i['item_basic']['brand'],
            i['item_basic']['liked_count'],
            i['item_basic']['price']/100000,
            i['item_basic']['price_min']/100000,
            i['item_basic']['price_max']/100000,
            pminbd,
            pmaxbd,
            i['item_basic']['discount'],
            ])
    f_header = ['shopid','itemid','produk','stok','terjual','histori_terjual','brand','jml_like','harga','harga_min','harga_max','harga_min_sebelum_disc','harga_max_sebelum_disc','diskon']
    with open(seller_id+'.csv', 'w',newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(f_header)
        writer.writerows(f_data)
    f.close()
    print("done! "+seller_id+".csv")

print("[ SHOPEE-PRODUCT-GRABBER v1.0 by heryan ]")
print("")
print("cth. username (link toko) https://shopee.co.id/aoki_official_store => (username) aoki_official_store")
print("")
sname = input("[+] Masukkan username seller: ")        
print("====== DETAIL SELLER ======")
grab_d_seller(sname)
print("====== GRABBING PRODUK ======")
grab_produk(grab_id_seller(sname))