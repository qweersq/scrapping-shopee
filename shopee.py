# Shopee Product Scrapper v2.0
# heryandp
# https://github.com/heryandp

from progressbar import progressbar
import requests as req
import urllib.parse as encode
import os,glob, json,time,csv

# Base Url
base_url = "https://shopee.co.id/"
ua = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}

class shopee_shop_detil():
    def detil(shopid):
        try:
            url_detil = base_url+"api/v4/recommend/get_shop_detail/?shopId="+str(shopid)
            grab_detil = req.get(url_detil,headers=ua,timeout=3000).json()
            return grab_detil['data']['account']['username']
        except:
            return "error"
class shopee_keyword():
    def __init__(self,keyword,lokasi):
        self.headerbrowser = ua
        self.katakunci = encode.quote(keyword)
        self.lokasikey = encode.quote(lokasi)
        self.fn = str(keyword).replace(" ","_").replace(".","_")
        # print(self.katakunci)
        self.grab_keyword()
    
    def grab_keyword(self):
        # session
        sess = req.Session()
        if not self.lokasikey:
            self.url_key = base_url+"api/v4/search/search_items?by=sales&keyword="+self.katakunci+"&limit=1&newest=0&order=desc&page_type=search&scenario=PAGE_GLOBAL_SEARCH&skip_autocorrect=1&version=2"
        else:
            self.url_key = base_url+"api/v4/search/search_items?by=sales&keyword="+self.katakunci+"&limit=1&locations="+self.lokasikey+"&newest=0&order=desc&page_type=search&scenario=PAGE_GLOBAL_SEARCH&skip_autocorrect=1&version=2"
        get_key = sess.get(self.url_key,headers=self.headerbrowser,timeout=3000).json()
        get_sess = sess.cookies
        cookies_sess = get_sess.get_dict()
        # print(cookies_sess)
        # print("[+] Total hasil keyword : ",get_key['total_count'])
        print("=== GRABBING PRODUK ===")
        print("[+] Hapus file lama ...")
        if not os.path.exists("data"):
            os.makedirs("data")
        for filename in glob.glob("data/"+self.fn+"_shopee*.json"):
            os.remove(filename)
        for filename in glob.glob("data/"+self.fn+"_shopee*.csv"):
            os.remove(filename)
        print("[+] Mulai download produk ...")
        print("\x1B[3m" +"(delay 5 detik untuk menghindari anti-spam!)"+"\x1B[0m")
        a = 0
        b = 1
        while(True):
            if not self.lokasikey:
                url_produk = base_url+"api/v4/search/search_items?by=sales&keyword="+self.katakunci+"&limit=100&newest="+str(a)+"&order=desc&page_type=search&scenario=PAGE_GLOBAL_SEARCH&skip_autocorrect=1&version=2"
            else:
                url_produk  = base_url+"api/v4/search/search_items?by=sales&keyword="+self.katakunci+"&limit=100&locations="+self.lokasikey+"&newest="+str(a)+"&order=desc&page_type=search&scenario=PAGE_GLOBAL_SEARCH&skip_autocorrect=1&version=2"
            cek_produk = req.get(url_produk,headers=self.headerbrowser,cookies=cookies_sess).json()
            if (cek_produk["total_count"]==0) or (not cek_produk['items']):
                # print(cek_produk)
                break
            else:
                print("-> download halaman "+ str(b) +" ("+ str(len(cek_produk["items"])) +")")
                # print(url_produk)
                with open("data/"+self.fn+"_shopee_"+str(b)+".json", 'w') as json_file:
                    json.dump(cek_produk['items'], json_file)
                a = a + 100
                b = b + 1
                time.sleep(5)

        # merging json
        print("[+] Merging data keyword produk ...")
        data = []
        for f in progressbar(glob.glob("data/"+self.fn+"_shopee_*.json")):
            with open(f,) as infile:
                data.extend(json.load(infile))
        with open("data/"+self.fn+"_shopee_all.json",'w') as outfile:
            json.dump(data, outfile)
        # create csv
        print("[+] Membuat csv data produk ...")
        print("\x1B[3m" +"(sabar ya... grabbing username tokonya lumayan lama)"+"\x1B[0m")
        f_data = []
        f = open("data/"+self.fn+"_shopee_all.json")
        f_read = json.load(f)
        for i in progressbar(f_read):
            namatoko = shopee_shop_detil.detil(i['item_basic']['shopid'])
            link_produk1 = str(i['item_basic']['name']).replace("/","-").replace(" ","-").replace("|","")
            link_produk2 = base_url+link_produk1+"-i."+str(i['item_basic']['shopid'])+"."+str(i['item_basic']['itemid'])
            time.sleep(0.2)
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
                namatoko,
                i['item_basic']['shop_location'],
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
                link_produk2
                ])
        f_header = ['shopid','username_toko','lokasi_toko','itemid','produk','stok','terjual','histori_terjual','brand','jml_like','harga','harga_min','harga_max','harga_min_sebelum_disc','harga_max_sebelum_disc','diskon','url_produk']
        with open(str(self.fn)+'_shopee.csv', 'w',newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(f_header)
            writer.writerows(f_data)
        f.close()
        print("done! "+str(self.fn)+"_shopee.csv")
class shopee():
    def __init__(self, usernametoko):
        self.tokourl = base_url+usernametoko
        self.namatoko = usernametoko
        self.headerbrowser = ua
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
                "rating" : grab_seller["data"]["rating_star"],
                "follower" : grab_seller["data"]["follower_count"],
                "shop_location" : grab_seller["data"]["shop_location"],
                "country" : grab_seller["data"]["country"]
            }
            print("=== DETAIL SELLER ===")
            print(self.data_seller)
            self.idseller = grab_seller["data"]["shopid"]
            self.grab_produk()
        except Exception as e:
            # print(e)
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
        b = 1
        while (True):
            url_produk = base_url+"api/v4/shop/search_items?limit=100&offset="+str(a)+"&shopid="+str(self.idseller)
            cek_produk = req.get(url_produk,headers=self.headerbrowser).json()
            if (cek_produk["total_count"]==0):
                break
            else:
                print("-> download halaman "+ str(b) +" ("+ str(len(cek_produk["items"])) +")")
                with open("data/"+str(self.idseller)+"_"+str(b)+'.json', 'w') as json_file:
                    json.dump(cek_produk["items"], json_file)
                a = a + 100
                b = b + 1
                time.sleep(3)

        # merging json
        print("[+] Merging data produk ...")
        data = []
        for f in progressbar(glob.glob("data/"+str(self.idseller)+"*.json")):
            with open(f,) as infile:
                data.extend(json.load(infile))
        with open("data/"+str(self.idseller)+"_all.json",'w') as outfile:
            json.dump(data, outfile)
        # create csv
        print("[+] Membuat csv data produk ...")
        f_data = []
        f = open("data/"+str(self.idseller)+"_all.json")
        f_read = json.load(f)
        for i in progressbar(f_read):
            link_produk1 = str(i['item_basic']['name']).replace("/","-").replace(" ","-").replace("|","-")
            link_produk2 = base_url+link_produk1+"-i."+str(i['item_basic']['shopid'])+"."+str(i['item_basic']['itemid'])
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
                self.data_seller['shop_location'],
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
                link_produk2
                ])
        f_header = ['shopid','username_toko','nama_toko','lokasi_toko','itemid','produk','stok','terjual','histori_terjual','brand','jml_like','harga','harga_min','harga_max','harga_min_sebelum_disc','harga_max_sebelum_disc','diskon','url_produk']
        with open(str(self.idseller)+'_shopee.csv', 'w',newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(f_header)
            writer.writerows(f_data)
        f.close()
        print("done! "+str(self.idseller)+"_shopee.csv")

print("[ SHOPEE-PRODUCT-GRABBER v2.0 by heryan ]")
print(" _____ _                           ")
print("/  ___| |                          ")
print("\ `--.| |__   ___  _ __   ___  ___ ")
print(" `--. \ '_ \ / _ \| '_ \ / _ \/ _ /")
print("/\__/ / | | | (_) | |_) |  __/  __/   v.2.0")
print("\____/|_| |_|\___/| .__/ \___|\___|")
print("                  | |              ")
print("                  |_|              ")
print("[+] https://github.com/heryandp/shopee-product-scrap")

while(True):
    print("===========================")
    print("[+] Pilih metode grab/scrap:")
    print("1) Username toko (download produk per toko)")
    print("2) Keyword + Lokasi/Daerah (download produk terlaris)")
    print("3) Keluar")
    choice = input("Ketik nomor :")
    if choice=="1":
        sname = input("[+] Masukkan username seller: https://shopee.co.id/")        
        act = shopee(sname)
        break
    elif choice=="2":
        keyword = input("[+] Masukkan keyword barang/produk (mis. tas wanita) :")
        lokasi = input("[+] Masukkan lokasi (provinsi/kosong=All, mis. Jawa Tengah) :")
        key = shopee_keyword(keyword,lokasi)
        break
    elif choice=="3":
        exit()
    else:
        print("Oops! Ketik nomor 1,2,atau 3 :")