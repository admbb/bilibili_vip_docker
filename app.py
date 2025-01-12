from flask import Flask, jsonify, send_from_directory, send_file
from flask_cors import CORS
from bilibili_login import BilibiliLogin
import logging
import qrcode
from io import BytesIO

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static')
CORS(app)

bili = BilibiliLogin()

@app.route('/')
def index():
    logger.info("访问首页")
    return send_from_directory('static', 'index.html')

@app.route('/api/qrcode', methods=['GET'])
def get_qrcode():
    logger.info("开始获取二维码")
    try:
        qr_data = bili.get_qrcode_data()
        logger.info(f"QR Data: {qr_data}")
        if qr_data:
            # 直接返回B站的登录URL和key
            response_data = {
                'qrcode_url': qr_data['url'],  # 直接使用B站返回的URL
                'qrcode_key': qr_data['qrcode_key']
            }
            logger.info(f"返回数据: {response_data}")
            return jsonify(response_data)
        logger.error("获取二维码失败")
        return jsonify({"error": "获取二维码失败"}), 500
    except Exception as e:
        logger.error(f"获取二维码时发生错误: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/check_scan/<qrcode_key>', methods=['GET'])
def check_scan(qrcode_key):
    logger.info(f"检查扫描状态: {qrcode_key}")
    try:
        result = bili.check_scan_status(qrcode_key)
        logger.info(f"扫描状态: {result}")
        return jsonify(result)
    except Exception as e:
        logger.error(f"检查扫描状态时发生错误: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    logger.info("服务器启动在 http://0.0.0.0:12222")
    app.run(host='0.0.0.0', port=12222, debug=True) 