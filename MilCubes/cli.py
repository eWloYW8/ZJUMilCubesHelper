#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MilCubes 命令行工具
提供便捷的命令行接口来操作 MilCubes 平台
"""

import argparse
import json
import os
import sys
from getpass import getpass
from typing import Optional

from api import MilCubesSession, Project


def login(args) -> Optional[MilCubesSession]:
    """登录 MilCubes 平台"""
    session = None
    
    if args.cookies:
        try:
            with open(args.cookies, 'r', encoding='utf-8') as f:
                cookies_json = f.read()
            session = MilCubesSession.from_cookies_json(cookies_json)
            print(f"已通过 cookies 文件 '{args.cookies}' 登录")
        except Exception as e:
            print(f"通过 cookies 登录失败: {e}")
            return None
    
    elif args.username:
        password = args.password or getpass("请输入密码: ")
        try:
            session = MilCubesSession.from_username_password(args.username, password)
            print(f"已通过用户名 '{args.username}' 登录")
        except Exception as e:
            print(f"通过用户名密码登录失败: {e}")
            return None
    
    return session


def list_projects(session: MilCubesSession, args):
    """列出所有项目"""
    projects = session.get_projects()
    print(f"共找到 {len(projects)} 个项目:")
    for project in projects:
        print(f"ID: {project.id}, 标题: {project.title}")


def download_project(session: MilCubesSession, args):
    """下载项目内容"""
    projects = session.get_projects()
    
    if args.id:
        try:
            project = projects.find_by_id(args.id)
            print(f"正在下载项目 '{project.title}' (ID: {project.id})...")
            project.download_content()
            print(f"项目内容已保存到 '{project.id}-{project.title}.html'")
        except ValueError as e:
            print(f"错误: {e}")
    
    elif args.title:
        try:
            project = projects.find_by_title(args.title)
            print(f"正在下载项目 '{project.title}' (ID: {project.id})...")
            project.download_content()
            print(f"项目内容已保存到 '{project.id}-{project.title}.html'")
        except ValueError as e:
            print(f"错误: {e}")
    
    elif args.all:
        print(f"正在下载所有 {len(projects)} 个项目...")
        projects.download_all_content()
        print("所有项目内容已下载完成")


def upload_project(session: MilCubesSession, args):
    """上传项目内容"""
    projects = session.get_projects()
    
    if args.id and args.file:
        try:
            project = projects.find_by_id(args.id)
            print(f"正在从文件 '{args.file}' 上传内容到项目 '{project.title}' (ID: {project.id})...")
            project.upload_from_file(args.file, session)
            print("上传完成")
        except ValueError as e:
            print(f"错误: {e}")
        except FileNotFoundError:
            print(f"错误: 文件 '{args.file}' 不存在")
    
    elif args.title and args.file:
        try:
            project = projects.find_by_title(args.title)
            print(f"正在从文件 '{args.file}' 上传内容到项目 '{project.title}' (ID: {project.id})...")
            project.upload_from_file(args.file, session)
            print("上传完成")
        except ValueError as e:
            print(f"错误: {e}")
        except FileNotFoundError:
            print(f"错误: 文件 '{args.file}' 不存在")


def upload_file(session: MilCubesSession, args):
    """上传文件到 MilCubes 平台"""
    if not os.path.exists(args.file):
        print(f"错误: 文件 '{args.file}' 不存在")
        return
    
    mime_type = args.mime or "application/octet-stream"
    try:
        url, file_id = session.upload_file_by_path(args.file, mime_type)
        print(f"文件上传成功:")
        print(f"URL: {url}")
        print(f"文件ID: {file_id}")
    except Exception as e:
        print(f"文件上传失败: {e}")


def main():
    """命令行工具主函数"""
    parser = argparse.ArgumentParser(description="MilCubes 命令行工具")
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    # 登录参数
    parser.add_argument("--username", "-u", help="登录用户名")
    parser.add_argument("--password", "-p", help="登录密码")
    parser.add_argument("--cookies", "-c", help="包含 cookies 的 JSON 文件路径")
    
    # 列出项目
    list_parser = subparsers.add_parser("list", help="列出所有项目")
    
    # 下载项目
    download_parser = subparsers.add_parser("download", help="下载项目内容")
    download_group = download_parser.add_mutually_exclusive_group(required=True)
    download_group.add_argument("--id", type=int, help="项目 ID")
    download_group.add_argument("--title", help="项目标题")
    download_group.add_argument("--all", action="store_true", help="下载所有项目")
    
    # 上传项目
    upload_parser = subparsers.add_parser("upload", help="上传项目内容")
    upload_group = upload_parser.add_mutually_exclusive_group(required=True)
    upload_group.add_argument("--id", type=int, help="项目 ID")
    upload_group.add_argument("--title", help="项目标题")
    upload_parser.add_argument("--file", required=True, help="要上传的 HTML 文件路径")
    
    # 上传文件
    file_parser = subparsers.add_parser("file", help="上传文件")
    file_parser.add_argument("--file", required=True, help="要上传的文件路径")
    file_parser.add_argument("--mime", help="文件的 MIME 类型")
    
    args = parser.parse_args()
    
    # 如果没有提供命令，显示帮助信息
    if not args.command and not (args.username or args.cookies):
        parser.print_help()
        return
    
    # 登录
    session = login(args)
    if not session:
        return
    
    # 执行相应的命令
    if args.command == "list":
        list_projects(session, args)
    elif args.command == "download":
        download_project(session, args)
    elif args.command == "upload":
        upload_project(session, args)
    elif args.command == "file":
        upload_file(session, args)


if __name__ == "__main__":
    main()