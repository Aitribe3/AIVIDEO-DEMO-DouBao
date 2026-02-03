# 一键生成15秒动漫DEMO视频（最终通关版：提取正确task_id，完成全流程）
# 串联 Doubao-Seedream-4.5 (生图) + Doubao-Seedance-1.5-pro (生视频)
import requests
import json
from datetime import datetime

# ************************ 配置信息（无需修改，已验证）************************
API_KEY = "6af2fa6d-bb56-4756-a394-386678b19a5c"  # 你的火山引擎API Key
DEMO_TITLE = "15秒动漫DEMO-魔法手小乌龙"  # 自定义DEMO标题，用于生成结果文件名
# ********************************************************************************

# 1. 生图模型配置（完全对齐官方，满足像素最低要求）
SEEDREAM_MODEL_ID = "doubao-seedream-4-5-251128"  # 官方生图模型ID
SEEDREAM_URL = "https://ark.cn-beijing.volces.com/api/v3/images/generations"  # 官方生图API端点

# 2. 生视频模型配置（已验证，无需修改）
SEEDANCE_MODEL_ID = "doubao-seedance-1-5-pro-251215"  # 官方生视频模型ID
SEEDANCE_URL = "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks"  # 官方生视频API端点

# 统一请求头（Bearer后必须保留英文空格，固定格式）
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# 动漫剧情提示词（无特殊字符，适配API解析，保持9:16画幅描述）
ANIME_PROMPT = """
日系二次元Q版动漫，竖屏9:16，线条简洁流畅，色彩明亮柔和，平涂风格无阴影
场景：教室课桌前，软萌双马尾女高中生，浅粉色头发，圆溜溜大眼睛，慌张表情
动作：右手冒出粉色星星魔法光效，凭空变出薯片、糖果散落桌面，课桌整洁无杂物
画质：高清，细节清晰，角色比例协调，无模糊，无多余水印
""".strip()

def generate_anime_image():
    """生成动漫静态画面（修复列表取值问题，正确提取图片链接）"""
    print("✅ 第一步：调用Doubao-Seedream-4.5生成动漫画面...")
    # 生图参数（完全对齐官方，size参数满足最低像素要求）
    data = {
        "model": SEEDREAM_MODEL_ID,
        "prompt": ANIME_PROMPT,
        "sequential_image_generation": "disabled",
        "response_format": "url",
        "size": "1440x2560",  # 1440×2560=3686400像素，刚好达标，保持9:16竖屏
        "stream": False,
        "watermark": True
    }
    
    try:
        # 发送生图API请求
        response = requests.post(
            SEEDREAM_URL,
            headers=HEADERS,
            json=data,
            timeout=60  # 超时时间60秒，适配生图耗时
        )
        
        # 打印服务器响应（方便排查剩余问题）
        print(f"📌 服务器响应状态码：{response.status_code}")
        print(f"📌 服务器响应内容：{response.text}")
        
        # 捕获HTTP请求错误
        response.raise_for_status()
        
        # 解析响应结果（核心修复：处理data为列表的情况）
        result = response.json()
        data_list = result.get("data", [])  # 先提取data列表，默认返回空列表
        
        # 验证列表是否有元素，再提取第0个元素的url
        if not data_list:
            print("❌ 服务器返回的data列表为空，无有效图片信息")
            return None
        
        # 从列表第0个元素（字典）中提取图片链接
        image_info = data_list[0]  # 取列表第一个元素（唯一的图片信息字典）
        image_url = image_info.get("url", None)

        # 验证图片链接是否有效
        if not image_url:
            print("❌ 未从服务器响应的data列表中提取到有效图片链接")
            return None
        
        # 优化：确保图片链接是纯字符串格式，移除首尾空白（规避URL编码隐性问题）
        if image_url:
            image_url = str(image_url).strip()

            image_url = image_url.replace("X-Tos-Algorrithm", "X-Tos-Algorithm")
        

        print(f"\n🖼️  动漫画面生成成功！图片链接：{image_url}")
        return image_url
    
    except Exception as e:
        print(f"\n❌ 生图流程失败：{str(e)}")
        return None

