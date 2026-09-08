import streamlit as st
import requests
import base64
import io
from PIL import Image

st.set_page_config(page_title="Travel Poster Studio", page_icon="🎨", layout="centered")

st.title("📸 Travel Poster AI Studio")
st.markdown("사용자 프롬프트 100% 직결 모드 (파이썬 합성 개입 없음)")

with st.sidebar:
    st.header("⚙️ 시스템 설정")
    saved_key = st.secrets.get("FAL_KEY", "")
    fal_api_key = st.text_input("Fal.ai API 키를 입력하세요", type="password", value=saved_key)
    st.markdown("[Fal.ai에서 API 키 발급받기](https://fal.ai/dashboard/keys)")

# 사용자가 기획한 원본 프롬프트의 정확한 영문 번역본 (분할, 원본유지, 화풍변경, 텍스트 삽입 등 모든 지시 포함)
styles = {
    "Style A: 실사 + 레트로 카툰 (Rubber Hose)": "A split layout editorial poster, 3:4 vertical aspect ratio. Top half faithfully preserves the original photograph. Clean horizontal boundary in the middle. Bottom half extracts the main subject and reconstructs it into a retro 1930s rubber hose cartoon character on a solid background. Elegant typography overlay: '{title}', '{subtitle}', '{desc}'.",
    "Style B: 파스텔 과슈 회화 (Pastel Gouache)": "A split layout editorial poster, 3:4 vertical aspect ratio. Top half faithfully preserves the original photograph. Clean horizontal boundary. Bottom half extracts the main subject and reconstructs it into a boldly cropped pastel and gouache painting on a quiet light-colored background. Elegant typography overlay: '{title}', '{subtitle}', '{desc}'.",
    "Style C: 단색 건축 에칭 판화 (Monochrome Etching)": "A split layout editorial poster, 3:4 vertical aspect ratio. Top half faithfully preserves the original photograph. Clean horizontal boundary. Bottom half reconstructs the exact same subject as a highly detailed, refined monochrome copperplate etching print on warm ivory paper. Elegant typography overlay: '{title}', '{subtitle}', '{desc}'.",
    "Style D: 여백 크레용 스케치 (Sparse Crayon)": "A split layout editorial poster, 3:4 vertical aspect ratio. Top half faithfully preserves the original photograph. Clean horizontal boundary. Bottom half reconstructs the main subject as an extremely simplified, sparse crayon sketch with lots of empty warm white paper. Elegant typography overlay: '{title}', '{subtitle}', '{desc}'.",
    "Style E: 고무도장 들판 노트 (Rubber Stamp)": "A split layout horizontal editorial poster, 4:3 aspect ratio. Left side (58%) faithfully preserves the original photo. No harsh dividing line. Right side (42%) features a small multi-color rubber stamp impression of the subject on a vintage field note paper background. Elegant typography overlay: '{title}', '{subtitle}', '{desc}'.",
    "Style F: 문자 하프톤 콜라주 (ASCII Halftone)": "A split layout vertical editorial poster, 3:4 aspect ratio. Top half faithfully preserves the original photograph. Clean horizontal boundary. Bottom half reconstructs the subject as an experimental halftone and ASCII character collage. Elegant typography overlay: '{title}', '{subtitle}', '{desc}'."
}

uploaded_file = st.file_uploader("변환할 스냅 사진을 올려주세요 (JPG, PNG)", type=["jpg", "png", "jpeg"])
selected_style = st.selectbox("포스터 화풍 선택:", list(styles.keys()))

st.header("📝 텍스트 설정")
col1, col2 = st.columns(2)
with col1:
    custom_title = st.text_input("메인 타이틀", "CAMERA PAL")
with col2:
    custom_subtitle = st.text_input("서브 타이틀/번호", "PHOTO PLAY 01")
custom_desc = st.text_input("관찰 문구 / 설명", "A small lens follows every curious step.")

def image_to_base64(img):
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def call_fal_api(base64_img, prompt, api_key):
    url = "https://fal.run/fal-ai/flux/dev/image-to-image"
    headers = {
        "Authorization": f"Key {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "image_url": f"data:image/jpeg;base64,{base64_img}",
        "prompt": prompt,
        "strength": 0.90,  # AI가 분할 레이아웃과 텍스트를 자유롭게 새로 짜도록 높은 자유도 부여
        "guidance_scale": 7.5
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()['images'][0]['url']
    else:
        st.error(f"API 에러 발생: {response.text}")
        return None

if st.button("✨ 포스터 생성하기", type="primary"):
    if not uploaded_file:
        st.warning("사진을 업로드해주세요!")
    elif not fal_api_key:
        st.warning("사이드바에 Fal.ai API 키를 입력해주세요!")
    else:
        with st.spinner("사용자의 프롬프트를 100% 적용하여 AI 포스터를 렌더링하고 있습니다..."):
            try:
                orig_img = Image.open(uploaded_file).convert("RGB")
                
                # 프롬프트에 텍스트 적용
                final_prompt = styles[selected_style].format(
                    title=custom_title,
                    subtitle=custom_subtitle,
                    desc=custom_desc
                )
                
                b64_img = image_to_base64(orig_img)
                
                # 파이썬 조작 없이 원본 이미지와 프롬프트를 통째로 AI에게 전달
                ai_img_url = call_fal_api(b64_img, final_prompt, fal_api_key)
                
                if ai_img_url:
                    ai_response = requests.get(ai_img_url)
                    ai_img = Image.open(io.BytesIO(ai_response.content))
                    
                    st.success("포스터 생성 완료!")
                    # 파이썬 합성 없이 AI가 통째로 그려낸 결과물을 그대로 출력
                    st.image(ai_img, caption="AI가 프롬프트대로 100% 창작한 포스터", use_container_width=True)
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
