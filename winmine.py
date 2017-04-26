#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-04-22 16:07:48
# @Author  : jiong (447991103@qq.com)
# @Version : $Id$

"""
Automatic demining tools

Usage:
	winmine.py [-sadc]
	winmine.py [-d]


Options:
	-h,--help 显示帮助
	-d        显示雷区布置
	-s        计时器停止
	-a        自动扫雷
	-c        点到雷也不会终止

"""
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
from docopt import docopt

from ctypes import *
import win32gui
import win32process
import win32con
import win32api

import time


"""
BOOL WriteProcessMemory(
HANDLE     hProcess,
LPVOID     lpBaseAddress,
LPCVOID    lpBuffer,
SIZE_T     nSize,
SIZE_T*    lpNumberOfBytesWritten
);

其参数含义如下。
hProcess:                   要写内存的进程句柄。
lpBaseAddress:              要写的内存起始地址。
lpBuffer:                   写入值的地址。
nSize:                      写入值的大小。
lpNumberOfBytesWritten:     实际写入的大小。
"""


MAX_ROWS = 24
MAX_COLUMNS = 30
# 雷区格子在窗体上的起始坐标及每个格子的宽度
MINE_BEGIN_X = 0xC
MINE_BEGIN_Y = 0x37
MINE_GRID_WIDTH = 0x10
MINE_GRID_HEIGHT = 0x10

# 边框、无雷、有雷的内部表示
MINE_BOARDER = 0x10

MINE_SAFE = 0x0F
MINE_DANGER = 0x8F

# 雷区在 扫雷程序中的存储地址
BOARD_ADDR = 0x1005340
width_address = 0x01005334
height_address = 0x01005338


# 定义_PROCESS_INFORMATION结构体
class _PROCESS_INFORMATION(Structure):
	_fields_ = [('hProcess', c_void_p),
				('hThread', c_void_p),
				('dwProcessId', c_ulong),
				('dwThreadId', c_ulong)]


# 定义_STARTUPINFO结构体
class _STARTUPINFO(Structure):
	_fields_ = [('cb', c_ulong),
				('lpReserved', c_char_p),
				('lpDesktop', c_char_p),
				('lpTitle', c_char_p),
				('dwX', c_ulong),
				('dwY', c_ulong),
				('dwXSize', c_ulong),
				('dwYSize', c_ulong),
				('dwXCountChars', c_ulong),
				('dwYCountChars', c_ulong),
				('dwFillAttribute', c_ulong),
				('dwFlags', c_ulong),
				('wShowWindow', c_ushort),
				('cbReserved2', c_ushort),
				('lpReserved2', c_char_p),
				('hStdInput', c_ulong),
				('hStdOutput', c_ulong),
				('hStdError', c_ulong)]


class SMineCtrl(Structure):
	_fields_ = [("hWnd", c_uint),
				("board", (c_byte * (MAX_COLUMNS + 2)) * (MAX_ROWS + 2)),
				("rows", c_byte),
				("columns", c_byte)
				]


ctrlData = SMineCtrl()

kernel32 = windll.LoadLibrary("kernel32.dll")   # 加载kernel32.dll
ProcessInfo = _PROCESS_INFORMATION()
StartupInfo = _STARTUPINFO()


