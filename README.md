## 自动化扫雷工具winmine

### 安装环境
- python2.7
- 扫雷程序（winmine.exe）

### requirement txt
```
docopt
ctypes
win32gui
win32con
win32api
time
```

### 使用方法
```
Usage:
    python winmine.py [-sadc]

Options:
    -h,--help 显示帮助
    -d        显示雷区布置
    -s        计时器停止
    -a        自动扫雷
    -c        点到雷也不会终止
```