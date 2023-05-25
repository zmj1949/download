from utlis.device import get_frida_device
from utlis import print_msg, write_xlsx
import frida
import sys
import argparse
import time
import traceback
import signal
from sys import exit


		
def frida_hook(args,is_show=True, execl_file=None):
	
	def on_message(message, payload):
		""" 消息处理 """
		if message["type"] == "error":
			print(message)
			os.kill(os.getpid(), signal.SIGTERM)
			return
		if message['type'] == 'send':
			#print(message)
			data = message["payload"]
			if data["type"] == "notice":
				alert_time = data['time']
				action = data['action']
				arg = data['arg']
				messages = data['messages']
				stacks = data['stacks']
				if is_show:
					print("------------------------------start---------------------------------")
					print("[*] {0}，APP行为：{1}、行为描述：{2}、传入参数：{3}".format(
						alert_time, action, messages, arg.replace('\r\n', '，')))
					print("[*] 调用堆栈：")
					print(stacks)
					print("-------------------------------end----------------------------------")
				if execl_file:
					global execl_data
					execl_data.append({
						'alert_time': alert_time,
						'action': action,
						'messages': messages,
						'arg': arg,
						'stacks': stacks,
						'privacy_policy_status': "同意隐私政策后",
					})
			if data['type'] == "isHook":
				global isHook
				isHook = True	
				print(isHook)
		



	device_info = get_frida_device(args.serial, args.host)
	device = device_info["device"]
	print_msg('device:'+device.id)
	try:
		print_msg('pkg_name:'+args.package)
		pid = device.spawn([args.package])
		print_msg(pid)
		time.sleep(1)
		# 连接远端设备 附加到进程
		process = device.attach(pid)
		time.sleep(1)
		#process = frida.get_usb_device().attach('com.trusfort.dfs.demo.citic')
		# 基于脚本内容创建运行脚本对象
		#script = process.create_script(jscode)
		with open("privacy.js", encoding="utf-8") as f:
			 script_code = f.read()
		script = process.create_script(script_code)
		script.on('message', on_message)
		# 加载脚本并执行
		script.load()
		
		time.sleep(1)
		#重启
		device.resume(pid)
		time.sleep(1)
		if(isHook):
			def stop(signum,fram):
				print_msg('stoped hook.')
				process.detach()
				if execl_file:
					global execl_data
					print('write_xlsx')
					write_xlsx(execl_data, execl_file)
				exit()
			#Python信号处理
			signal.signal(signal.SIGINT, stop)
			signal.signal(signal.SIGTERM, stop)
			sys.stdin.read()
		else:
			print_msg("hook fail, try delaying hook, adjusting delay time")
		#sys.stdin.read()
	except frida.NotSupportedError as e:
			if 'unable to find application with identifier' in str(e):
				print_msg('找不到 {} 应用，请排查包名是否正确'.format(app_name))
			else:
				print_msg('frida-server没有运行/frida-server与frida版本不一致，请排查')
				print_msg(e)
	except frida.ProtocolError as e:
			print_msg('frida-server没有运行/frida-server与frida版本不一致，请排查')
			print_msg(e)
	except frida.ServerNotRunningError as e:
		print_msg('frida-server没有运行/没有连接设备，请排查')
		print_msg(e)
	except frida.ProcessNotFoundError as e:
		print_msg("找不到该进程，{}".format(str(e)))
	except frida.InvalidArgumentError as e:
		print_msg("script.js脚本错误，请排查")
		print_msg(e)
	except frida.InvalidOperationError as e:
		print_msg('hook被中断，是否运行其他hook框架(包括其他frida)，请排查')
	except frida.TransportError as e:
		print_msg('hook关闭或超时，是否运行其他hook框架(包括其他frida)/设备是否关闭selinux，请排查')
		print_msg(e)
	except KeyboardInterrupt:
		print_msg('You have stoped hook.')
	except Exception as e:
		print_msg("hook error ")
		print(traceback.format_exc())
	finally:
		exit()
		


#argparse是python用于解析命令行参数和选项的标准模块，用于解析命令行参数，目的是在终端窗口(ubuntu是终端窗口，windows是命令行窗口)输入训练的参数和选项。
#1:创建一个解析对象
parser = argparse.ArgumentParser(description="App privacy compliance testing.")
parser.add_argument("--serial", "-s", required=False,
                        help="use device with given serial(device id), you can get it by exec 'adb devices'")
parser.add_argument("--host", "-H", required=False,
                        help="connect to remote frida-server on HOST,ex:127.0.0.1:1234")
						
#2向该对象中添加你要关注的命令行参数和选项，每一个add_argument方法对应一个你要关注的参数或选项
parser.add_argument("package", help="APP_NAME or process ID ex: com.test.demo01")
parser.add_argument("--noshow", "-ns", required=False, action="store_const", default=True, const=False,
                        help="Showing the alert message")
parser.add_argument("--file", "-f", metavar="<path>", required=False, help="Name of Excel file to write")
						
#3最后调用parse_args()方法进行解析
args = parser.parse_args()
# 全局变量
isHook = False
execl_data = []

frida_hook(args,args.noshow,args.file)
    














