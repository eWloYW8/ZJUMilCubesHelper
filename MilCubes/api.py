# -*- coding: utf-8 -*-

"""
MilCubes API 客户端核心模块
提供与 MilCubes 平台交互的类和方法
"""

import requests
import json
import os
from typing import List, Dict, Tuple, Optional, Union, Any

class MilCubesError(Exception):
    """MilCubes API 错误基类"""
    pass

class AuthenticationError(MilCubesError):
    """认证错误"""
    pass

class APIError(MilCubesError):
    """API 调用错误"""
    pass

class MilCubesSession:
    """
    MilCubes 会话类，用于与 MilCubes 平台交互
    
    提供登录、获取项目、上传文件等功能
    """
    
    BASE_URL = 'https://milcubes.zju.edu.cn'
    LOGIN_URL = f'{BASE_URL}/login'
    AUTH_URL = f'{BASE_URL}/login/admin'
    INDEX_URL = f'{BASE_URL}/'
    API_URL = f'{BASE_URL}/api/admin'
    
    DEFAULT_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    
    def __init__(self, auth_token: str = None, session: requests.Session = None):
        """
        初始化 MilCubes 会话
        
        Args:
            auth_token: 认证令牌
            session: 请求会话对象，如果为 None 则创建新会话
        """
        self.session = session or requests.Session()
        self.auth_token = auth_token
        
        if auth_token:
            self.headers = self.DEFAULT_HEADERS.copy()
            self.headers['Authorization'] = f'Bearer {auth_token}'
        else:
            self.headers = self.DEFAULT_HEADERS.copy()
    
    @classmethod
    def from_cookies(cls, cookies: Dict[str, str]) -> 'MilCubesSession':
        """
        从 cookies 创建会话
        
        Args:
            cookies: cookies 字典
            
        Returns:
            MilCubesSession 实例
            
        Raises:
            AuthenticationError: 认证失败
        """
        session = requests.Session()
        session.cookies = requests.utils.cookiejar_from_dict(cookies)
        
        try:
            response = session.get(cls.AUTH_URL, headers=cls.DEFAULT_HEADERS, cookies=cookies, allow_redirects=False)
            
            if 'Location' not in response.headers:
                raise AuthenticationError("无法从 cookies 获取认证令牌")
                
            auth_token = response.headers['Location'].split('=')[1]
            return cls(auth_token, session)
        except Exception as e:
            raise AuthenticationError(f"从 cookies 创建会话失败: {str(e)}")
    
    @classmethod
    def from_cookies_json(cls, cookie_json: str) -> 'MilCubesSession':
        """
        从 JSON 格式的 cookies 创建会话
        
        Args:
            cookie_json: JSON 格式的 cookies 字符串
            
        Returns:
            MilCubesSession 实例
        """
        try:
            cookies = {}
            for item in json.loads(cookie_json):
                cookies[item['name']] = item['value']
            return cls.from_cookies(cookies)
        except Exception as e:
            raise AuthenticationError(f"从 JSON cookies 创建会话失败: {str(e)}")
    
    @classmethod
    def from_username_password(cls, username: str, password: str) -> 'MilCubesSession':
        """
        从用户名和密码创建会话
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            MilCubesSession 实例
            
        Raises:
            AuthenticationError: 认证失败
        """
        session = requests.Session()
        
        try:
            # 获取 CSRF 令牌
            response = session.get(cls.INDEX_URL, headers=cls.DEFAULT_HEADERS)
            if 'csrf-token" content="' not in response.text:
                raise AuthenticationError("无法获取 CSRF 令牌")
                
            token = response.text.split('csrf-token" content="')[1].split('">')[0]
            
            # 登录
            login_data = {'email': username, 'password': password, '_token': token}
            response = session.post(cls.LOGIN_URL, headers=cls.DEFAULT_HEADERS, data=login_data, allow_redirects=False)
            
            if response.status_code != 302:
                raise AuthenticationError("登录失败，请检查用户名和密码")
            
            # 获取认证令牌
            response = session.get(cls.AUTH_URL, headers=cls.DEFAULT_HEADERS, allow_redirects=False)
            
            if 'Location' not in response.headers:
                raise AuthenticationError("无法获取认证令牌")
                
            auth_token = response.headers['Location'].split('=')[1]
            return cls(auth_token, session)
        except AuthenticationError:
            raise
        except Exception as e:
            raise AuthenticationError(f"登录失败: {str(e)}")
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        发送 API 请求并返回响应数据
        
        Args:
            method: 请求方法 (get, post, put, delete)
            endpoint: API 端点
            **kwargs: 请求参数
            
        Returns:
            响应数据字典
            
        Raises:
            APIError: API 调用错误
        """
        url = f"{self.API_URL}/{endpoint}"
        
        if 'headers' not in kwargs:
            kwargs['headers'] = self.headers
        
        try:
            response = getattr(self.session, method.lower())(url, **kwargs)
            response.raise_for_status()
            data = response.json()
            
            if 'data' not in data:
                raise APIError(f"API 响应格式错误: {response.text}")
                
            return data['data']
        except requests.exceptions.RequestException as e:
            raise APIError(f"API 请求失败: {str(e)}")
        except json.JSONDecodeError:
            raise APIError(f"API 响应解析失败: {response.text}")
    
    def get_projects(self, offset: int = 0, limit: int = 1000) -> 'ProjectCollection':
        """
        获取项目列表
        
        Args:
            offset: 分页偏移量
            limit: 分页大小
            
        Returns:
            ProjectCollection 实例
        """
        data = self._make_request('get', 'project', params={'offset': offset, 'limit': limit})
        projects = [Project.from_dict(item) for item in data]
        return ProjectCollection(projects, self)
    
    def get_project(self, project_id: int) -> 'Project':
        """
        获取单个项目
        
        Args:
            project_id: 项目 ID
            
        Returns:
            Project 实例
        """
        data = self._make_request('get', f'project/{project_id}')
        return Project.from_dict(data)
    
    def update_project(self, project: 'Project') -> None:
        """
        更新项目
        
        Args:
            project: 要更新的项目
        """
        project.update(self)
    
    def upload_project(self, project: 'Project') -> None:
        """
        上传项目
        
        Args:
            project: 要上传的项目
        """
        project.upload(self)
    
    def upload_file(self, content: bytes, file_name: str, mime_type: str = 'application/octet-stream') -> Tuple[str, int]:
        """
        上传文件
        
        Args:
            content: 文件内容
            file_name: 文件名
            mime_type: MIME 类型
            
        Returns:
            (文件 URL, 文件 ID) 元组
        """
        # 获取上传签名
        data = self._make_request('get', 'file', params={'path': file_name, 'method': 'post'})
        signature = data['signature']
        
        # 上传文件到 OSS
        body = {
            'key': signature['dir'],
            'success_action_status': '200',
            'policy': signature['policy'],
            'OSSAccessKeyId': signature['accessid'],
            'Signature': signature['signature'],
        }
        
        try:
            self.session.post(
                signature['host'], 
                headers=self.headers, 
                data=body, 
                files={'file': (file_name, content, mime_type)}
            )
        except requests.exceptions.RequestException as e:
            raise APIError(f"文件上传失败: {str(e)}")
        
        # 注册文件
        file_data = self._make_request(
            'post', 
            'file', 
            data={'mime': mime_type, 'name': file_name, 'path': signature['dir']}
        )
        
        return (signature['host'] + signature['dir'], file_data['id'])
    
    def upload_file_by_path(self, file_path: str, mime_type: str = None) -> Tuple[str, int]:
        """
        通过文件路径上传文件
        
        Args:
            file_path: 文件路径
            mime_type: MIME 类型，如果为 None 则自动检测
            
        Returns:
            (文件 URL, 文件 ID) 元组
        """
        if mime_type is None:
            import mimetypes
            mime_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
            
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            return self.upload_file(content, os.path.basename(file_path), mime_type)
        except IOError as e:
            raise APIError(f"读取文件失败: {str(e)}")


class ProjectCollection:
    """
    项目集合类，用于管理多个项目
    """
    
    def __init__(self, projects: List['Project'], session: Optional[MilCubesSession] = None):
        """
        初始化项目集合
        
        Args:
            projects: 项目列表
            session: MilCubesSession 实例
        """
        self.projects = projects
        self.session = session
    
    def __iter__(self):
        return iter(self.projects)
    
    def __len__(self):
        return len(self.projects)
    
    def __getitem__(self, index):
        return self.projects[index]
    
    def __str__(self):
        return '\n'.join(str(project) for project in self.projects)
    
    def list(self) -> List[Tuple[int, str]]:
        """
        列出所有项目的 ID 和标题
        
        Returns:
            (项目 ID, 项目标题) 元组列表
        """
        return [(project.id, project.title) for project in self.projects]
    
    def find_by_id(self, project_id: int) -> 'Project':
        """
        通过 ID 查找项目
        
        Args:
            project_id: 项目 ID
            
        Returns:
            Project 实例
            
        Raises:
            ValueError: 项目未找到
        """
        for project in self.projects:
            if project.id == project_id:
                if self.session:
                    project.update(self.session)
                return project
        raise ValueError(f'未找到 ID 为 {project_id} 的项目')
    
    def find_by_title(self, title: str) -> 'Project':
        """
        通过标题查找项目
        
        Args:
            title: 项目标题
            
        Returns:
            Project 实例
            
        Raises:
            ValueError: 项目未找到
        """
        for project in self.projects:
            if project.title == title:
                if self.session:
                    project.update(self.session)
                return project
        raise ValueError(f'未找到标题为 {title} 的项目')
    
    def download_all_content(self, output_dir: str = '.') -> None:
        """
        下载所有项目内容
        
        Args:
            output_dir: 输出目录
        """
        os.makedirs(output_dir, exist_ok=True)
        for project in self.projects:
            project.download_content(output_dir)
    
    def upload_all_content(self) -> None:
        """
        上传所有项目内容
        
        Raises:
            ValueError: 未设置会话
        """
        if not self.session:
            raise ValueError("未设置会话，无法上传内容")
            
        for project in self.projects:
            project.upload(self.session)


class Project:
    """
    MilCubes 项目类
    """
    
    def __init__(
        self, 
        id: int, 
        group_id: int, 
        episode_id: int, 
        title: str, 
        cover: str, 
        content: str, 
        books: List[str] = None, 
        books_file_ids: List[int] = None, 
        images: List[str] = None, 
        images_file_ids: List[int] = None, 
        videos: List[str] = None, 
        videos_file_ids: List[int] = None, 
        **kwargs
    ):
        """
        初始化项目
        
        Args:
            id: 项目 ID
            group_id: 组 ID
            episode_id: 集 ID
            title: 标题
            cover: 封面 URL
            content: 内容 HTML
            books: 书籍 URL 列表
            books_file_ids: 书籍文件 ID 列表
            images: 图片 URL 列表
            images_file_ids: 图片文件 ID 列表
            videos: 视频 URL 列表
            videos_file_ids: 视频文件 ID 列表
            **kwargs: 其他属性
        """
        self.id = id
        self.group_id = group_id
        self.episode_id = episode_id
        self.title = title
        self.cover = cover
        self.content = content
        self.books = books or []
        self.books_file_ids = books_file_ids or []
        self.images = images or []
        self.images_file_ids = images_file_ids or []
        self.videos = videos or []
        self.videos_file_ids = videos_file_ids or []
        
        # 保存其他属性
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @classmethod
    def from_json(cls, json_data: str) -> 'Project':
        """
        从 JSON 字符串创建项目
        
        Args:
            json_data: JSON 字符串
            
        Returns:
            Project 实例
        """
        try:
            return cls.from_dict(json.loads(json_data))
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON 解析失败: {str(e)}")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Project':
        """
        从字典创建项目
        
        Args:
            data: 项目数据字典
            
        Returns:
            Project 实例
        """
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将项目转换为字典
        
        Returns:
            项目数据字典
        """
        return {
            'id': self.id,
            'group_id': self.group_id,
            'episode_id': self.episode_id,
            'title': self.title,
            'cover': self.cover,
            'content': self.content,
            'books': self.books,
            'books_file_ids': self.books_file_ids,
            'images': self.images,
            'images_file_ids': self.images_file_ids,
            'videos': self.videos,
            'videos_file_ids': self.videos_file_ids
        }
    
    def to_json(self) -> str:
        """
        将项目转换为 JSON 字符串
        
        Returns:
            JSON 字符串
        """
        return json.dumps(self.to_dict(), ensure_ascii=False)
    
    def __repr__(self):
        return f'Project(id={self.id}, title="{self.title}")'
    
    def __str__(self):
        return f'({self.id})\t{self.title}'
    
    def upload(self, session: MilCubesSession) -> None:
        """
        上传项目
        
        Args:
            session: MilCubesSession 实例
        """
        try:
            session._make_request(
                'put', 
                f'project/{self.id}', 
                data=self.to_dict()
            )
        except APIError as e:
            raise APIError(f"上传项目失败: {str(e)}")
    
    def update(self, session: MilCubesSession) -> None:
        """
        从服务器更新项目数据
        
        Args:
            session: MilCubesSession 实例
        """
        try:
            data = session._make_request('get', f'project/{self.id}')
            
            for key, value in data.items():
                setattr(self, key, value)
        except APIError as e:
            raise APIError(f"更新项目失败: {str(e)}")
    
    def download_content(self, output_dir: str = '.') -> str:
        """
        下载项目内容到文件
        
        Args:
            output_dir: 输出目录
            
        Returns:
            输出文件路径
        """
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, f'{self.id}-{self.title}.html')
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.content)
            return file_path
        except IOError as e:
            raise IOError(f"写入文件失败: {str(e)}")
    
    def upload_from_file(self, file_path: str, session: MilCubesSession) -> None:
        """
        从文件上传项目内容
        
        Args:
            file_path: 文件路径
            session: MilCubesSession 实例
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.content = f.read()
            self.upload(session)
        except IOError as e:
            raise IOError(f"读取文件失败: {str(e)}")