import serial
import time
class SerialManager:
	def __init__ (self,port,baudrate=115200,timeout=1):
		self.port=port
		self.baudrate=baudrate
		self.timeout=timeout
		self.ser=None
	def open(self):
		if self.ser is not None and self.ser.is_open:
			return True
		try:
			self.ser=serial.Serial(port=self.port,baudrate=self.baudrate,timeout=self.timeout)
			return self.ser.is_open
		except serial.SerialException as ex:
			print(f"[serial error]{ex}")
			return False
		except Exception as ex:
			print(f"[serial error]{ex}")
			return False
	def close(self):
		if self.ser is None or not self.ser.is_open :
			return True
		try:
			self.ser.close()
			self.ser=None
			return True
		except serial.SerialException as ex:
			print(f"[serial error]{ex}")
			return False
		except Exception as ex:
			print(f"[serial error]{ex}")
			return False
	def write(self,cmd):
		try:
			if self.ser is None or not self.ser.is_open:
				return False
			command=f"{cmd}\r\n"
			send=self.ser.write(command.encode())
			if send > 0:
				return True
			else:
				print("send is empty")
				return False
		except serial.SerialException as ex:
			print(f"[serial error]{ex}")
			return False
		except Exception as ex:
			print(f"[serial send error]{ex}")
			return False
	def write_bytes(self,data):
		try:
			if self.ser is None or not self.ser.is_open:
				return False
			send=self.ser.write(data)
			return send > 0
		except Exception as ex:
			print(ex)
			return False
	def read(self):
		try:
			if self.ser is None or not self.ser.is_open:
				return False
			response = self.ser.read_all()
			return response
		except serial.SerialException as ex:
			print(f"[serial error]{ex}")
			return False
		except Exception as ex:
			print(f"[serial read error]{ex}")
			return False
	def read_response(self,timeout=10):
		try:
			if self.ser is None or not self.ser.is_open:
				return False
			old_timeout=self.ser.timeout
			self.ser.timeout=0.2
			response = bytearray()
			start_time = time.time()
			while time.time() - start_time < timeout:
				waiting = self.ser.in_waiting
				if waiting > 0:
					response.extend(self.ser.read(waiting))
					if b"OK\r\n" in response:
						break
				time.sleep(0.1)
			self.ser.timeout = old_timeout
			return bytes(response)
		except serial.SerialException as ex:
			print(f"[serial error] {ex}")
			return False
		except Exception as ex:
			print(f"[serial read response error] {ex}")
			return False
	def flush(self):
		if self.ser is None or not self.ser.is_open:
			return False
		try:
			self.ser.flush()
			return True
		except serial.SerialException as ex:
			print(f"[serial error]{ex}")
			return False
		except Exception as ex:
			print(f"[serial flush error]{ex}")
			return False			
	def is_open(self):
		return self.ser is not None and self.ser.is_open
	def read_line(self):
		if self.ser is None or not self.ser.is_open:
			return False
		try:
			response = self.ser.readline()
			return response
		except serial.SerialException as ex:
			print(f"[serial error]{ex}")
			return False
		except Exception as ex:
			print(f"[serial read_line error]{ex}")
			return False
	def read_until(self,char):
		if self.ser is None or not self.ser.is_open:
			return False
		try:
			if isinstance(char,str):
				char=char.encode()
			response = self.ser.read_until(char)
			return response
		except serial.SerialException as ex:
			print(f"[serial error]{ex}")
			return False
		except Exception as ex:
			print(f"[serial read until error]{ex}")
			return False			
	def clear_buffer(self):
		if self.ser is None or not self.ser.is_open:
			return False
		try:
			self.ser.reset_input_buffer()
			self.ser.reset_output_buffer()
			return True
		except serial.SerialException as ex:
			print(f"[serial error]{ex}")
			return False
		except Exception as ex:
			print(f"[serial clear buffer error]{ex}")
			return False
