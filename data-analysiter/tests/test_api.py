# Please install OpenAI SDK first: `pip3 install openai`
import os
from openai import OpenAI
with open("snapshots/星球研究所InstituteforPlanet_2025-11-17.json", "r", encoding="utf-8") as f:
    snapshot = f.read()
client = OpenAI(
    #api_key=os.environ.get('DEEPSEEK_API_KEY'),
    api_key="sk-fc8855de5f0f4bfd9760e03bcd67e2ef",
    base_url="https://api.deepseek.com")

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are an analyst. Always reply in strict JSON with fields: user_basic, content_topics, content_style, audience, value_points, content_clusters."},
        {"role": "user", "content": "here is the user data and notes snapshots: " + snapshot + " Please analyze and summarize,and generate user profile."},
    ],
    stream=False
)


print(response.choices[0].message.content)