import requests

# 配置信息（直接复制你的原有配置，无需改动）
API_KEY = "6af2fa6d-bb56-4756-a394-386678b19a5c"
TASK_ID = "cgt-20260202191216-8wc5n"  # 你的视频任务ID

# 构建请求头和查询URL
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}
STATUS_URL = f"https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks/{TASK_ID}"

def check_video_status():
    print(f"🔍 正在查询任务 {TASK_ID} 的状态...")
    try:
        response = requests.get(STATUS_URL, headers=HEADERS, timeout=30)
        response.raise_for_status()
        
        # 格式化输出结果，方便查看
        result = response.json()
        print("✅ 查询成功，任务详情如下：")
        print(requests.utils.dump_json(result, indent=4))
        
        # 提取关键信息提示
        task_status = result.get("status", "unknown")
        print(f"\n📌 任务当前状态：{task_status}")
        
        if task_status == "succeeded":
            video_url = result.get("output", {}).get("video", {}).get("url", None)
            if video_url:
                print(f"\n🎥 视频生成成功！下载链接：{video_url}")
            else:
                print("\n❌ 任务成功但未找到视频下载链接")
        elif task_status == "failed":
            error_msg = result.get("error", {}).get("message", "未知错误")
            print(f"\n❌ 视频生成失败：{error_msg}")
        else:
            print("\n⏳ 视频还在生成中，请稍后再查询（建议等待3-5分钟）")
    
    except Exception as e:
        print(f"\n❌ 查询失败：{str(e)}")

if __name__ == "__main__":
    check_video_status()