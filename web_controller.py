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
    {"name": "pay_type", "label": "支付类型", "type": "number", "default": "1", "required": True, 
     "description": "1-个人中心信用卡 2-For You信用卡 3-个人中心PayPal 4-For You PayPal\n5-个人中心老aw_more 6-For You老aw_more\n7-个人中心老st_more 8-For You老st_more\n9-个人中心新aw_more 10-For You新aw_more\n11-个人中心新st_more 12-For You新st_more"},
    # 将支付相关参数改为非必填
    {"name": "user_email", "label": "用户邮箱", "type": "text", "default": "2985084405su@gmail.com", "required": False,
     "description": "用于支付的用户邮箱（可选，不填使用默认值）\npaypal邮箱：sx-duanjuceshi@personal.example.com"},
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
    if os.path.exists(VARIABLES_FILE):
        with open(VARIABLES_FILE, 'r', encoding='utf-8') as f:
            variables = json.load(f)
    else:
        variables = default_variables.copy()
    
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
            clean_variables.append(clean_var)
        json.dump(clean_variables, f, ensure_ascii=False, indent=2)

def run_script_with_variables(variables):
    """使用变量运行测试脚本"""
    global current_process, script_output
    
    try:
        from datetime import datetime
        
        # 构建命令行参数 - 修正路径为 tuoliuC/testsmart.py
        # 注意：这里我们假设 testsmart.py 和 web_controller.py 在同一目录下，或者使用相对路径
        # 根据用户上传的文件，它们似乎在同一层级，但原代码中有 tuoliuC/ 前缀
        # 稳健做法：检查文件是否存在，优先使用当前目录
        script_path = 'testsmart.py'
        if not os.path.exists(script_path) and os.path.exists('tuoliuC/testsmart.py'):
            script_path = 'tuoliuC/testsmart.py'
            
        cmd = [sys.executable, script_path]
        
        # 添加变量作为环境变量
        env = os.environ.copy()
        env['PYTHONUTF8'] = '1'  # 启用UTF-8模式
        
        # 记录实际使用的变量值
        actual_values = []
        for var in variables:
            value = var.get('value', var.get('default', ''))
            # 如果用户留空，则使用默认值
            if value == '' and not var.get('required', False):
                value = var.get('default', '')
            env[var['name']] = str(value)
            actual_values.append(f"{var['name']}={value}")
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        script_output.append(f"[{timestamp}] 开始运行测试脚本")
        script_output.append(f"[{timestamp}] 脚本路径: {script_path}")
        script_output.append(f"[{timestamp}] 使用的变量值: {', '.join(actual_values)}")
        
        # 运行脚本
        current_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=env,
            encoding='utf-8',
            errors='replace'
        )
        
        # 实时读取输出
        for line in iter(current_process.stdout.readline, ''):
            if line:
                cleaned_line = line.strip()
                # 如果是API捕获数据，直接透传，不添加时间戳前缀，方便前端解析
                if "__API_CAPTURE__|" in cleaned_line:
                     script_output.append(cleaned_line)
                else:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    script_output.append(f"[{timestamp}] {cleaned_line}")
                
                # 保持日志长度合理，但不要太短以免丢失API数据
                if len(script_output) > 2000:
                    script_output.pop(0)
        
        current_process.stdout.close()
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
    # 增加返回的行数限制，确保前端能收到完整的JSON大对象
    recent_output = script_output[-500:] if len(script_output) > 500 else script_output.copy()
    return jsonify({
        "output": "\n".join(recent_output),
        "total_lines": len(script_output),
        "timestamp": time.time()
    })

if __name__ == '__main__':
    # 确保模板目录存在
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # 保存初始变量配置
    if not os.path.exists(VARIABLES_FILE):
        save_variables(default_variables)
    
    print("启动测试脚本控制器...")
    print("请访问: http://localhost:5000")
    
    app.run(debug=True, port=5000)