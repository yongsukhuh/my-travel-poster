import streamlit as st
import requests
import base64
import io
from PIL import Image, ImageDraw, ImageFont

# --- 1. 페이지 및 상태 설정 ---
st.set_page_config(page_title="Travel Poster Studio", page_icon="🎨", layout="centered")

st.title("📸 Travel Poster AI Studio")
st.markdown("여행 사진을 고품질 예술 포스터로 변환합니다. (Fal.ai Flux API 연동)")

# 사이드바: API 키 설정
with st.sidebar:
    st.header("⚙️ 시스템 설정")
        # 비밀금고에서 키를 자동으로 가져오기
    saved_key = st.secrets.get("FAL_KEY", "")
    fal_api_key = st.text_input("Fal.ai API 키를 입력하세요", type="password", value=saved_key)
    st.markdown("[Fal.ai에서 API 키 발급받기](https://fal.ai/dashboard/keys)")

# --- 2. 스타일 프롬프트 딕셔너리 ---
styles = {
    "Style A: 실사 + 레트로 카툰 (Rubber Hose)": "A split layout editorial poster, 3:4 aspect ratio. Bottom half features a retro 1930s rubber hose cartoon character interacting with the main subject. Clean boundary, humorous, vintage style, high resolution --ar 3:4",
    "Style B: 파스텔 과슈 회화 (Pastel Gouache)": "A boldly cropped pastel and gouache painting portrait. Matte opaque gouache, dry brush pastel, rough charcoal outlines, visible paper texture and rough unfinished brush edges. Traditional media style --ar 3:4",
    "Style C: 단색 건축 에칭 판화 (Monochrome Etching)": "A refined monochrome copperplate etching print on warm ivory paper. Highly detailed etching lines, cross-hatching, stippling. Single ink color in warm dark brown. --ar 3:4",
    "Style D: 여백 크레용 스케치 (Sparse Crayon)": "An extremely simplified, sparse crayon sketch. Hesitant, broken black crayon outlines, partially filled with 1-2 light crayon colors. Lots of empty warm white paper. Minimalist, handmade sketch style --ar 3:4",
    "Style E: 고무도장 들판 노트 (Rubber Stamp)": "A small multi-color rubber stamp impression of the architectural skyline. 3 spot colors. Authentic hand-carved rubber stamp texture, uneven ink coverage, dry ink. Minimalist field note style --ar 4:3",
    "Style F: 문자 하프톤 콜라주 (ASCII Halftone)": "An experimental halftone and ASCII character collage. Torn photo fragments blending into black halftone dots and ASCII characters (. : / | + = # @). Experimental photography book --ar 3:4"
}

# --- 3. 이미지 업로드 및 설정 ---
uploaded_file = st.file_uploader("변환할 스냅 사진을 올려주세요 (JPG, PNG)", type=["jpg", "png", "jpeg"])

selected_style = st.selectbox("원하는 포스터 화풍을 선택하세요:", list(styles.keys()))

st.header("📝 텍스트 설정")
col1, col2 = st.columns(2)
with col1:
    custom_title = st.text_input("메인 타이틀", "MY TRAVEL")
with col2:
    custom_subtitle = st.text_input("서브 타이틀/번호", "PLATE NO. 01")
custom_desc = st.text_input("관찰 문구 / 설명", "Captured memories from the journey.")

# --- 4. 합성 및 생성 로직 ---
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
        "strength": 0.85,
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
        with st.spinner("최고 화질의 AI 포스터를 렌더링하고 있습니다... (약 10~20초 소요)"):
            try:
                orig_img = Image.open(uploaded_file).convert("RGB")
                base_prompt = styles[selected_style]
                b64_img = image_to_base64(orig_img)
                
                ai_img_url = call_fal_api(b64_img, base_prompt, fal_api_key)
                
                if ai_img_url:
                    ai_response = requests.get(ai_img_url)
                    ai_img = Image.open(io.BytesIO(ai_response.content))
                    
                    width, height = orig_img.size
                    final_canvas = Image.new('RGB', (width, height))
                    
                    top_half = orig_img.crop((0, 0, width, height // 2))
                    final_canvas.paste(top_half, (0, 0))
                    
                    bottom_half = ai_img.crop((0, height // 2, width, height))
                    final_canvas.paste(bottom_half, (0, height // 2))
                    
                    draw = ImageDraw.Draw(final_canvas)
                    draw.text((50, height // 2 + 50), custom_title, fill="black")
                    draw.text((50, height // 2 + 80), custom_subtitle, fill="black")
                    draw.text((50, height // 2 + 110), custom_desc, fill="black")
                    
                    st.success("포스터 생성 완료!")
                    st.image(final_canvas, caption="완성된 최종 포스터", use_container_width=True)
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
