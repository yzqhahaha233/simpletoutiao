# 新闻资讯 App（SimpleToutiao）

模仿今日头条实现的移动端新闻资讯应用，前后端分离架构，内置 AI 问答功能。适合作为期末课程设计，依赖少、部署简单。

## 功能特性

- **用户系统** — 注册、登录、Token 认证、修改资料与密码
- **新闻浏览** — 分类列表、新闻列表（分页）、详情查看
- **收藏管理** — 收藏 / 取消收藏、收藏列表、一键清空
- **浏览历史** — 自动记录、列表查看、单条删除、全部清空
- **AI 问答** — 基于通义千问的新闻问答助手，回答支持 Markdown 渲染
- **个性化** — 中英文国际化、深色 / 浅色主题、移动端适配

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Vue 3、Vite 7、Pinia（含持久化）、Vue Router 4、Vant 4、Axios、vue-i18n、marked + DOMPurify |
| 后端 | FastAPI、SQLAlchemy 2.0（异步）、aiomysql、Pydantic |
| 数据存储 | MySQL 8（主库）、Redis（缓存） |
| 密码安全 | bcrypt（`$2b$` 哈希） |

## 项目结构

```
toutiao/
├── 项目物料/
│   ├── 01-接口规范文档/
│   │   └── API接口规范文档.md          # 全部接口的详细说明
│   ├── 02-数据库sql文件/
│   │   └── database.sql                # 建表语句 + 分类/新闻/测试账号种子数据
│   ├── 03-前端项目代码/
│   │   └── xwzx-news/                  # Vue 3 前端工程
│   │       ├── src/
│   │       │   ├── views/              # 页面：首页、分类、详情、收藏、历史、我的、AI 问答…
│   │       │   ├── components/         # 通用组件：NewsItem、TabBar
│   │       │   ├── store/              # Pinia 状态：user、news、favorite、history、theme、language
│   │       │   ├── i18n/               # 国际化：zh-CN / en-US
│   │       │   ├── config/api.js       # 后端地址与 AI 配置
│   │       │   └── router/             # 路由表
│   │       ├── package.json
│   │       └── vite.config.js
│   ├── toutiao_backend/                # FastAPI 后端
│   │   ├── main.py                     # 应用入口，注册路由与 CORS
│   │   ├── config/                     # 数据库、Redis 配置
│   │   ├── routers/                    # 路由层：news、users、favorite、history
│   │   ├── crud/                       # 数据访问层
│   │   ├── models/                     # SQLAlchemy 模型
│   │   ├── schemas/                    # Pydantic 校验模型
│   │   ├── utils/                      # 认证、密码、异常处理、统一响应
│   │   └── requirements.txt
│   └── 项目后端设计说明文档.md
└── README.md
```

## 快速开始

### 环境要求

| 依赖 | 版本 |
|---|---|
| Python | 3.10 及以上 |
| Node.js | 18 及以上 |
| MySQL | 8.0 及以上 |
| Redis | 5.0 及以上（不做缓存可跳过） |

### 第一步：初始化数据库

```sql
CREATE DATABASE news_app DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

导入建表语句与种子数据：

```bash
mysql -u root -p news_app < "项目物料/02-数据库sql文件/database.sql"
```

导入后得到 8 张表：`user`、`user_token`、`news_category`、`news`、`related_news`、`favorite`、`history`、`ai_chat`，并附带一个测试账号 `admin`（密码为 bcrypt 哈希，课程演示用，建议自行注册新账号）。

### 第二步：启动后端

```bash
cd 项目物料/toutiao_backend

# 安装依赖
pip install -r requirements.txt

# 从模板生成配置文件（模板里不含真实密码）
copy config\db_conf.example.py config\db_conf.py

# 打开 db_conf.py，把 your_password 换成你的 MySQL 密码
notepad config\db_conf.py

# 启动服务
python main.py
```

启动后：

- 服务地址：<http://127.0.0.1:8000>
- 交互式 API 文档：<http://127.0.0.1:8000/docs>

### 第三步：启动前端

```bash
cd 项目物料/03-前端项目代码/xwzx-news

npm install
npm run dev
```

按终端提示的地址访问（通常是 <http://localhost:5173>）。

### 第四步：按需调整配置

| 配置项 | 文件 | 说明 |
|---|---|---|
| 数据库连接 | `toutiao_backend/config/db_conf.py` | 库名、账号、密码 |
| Redis 连接 | `toutiao_backend/config/cache_conf.py` | 默认 `localhost:6379`，使用 `db=1` |
| 后端地址 | `xwzx-news/src/config/api.js` | 前端请求的 `baseURL`，默认 `http://127.0.0.1:8000` |
| AI 问答密钥 | `xwzx-news/src/config/api.js` | `aiChatConfig.apiKey`，需填入自己的通义千问密钥 |

## 接口一览

完整参数说明见 [`项目物料/01-接口规范文档/API接口规范文档.md`](项目物料/01-接口规范文档/API接口规范文档.md)。

统一响应结构：

```json
{ "code": 200, "message": "success", "data": {} }
```

需认证的接口在请求头携带 `Authorization: <token>`。

| 模块 | 方法 | 路径 | 说明 |
|---|---|---|---|
| 用户 | POST | `/api/user/register` | 注册 |
| 用户 | POST | `/api/user/login` | 登录 |
| 用户 | GET | `/api/user/info` | 获取用户信息 |
| 用户 | PUT | `/api/user/update` | 更新资料 |
| 用户 | PUT | `/api/user/password` | 修改密码 |
| 新闻 | GET | `/api/news/categories` | 分类列表 |
| 新闻 | GET | `/api/news/list` | 新闻列表（分页） |
| 新闻 | GET | `/api/news/detail` | 新闻详情 |
| 收藏 | GET | `/api/favorite/check` | 收藏状态 |
| 收藏 | POST | `/api/favorite/add` | 添加收藏 |
| 收藏 | DELETE | `/api/favorite/remove` | 取消收藏 |
| 收藏 | GET | `/api/favorite/list` | 收藏列表 |
| 收藏 | DELETE | `/api/favorite/clear` | 清空收藏 |
| 历史 | POST | `/api/history/add` | 添加浏览记录 |
| 历史 | GET | `/api/history/list` | 历史列表 |
| 历史 | DELETE | `/api/history/delete/{history_id}` | 删除单条 |
| 历史 | DELETE | `/api/history/clear` | 清空历史 |

## 说明

- **数据库配置不入库**：`config/db_conf.py` 已加入 `.gitignore`，仓库中只保留 `db_conf.example.py` 模板，克隆后需按第二步自行生成。
- **CORS 为开发配置**：`main.py` 中 `allow_origins=["*"]` 仅适用于本地开发，部署到服务器前应改为具体域名。
- **AI 密钥**：`src/config/api.js` 中的 `apiKey` 需替换为你自己的密钥。前端代码对用户可见，生产环境建议改为由后端代理调用，避免密钥暴露。
- **热重载**：`main.py` 中设置了 `WATCHFILES_FORCE_POLLING=1`，解决 PyCharm 保存时 watchfiles 监听失效导致热重载不触发的问题。

## 许可证

本项目为学习实践项目，未指定开源许可证。如需开源，建议补充 `LICENSE` 文件。
