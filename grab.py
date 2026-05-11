import requests
import re
from urllib.parse import quote, urljoin

# Cấu hình giả lập và Logo
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
LOGO_URL = "https://nha-cai.com/wp-content/uploads/2023/11/qua-bong-da.jpg"
SERVERS = ['https://sv1.hoiquan3.live/', 'https://sv2.hoiquan3.live/', 'https://sv3.hoiquan3.live/']

def get_m3u():
    # Khởi tạo nội dung M3U
    m3u = "#EXTM3U\n"
    h = {'User-Agent': UA, 'Referer': 'https://hoiquan3.live/'}
    processed_links = set()

    for base_url in SERVERS:
        try:
            r = requests.get(base_url, headers=h, timeout=10).text
            # Quét các link trận đấu
            matches = re.findall(r'href="([^"]*(?:truc-tiep|match)/[^"]+)"', r)
            for m_url in list(set(matches)):
                full_u = urljoin(base_url, m_url)
                if full_u in processed_links: continue
                
                try:
                    d = requests.get(full_u, headers=h, timeout=5).text
                    # Bốc link stream
                    streams = re.findall(r'(https?://[^\s"\'<>]+?\.m3u8[^\s"\'<>]*)', d)
                    if streams:
                        # Bốc tên trận và tên BLV từ Title
                        title_match = re.search(r'<title>(.*?)</title>', d)
                        raw_title = title_match.group(1) if title_match else "Bóng đá"
                        # Xử lý tên cho đẹp: "Trực tiếp MU vs Arsenal | BLV Batman" -> "MU vs Arsenal (BLV Batman)"
                        clean_name = raw_title.split('|')[0].replace('Trực tiếp', '').strip()
                        blv_name = ""
                        if '|' in raw_title:
                            blv_part = raw_title.split('|')[-1].strip()
                            if "BLV" in blv_part:
                                blv_name = f" [{blv_part}]"
                        
                        display_name = f"{clean_name}{blv_name}"

                        for i, s in enumerate(streams):
                            s_link = s.replace('\\', '')
                            # Gắn Header lách chặn trực tiếp vào link
                            final_link = f"{s_link}|User-Agent={quote(UA)}&Referer={quote(full_u)}"
                            # Ghi vào list với Logo và Tên chuẩn
                            m3u += f'#EXTINF:-1 tvg-logo="{LOGO_URL}", {display_name} - Server {i+1}\n{final_link}\n'
                except: continue
                processed_links.add(full_u)
        except: continue
    
    # Ghi đè file list.m3u
    with open("list.m3u", "w", encoding="utf-8") as f:
        f.write(m3u)
    print(f"Update thành công {len(processed_links)} trận.")

if __name__ == "__main__":
    get_m3u()
