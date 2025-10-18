# HyperLLM GUI Updates | 更新日志 | 업데이트 로그

## Version 1.1 - October 2025

### New Features | 新功能 | 새로운 기능

#### 1. API Configuration Interface | API配置界面 | API 구성 인터페이스

**English:**
- Added dedicated API Configuration section in Parameters tab
- Users can now configure API Key and Base URL directly in the GUI
- Configuration is saved and persists across sessions
- No need to manually edit configuration files

**中文:**
- 在参数配置标签页添加了专用的API配置区域
- 用户现在可以直接在GUI中配置API密钥和基础URL
- 配置会被保存并在会话之间保持
- 无需手动编辑配置文件

**한국어:**
- 매개변수 탭에 전용 API 구성 섹션 추가
- 이제 GUI에서 직접 API 키와 기본 URL 구성 가능
- 구성이 저장되고 세션 간에 유지됨
- 구성 파일을 수동으로 편집할 필요 없음

**Features:**
- Password-masked API Key input
- Base URL configuration
- Save button with validation
- Auto-load on startup
- Environment variable integration

---

#### 2. Preferential Attachment Probability Parameter | 优先连接概率参数 | 우선 연결 확률 매개변수

**English:**
- Added Preferential Attachment Probability parameter in Parameters tab
- Default value: 0.85 (85% probability)
- Currently displayed for reference (hard-coded in core script)
- Future versions will support dynamic configuration

**中文:**
- 在参数配置标签页添加了优先连接概率参数
- 默认值：0.85（85%概率）
- 目前显示供参考（在核心脚本中硬编码）
- 未来版本将支持动态配置

**한국어:**
- 매개변수 탭에 우선 연결 확률 매개변수 추가
- 기본값: 0.85 (85% 확률)
- 현재 참조용으로 표시됨 (핵심 스크립트에 하드코딩)
- 향후 버전에서 동적 구성 지원 예정

**Note:** This parameter controls the probability of selecting high-degree nodes during the building phase, implementing the "rich get richer" principle in network evolution.

---

#### 3. Personas Viewer | 节点查看器 | 페르소나 뷰어

**English:**
- Added comprehensive Personas Viewer in Entity Generation tab
- Right-side panel for viewing all persona details
- Features include:
  - Load and browse personas JSON files
  - Display total persona count
  - Search by persona ID
  - Interactive list with formatted display
  - Detailed view of selected persona
  - Refresh functionality

**中文:**
- 在节点生成标签页添加了全面的节点查看器
- 右侧面板用于查看所有节点详情
- 功能包括：
  - 加载和浏览节点JSON文件
  - 显示节点总数
  - 按节点ID搜索
  - 交互式格式化显示列表
  - 选定节点的详细视图
  - 刷新功能

**한국어:**
- 엔티티 생성 탭에 포괄적인 페르소나 뷰어 추가
- 모든 페르소나 세부 정보를 보기 위한 오른쪽 패널
- 기능 포함:
  - 페르소나 JSON 파일 로드 및 찾아보기
  - 총 페르소나 수 표시
  - 페르소나 ID로 검색
  - 형식화된 표시가 있는 대화형 목록
  - 선택한 페르소나의 상세 보기
  - 새로 고침 기능

**UI Layout:**
```
┌─────────────────────────┬──────────────────────┐
│ Entity Generation       │ Personas Viewer      │
│                         │                      │
│ • Generation Method     │ [Load File Button]   │
│ • Parameters            │ Total: 1000          │
│ • Generate Button       │ [Search Box]         │
│ • Log Display           │                      │
│                         │ ┌──────────────────┐ │
│                         │ │ Personas List    │ │
│                         │ │ ID | Gender|Race │ │
│                         │ └──────────────────┘ │
│                         │                      │
│                         │ ┌──────────────────┐ │
│                         │ │ Persona Details  │ │
│                         │ │ Full info display│ │
│                         │ └──────────────────┘ │
└─────────────────────────┴──────────────────────┘
```

---

### Technical Improvements | 技术改进 | 기술 개선

#### UTF-8 Encoding Fix | UTF-8编码修复 | UTF-8 인코딩 수정

**Problem:** Windows GBK encoding error when displaying emoji characters

**Solution:**
- Added `PYTHONIOENCODING='utf-8'` environment variable
- Set `encoding='utf-8'` and `errors='replace'` for all subprocess calls
- Ensures compatibility with emoji and special characters on all platforms

