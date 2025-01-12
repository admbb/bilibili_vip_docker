import requests
import qrcode
import time
from PIL import Image
import json

class BilibiliLogin:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Referer": "https://www.bilibili.com",
            "Accept": "application/json, text/plain, */*",
        }
        
    def format_cookie(self, cookies):
        """格式化cookie为B站标准格式"""
        cookie_dict = requests.utils.dict_from_cookiejar(cookies)
        
        # 按照B站要求的顺序重组cookie
        ordered_keys = ['SESSDATA', 'bili_jct', 'DedeUserID', 'DedeUserID__ckMd5']
        formatted_pairs = []
        for key in ordered_keys:
            if key in cookie_dict:
                formatted_pairs.append(f"{key}={cookie_dict[key]}")
        
        return '; '.join(formatted_pairs) + ';'
        
    def get_qrcode(self):
        """获取二维码及登录密钥"""
        url = "https://passport.bilibili.com/x/passport-login/web/qrcode/generate"
        response = self.session.get(url)
        data = response.json()
        
        if data["code"] == 0:
            qr_url = data["data"]["url"]
            qrcode_key = data["data"]["qrcode_key"]
            
            # 生成二维码
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qr_url)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_img.save("bilibili_qr.png")
            
            # 显示二维码
            Image.open("bilibili_qr.png").show()
            
            return qrcode_key
        return None

    def check_scan(self, qrcode_key):
        """检查扫码状态"""
        url = "https://passport.bilibili.com/x/passport-login/web/qrcode/poll"
        params = {"qrcode_key": qrcode_key}
        
        while True:
            try:
                response = self.session.get(url, params=params)
                scan_result = response.json()
                
                if scan_result["code"] == 0:
                    data = scan_result["data"]
                    if data["code"] == 0:
                        print("登录成功！")
                        # 格式化并保存cookie
                        formatted_cookie = self.format_cookie(self.session.cookies)
                        with open("bilibili_cookies.json", "w", encoding="utf-8") as f:
                            f.write(formatted_cookie)
                        print("Cookie已保存到 bilibili_cookies.json")
                        return True
                    elif data["code"] == 86038:
                        print("二维码已过期")
                        return False
                    elif data["code"] == 86090:
                        print("二维码已扫描，等待确认...")
                    elif data["code"] == 86101:
                        print("等待扫码...")
                    
                time.sleep(2)
                
            except Exception as e:
                print(f"发生错误: {e}")
                time.sleep(2)

    def get_qrcode_data(self):
        """获取二维码数据供前端使用"""
        url = "https://passport.bilibili.com/x/passport-login/web/qrcode/generate"
        response = self.session.get(url)
        data = response.json()
        
        if data["code"] == 0:
            return {
                "url": data["data"]["url"],
                "qrcode_key": data["data"]["qrcode_key"]
            }
        return None

    def check_scan_status(self, qrcode_key):
        """检查扫码状态并返回结果"""
        url = "https://passport.bilibili.com/x/passport-login/web/qrcode/poll"
        params = {"qrcode_key": qrcode_key}
        
        try:
            response = self.session.get(url, params=params)
            scan_result = response.json()
            
            if scan_result["code"] == 0:
                data = scan_result["data"]
                if data["code"] == 0:
                    # 登录成功
                    formatted_cookie = self.format_cookie(self.session.cookies)
                    return {"status": "success", "cookie": formatted_cookie}
                elif data["code"] == 86038:
                    return {"status": "expired"}
                elif data["code"] == 86090:
                    return {"status": "scanned"}
                elif data["code"] == 86101:
                    return {"status": "waiting"}
            
            return {"status": "error", "message": "未知错误"}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

def main():
    bili = BilibiliLogin()
    print("正在获取二维码...")
    qrcode_key = bili.get_qrcode()
    
    if qrcode_key:
        print("请使用哔哩哔哩手机APP扫描二维码登录")
        bili.check_scan(qrcode_key)
    else:
        print("获取二维码失败")

if __name__ == "__main__":
    main() 