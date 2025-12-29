from flask import Flask, render_template, request, jsonify, redirect, url_for
import subprocess
import threading
import json
import os
import sys

app = Flask(__name__)

# 存储变量配置
VARIABLES_FILE = 'variables_config.json'

# 默认变量配置
default_variables = [
    {"name": "site_name", "label": "站点名称", "type": "text", "default": "VAVA", "required": True},
    {"name": "subscribe_type", "label": "订阅类型", "type": "number", "default": "2", "required": True},
    {"name": "pay_type", "label": "支付类型", "type": "number", "default": "1", "required": True, 
     "description": "1-个人中心信用卡 2-For You信用卡 3-个人中心PayPal 4-For You PayPal\n5-个人中心老aw_more 6-For You老aw_more\n7-个人中心老st_more 8-For You老st_more\n9-个人中心新aw_more 10-For You新aw_more\n11-个人中心新st_more 12-For You新st_more"}
]

# 存储当前进程
current_process = None
script_output = []

def load_variables():
    """加载变量配置"""
    if os.path.exists(VARIABLES_FILE):
        with open(VARIABLES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return default_variables.copy()

def save_variables(variables):
    """保存变量配置"""
    with open(VARIABLES_FILE, 'w', encoding='utf-8') as f:
        json.dump(variables, f, ensure_ascii=False, indent=2)

def run_script_with_variables(variables):
    """使用变量运行测试脚本"""
    global current_process, script_output
    
    try:
        # 构建命令行参数
        cmd = [sys.executable, 'tuoliuC/testsmart.py']
        
        # 添加变量作为环境变量
        env = os.environ.copy()
        for var in variables:
            env[var['name']] = var['value']
        
        # 运行脚本
        current_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=env
        )
        
        # 实时读取输出
        script_output = []
        for line in iter(current_process.stdout.readline, ''):
            script_output.append(line.strip())
            if len(script_output) > 100:  # 限制输出行数
                script_output.pop(0)
        
        current_process.stdout.close()
        current_process.wait()
        
    except Exception as e:
        script_output.append(f"错误: {str(e)}")

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
    variables = load_variables()
    form_data = request.form.to_dict()
    
    # 更新变量值
    for var in variables:
        var_name = var['name']
        if var_name in form_data:
            var['value'] = form_data[var_name]
    
    # 保存变量值（可选）
    save_variables(variables)
    
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

@app.route('/add_variable', methods=['POST'])
def add_variable():
    """添加新变量"""
    variables = load_variables()
    
    new_var = {
        "name": request.form.get('name', '').strip(),
        "label": request.form.get('label', '').strip(),
        "type": request.form.get('type', 'text'),
        "default": request.form.get('default', ''),
        "required": request.form.get('required') == 'true',
        "description": request.form.get('description', '')
    }
    
    if new_var['name']:
        variables.append(new_var)
        save_variables(variables)
    
    return redirect(url_for('index'))

@app.route('/remove_variable/<var_name>')
def remove_variable(var_name):
    """移除变量"""
    variables = load_variables()
    variables = [v for v in variables if v['name'] != var_name]
    save_variables(variables)
    return redirect(url_for('index'))

@app.route('/get_output')
def get_output():
    """获取脚本输出（用于AJAX更新）"""
    return jsonify({"output": "\n".join(script_output)})

@app.route('/reset_variables')
def reset_variables():
    """重置变量为默认值"""
    save_variables(default_variables.copy())
    return redirect(url_for('index'))

if __name__ == '__main__':
    # 确保模板目录存在
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # 保存初始变量配置
    if not os.path.exists(VARIABLES_FILE):
        save_variables(default_variables)
    
    app.run(debug=True, port=5000)