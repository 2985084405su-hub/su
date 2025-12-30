import time
from flask import Flask, render_template, request, jsonify, redirect, url_for
import subprocess
import threading
import json
import os
import sys

app = Flask(__name__)

# 存储变量配置
VARIABLES_FILE = 'variables_config.json'
VALUES_FILE = 'user_values.json'

# 更新默认变量配置，将支付相关参数改为非必填
default_variables = [
    {"name": "site_name", "label": "站点名称", "type": "text", "default": "VAVA", "required": True},
    {"name": "subscribe_type", "label": "订阅类型", "type": "number", "default": "2", "required": True},
    # 添加无头模式开关 - 简化配置
    {"name": "headless_mode", "label": "无头模式", "type": "select", "default": "1", "required": True,
     "options": [
         {"value": "1", "label": "启用（不显示浏览器）"},
         {"value": "0", "label": "禁用（显示浏览器）"}
     ],
     "description": "启用后浏览器将在后台运行，不显示界面"},
    {"name": "pay_type", "label": "支付类型", "type": "number", "default": "1", "required": True, 
     "description": "1-个人中心信用卡 2-For You信用卡 3-个人中心PayPal 4-For You PayPal\n5-个人中心老aw_more 6-For You老aw_more\n7-个人中心老st_more 8-For You老st_more\n9-个人中心新aw_more 10-For You新aw_more\n11-个人中心新st_more 12-For You新st_more"},
    # 将支付相关参数改为非必填
    {"name": "user_email", "label": "用户邮箱", "type": "text", "default": "2985084405su@gmail.com", "required": False,
     "description": "用于支付的用户邮箱（可选，不填使用默认值）"},
    {"name": "card_no", "label": "信用卡号", "type": "text", "default": "4111111111111111", "required": False,
     "description": "信用卡号码（可选，不填使用默认值）"},
    {"name": "card_expire", "label": "信用卡有效期", "type": "text", "default": "03/30", "required": False,
     "description": "格式: MM/YY（可选，不填使用默认值）"},
    {"name": "card_cvv", "label": "CVV安全码", "type": "text", "default": "737", "required": False,
     "description": "信用卡背面3位安全码（可选，不填使用默认值）"}
]

# 存储当前进程和输出
current_process = None
script_output = []

def load_variables():
    """加载变量配置"""
    # 如果变量配置文件不存在，创建它
    if not os.path.exists(VARIABLES_FILE):
        save_variables(default_variables)
    
    # 加载变量配置文件
    if os.path.exists(VARIABLES_FILE):
        try:
            with open(VARIABLES_FILE, 'r', encoding='utf-8') as f:
                saved_variables = json.load(f)
        except:
            saved_variables = []
    else:
        saved_variables = []
    
    # 创建最终变量列表，确保包含所有默认变量
    variables = []
    
    # 首先添加所有默认变量
    for default_var in default_variables:
        # 查找是否有对应的已保存变量
        saved_var = next((v for v in saved_variables if v['name'] == default_var['name']), None)
        
        if saved_var:
            # 合并默认值和保存的值
            merged_var = default_var.copy()
            # 更新保存的值，但保留默认值中没有的字段
            merged_var.update(saved_var)
            variables.append(merged_var)
        else:
            # 使用默认值
            variables.append(default_var.copy())
    
    # 加载用户上次输入的值
    user_values = load_user_values()
    
    # 将用户值合并到变量中
    for var in variables:
        var_name = var['name']
        if var_name in user_values:
            var['value'] = user_values[var_name]
        elif 'value' not in var:  # 确保有value字段
            var['value'] = var.get('default', '')
    
    return variables


def load_user_values():
    """加载用户输入的值"""
    if os.path.exists(VALUES_FILE):
        try:
            with open(VALUES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_user_values(values):
    """保存用户输入的值"""
    with open(VALUES_FILE, 'w', encoding='utf-8') as f:
        json.dump(values, f, ensure_ascii=False, indent=2)

def save_variables(variables):
    """保存变量配置"""
    with open(VARIABLES_FILE, 'w', encoding='utf-8') as f:
        # 只保存配置，不保存临时值
        clean_variables = []
        for var in variables:
            clean_var = {
                "name": var["name"],
                "label": var["label"],
                "type": var["type"],
                "default": var.get("default", ""),
                "required": var.get("required", False),
                "description": var.get("description", "")
            }
            # 保存 options 字段（如果存在）
            if 'options' in var:
                clean_var['options'] = var['options']
            clean_variables.append(clean_var)
        json.dump(clean_variables, f, ensure_ascii=False, indent=2)

def save_variables(variables):
    """保存变量配置"""
    with open(VARIABLES_FILE, 'w', encoding='utf-8') as f:
        # 只保存配置，不保存临时值
        clean_variables = []
        for var in variables:
            clean_var = {
                "name": var["name"],
                "label": var["label"],
                "type": var["type"],
                "default": var.get("default", ""),
                "required": var.get("required", False),
                "description": var.get("description", "")
            }
            clean_variables.append(clean_var)
        json.dump(clean_variables, f, ensure_ascii=False, indent=2)

def run_script_with_variables(variables):
    """使用变量运行测试脚本"""
    global current_process, script_output
    
    try:
        from datetime import datetime
        
        # 构建命令行参数 - 修正路径为 tuoliuC/testsmart.py
        cmd = [sys.executable, '-u', 'tuoliuC/testsmart.py']  # 添加 -u 参数用于无缓冲输出
        
        # 添加变量作为环境变量
        env = os.environ.copy()
        env['PYTHONUTF8'] = '1'  # 启用UTF-8模式
        env['PYTHONUNBUFFERED'] = '1'  # 强制无缓冲输出
        
        # 记录实际使用的变量值
        actual_values = []
        for var in variables:
            value = var.get('value', var.get('default', ''))
            # 如果用户留空，则使用默认值
            if value == '' and not var.get('required', False):
                value = var.get('default', '')
            env[var['name']] = str(value)
            actual_values.append(f"{var['name']}={value}")
        
        # 特别处理无头模式参数（转换为布尔值）
        headless_mode = env.get('headless_mode', '1')
        env['HEADLESS'] = 'True' if headless_mode == '1' else 'False'
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        script_output.append(f"[{timestamp}] 开始运行测试脚本")
        script_output.append(f"[{timestamp}] 脚本路径: tuoliuC/testsmart.py")
        script_output.append(f"[{timestamp}] 使用的变量值: {', '.join(actual_values)}")
        script_output.append(f"[{timestamp}] 无头模式: {'启用' if headless_mode == '1' else '禁用'}")
        
        # 运行脚本
        current_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,  # 行缓冲
            env=env,
            encoding='utf-8',
            errors='replace',
            universal_newlines=True  # 确保文本模式
        )
        
        # 创建线程来读取输出
        def read_output():
            try:
                while True:
                    line = current_process.stdout.readline()
                    if not line and current_process.poll() is not None:
                        break
                    if line:
                        cleaned_line = line.strip()
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        script_output.append(f"[{timestamp}] {cleaned_line}")
                        if len(script_output) > 1000:
                            script_output.pop(0)
            except Exception as e:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                script_output.append(f"[{timestamp}] 读取输出错误: {str(e)}")
        
        # 启动读取线程
        output_thread = threading.Thread(target=read_output)
        output_thread.daemon = True
        output_thread.start()
        
        # 等待进程完成
        return_code = current_process.wait()
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "成功" if return_code == 0 else "失败"
        script_output.append(f"[{timestamp}] 脚本执行完成，状态: {status}，退出码: {return_code}")
        
    except Exception as e:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        script_output.append(f"[{timestamp}] 错误: {str(e)}")


        
