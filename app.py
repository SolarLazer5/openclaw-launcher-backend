import os
from flask import Flask, request, jsonify, send_file, abort
from Config import TARGET_VERSION

UPDATES_DIR = os.path.join(os.path.dirname(__file__), "updates")

app = Flask(__name__)

# 配置更新包存放的目录（建议在服务端项目根目录下创建一个 updates 文件夹）
UPDATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'updates')
UPDATE_FILENAME = 'updated.zip'

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


# 新增：心跳/连通性测试接口
@app.route('/api/hello', methods=['POST'])
def api_hello():
    try:
        data = request.get_json(force=True)  # 强制解析 JSON
        machine_id = data.get('machine_id', 'unknown_id')

        # 记录日志或者更新数据库中的机器在线状态
        print(f"[Hello] Received heartbeat from machine: {machine_id}")

        return jsonify({
            "status": "success",
            "message": "Connected to server",
            "machine_id": machine_id
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

UPDATES_DIR = os.path.join(os.path.dirname(__file__), "updates")


@app.route("/api/update/check", methods=["POST"])
def api_update_check():
    """
    第一步：检查是否需要更新
    客户端 POST: {"version": "202603013-13:49"}
    返回: {"need_update": true/false, "target_version": "202603131800"}
    """
    data = request.get_json(silent=True) or {}
    client_version = data.get("version", "")

    need_update = (client_version != TARGET_VERSION)
    return jsonify({
        "need_update": need_update,
        "target_version": TARGET_VERSION
    }), 200


@app.route("/api/update/download", methods=["GET"])
def api_update_download():
    """
    第二步：下载更新包
    """
    zip_path = os.path.join(UPDATES_DIR, TARGET_VERSION, "updated.zip")
    if not os.path.isfile(zip_path):
        return jsonify({"error": "Update package not found"}), 404

    return send_file(
        zip_path,
        mimetype="application/zip",
        as_attachment=True,
        download_name="update.zip"
    )


@app.route('/api/update', methods=['GET'])
def api_update():
    file_path = os.path.join(UPDATE_DIR, UPDATE_FILENAME)

    # 防御性检查：确保更新文件存在，避免抛出异常返回含有 HTML 的500错误给客户端
    if not os.path.exists(file_path):
        print(f"[Update] Error: File {file_path} not found.")
        abort(404, description="Update package not found on server.")

    # 使用 send_file 安全、流式下发大文件
    return send_file(
        file_path,
        mimetype='application/zip',
        as_attachment=True,
        download_name=UPDATE_FILENAME
    )


if __name__ == '__main__':
    # 确保 updates 目录存在，方便部署时不报错
    os.makedirs(UPDATE_DIR, exist_ok=True)
    app.run()