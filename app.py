import streamlit as st
import requests
import base64
import io
from PIL import Image, ImageOps

st.set_page_config(page_title="Travel Poster Studio", page_icon="🎨", layout="centered")

st.title("📸 Travel Poster AI Studio")
st.markdown("제미나이급 스마트 파이프라인 (화풍별 맞춤 렌더링)")

with st.sidebar:
    st.header("⚙️ 시스템 설정")
    saved_key = st.secrets.get("FAL_KEY", "")
    fal_api_key = st.text_input("Fal.ai API 키를 입력하세요", type="password", value=saved_key)
    st.info("Style A, B 선택 시 배경 제거(누끼) 처리를 위해 약간의 추가 시간이 소요될 수 있습니다.")

styles = {
    "Style A: 실사 + 레트로 카툰 (Rubber Hose)": """제출한 각 초상 사진을 각각 독립적인 고급 디자인 포스터로 제작해 주세요. 여러 장을 합치지 말고, 각 사진을 개별적으로 출력하세요.

전체적으로 3:4 세로 구성을 사용하며, 명확한 상하 대비 영역을 설정하세요. 두 영역의 높이는 대략 균형 있게 유지하되, 고정된 비율을 위해 원본 이미지를 늘리거나 왜곡하지 마세요. 가운데에는 깨끗하고 명확한 수평 경계를 남겨 두세요.

상단 부분은 원본 사진을 충실히 보존하며, 인물의 신원, 얼굴 이목구비, 표정, 헤어스타일, 자세, 의상, 손짓, 실제 물건, 공간 관계, 자연광과 그림자, 그리고 기존 색상 분위기를 정확히 유지하세요. 가벼운 고급 사진 톤 조정과 극도로 미세한 필름 입자 처리만 허용되며, 인물을 새로 그리거나 인물의 신원을 변경하지 마세요.

하단 부분은 동일한 인물을 고해상도 사진 컷아웃 형태로 간결한 단색 빈 필드에 배치하세요. 인물은 여전히 실제 사진 질감을 유지해야 하며, 일러스트나 만화 캐릭터로 변환하지 마세요.

원본 사진에서 이미 실제로 존재하며 인물과 가장 밀접한 관계가 있는 한 가지 물건을 선택하세요. 예를 들어 카메라, 음료 컵, 여행 가방, 과일, 책, 또는 소지품 등이며, 이를 유일한 개성화된 만화 파트너로 변환하세요. 물건의 원래 형태, 색상, 인식 특징을 유지한 채, 거친 검은 고무 튜브 스타일의 손발, 타원형 눈, 흰 장갑, 소량의 베니어 점, 그리고 절제된 복고 애니메이션 인쇄 질감을 추가하세요.

만화 물건은 단순히 인물 옆에 붙여놓는 것이 아니라, 실제 인물과 명확한 공간적 상호작용을 일으켜야 합니다. 예를 들어 손을 잡거나, 건네주거나, 잔을 부딪치거나, 안아주거나, 동작에 응답하거나, 함께 앞으로 나아가는 식으로요. 상호작용은 자연스럽고 재미있으며 한눈에 읽히도록 하되, 인물의 얼굴을 가리지 말고, 두 번째 만화 캐릭터를 추가하지 마세요.

하단 부분의 배경색은 원본 사진이나 물건에서 추출하며, 절제된 제한된 색상 팔레트를 사용하세요. 약 22%—30%의 연속적인 여백을 유지하세요. 스티커 벽, 빽빽한 장식, 복잡한 장면은 피하세요.

사진 내용에 따라 짧은 영어 제목을 생성하고, 번호 "PHOTO PLAY 01"과 관찰적인 느낌의 영어 짧은 문장을 곁들여 주세요. 메인 제목은 크고 복고 만화 느낌의 손그림 폰트를 사용하며, 보조 텍스트는 명확하고 절제되게 하여 물건의 인쇄 재질과 조화를 이루게 하세요.

전체적으로 실제인 사진과 복고 물건 만화가 공존하는 편집 포스터 효과를생성하며, 가볍고, 유머러스하고, 영리하며, 세련된 느낌을 주되, 실제 여행 사진의 감정을 유지하세요.

인물의 만화화, 여러 마스코트, 기존 애니메이션 캐릭터, 브랜드 로고, 스티커 쌓기, 얼굴 가림, 잘못된 손 부분, 저렴한 템플릿, 글자 깨짐, 작가 이름, QR 코드, 워터마크를 피하세요.""",
    
    "Style B: 파스텔 과슈 회화 (Pastel Gouache)": """prompt：
请将我上传的每一张照片分别制作成一张独立的
「PASTEL GOUACHE FASHION TRAVEL PORTRAIT｜粉彩水粉旅拍小像」
原图对比海报，不多图拼接。

整体采用竖版上下双联结构，上下区域各占约50%，中间使用清楚平直的水平边界。

上半部分忠实保留原始照片。准确保持人物身份、脸型、表情、视线、发型、姿态、服装、随身物件、光影与旅行环境，仅进行轻微艺术杂志摄影调色。不得重绘照片区域，不得改变人物身份、年龄、动作或服装。

下半部分从同一人物中提取最有识别度的脸部、发型、帽子、围巾、衣服色彩、手持物和身体姿态，重构成大胆裁切的粉彩水粉旅拍小像。

不要完整照抄原照片构图。将头像或半身适度放大，让发梢、帽檐或衣服可以越出画面边缘；背景压缩成一至三块安静的浅色形状，只保留极少量能够说明旅行地点的线索。

使用哑光不透明水粉、粉彩干刷、宽刷色束和略粗的炭笔轮廓。五官可以适度概括，但必须保持人物身份和真实情绪。保留纸张纹理、毛糙边缘、越线、干刷缺口和局部未完成感，避免光滑数字插画。

配色从原照片提取并归纳为五至七种柔和颜色。保留人物服装中最有辨识度的颜色，同时降低背景杂色。

下半部分保留约20%—30%的连续浅色空场，用于加入一个1—3词英文标题、`GOUACHE NOTE 01`式字段和一句简短观察文字。文字使用哑光手绘窄体字或温和的人文无衬线字体，带轻微干刷缺口，不覆盖五官。

避免动漫脸、光滑矢量画、塑料皮肤、精细写实皮肤、人物身份变化、凭空增加饰品、完整复制摄影背景、悬浮数字排版、作者签名、Logo和水印。""",
    
    "Style C: 단색 건축 에칭 판화 (Monochrome Etching)": """제가 업로드한 유럽 건축 여행 사진 한 장 한 장을 각각 독립된 고급 단색 건축 에칭 판화 대비 포스터로 제작해 주세요. 여러 장 붙이지 말고, 각 사진을 별도로 출력하세요.  

전체적으로 3:4 세로 구도를 채택하며, 상하로 원본과 재구성된 그림이 명확하지만 자연스럽게 대조되도록 합니다. 두 영역은 보통 각각 약 50%를 차지하며, 원본 주제 비율에 따라 약간 조정할 수 있지만 원본 대비 관계는 절대 취소하지 않습니다.  

상반부는 원본 사진을 고해상도로 충실히 보존합니다. 건축의 정체성, 주제 구조, 실제 재질, 원근 관계, 자연광 그림자, 환경 규모와 기존 색채 분위기를 유지하며, 건축 잡지, 독립 출판물 및 전시 사진의 질감을 가진 가벼운 고급 사진 보정만 합니다. 화면비에 맞추기 위해 하늘, 지면 또는 환경 배경을 자연스럽게 확장할 수 있지만, 건축 주제를 늘리거나 왜곡, 교체하거나 임의로 변경하지 않습니다.  

하반부는 원본에서 건축의 가장 식별 가능한 윤곽, 구조와 공간 관계를 추출해 단색 동판 에칭이나 고전 건축 판화로 재구성합니다. 전체 사진을 직접 선화로 바꾸거나 상반부 구성을 기계적으로 복제하지 말아야 합니다. 건축 특징에 따라 규모, 자르기와 위치를 새로 선택할 수 있습니다. 아치, 첨탑, 돔, 주랑이나 산벽을 확대하거나 연속적인 입면을 수평 리듬으로 압축해 아래를 편집되고 정제된 독립 판본으로 만들되, 여전히 원본 건축을 한눈에 알아볼 수 있게 합니다.  

극도로 가는 에칭 선, 평행 음영선, 교차 음영선, 점묘, 단속선과 약간의 드라이 포인트 긁힘으로 석재, 벽돌벽, 조각, 창살, 금속 지붕과 공간 그림자를 형성합니다. 근경 구조는 명확하며, 어두운 부분은 큰 덩어리 순수 검정 대신 선 밀도로 구축합니다. 원경, 공기, 하늘과 화면 가장자리는 선과 점묘를 점차 줄여 종이로 자연스럽게 흩어지게 하며, 딱딱한 직사각형 테두리나 완전한 사진 윤곽을 피합니다.  

하반부는 따뜻한 아이보리 백, 자연 미백이나 약간 낡은 종이 배경을 사용하며, 약 35%—55%의 연속 종이 백을 유지합니다. 주제는 우선 중하부에 집중하고, 주위에 숨 쉴 여유 있는 빈 공간을 둡니다. 종이는 절제된 실제 섬유, 미세한 압흔과 판 압력을 가지되, 더러운 양피지나 과도한 복고 필터로 만들지 않습니다.  

각 작품은 한 가지 먹색과 그 명도 변화만 허용합니다. 먹색은 원본 기질에 따라 깊은 남색, 프로이센 블루, 청회색, 숯 먹 또는 따뜻한 진한 갈색을 자율적으로 선택하지만, 같은 작품에서 여러 가지 유색 잉크를 섞지 않습니다. 동색 선의 굵기, 밀도, 겹침과 먹 빠짐 변화로 부피, 거리와 빛을 구축합니다.  

사진 속 장소, 건축 유형, 형태나 여행 감각에 따라 1—3개 영어 단어로 된 제목을 추출하고, “PLATE NO. 01” 형식의 판본 번호와 5—10개 영어 단어로 된 관찰 짧은 문장을 추가합니다.  

문자는 판화와 같은 색의 좁은 체 대문자 세리프 글씨나 오래된 지리지 납자판을 사용하며, 선명하게 읽히고 약간의 먹 빠짐과 종이 이빨을 가집니다. 연속 여백에 배치해 건축 주제와 어우러진 드문드문하고 절제된 출판물 판식을 형성합니다. 무의미한 긴 글자나 주제를 빼앗는 대면적 문자를 나타내지 않습니다.  

전체적으로 고전 동판 에칭, 유럽 도시 지리지, 박물관 건축 판본, 오래된 건축 측량집과 현대 고급 편집 디자인을 참고해 정확하고 조용하며 합리적인, 수집감과 실제 인쇄 촉감을 가진 시각적 기질을 제시합니다.  

단순 흑백 필터, 연필 스케치, 수채, 수채화, 만화 잉크선, CAD 도면, 순수 벡터 선화, 실크스크린 도트, 다색 인쇄, 사진 경계 묘사, 여백 없는 전면, 딱딱한 직사각형 일러스트 프레임, 3D 렌더링, 플라스틱감, 전자상거래감이나 템플릿감을 피합니다.""",
    
    "Style D: 여백 크레용 스케치 (Sparse Crayon)": """내가 업로드한 사진 한 장 한 장을 각각 독립적인
「SPARSE CRAYON TRAVEL GESTURE｜留白蜡笔旅行姿态」
원본 대비 포스터로 제작해 주세요. 여러 장을 붙인 형태는 피하세요.

이 스타일은 윤곽과 자세가 명확한 단일 동물에 적합할 뿐만 아니라, 여행 중에 명확한 단체 윤곽을 가진 물건(예: 여행 가방, 카메라, 모자, 신발, 커피 컵, 도자기, 자전거, 길가 의자나 작은 기념품)에도 적용됩니다.

전체적으로 세로 형식의 상하 쌍연 구조를 사용하며, 상하 영역이 각각 약 50%를 차지하고 중앙 경계는 명확하고 직선적입니다.

상반부는 원본 사진을 충실히 보존합니다. 동물이나 여행 물건의 정체성, 수량, 자세, 방향, 외곽 윤곽, 주요 구조, 명암과 실제 환경을 정확히 유지하며, 가벼운 사진 보정만 허용됩니다. 주제를 변경하거나 사진 영역을 일러스트화해서는 안 됩니다.

하반부는 극단적으로 축소하여 추출합니다.

주제가 동물인 경우, 가장 중요한 귀 모양, 머리-몸 비율, 꼬리 방향, 서 있거나 앉은 자세와 표정만 남깁니다.

주제가 여행 물건인 경우, 그 정체성을 결정짓는 외곽 윤곽, 손잡이, 바퀴, 렌즈, 컵 입구, 접힌 면, 끈이나 마모 특징만 남깁니다.

거의 모든 배경을 삭제하고, 땅의 한 선, 벽 모서리, 돌덩이 또는 사용 장면을 설명할 수 있는 1~2개의 가벼운 단서만 남깁니다.

망설이고, 끊기며, 약간의 멈춤이 있는 검은색 크레용 윤곽선을 사용하고, 원본 사진에서 추출한 1~2개의 연한 색 크레용 스케치로 표현합니다. 선을 넘거나, 종이 가장자리, 채워지지 않은 부분, 반복 선, 부분적 멈춤을 허용합니다.

주제를 완전히 채워 칠하지 마세요. 종이의 흰 공간이 동물의 몸, 물건의 표면, 주변 공간을 직접 구성하게 합니다. 여행 물건을 정교한 제품 일러스트나 정확한 산업 도면으로 그리지 마세요.

주제는 재구성 영역의 너비 38%—58%, 높이 30%—52%를 차지하며, 보통 중앙 하단이나 약간 한쪽으로 치우쳐 배치합니다. 연속된 따뜻한 흰 종이 여백은 55% 이상이어야 합니다.

조용한 종이 흰 공간 한 곳에 간단한 영어 제목, `CRAYON STUDY 01` 스타일의 필드, 그리고 사진 사실에서 나온 관찰 문구 한 문장을 추가합니다. 텍스트는 화면과 동일한 약간 흔들리는 크레용 필기체를 사용하며, 반드시 선명하고 읽기 쉽게 해야 합니다.

정교한 털 묘사, 귀여운 벡터 마스코트, 완전 채색, 빽빽한 낙서, 완전한 배경, 부드러운 디지털 연필, 정교한 제품 일러스트, 너무 작은 텍스트, 작가 서명, 로고와 워터마크를 피하세요.""",
    
    "Style E: 고무도장 여행 들판 노트 (Rubber Stamp)": """프롬프트:  
제발 제가 업로드한 사진 한 장 한 장을 각각 독립적인 '고무도장 여행 들판 노트 포스터'로 제작해주세요. 각 사진 별도로 출력하고, 여러 장 붙이지 마세요.

전체적으로 4:3 가로 구성으로 하되, 좌우 두 영역으로 나누세요. 왼쪽 58%, 오른쪽 42%.

왼쪽 58%는 원본 사진 충실히 보존. 
오른쪽 42%는 원본 장소의 가장 상징적 건축이나 풍경을 추출해 작은 다색 고무도장 이미지로 압축하세요. 도장은 오른쪽 영역 중하단에 위치(오른쪽 영역 높이의 30~38%).""",
    
    "Style F: 문자 하프톤 콜라주 (ASCII Halftone)": """prompt:
내가 업로드한 모든 여행 사진을 각각 독립적인 한 장씩
「ASCII HALFTONE TRAVEL COLLAGE｜문자 하프톤 여행 콜라주」
고급 대비 포스터로 제작해 주세요. 여러 장을 합치지 말고, 각 사진을 개별적으로 출력하세요.

전체적으로 세로 형식 구성을 채택하며, 상하 두 개의 영역으로 구성됩니다. 상하 영역 비율은 1:1에 가깝게 하고, 명확하고 직선적인 수평 경계로 구분합니다.

【상반부｜원본 사진】
상반부는 원본 사진을 그대로 유지합니다.

【하반부｜문자 하프톤 콜라주】
사진에서 가장 식별성 높은 하나의 핵심 시각 주제를 추출하여 ASCII 하프톤으로 콜라주하세요."""
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
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def pipeline_cutout_inpainting(orig_img, prompt, api_key):
    try:
        from rembg import remove
    except ImportError:
        st.error("⚠️ [환경 오류] 누끼 툴(rembg)이 현재 실행 중인 파이썬 환경에 설치되지 않았습니다.\n\n앱을 실행하신 터미널 창(검은 화면)에서 앱을 잠시 끄시고(Ctrl+C) `pip install rembg` 를 입력해 설치한 뒤 다시 켜주세요!\n\n(참고: Style C, D, E, F는 누끼 툴 없이 지금 바로 작동합니다!)")
        return None
        
    top_img = ImageOps.fit(orig_img, (1200, 900), Image.Resampling.LANCZOS)
    cutout = remove(top_img)
    
    composite = Image.new("RGB", (1200, 1800), (255, 255, 255))
    composite.paste(top_img, (0, 0))
    bottom_bg = Image.new("RGB", (1200, 900), (240, 248, 255))
    bottom_bg.paste(cutout, (0, 0), cutout)
    composite.paste(bottom_bg, (0, 900))
    
    mask = Image.new("L", (1200, 1800), 0)
    bottom_mask = Image.new("L", (1200, 900), 255)
    
    alpha = cutout.split()[3]
    inv_alpha = ImageOps.invert(alpha)
    bottom_mask.paste(inv_alpha, (0, 0))
    mask.paste(bottom_mask, (0, 900))
    
    url = "https://fal.run/fal-ai/flux/dev/inpainting"
    payload = {
        "image_url": f"data:image/png;base64,{image_to_base64(composite)}",
        "mask_url": f"data:image/png;base64,{image_to_base64(mask)}",
        "prompt": prompt,
        "strength": 0.95,
        "guidance_scale": 7.5
    }
    response = requests.post(url, headers={"Authorization": f"Key {api_key}"}, json=payload)
    if response.status_code == 200:
        return response.json()['images'][0]['url']
    else:
        st.error(f"API 에러: {response.text}")
        return None

def pipeline_universal_stitch(orig_img, style_name, prompt, api_key):
    if "Style E" in style_name:
        target_size = (1200, 900)
        is_horizontal = True
        split_ratio = 0.58
    else:
        target_size = (900, 1200)
        is_horizontal = False
        split_ratio = 0.5
        
    orig_formatted = ImageOps.fit(orig_img, target_size, Image.Resampling.LANCZOS)
    
    url = "https://fal.run/fal-ai/flux/dev/image-to-image"
    payload = {
        "image_url": f"data:image/png;base64,{image_to_base64(orig_formatted)}",
        "prompt": prompt,
        "strength": 0.8,
        "guidance_scale": 7.5
    }
    response = requests.post(url, headers={"Authorization": f"Key {api_key}"}, json=payload)
    
    if response.status_code == 200:
        ai_img_url = response.json()['images'][0]['url']
        ai_response = requests.get(ai_img_url)
        ai_img = Image.open(io.BytesIO(ai_response.content)).convert("RGB")
        ai_img = ai_img.resize(target_size)
        
        final_canvas = ai_img.copy()
        if is_horizontal:
            split_px = int(target_size[0] * split_ratio)
            final_canvas.paste(orig_formatted.crop((0, 0, split_px, target_size[1])), (0, 0))
        else:
            split_px = int(target_size[1] * split_ratio)
            final_canvas.paste(orig_formatted.crop((0, 0, target_size[0], split_px)), (0, 0))
            
        return final_canvas
    else:
        st.error(f"API 에러: {response.text}")
        return None

if st.button("✨ 포스터 생성하기", type="primary"):
    if not uploaded_file:
        st.warning("사진을 업로드해주세요!")
    elif not fal_api_key:
        st.warning("사이드바에 Fal.ai API 키를 입력해주세요!")
    else:
        with st.spinner(f"[{selected_style[:7]}] 스마트 파이프라인 가동 중..."):
            try:
                orig_img = Image.open(uploaded_file).convert("RGB")
                final_prompt = styles[selected_style] + f"\n\n[필수 지시사항]\nMain Title: {custom_title}\nSubtitle: {custom_subtitle}\nDescription: {custom_desc}"
                
                if "Style A" in selected_style or "Style B" in selected_style:
                    ai_img_url = pipeline_cutout_inpainting(orig_img, final_prompt, fal_api_key)
                    if ai_img_url:
                        ai_response = requests.get(ai_img_url)
                        final_img = Image.open(io.BytesIO(ai_response.content))
                        st.success("포스터 생성 완료!")
                        st.image(final_img, caption="상단 보존 + 하단 컷아웃 및 완벽 합성", use_container_width=True)
                else:
                    final_img = pipeline_universal_stitch(orig_img, selected_style, final_prompt, fal_api_key)
                    if final_img:
                        st.success("포스터 생성 완료!")
                        st.image(final_img, caption="프롬프트 구조 기반 완벽 렌더링 + 원본 100% 복구", use_container_width=True)
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