**Affected Functions:**
- `_run_generation()`
- `_run_evaluation_script()`
- `_generate_entities()`

---

### Updated Language Keys | 更新的语言键 | 업데이트된 언어 키

New translation keys added to `languages.json`:

```json
{
  "api_configuration": "API Configuration / API配置 / API 구성",
  "api_key": "API Key / API密钥 / API 키",
  "api_base_url": "API Base URL / API基础URL / API 기본 URL",
  "save_api_config": "Save API Config / 保存API配置 / API 구성 저장",
  "preferential_attachment": "Preferential Attachment Probability / 优先连接概率 / 우선 연결 확률",
  "personas_viewer": "Personas Viewer / 节点查看器 / 페르소나 뷰어",
  "load_personas": "Load Personas File / 加载节点文件 / 페르소나 파일 로드",
  "total_personas": "Total Personas / 总节点数 / 총 페르소나",
  "search_persona": "Search by ID / 按ID搜索 / ID로 검색",
  "persona_details": "Persona Details / 节点详情 / 페르소나 세부정보",
  "refresh": "Refresh / 刷新 / 새로 고침",
  "clear": "Clear / 清空 / 지우기",
  "api_config_saved": "API configuration saved successfully / API配置保存成功 / API 구성이 성공적으로 저장되었습니다",
  "load_file_first": "Please load a personas file first / 请先加载节点文件 / 먼저 페르소나 파일을 로드하세요"
}
```

---

### File Changes | 文件更改 | 파일 변경

#### Modified Files | 修改的文件 | 수정된 파일

1. **main.py** (~1000 lines)
   - Added API configuration section
   - Added personas viewer in entity tab
   - Added preferential attachment parameter display
   - Fixed UTF-8 encoding issues
   - Added new helper methods

2. **languages.json** (~342 lines)
   - Added 13 new translation keys
   - Full tri-language support for all new features

3. **UPDATES.md** (this file)
   - Documentation of all changes

---

### Usage Instructions | 使用说明 | 사용 지침

#### Configuring API | API配置 | API 구성

1. Go to **Parameters** tab
2. Enter your API Key (will be hidden)
3. Enter your API Base URL
4. Click **Save API Config**
5. Configuration will be loaded automatically next time

#### Using Personas Viewer | 使用节点查看器 | 페르소나 뷰어 사용

1. Go to **Entity Generation** tab
2. In the right panel, click **Browse** to select a personas JSON file
3. Click **Load Personas File**
4. View the list of all personas
5. Use the search box to filter by ID
6. Click on any persona to view full details

#### Preferential Attachment | 优先连接概率 | 우선 연결 확률

1. Go to **Parameters** tab
2. Find **Preferential Attachment Probability** field
3. Default value is 0.85 (85%)
4. Note: This is currently for reference only
5. Future versions will support changing this value

---

### Known Limitations | 已知限制 | 알려진 제한사항

1. **Preferential Attachment Parameter:**
   - Currently hard-coded in core script
   - GUI displays value but doesn't pass to script yet
   - Will be fully functional in future versions

2. **Personas Viewer:**
   - Read-only (cannot edit personas in GUI)
   - Large files (>10,000 personas) may take time to load

---

### Future Enhancements | 未来增强 | 향후 개선

1. Make preferential attachment parameter configurable in core script
2. Add persona editing capabilities
3. Support for creating new personas in GUI
4. Batch operations in personas viewer
5. Export filtered personas to new file
6. Visual statistics display in personas viewer

---

### Compatibility | 兼容性 | 호환성

- **Windows:** ✅ Fully tested with UTF-8 encoding fixes
- **macOS:** ✅ Compatible
- **Linux:** ✅ Compatible
- **Python:** 3.7+ required

---

### Credits | 致谢 | 크레딧

Version 1.1 updates include user-requested features for better API management, parameter visibility, and persona data exploration.

感谢用户反馈，本版本添加了API管理、参数可见性和节点数据浏览等功能。

사용자 피드백에 감사드리며, 이 버전에는 더 나은 API 관리, 매개변수 가시성 및 페르소나 데이터 탐색을 위한 기능이 추가되었습니다。

---

**For questions or issues, please refer to the main documentation or contact the development team.**

**如有问题，请参考主要文档或联系开发团队。**

**질문이나 문제가 있으면 주요 문서를 참조하거나 개발 팀에 문의하세요。**

