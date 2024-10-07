import json
from jinja2 import Environment, FileSystemLoader

# JSON 데이터 로드
with open('data/physics_postdocs_updated.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Jinja2 환경 설정
env = Environment(loader=FileSystemLoader('.'))
template = env.from_string('''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Physics Postdoc Institutes</title>
    <style>
        body { font-family: Arial, sans-serif; }
        .controls { margin: 20px; }
        .job { border: 1px solid #ccc; padding: 15px; margin: 15px; }
        .institution { font-size: 1.5em; font-weight: bold; }
        .title { font-size: 1.2em; }
        .deadline { color: red; }
        .materials { margin-top: 10px; }
        .hidden { display: none; }
        .favorite { background-color: #ffffcc; } /* 관심 공고 표시를 위한 배경색 */
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #ccc; padding: 8px; text-align: left; vertical-align: top; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h1>Physics Postdoc Institutes</h1>
    <div class="controls">
        <label><input type="checkbox" id="toggleMaterials" checked> Application Materials 있는 공고만 보기</label>
        &nbsp;&nbsp;
        <label><input type="checkbox" id="toggleFellow" checked> Fellow 공고 포함하기</label>
        &nbsp;&nbsp;
        <label>정렬 기준:
            <select id="sortOption">
                <option value="deadline">마감일 순</option>
                <option value="country">국가별</option>
            </select>
        </label>
        &nbsp;&nbsp;
        <label><input type="checkbox" id="toggleFavorites"> 관심 공고만 보기</label>
        &nbsp;&nbsp;
        <label><input type="checkbox" id="toggleTableView"> Table View</label>
    </div>
    <div id="jobs">
        {% for job in jobs %}
        <div class="job" data-id="{{ loop.index0 }}" data-has-materials="{{ '1' if job.application_materials else '0' }}" data-is-fellow="{{ '1' if 'fellow' in job.title.lower() else '0' }}" data-deadline="{{ job.deadline }}" data-country="{{ job.country }}">
            <div class="institution">{{ job.institution }} - {{ job.department }}</div>
            <div class="title">{{ job.title }}</div>
            <div class="deadline">마감일: {{ job.deadline }}</div>
            <div class="location">위치: {{ job.position_location }}</div>
            <div class="country">국가: {{ job.country }}</div>
            {% if job.subject_area %}
            <div class="subject-area">분야: {{ job.subject_area }}</div>
            {% endif %}
            {% if job.application_materials %}
            <div class="materials">
                <strong>Application Materials:</strong>
                <ul>
                    {% for material in job.application_materials %}
                    <li>{{ material }}</li>
                    {% endfor %}
                </ul>
            </div>
            {% endif %}
            <div><a href="{{ job.job_url }}">More Info</a></div>
            <!-- 관심 표시 버튼 추가 -->
            <button class="favorite-btn">관심 공고 추가</button>
        </div>
        {% endfor %}
    </div>
    <div id="jobsTable" class="hidden">
        <table>
            <thead>
                <tr>
                    <th>Institution</th>
                    <th>Department</th>
                    <th>Title</th>
                    <th>Deadline</th>
                    <th>Location</th>
                    <th>Country</th>
                    <th>Subject Area</th>
                    <th>Application Materials</th>
                    <th>Link</th>
                    <th>Favorite</th>
                </tr>
            </thead>
            <tbody>
                {% for job in jobs %}
                <tr class="job-row" data-id="{{ loop.index0 }}" data-has-materials="{{ '1' if job.application_materials else '0' }}" data-is-fellow="{{ '1' if 'fellow' in job.title.lower() else '0' }}" data-deadline="{{ job.deadline }}" data-country="{{ job.country }}">
                    <td>{{ job.institution }}</td>
                    <td>{{ job.department }}</td>
                    <td>{{ job.title }}</td>
                    <td>{{ job.deadline }}</td>
                    <td>{{ job.position_location }}</td>
                    <td>{{ job.country }}</td>
                    <td>{{ job.subject_area }}</td>
                    <td>
                        {% if job.application_materials %}
                        <ul>
                            {% for material in job.application_materials %}
                            <li>{{ material }}</li>
                            {% endfor %}
                        </ul>
                        {% endif %}
                    </td>
                    <td><a href="{{ job.job_url }}">More Info</a></td>
                    <td><button class="favorite-btn">관심 공고 추가</button></td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    <script>
        // 관심 공고 불러오기
        function loadFavorites() {
            var favorites = localStorage.getItem('favorites');
            if (favorites) {
                return JSON.parse(favorites);
            } else {
                return [];
            }
        }

        // 관심 공고 저장하기
        function saveFavorites(favorites) {
            localStorage.setItem('favorites', JSON.stringify(favorites));
        }

        // 초기 관심 공고 목록 로드
        var favorites = loadFavorites();

        function setupFavoriteButtons() {
            var favoriteButtons = document.querySelectorAll('.favorite-btn');

            favoriteButtons.forEach(function(button) {
                var jobElement = button.closest('.job, .job-row');
                var jobId = jobElement.getAttribute('data-id');

                // 이미 관심 공고인지 확인
                if (favorites.includes(jobId)) {
                    button.textContent = '관심 공고 제거';
                    jobElement.classList.add('favorite');
                }

                // 클릭 이벤트 추가
                button.addEventListener('click', function() {
                    if (favorites.includes(jobId)) {
                        // 관심 공고 제거
                        favorites = favorites.filter(function(id) { return id !== jobId; });
                        button.textContent = '관심 공고 추가';
                        jobElement.classList.remove('favorite');
                    } else {
                        // 관심 공고 추가
                        favorites.push(jobId);
                        button.textContent = '관심 공고 제거';
                        jobElement.classList.add('favorite');
                    }
                    saveFavorites(favorites);
                    applyFilters(); // 필터링 다시 적용
                });
            });
        }

        function applyFilters() {
            var showMaterials = document.getElementById('toggleMaterials').checked;
            var includeFellow = document.getElementById('toggleFellow').checked;
            var sortOption = document.getElementById('sortOption').value;
            var showFavoritesOnly = document.getElementById('toggleFavorites').checked;
            var isTableView = document.getElementById('toggleTableView').checked;

            var jobsDiv = document.getElementById('jobs');
            var jobsTableDiv = document.getElementById('jobsTable');

            if (isTableView) {
                jobsDiv.classList.add('hidden');
                jobsTableDiv.classList.remove('hidden');
            } else {
                jobsDiv.classList.remove('hidden');
                jobsTableDiv.classList.add('hidden');
            }

            var jobs = Array.from(document.querySelectorAll(isTableView ? '.job-row' : '.job'));

            // 필터링
            jobs.forEach(function(job) {
                var hasMaterials = job.getAttribute('data-has-materials') === '1';
                var isFellow = job.getAttribute('data-is-fellow') === '1';
                var jobId = job.getAttribute('data-id');
                var isFavorite = favorites.includes(jobId);

                var show = true;

                if (showMaterials && !hasMaterials) {
                    show = false;
                }

                if (!includeFellow && isFellow) {
                    show = false;
                }

                if (showFavoritesOnly && !isFavorite) {
                    show = false;
                }

                if (show) {
                    job.classList.remove('hidden');
                } else {
                    job.classList.add('hidden');
                }
            });

            // 정렬
            var visibleJobs = jobs.filter(function(job) {
                return !job.classList.contains('hidden');
            });

            if (sortOption === 'deadline') {
                visibleJobs.sort(function(a, b) {
                    var deadlineA = a.getAttribute('data-deadline');
                    var deadlineB = b.getAttribute('data-deadline');

                    var dateA = parseDeadline(deadlineA);
                    var dateB = parseDeadline(deadlineB);

                    return dateA - dateB;
                });
            } else if (sortOption === 'country') {
                visibleJobs.sort(function(a, b) {
                    var countryA = a.getAttribute('data-country').toLowerCase();
                    var countryB = b.getAttribute('data-country').toLowerCase();

                    if (countryA < countryB) return -1;
                    if (countryA > countryB) return 1;
                    return 0;
                });
            }

            // 정렬된 요소들을 DOM에 다시 추가
            if (isTableView) {
                var tbody = jobsTableDiv.querySelector('tbody');
                visibleJobs.forEach(function(job) {
                    tbody.appendChild(job);
                });
            } else {
                var jobsContainer = document.getElementById('jobs');
                visibleJobs.forEach(function(job) {
                    jobsContainer.appendChild(job);
                });
            }
        }

        function parseDeadline(deadlineStr) {
            // (deadline 2024/11/01 11:59PM*)
            var match = deadlineStr.match(/(\d{4})\/(\d{2})\/(\d{2}) (\d{1,2}):(\d{2})(AM|PM)/);
            if (match) {
                var year = parseInt(match[1]);
                var month = parseInt(match[2]) - 1; // JavaScript months are 0-based
                var day = parseInt(match[3]);
                var hour = parseInt(match[4]);
                var minute = parseInt(match[5]);
                var ampm = match[6];

                if (ampm === 'PM' && hour !== 12) {
                    hour += 12;
                } else if (ampm === 'AM' && hour === 12) {
                    hour = 0;
                }

                return new Date(year, month, day, hour, minute);
            } else {
                // 날짜 파싱 실패 시, 최대값 반환하여 끝으로 보냄
                return new Date(9999, 11, 31);
            }
        }

        document.getElementById('toggleMaterials').addEventListener('change', applyFilters);
        document.getElementById('toggleFellow').addEventListener('change', applyFilters);
        document.getElementById('sortOption').addEventListener('change', applyFilters);
        document.getElementById('toggleFavorites').addEventListener('change', applyFilters);
        document.getElementById('toggleTableView').addEventListener('change', applyFilters);

        // 페이지 로드 시 초기화
        setupFavoriteButtons();
        applyFilters();
    </script>
</body>
</html>
''')

# 템플릿 렌더링
html_content = template.render(jobs=data)

# HTML 파일로 저장
with open('physics_postdocs_positions.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("HTML 파일이 생성되었습니다: physics_postdocs_positions.html")
