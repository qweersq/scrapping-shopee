# Shopee Product Scrapper v1.0
# heryandp
# https://github.com/heryandp

import requests as req
import os,glob, json,time,csv

# Base Url
base_url = "https://shopee.co.id/"

class shopee():
    def __init__(self, usernametoko):
        self.tokourl = base_url+usernametoko
        self.namatoko = usernametoko
        self.headerbrowser = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}
        self.grab_id_seller()

    # grab detil seller (id)
    def grab_id_seller(self):
        try:
            url_seller = base_url+"api/v4/shop/get_shop_detail?username="+self.namatoko
            grab_seller = req.get(url_seller,headers=self.headerbrowser).json()
            self.data_seller = {
                "name" : grab_seller["data"]["name"],
                "userid" : grab_seller["data"]["userid"],
                "shopid" : grab_seller["data"]["shopid"],
                "shopid" : grab_seller["data"]["shopid"],
                "rating" : grab_seller["data"]["rating_star"],
                "follower" : grab_seller["data"]["follower_count"],
                "shop_location" : grab_seller["data"]["shop_location"],
                "country" : grab_seller["data"]["country"]
            }
            print("=== DETAIL SELLER ===")
            print(self.data_seller)
            self.idseller = grab_seller["data"]["shopid"]
            self.grab_produk()
        except:
            print("URL/Toko tidak valid!")

    def grab_produk(self):
        print("=== GRABBING PRODUK ===")
        url_total = base_url+"api/v4/shop/search_items?limit=1&offset=0&shopid="+str(self.idseller)
        cek_total = req.get(url_total,headers=self.headerbrowser).json()
        print("[+] Total Produk : "+str(cek_total["total_count"]))
        
        print("[+] Hapus file lama ...")
        if not os.path.exists("data"):
            os.makedirs("data")
        for filename in glob.glob("data/"+str(self.idseller)+"*.json"):
            os.remove(filename)
        for filename in glob.glob(str(self.idseller)+".csv"):
            os.remove(filename)

        print("[+] Mulai download produk ...")
        print("\x1B[3m" +"(delay 3 detik untuk menghindari anti-spam!)"+"\x1B[0m")
        a = 0
        b = 0
        while (True):
            print("-> download halaman "+ str(b))
            url_produk = base_url+"api/v4/shop/search_items?limit=100&offset="+str(a)+"&shopid="+str(self.idseller)
            cek_produk = req.get(url_produk,headers=self.headerbrowser).json()
            if (cek_produk["total_count"]==0):
                break
            else:
                with open("data/"+str(self.idseller)+"_"+str(b)+'.json', 'w') as json_file:
                    json.dump(cek_produk["items"], json_file)
                a = a + 100
                b = b + 1
                time.sleep(3)

        # merging json
        print("[+] Merging data produk ...")
        data = []
        for f in glob.glob("data/"+str(self.idseller)+"*.json"):
            with open(f,) as infile:
                data.extend(json.load(infile))
        with open("data/"+str(self.idseller)+"_all.json",'w') as outfile:
            json.dump(data, outfile)
        # create csv
        print("[+] Membuat csv data produk ...")
        f_data = []
        f = open("data/"+str(self.idseller)+"_all.json")
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
                self.namatoko,
                self.data_seller['name'],
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
        f_header = ['shopid','username_toko','nama_toko','itemid','produk','stok','terjual','histori_terjual','brand','jml_like','harga','harga_min','harga_max','harga_min_sebelum_disc','harga_max_sebelum_disc','diskon']
        with open(str(self.idseller)+'_shopee.csv', 'w',newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(f_header)
            writer.writerows(f_data)
        f.close()
        print("done! "+str(self.idseller)+"_shopee.csv")

print("[ SHOPEE-PRODUCT-GRABBER v1.0 by heryan ]")
print(" _____ _                           ")
print("/  ___| |                          ")
print("\ `--.| |__   ___  _ __   ___  ___ ")
print(" `--. \ '_ \ / _ \| '_ \ / _ \/ _ /")
print("/\__/ / | | | (_) | |_) |  __/  __/")
print("\____/|_| |_|\___/| .__/ \___|\___|")
print("                  | |              ")
print("                  |_|              ")
print("[+] https://github.com/heryandp/shopee-product-scrap")
sname = input("[+] Masukkan username seller: https://shopee.co.id/")        
act = shopee(sname)