@app.route('/')
def index():
    """主页面"""
    variables = load_variables()
    return render_template('index.html', variables=variables, output=script_output)

@app.route('/run', methods=['POST'])
def run_test():
    """运行测试脚本"""
    global script_output
    
    # 获取表单数据
    form_data = request.form.to_dict()
    
    # 保存用户输入的值
    save_user_values(form_data)
    
    # 加载变量配置并合并用户值
    variables = load_variables()
    for var in variables:
        var_name = var['name']
        if var_name in form_data:
            # 如果用户留空且不是必填参数，使用默认值
            if form_data[var_name] == '' and not var.get('required', False):
                var['value'] = var.get('default', '')
            else:
                var['value'] = form_data[var_name]
    
    # 在后台线程中运行脚本
    script_output = ["开始运行测试脚本..."]
    thread = threading.Thread(target=run_script_with_variables, args=(variables,))
    thread.daemon = True
    thread.start()
    
    return redirect(url_for('index'))

@app.route('/stop')
def stop_test():
    """停止当前运行的测试"""
    global current_process
    if current_process:
        current_process.terminate()
        current_process = None
        script_output.append("测试已停止")
    return redirect(url_for('index'))

@app.route('/reset_variables')
def reset_variables():
    """重置变量为默认值"""
    save_variables(default_variables.copy())
    
    # 清空用户值
    save_user_values({})
    
    return redirect(url_for('index'))

@app.route('/reset_values')
def reset_values():
    """清除用户输入的值"""
    save_user_values({})
    return redirect(url_for('index'))

@app.route('/clear_output', methods=['POST'])
def clear_output():
    """清空输出"""
    global script_output
    script_output = []
    return jsonify({"success": True, "message": "输出已清空"})

@app.route('/get_output')
def get_output():
    """获取脚本输出（用于AJAX更新）"""
    global script_output
    # 只返回最后100行，避免数据过大
    recent_output = script_output[-100:] if len(script_output) > 100 else script_output.copy()
    return jsonify({
        "output": "\n".join(recent_output),
        "total_lines": len(script_output),
        "timestamp": time.time()
    })
# web_controller.py 中添加

@app.route('/check_status')
def check_status():
    """检查脚本执行状态"""
    global current_process
    is_running = current_process is not None and current_process.poll() is None
    return jsonify({
        "is_running": is_running,
        "pid": current_process.pid if current_process else None
    })

if __name__ == '__main__':
    # 确保模板目录存在
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # 确保变量配置文件的格式正确
    if not os.path.exists(VARIABLES_FILE):
        save_variables(default_variables)
    else:
        # 检查现有配置文件，确保包含所有字段
        try:
            with open(VARIABLES_FILE, 'r', encoding='utf-8') as f:
                existing_vars = json.load(f)
                # 如果缺少无头模式配置，添加它
                has_headless = any(var.get('name') == 'headless_mode' for var in existing_vars)
                if not has_headless:
                    print("检测到缺少无头模式配置，正在添加...")
                    # 找到无头模式在默认配置中的位置
                    for i, default_var in enumerate(default_variables):
                        if default_var['name'] == 'headless_mode':
                            # 插入到 subscribe_type 之后
                            if len(existing_vars) > 1:
                                existing_vars.insert(2, default_var)
                            else:
                                existing_vars.append(default_var)
                            save_variables(existing_vars)
                            break
        except:
            # 如果配置文件损坏，重新创建
            save_variables(default_variables)
    
    print("启动测试脚本控制器...")
    print("脚本路径: tuoliuC/testsmart.py")
    print("请访问: http://localhost:5001")
    print("外部访问: http://<你的IP地址>:5001")
    
    app.run(debug=True, host='0.0.0.0', port=5001)