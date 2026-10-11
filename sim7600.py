#Class for Connection To Hardware
import time
import math
from hardware.serial_manager import SerialManager
class SIM7600:
	def __init__(self,serial_manager:SerialManager):
		self.serial = serial_manager

#Connection
	def connect(self):
		return self.serial.open()
	def disconnect(self):
		return self.serial.close()
	def is_connected(self):
		return self.serial.is_open()
	def initialize(self):
		try:
			print("SIM INITIALIZE START!!!")
			Cconnection = self.check_connection()
			if(Cconnection):
				print("Check connection: True")
			else:
				print("Check connection: False")
				return False
			Cecho = self.send_command("ATE0")
			if(Cecho and "OK" in Cecho):
				print("Turn off echo: True")
			else:
				print("Turn off echo: False")
				return False
			er = self.complete_error()
			if not er:
				return False
			gss = self.get_sim_status()
			if not gss:
				return False
			gnr = self.get_network_registration()
			if not gnr:
				return False
			gsq = self.get_signal_quality()
			if not gsq:
				return False
			csm = self.configure_sms_mode()
			if not csm:
				return False
			Cmemory = self.send_command('AT+CPMS="SM","SM","SM"')
			if (Cmemory and "OK" in Cmemory):
				print("check memory: SM")
			else:
				print("check memory: False")
				return False
			print("SIM INITIALIZE END!!!")
			return True
		except Exception as Ex:
			print(f"initialize sim7600 isn't work because:\n {Ex}")
			return False
#General
	def send_command(self,command,expected="OK",timeout:float=1.5):
		try:
			#self.serial.clear_buffer()
			resp = self.serial.write(command)
			if not resp:
				return None
			time.sleep(timeout)
			response = self.serial.read().decode("utf-8",errors="ignore")
			if expected is None:
				return response
			if expected in response:
				return response
			else:
				print(f"[sim response isn't expected:\n{response}]")
				return None
		except Exception as ex:
			print(f"[sim send command error:\n{ex}]")
			return None
	def check_connection(self):
		try:
			command="AT"
			response = self.send_command(command)
			if not response:
				print(f"[SIM] response isn't expected \n {response}")
				return None
			else:
				return True
		except Exception as Ex:
				print (f"[SIM] send command error {Ex}")
				return None

	def reset(self):
		try:
			if(self.check_connection()):
				command="AT+CRESET"
				response = self.send_command(command,"READY",5.0)
				if(response):
					return response
				else:
					None
			else:
				return None
		except Exception as Ex:
			print (f"[SIM] Reset function Error \n {Ex}")
			return None
	def get_imei(self):
		try:
			if(self.check_connection()):
				command="AT+CGSN"
				response = self.send_command(command)
				if(response):
					return response
				else:
					return None
		except Exception as Ex:
			print (f"[SIM] get_imei function Error \n {Ex}")
			return None