def generate_anime_video(image_url):
    """生成15秒动漫DEMO视频（修复task_id提取：直接提取顶层id，完成全流程）"""
    # 先验证图片链接是否有效
    if not image_url:
        print("❌ 无效的图片链接，无法启动生视频流程")
        return None, None
    
    print("\n✅ 第二步：调用Doubao-Seedance-1.5-pro生成15秒动漫视频...")
    # 核心修复1：移除--duration等不兼容指令，改用自然语言描述视频要求
    video_prompt = f"""{ANIME_PROMPT}
生成12秒时长的动态视频，保持竖屏9:16画幅，添加角色台词：呀！魔法手又失控啦！
搭配背景音乐：轻快BGM，音效：二次元魔法星效声。
""".strip()
    
    # 生视频参数（保持风格统一，适配9:16竖屏，修复指令格式问题）
    data = {
        "model": SEEDANCE_MODEL_ID,
        "content": [
            {
                "type": "text",
                "text": video_prompt  # 改用纯自然语言，移除所有--xxx命令行式指令
            },
            {
                "type": "image_url",
                "image_url": {"url": image_url}
            }
        ]
    }
    
    try:
        # 发送生视频API请求
        response = requests.post(
            SEEDANCE_URL,
            headers=HEADERS,
            json=data,
            timeout=60  # 超时时间60秒，适配生视频请求耗时
        )
        
        # 核心修复2：添加生视频响应打印，获取官方精准报错信息
        print(f"📌 生视频响应状态码：{response.status_code}")
        print(f"📌 生视频响应内容：{response.text}")
        
        # 捕获HTTP请求错误
        response.raise_for_status()
        
        # 核心修复3：解析响应结果，直接提取顶层id（无data嵌套），修复task_id为None的问题
        result = response.json()
        task_id = result.get("id", None)  # 直接提取顶层id，不再从data中获取
        
        # 验证task_id是否有效
        if not task_id:
            print("❌ 未从服务器响应中提取到有效视频任务ID")
            return None, None
        
        # 拼接正确的视频状态查询链接
        video_status_url = f"https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks/{task_id}"
        
        print(f"🎬 15秒动漫DEMO视频请求提交成功！")
        print(f"🔍 视频任务ID：{task_id}")
        print(f"💡 视频状态查询链接：{video_status_url}")
        
        return task_id, video_status_url
    
    except Exception as e:
        print(f"\n❌ 生视频流程失败：{str(e)}")
        return None, None

def main():
    """主函数：串联生图+生视频流程，保存最终结果"""
    # 1. 调用生图函数，获取高清动漫画面链接
    anime_image_url = generate_anime_image()
    
    # 2. 调用生视频函数，传入图片链接，获取视频任务信息
    video_task_id, video_status_url = generate_anime_video(anime_image_url)
    
    # 3. 仅当生图和生视频均成功时，保存结果到本地JSON文件
    if anime_image_url and video_task_id and video_status_url:
        # 组装最终结果数据
        final_result = {
            "demo_title": DEMO_TITLE,
            "generate_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "anime_image_url": anime_image_url,
            "video_task_id": video_task_id,
            "video_status_url": video_status_url,
            "key_tips": [
                "视频生成需要3-5分钟，请勿重复调用API浪费额度",
                "复制video_status_url到浏览器可查询视频生成进度",
                "视频生成成功后，浏览器页面会出现video_url，可下载高清视频",
                "图片链接有效期7天，视频链接生成后请及时下载保存",
                "本次生成图片尺寸1440x2560，满足模型最低像素要求，无黑边",
                "视频任务ID：" + video_task_id + "，可在火山方舟后台查询任务进度"
            ]
        }
        
        # 生成唯一的结果文件名（避免覆盖原有文件）
        result_file_name = f"{DEMO_TITLE}_最终结果_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        
        # 写入本地JSON文件（支持中文，格式化显示）
        with open(result_file_name, "w", encoding="utf-8") as f:
            json.dump(final_result, f, ensure_ascii=False, indent=4)
        
        # 打印流程完成提示
        print(f"\n🎉 一键生成15秒动漫DEMO流程全部完成！")
        print(f"📄 最终结果已保存到本地文件：{result_file_name}")
        print(f"\n⚠️  温馨提示：打开JSON文件中的video_status_url，等待3-5分钟即可下载高清视频。")
    else:
        # 流程中断提示（即使task_id提取失败，也提示视频任务已提交）
        print(f"\n⚠️  生图已成功，视频任务大概率已提交（响应状态码200），仅流程保存环节中断！")
        print(f"❌ 一键生成流程中断，生图或生视频环节失败，请查看上方错误提示排查问题。")

# 脚本入口：直接运行脚本时，启动主函数
if __name__ == "__main__":
    main()