class winmine():

	def __init__(self,):

		self.NORMAL_PRIORITY_CLASS = 0x00000020              # 定义NORMAL_PRIORITY_CLASS
		self.file = './winmine.exe'                           # 要进行修改的文件
		self.CreateProcess = kernel32.CreateProcessA         # 获得CreateProcess函数地址

		self.ReadProcessMemory = kernel32.ReadProcessMemory  # 获得ReadProcessMemory函数地址
		self.WriteProcessMemory = kernel32.WriteProcessMemory  # 获得WriteProcessMemory函数地址
		self.TerminateProcess = kernel32.TerminateProcess

	def start(self):

		if self.CreateProcess(self.file, 0, 0, 0, 0, self.NORMAL_PRIORITY_CLASS, 0, 0, byref(StartupInfo), byref(ProcessInfo)):
			print 'create success'
		else:
			print 'Create Process error'

	def stop_clock(self):

		address = 0x01002FF5                            # 要修改的内存地址
		buffer = c_char_p("_")                          # 缓冲区地址
		bytesRead = c_ulong(4)                          # 读入的字节数
		bufferSize = len(buffer.value)                  # 缓冲区大小

		# os.system('pause')

		if self.ReadProcessMemory(ProcessInfo.hProcess, address, buffer, bufferSize, byref(bytesRead)):
			# print buffer.value
			# print '\xFF'
			a = []
			a.append(buffer.value)
			print a
			if buffer.value == '\xFF':
				# \x90是nop 空指令
				# print 'aaa'
				buffer.value = '\x90'
				# 修改内存
				if self.WriteProcessMemory(ProcessInfo.hProcess, address, buffer, bufferSize, byref(bytesRead)):
					print 'write sucess \n now clock is stopped'
				else:
					print 'write fail'
			else:
				print 'open error'
				TerminateProcess(ProcessInfo.hProcess, 0)   # 如果不是要修改的文件，则终止进程
		else:
			print 'read Memory error'

	def auto_mining(self):
		buffer = c_char_p("_")
		bytesRead = c_ulong(4)
		bufferSize = len(buffer.value)
		# print bufferSize
		a=[]
		if self.ReadProcessMemory(ProcessInfo.hProcess, width_address, buffer, bufferSize, byref(bytesRead)):
			# print buffer.value.encode('hex')
			print 'width'
			a.append(buffer.value)

		if self.ReadProcessMemory(ProcessInfo.hProcess, height_address, buffer, bufferSize, byref(bytesRead)):
			print 'height'
			a.append(buffer.value)
		print len(a)
		print 'width:', ord(a[0]), 'height:', ord(a[1])

		self.ReadProcessMemory(ProcessInfo.hProcess, BOARD_ADDR, byref(
			ctrlData.board), SMineCtrl.board.size, byref(bytesRead))

		# 获取本次程序雷区的实际大小
		ctrlData.rows = 0
		ctrlData.columns = 0
		print 'MAX_COLUMNS',MAX_COLUMNS
		for i in range(0, MAX_COLUMNS + 2):
			if MINE_BOARDER == ctrlData.board[0][i]:
				ctrlData.columns += 1
			else:
				break
		print 'columns'
		print ctrlData.columns
		# print ctrlData.board[1]

		ctrlData.columns -= 2
		for i in range(1, MAX_ROWS + 1):
			if MINE_BOARDER != ctrlData.board[i][1]:
				ctrlData.rows += 1
			else:
				break
		print 'rows'
		print ctrlData.rows

		ctrlData.hWnd = win32gui.FindWindow('Minesweeper', None)
		# print type(ctrlData.hWnd)

		# 模拟鼠标点击动作
		for i in range(0, ctrlData.rows):
			for j in range(0, ctrlData.columns):
				if MINE_SAFE == ctrlData.board[i + 1][j + 1]:
					# print '11'
					time.sleep(0.001)
					win32api.SendMessage(ctrlData.hWnd,
										 win32con.WM_LBUTTONDOWN,
										 win32con.MK_LBUTTON,
										 win32api.MAKELONG(MINE_BEGIN_X + MINE_GRID_WIDTH * j + MINE_GRID_WIDTH / 2,
														   MINE_BEGIN_Y + MINE_GRID_HEIGHT * i + MINE_GRID_HEIGHT / 2))
					win32api.SendMessage(ctrlData.hWnd,
										 win32con.WM_LBUTTONUP,
										 win32con.MK_LBUTTON,
										 win32api.MAKELONG(MINE_BEGIN_X + MINE_GRID_WIDTH * j + MINE_GRID_WIDTH / 2,
														   MINE_BEGIN_Y + MINE_GRID_HEIGHT * i + MINE_GRID_HEIGHT / 2))
		# 搞定!
		# win32api.MessageBox(0, "搞定！".encode('gbk'), "信息".encode('gbk'), win32con.MB_ICONINFORMATION)

	def display(self):

		buffer = c_char_p("_")                          # 缓冲区地址
		bytesRead = c_ulong(6)                          # 读入的字节数
		bufferSize = len(buffer.value)                  # 缓冲区大小

		self.ReadProcessMemory(ProcessInfo.hProcess, BOARD_ADDR, byref(
			ctrlData.board), SMineCtrl.board.size, byref(bytesRead))

		# 获取本次程序雷区的实际大小
		ctrlData.rows = 0
		ctrlData.columns = 0

		for i in range(0, MAX_COLUMNS + 2):
			if MINE_BOARDER == ctrlData.board[0][i]:
				ctrlData.columns += 1
			else:
				break
		print ctrlData.columns
		# print ctrlData.board[1]

		ctrlData.columns -= 2

		for i in range(1, MAX_ROWS + 1):
			if MINE_BOARDER != ctrlData.board[i][1]:
				ctrlData.rows += 1
			else:
				break
		print '\nrows'
		print ctrlData.rows

		res = []
		for i in range(0, ctrlData.rows):
			res = []
			for j in range(0, ctrlData.columns):

				if MINE_SAFE == ctrlData.board[i + 1][j + 1]:
					# print '11'
					time.sleep(0.001)
					res.append('-')
					# print '-'
				else:
					res.append('*')
					# print '*'+
			print ''.join(res)

	def no_explode(self):

		no_explode_address = 0x01003591

		buffer = c_char_p("--")
		bytesRead = c_ulong(2)
		bufferSize = len(buffer.value)
		print bufferSize
		if self.ReadProcessMemory(ProcessInfo.hProcess, no_explode_address, buffer, bufferSize, byref(bytesRead)):
			buffer.value = '\xEB\x1D'
			if self.WriteProcessMemory(ProcessInfo.hProcess, no_explode_address, buffer, bufferSize, byref(bytesRead)):
				print 'write sucess \n now no explode'
			else:
				print 'write fail'
		else:
			print 'read error'


def cli(test):
	arguments = docopt(__doc__)
	if arguments['-s']:
		test.stop_clock()

	if arguments['-d']:
		test.display()

	if arguments['-a']:
		test.auto_mining()

	if arguments['-c']:
		test.no_explode()

	print arguments


if __name__ == '__main__':
	test = winmine()
	test.start()
	time.sleep(2)
	cli(test)
