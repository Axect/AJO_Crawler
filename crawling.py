import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os
import concurrent.futures

def parse_date(date_str):
    if 'deadline' in date_str:
        date_str = date_str.split('deadline')[1].strip()
    try:
        return datetime.strptime(date_str, '%Y/%m/%d %I:%M%p')
    except ValueError:
        return datetime.max

def get_application_materials(soup):
    materials = []
    app_materials = soup.find('b', string='Application Materials Required:')
    if app_materials:
        ul = app_materials.find_next('ul')
        if ul:
            # 'ul'의 내용을 문자열로 변환
            ul_content = ul.decode_contents()
            # '<li>' 태그를 기준으로 분리
            items = ul_content.split('<li>')
            materials = []
            for item in items[1:]:  # 첫 번째 요소는 '<li>' 이전의 내용이므로 제외
                # '</li>' 또는 다른 태그로 끝날 수 있으므로 첫 번째 닫는 태그 이전까지만 사용
                item = item.split('</li>')[0]
                # 남아있는 HTML 태그 제거
                item_soup = BeautifulSoup(item, 'html.parser')
                text = item_soup.get_text(separator=' ', strip=True)
                if text:
                    materials.append(text)
    return materials

def get_position_details(soup):
    position_location = ""
    subject_area = ""
    
    # Position Location 찾기
    location_b = soup.find('b', string='Position Location:')
    if location_b:
        location_div = location_b.parent
        next_div = location_div.find_next_sibling('div')
        if next_div:
            position_location = next_div.text.strip()
    
    # Subject Area 찾기
    subject_b = soup.find('b', string='Subject Area:')
    if subject_b:
        subject_div = subject_b.parent
        next_div = subject_div.find_next_sibling('div')
        if next_div:
            subject_area = next_div.text.strip()
    
    return position_location, subject_area

def normalize_job(job):
    # application_materials를 정렬하여 비교 시 순서 차이로 인한 문제를 방지
    if 'application_materials' in job and isinstance(job['application_materials'], list):
        job['application_materials'] = sorted(job['application_materials'])
    # 문자열 공백 제거
    for key in job:
        if isinstance(job[key], str):
            job[key] = job[key].strip()
    return job

def extract_title(position):
    job_link = position.find('a')
    
    # 'a' 태그 이후부터 시작
    current_element = job_link.next_sibling
    title_parts = []
    
    # 'deadline'을 나타내는 'span' 태그 찾기
    deadline_span = position.find('span', class_='purplesml')
    
    while current_element and current_element != deadline_span:
        if isinstance(current_element, str):
            text = current_element.strip()
            if text:
                title_parts.append(text)
        elif current_element.name in ['a', 'b', 'i', 'u']:
            text = current_element.get_text(strip=True)
            if text:
                title_parts.append(text)
        # 이미지나 기타 태그는 무시
        current_element = current_element.next_sibling
    
    # 제목 조합
    title = ' '.join(title_parts).strip()
    
    # 앞에 남아있을 수 있는 ']' 문자 제거
    if title.startswith(']'):
        title = title[1:].strip()
    
    return title

def process_job(position, institution, department, existing_jobs_dict):
    job_id = position.find('a').text.strip('[]')
    title = extract_title(position)
    deadline = position.find('span', class_='purplesml')
    deadline = deadline.text.strip() if deadline else "No deadline specified"

    # 물리학 혹은 AI 및 자연과학 관련 Post-Doctoral 포지션인지 확인
    if ('physics' in title.lower() or 'physics' in department.lower() or 'artificial' in title.lower() or 'natural' in title.lower()):
        job_url = f"https://academicjobsonline.org{position.find('a')['href']}"

        existing_job = existing_jobs_dict.get(job_id)

        try:
            job_response = requests.get(job_url)
            job_soup = BeautifulSoup(job_response.content, 'html.parser')

            application_materials = get_application_materials(job_soup)
            position_location, subject_area = get_position_details(job_soup)

            new_job_data = {
                'institution': institution,
                'department': department,
                'job_id': job_id,
                'title': title,
                'deadline': deadline,
                'job_url': job_url,
                'application_materials': application_materials,
                'position_location': position_location,
                'subject_area': subject_area
            }
            normalize_job(new_job_data)

            if not existing_job:
                # 새로운 공고
                return new_job_data
            else:
                normalize_job(existing_job)
                if new_job_data != existing_job:
                    # 업데이트된 공고
                    return new_job_data
                else:
                    # 변경사항 없는 기존 공고
                    return existing_job
        except Exception as e:
            print(f"Error processing job {job_id}: {e}")
            return None
    else:
        return None

def crawl_physics_postdocs(url, existing_jobs_dict):
    jobs = []
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    job_listings = soup.find_all('div', class_='clr')

    # 처리할 작업 목록 생성
    tasks = []
    for listing in job_listings:
        institution = listing.find('h3').find('a').text.strip()
        department = listing.find('h3').find_all('a')[1].text.strip() if len(listing.find('h3').find_all('a')) > 1 else ""

        positions = listing.find('ol', class_='sp5').find_all('li')

        for position in positions:
            tasks.append((position, institution, department))

    # 스레드 풀을 사용하여 병렬 처리
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_job, task[0], task[1], task[2], existing_jobs_dict) for task in tasks]
        for future in concurrent.futures.as_completed(futures):
            job = future.result()
            if job:
                jobs.append(job)

    # 마감일 기준으로 정렬
    jobs.sort(key=lambda x: parse_date(x['deadline']))

    return jobs

def load_existing_jobs(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_as_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    url = "https://academicjobsonline.org/ajo?joblist-0-0-0-3---0-dt--"
    json_filename = "data/physics_postdocs.json"

    existing_jobs = load_existing_jobs(json_filename)
    existing_jobs = [normalize_job(job) for job in existing_jobs]
    existing_jobs_dict = {job['job_id']: job for job in existing_jobs}

    jobs = crawl_physics_postdocs(url, existing_jobs_dict)
    jobs = [normalize_job(job) for job in jobs]
    save_as_json(jobs, json_filename)

    # 새로운 공고와 업데이트된 공고 구분
    existing_job_ids = set(existing_jobs_dict.keys())
    current_job_ids = set(job['job_id'] for job in jobs)

    new_job_ids = current_job_ids - existing_job_ids
    possible_updated_job_ids = current_job_ids & existing_job_ids

    new_jobs = [job for job in jobs if job['job_id'] in new_job_ids]
    updated_jobs = []
    for job_id in possible_updated_job_ids:
        existing_job = existing_jobs_dict[job_id]
        current_job = next(job for job in jobs if job['job_id'] == job_id)
        if existing_job != current_job:
            updated_jobs.append(current_job)

    print(f"총 {len(jobs)}개의 Physics 관련 Post-Doctoral 공고를 찾았습니다.")
    print(f"새로운 공고: {len(new_jobs)}개")
    print(f"업데이트된 공고: {len(updated_jobs)}개")
    print("결과가 data/physics_postdocs.json 파일로 저장되었습니다.")