#Modem Control
	def get_sms_list(self):
		try:
			response = self.send_command(
				"AT+CMGL=4",
				expected=None,
				timeout=3
			)

			if response:
				print("All message")
				return response

			print("[SIM] No SMS response")
			return ""

		except Exception as ex:
			print(f"[SIM] get_sms_list error: {ex}")
			return ""
	def unread_messages(self):
		try:
			command=f'AT+CMGL="REC UNREAD"'
			response=self.send_command(command)
			if(response):
				return response
			else:
				return None
		except Exception as ex:
			return ex
	def read_sms(self,index):
		try:
			if(self.check_connection()):
				command=f'AT+CMGR={index}'
				response=self.send_command(command)
				if(response):
					print(f"message {index} ready")
					return response
				else:
					return None
		except Exception as ex:
			print(ex)
			return None
	def delete_sms(self, index):
		try:
			if not self.check_connection():
				print(f"[SIM] Cannot delete SMS {index}: not connected")
				return False

			command = f'AT+CMGD={index}'
			response = self.send_command(command, expected="OK")

			if response:
				print(f"[SIM] Message {index} deleted")
				return True

			print(f"[SIM] Failed to delete message {index}")
			return False

		except Exception as ex:
			print(f"[SIM] Delete SMS error: {ex}")
			return False
	def delete_sms_all(self):
		if(self.check_connection()):
			command='AT+CMGD=1,4'
			response=self.send_command(command)
			if(response):
				print(f"All message deleted")
				return response
			else:
				return None
	def delete_sms_read(self):
		if(self.check_connection()):
			command='AT+CMGD=0,1'
			response=self.send_command(command)
			if(response):
				print(f"All message reading deleted")
				return response
			else:
				return None
	def delete_sms_unread(self):
		if(self.check_connection()):
			command='AT+CMGD=0,2'
			response=self.send_command(command)
			if(response):
				print(f"All message unread deleted")
				return response
			else:
				return None
	def delete_sms_send(self):
		if(self.check_connection()):
			command='AT+CMGD=0,3'
			response=self.send_command(command)
			if(response):
				print(f"All message send deleted")
				return response
			else:
				return None
	def send_sms(self, number, text):
		try:
			print("[SMS] send_sms START")

			# Check connection
			if not self.is_connected():
				print("[SMS] Modem is not connected.")
				self.connect()

			print("[SMS] Modem connected.")

			# Encode text to PDU
			pdu_list = self.PDUEncoder(number, text)

			print(f"[SMS] PDU list: {pdu_list}")

			if not pdu_list:
				print("[SMS] PDU encoding failed.")
				return False

			# Set PDU mode
			response = self.send_command(
				"AT+CMGF=0",
				expected="OK"
			)

			print(f"[SMS] CMGF response: {response}")

			if not response:
				print("[SMS] Cannot set PDU mode.")
				return False

			# Send every PDU part
			for part_number, pdu in enumerate(pdu_list, start=1):

				print(
					f"[SMS] Sending part "
					f"{part_number}/{len(pdu_list)}"
				)

				print(f"[SMS] PDU: {pdu}")

				# PDU must be valid HEX
				try:
					pdu_bytes = bytes.fromhex(pdu)
				except ValueError as ex:
					print(f"[SMS] Invalid PDU: {ex}")
					return False

				# SMSC length
				smsc_length = int(pdu[0:2], 16)

				# CMGS expects TPDU length in octets
				tpdu_length = len(pdu_bytes) - 1 - smsc_length

				print(f"[SMS] TPDU length: {tpdu_length}")

				# Clear serial buffer
				self.serial.clear_buffer()

				# Ask modem to receive PDU
				response = self.send_command(
					f"AT+CMGS={tpdu_length}",
					expected=">"
				)

				print(f"[SMS] CMGS response: {response}")

				if not response:
					print("[SMS] Modem did not return >")
					return False

				# Send PDU
				print("[SMS] Sending PDU...")

				self.serial.write_bytes(
					pdu.encode("ascii")
				)

				# CTRL+Z
				print("[SMS] Sending CTRL+Z...")

				self.serial.write_bytes(
					b"\x1A"
				)

				# Wait for modem
				time.sleep(5)

				result = self.serial.read_response(timeout=10)
				if result is False:
					print("[SMS] Failed to read modem response.")
					return False
				
				result = result.decode("utf-8",errors="ignore")

				print(f"[SMS] Final response:\n{result}")

				# Check modem result
				if "+CMGS:" not in result:
					print("[SMS] SMS sending failed.")
					return False
				if "+CMS ERROR" in result:
					print("[SMS] send failed.")
				print(
					f"[SMS] Part {part_number} "
					f"sent successfully."
				)

			print("[SMS] ALL SMS PARTS SENT.")
			return True

		except Exception as ex:
			print(f"[SMS] send_sms ERROR:\n{ex}")
			return False

	def PDUEncoder(self, number, text):
		"""
		Build SMS-SUBMIT PDU.

		Current implementation:
			- UCS2
			- Single-part SMS
			- Multipart SMS
			- Iranian mobile destination
		"""

		try:
			if not text:
				return None

			# -------------------------------------------------
			# Destination Address
			# -------------------------------------------------

			destination_address = self.change_number_to_DA(number)

			if destination_address is None:
				return None

			# -------------------------------------------------
			# SMS-SUBMIT fixed fields
			# -------------------------------------------------

			smsc = "00"
			pdu_type = "01"
			message_reference = "00"
			pid = "00"
			dcs = "08"       # UCS2

			# -------------------------------------------------
			# Single-part SMS
			# -------------------------------------------------

			if len(text) <= 70:

				user_data = text.encode("utf-16-be")

				# Convert bytes -> HEX string
				user_data_hex = user_data.hex().upper()

				# UDL = number of octets
				udl = len(user_data)

				# UDL must be represented as one byte in HEX
				udl_hex = f"{udl:02X}"

				pdu = (
					smsc
					+ pdu_type
					+ message_reference
					+ destination_address
					+ pid
					+ dcs
					+ udl_hex
					+ user_data_hex
				)

				return [pdu]

			# -------------------------------------------------
			# Multipart SMS
			# -------------------------------------------------

			# UCS2 + UDH:
			# 140 octets maximum
			#
			# 6 octets UDH
			# 134 octets remain for text
			# 134 / 2 = 67 UCS2 characters
			#
			# NOTE:
			# The exact UDH length should be verified against
			# the modem/network behavior during testing.
			# -------------------------------------------------

			part_size = 67

			number_of_parts = math.ceil(len(text) / part_size)

			if number_of_parts > 9:
				print("Length of SMS is out of range!")
				return None

			# Concatenation reference
			reference = 0x01

			list_pdu = []

			for part_number in range(1, number_of_parts + 1):

				# Get current text part
				start = (part_number - 1) * part_size
				end = part_number * part_size

				text_part = text[start:end]

				# ---------------------------------------------
				# UDH
				#
				# 05 = UDH length
				# 00 = IEI: concatenated SMS
				# 03 = IE data length
				# XX = reference
				# YY = total parts
				# ZZ = current part
				# ---------------------------------------------

				udh = (
					"05"
					+ "00"
					+ "03"
					+ f"{reference:02X}"
					+ f"{number_of_parts:02X}"
					+ f"{part_number:02X}"
				)

				# Encode text as UCS2
				text_bytes = text_part.encode("utf-16-be")
				text_hex = text_bytes.hex().upper()

				# UDL contains UDH + text
				udl = len(bytes.fromhex(udh)) + len(text_bytes)
				udl_hex = f"{udl:02X}"

				# ---------------------------------------------
				# Complete PDU
				# ---------------------------------------------

				# 01 instead of 11:
				# UDHI bit must be enabled because UDH exists.
				multipart_pdu_type = "41"

				pdu = (
					smsc
					+ multipart_pdu_type
					+ message_reference
					+ destination_address
					+ pid
					+ dcs
					+ udl_hex
					+ udh
					+ text_hex
				)

				list_pdu.append(pdu)

			return list_pdu

		except Exception as ex:
			print("PDUEncoder error:", ex)
			return None
	def change_number_to_DA(self, number):
		try:
			number = str(number).strip()

			if not number:
				return None

			# 09xxxxxxxxx -> 98xxxxxxxxxx
			if number.startswith("0"):
				international_number = "98" + number[1:]
			else:
				international_number = number

			# Iranian mobile number:
			# 989xxxxxxxxx = 12 digits
			if len(international_number) != 12:
				print("[PDU] Invalid Iranian mobile number")
				return None

			# Number of digits in destination address
			address_length = f"{len(international_number):02X}"

			# International number
			type_of_address = "91"

			# Semi-octet encoding
			encoded_number = ""

			for i in range(0, len(international_number), 2):
				pair = international_number[i:i + 2]
				encoded_number += pair[1] + pair[0]

			return (
				address_length
				+ type_of_address
				+ encoded_number
			)

		except Exception as ex:
			print("[PDU] change_number_to_DA error:", ex)
			return None
	def call(self,number):
		pass
	def hangup(self):
		pass

	def get_sim_status(self):
		try:
			Csimcard = self.send_command("AT+CPIN?")
			if(Csimcard and "+CPIN: READY" in Csimcard):
				print("Check SIM: True")
				return True
			else:
				print("Check SIM: False")
				return False
		except Exception as Ex:
			print(Ex)
			return False
			
	def get_signal_quality(self):
		try:
			Csignal = self.send_command("AT+CSQ")
			value=0
			for line in Csignal.splitlines():
				if "+CSQ:" in line:
					value=int(line.split(":")[1].split(",")[0])
			if value==0:
				print("signal status is: No Signal")
				return False
			elif (value > 0 and value < 9):
				print("signal status is: poor")
				return value
			elif (value >= 9  and value < 14):
				print("signal status is: middle")
				return value
			elif (value >= 14  and value < 19):
				print("signal status is: good")
				return value
			elif (value >= 19  and value < 31):
				print("signal status is: perfect")
				return value
			else:
				print("signal status is Unknown")
				return False
		except Exception as Ex:
			print(Ex)
					
	def get_network_registration(self):
		try:
			Cnetwork = self.send_command("AT+CREG?")
			if("+CREG: 0,1" in Cnetwork):
				print("SIM register: True")
				return True
			elif("+CREG: 0,0" in Cnetwork):
				print("SIM register: Not Registered")
				return False
			elif("+CREG: 0,2" in Cnetwork):
				print("SIM register: Searching")
				return False
			elif("+CREG: 0,3" in Cnetwork):
				print("SIM register: Denied")
				return False
			elif("+CREG: 0,4" in Cnetwork):
				print("SIM register: Unknown")
				return False
			elif("+CREG: 0,5" in Cnetwork):
				print("SIM register: Roaming")
				return True
			else:
				print("SIM register: Unknown")
				return False
		except Exception as Ex:
			print(Ex)

	def configure_sms_mode(self):
		try:
			Creading = self.send_command("AT+CMGF=0")
			if (Creading and "OK" in Creading):
				print("pdu mode: True")
				return True
			else:
				print("pdu mode: False")
				return False
		except Exception as Ex:
			print(Ex)
			return False	
	def complete_error(self):
		try:
			Cerror = self.send_command("AT+CMEE=2")
			if("OK" in Cerror):
				print("Error details: True")
				return True
			else:
				print("Error details: False")
				return False
		except Exception as Ex:
			print(Ex)
			return False
